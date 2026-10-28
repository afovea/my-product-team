#!/usr/bin/env node
// Render an animation built from assets/template.html to MP4, frame by frame.
//
//   node export.mjs animation.html out.mp4 [--fps 30]
//
// Needs Node 22+ (built-in WebSocket), ffmpeg, and Chrome or Chromium. Set
// CHROME=/path/to/chrome if it is not found. No npm install: it speaks the
// DevTools protocol directly, so the only moving parts are the two binaries.
//
// Frames are drawn by calling window.__anim.render(t) at exact times, never by
// recording real time, so a slow machine produces the same video, only slower.

import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const args = process.argv.slice(2);
const fpsAt = args.indexOf("--fps");
const fps = fpsAt >= 0 ? Number(args.splice(fpsAt, 2)[1]) : 30;
const [input, output = "animation.mp4"] = args;
if (!input || !existsSync(input) || !(fps > 0)) {
  console.error("usage: node export.mjs animation.html out.mp4 [--fps 30]");
  process.exit(1);
}

const chrome = [
  process.env.CHROME,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Chromium.app/Contents/MacOS/Chromium",
  "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
].find(p => p && existsSync(p));
if (!chrome) { console.error("Chrome not found. Set CHROME=/path/to/chrome."); process.exit(1); }
if (typeof WebSocket === "undefined") { console.error("Node 22+ is required."); process.exit(1); }

const profile = mkdtempSync(join(tmpdir(), "motion-export-"));
const browser = spawn(chrome, [
  "--headless=new", "--remote-debugging-port=0", `--user-data-dir=${profile}`,
  "--hide-scrollbars", "--force-device-scale-factor=1", "--no-first-run", "about:blank",
], { stdio: ["ignore", "ignore", "pipe"] });

let ffmpeg;
const cleanup = () => { browser.kill(); ffmpeg?.kill(); rmSync(profile, { recursive: true, force: true }); };
process.on("exit", cleanup);

// Chrome prints its DevTools endpoint on stderr once it is listening.
const port = await new Promise((ok, fail) => {
  let buf = "";
  browser.stderr.on("data", d => { buf += d; const m = buf.match(/ws:\/\/[^:]+:(\d+)\//); if (m) ok(m[1]); });
  browser.on("exit", () => fail(new Error("Chrome exited before it was ready:\n" + buf)));
});

const page = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(t => t.type === "page");
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(ok => ws.addEventListener("open", ok, { once: true }));

let nextId = 0;
const pending = new Map();
ws.addEventListener("message", e => {
  const msg = JSON.parse(e.data);
  if (!pending.has(msg.id)) return;
  const { ok, fail } = pending.get(msg.id); pending.delete(msg.id);
  msg.error ? fail(new Error(msg.error.message)) : ok(msg.result);
});
const send = (method, params = {}) => new Promise((ok, fail) => {
  const id = ++nextId; pending.set(id, { ok, fail }); ws.send(JSON.stringify({ id, method, params }));
});
const evaluate = async (expression) => {
  const r = await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description ?? r.exceptionDetails.text);
  return r.result.value;
};

await send("Page.enable");
const url = pathToFileURL(resolve(input)); url.search = "export";
const loaded = new Promise(ok => ws.addEventListener("message", function on(e) {
  if (JSON.parse(e.data).method === "Page.loadEventFired") { ws.removeEventListener("message", on); ok(); }
}));
await send("Page.navigate", { url: url.href });
await loaded;

const meta = await evaluate("window.__anim ? __anim.ready.then(() => ({ w: __anim.width, h: __anim.height, d: __anim.duration })) : null");
if (!meta) { console.error("No window.__anim on that page — was it built from assets/template.html?"); process.exit(1); }
await send("Emulation.setDeviceMetricsOverride", { width: meta.w, height: meta.h, deviceScaleFactor: 1, mobile: false });

ffmpeg = spawn("ffmpeg", [
  "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(fps), "-i", "-",
  // yuv420p needs even dimensions; the pad is a no-op for every preset size.
  "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p",
  "-crf", "18", "-movflags", "+faststart", output,
], { stdio: ["pipe", "inherit", "inherit"] });
const done = new Promise((ok, fail) => ffmpeg.on("exit", c => c === 0 ? ok() : fail(new Error(`ffmpeg exited ${c}`))));

const frames = Math.round(meta.d * fps);
for (let i = 0; i < frames; i++) {
  await evaluate(`__anim.render(${i / fps})`);
  const { data } = await send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width: meta.w, height: meta.h, scale: 1 } });
  if (!ffmpeg.stdin.write(Buffer.from(data, "base64"))) await new Promise(ok => ffmpeg.stdin.once("drain", ok));
  if (i % fps === 0) process.stdout.write(`\r  ${Math.round(i / frames * 100)}%  frame ${i}/${frames}`);
}
ffmpeg.stdin.end();
await done;
console.log(`\r  wrote ${output}  ${meta.w}×${meta.h}, ${meta.d}s at ${fps}fps`);
process.exit(0);
