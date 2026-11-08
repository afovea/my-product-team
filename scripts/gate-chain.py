#!/usr/bin/env python3
"""Run a project's gate chain and report a machine-readable result.

Standalone: no third-party dependencies, no JavaScript assumptions.
Usable from a skill, from CI, or from the Stop hook in gate-stop.py.

Gate list resolution, first hit wins:
  1. <config>/pipeline-gates.json
  2. <config>/pipeline-adapter.md: a ```gates fenced block, or else the
     `gates: chain:` list in its ```yaml block (reference/project-adapter.md)
  3. discovery from package.json, Makefile, pyproject.toml

Ratchets. A non-blocking gate with a baseline is a ratchet: its exit code is
ignored, the count read from its output must be no worse than the accepted
baseline, and a worse count fails the chain like a blocking gate. A
non-blocking gate without a baseline only reports.

<config> is .claude/ or .agents/ — whichever the project actually uses. See
config_dir().

Subcommands:
  run     [--stamp]  run the chain; on a clean pass optionally write a stamp
  status             exit 0 if a valid stamp exists for the current tree
  gates              print the resolved gate list and exit

Exit codes:
  0  all blocking gates passed (run) / valid stamp present (status)
  1  a blocking gate failed (run) / no valid stamp (status)
  3  configuration problem

A JSON summary is printed to stdout in every case.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_TIMEOUT = 900
GATE_DIR = ".gate"          # everything this tool leaves behind lives here
STAMP_NAME = "stamp.json"


# --------------------------------------------------------------------------
# project resolution
# --------------------------------------------------------------------------

def project_dir() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR")
                or os.environ.get("CODEX_PROJECT_DIR")
                or os.getcwd()).resolve()


def config_dir(root: Path) -> Path:
    """Where the pipeline's declared config and its scratch live.

    `.claude/` is the original home and `.agents/` is the open-standard location
    other SKILL.md hosts use. Whichever actually holds pipeline config wins, so a
    project that has both — a Claude Code settings directory beside an `.agents`
    install, say — still resolves to the one with the adapter in it. Failing
    that, an existing directory; failing that, `.claude/`, which is where a
    fresh Claude install puts things.
    """
    candidates = (root / ".claude", root / ".agents")
    for base in candidates:
        if (base / "pipeline-gates.json").is_file() or (base / "pipeline-adapter.md").is_file():
            return base
    for base in candidates:
        if base.is_dir():
            return base
    return root / ".claude"


# --------------------------------------------------------------------------
# tree fingerprint
# --------------------------------------------------------------------------

def untracked_digest(root: Path) -> str:
    """Hash the contents of untracked files that git is not ignoring.

    `git status` lists untracked paths but never their contents, and
    `git diff HEAD` ignores them altogether. Without this a new file would
    move the fingerprint exactly once — when it first appears — and every
    edit after that would be invisible, leaving a stamp that still vouches
    for code which has since changed. New source files are untracked until
    they are committed, so this is the common case, not the corner case.

    --exclude-standard honours .gitignore, so ignored trees such as
    node_modules are not walked.
    """
    try:
        proc = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "-z"],
            cwd=root, capture_output=True, text=True, timeout=60)
    except (subprocess.SubprocessError, OSError):
        return ""
    if proc.returncode != 0 or not proc.stdout:
        return ""

    digest = hashlib.sha256()
    for name in sorted(n for n in proc.stdout.split("\0") if n):
        digest.update(name.encode("utf-8"))
        try:
            with (root / name).open("rb") as handle:
                for block in iter(lambda: handle.read(65536), b""):
                    digest.update(block)
        except OSError:
            digest.update(b"<unreadable>")  # a path we cannot read still counts
    return digest.hexdigest()


def fingerprint(root: Path) -> str:
    """Identify the working tree, including uncommitted changes.

    Any further edit changes the fingerprint, which invalidates an existing
    stamp. That is deliberate: a gate result only vouches for the tree it
    actually ran against.
    """
    parts: list[str] = []
    if shutil.which("git"):
        for cmd in (["git", "rev-parse", "HEAD"],
                    ["git", "status", "--porcelain=v1", "-uall"],
                    ["git", "diff", "HEAD"]):
            try:
                out = subprocess.run(cmd, cwd=root, capture_output=True,
                                     text=True, timeout=60)
                parts.append(out.stdout)
            except (subprocess.SubprocessError, OSError):
                parts.append("")
        parts.append(untracked_digest(root))
    if not any(parts):
        # No git, or git unusable. Fall back to mtimes of tracked-ish files.
        for path in sorted(root.rglob("*")):
            if any(seg.startswith(".") for seg in path.parts):
                continue
            if path.is_file():
                parts.append(f"{path}:{path.stat().st_mtime_ns}")
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:16]


# --------------------------------------------------------------------------
# gate resolution
# --------------------------------------------------------------------------

def _normalise(raw: list[dict]) -> list[dict]:
    gates = []
    for i, g in enumerate(raw):
        command = g.get("command")
        if not command:
            continue
        gates.append({
            "name": g.get("name") or f"gate-{i + 1}",
            "command": command,
            "blocking": bool(g.get("blocking", True)),
            "timeout": int(g.get("timeout", DEFAULT_TIMEOUT)),
        })
        base = g.get("baseline")
        if isinstance(base, (int, str)) and str(base).isdigit():
            base = {"accepted": int(base)}
        if isinstance(base, dict) and str(base.get("accepted", "")).isdigit():
            gates[-1]["baseline"] = {"accepted": int(base["accepted"]), "read": base.get("read")}
    return gates


def from_config(root: Path) -> list[dict]:
    path = config_dir(root) / "pipeline-gates.json"
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return _normalise(data.get("gates", []))


GATE_LINE = re.compile(r"^(?P<name>.+?)(?:\s*\(baseline\s+(?P<baseline>\d+)\))?:\s+(?P<command>.+)$")


def from_adapter(root: Path) -> list[dict]:
    """Read the gate chain out of the pipeline adapter.

    A ```gates fenced block wins: one gate per line, `name: command` (names
    may contain colons, so the separator is a colon followed by a space), or
    a bare command. A leading `?` marks the gate non-blocking, and
    `?name (baseline 47): command` makes it a ratchet that may not exceed 47.
    Without one, the `gates: chain:` list of the adapter's ```yaml block is
    read instead.
    """
    path = config_dir(root) / "pipeline-adapter.md"
    if not path.is_file():
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    block = re.search(r"^```gates[ \t]*\n(.*?)^```", text, re.S | re.M)
    if not block:
        yaml = re.search(r"^```ya?ml[ \t]*\n(.*?)^```", text, re.S | re.M)
        return _normalise(yaml_chain(yaml.group(1))) if yaml else []
    raw = []
    for line in block.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        blocking = True
        if line.startswith("?"):
            blocking = False
            line = line[1:].strip()
        m = GATE_LINE.match(line)
        if m:
            raw.append({"name": m["name"].strip(), "command": m["command"].strip(),
                        "blocking": blocking, "baseline": m["baseline"]})
        else:
            raw.append({"name": line, "command": line, "blocking": blocking})
    return _normalise(raw)


def _scalar(value: str):
    value = re.sub(r"\s+#.*$", "", value).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    return value


def yaml_chain(text: str) -> list[dict]:
    """The `gates: chain:` list from the adapter's YAML, without a YAML library.

    Reads only the shape project-adapter.md documents: list items under
    `chain:` with `name`, `command`, `blocking`, `timeout`, and a `baseline`
    mapping holding `accepted` and `read`.
    """
    gates, item, in_gates, in_chain, in_base = [], None, False, False, False
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        body = line.strip()
        if indent == 0:
            in_gates, in_chain = body == "gates:", False
            continue
        if not in_gates:
            continue
        if body == "chain:":
            in_chain = True
            continue
        if not in_chain:
            continue
        if body.startswith("- "):
            item, in_base = {}, False
            gates.append(item)
            body = body[2:]
        if item is None or ":" not in body:
            continue
        key, _, value = body.partition(":")
        key, value = key.strip(), value.strip()
        if key == "baseline" and not value:
            in_base, item["baseline"] = True, {}
        elif in_base and key in ("accepted", "read"):
            item["baseline"][key] = _scalar(value)
        else:
            in_base = False
            item[key] = _scalar(value)
    return gates


def discover(root: Path) -> list[dict]:
    """Infer a gate chain when nothing is declared.

    Deliberately conservative and ordered cheapest first. Discovery is a
    fallback, not a substitute for declaring the chain in the adapter.
    """
    raw: list[dict] = []

    pkg = root / "package.json"
    if pkg.is_file():
        try:
            scripts = json.loads(pkg.read_text(encoding="utf-8")).get("scripts", {})
        except (json.JSONDecodeError, OSError):
            scripts = {}
        runner = "npm run"
        if (root / "pnpm-lock.yaml").is_file():
            runner = "pnpm run"
        elif (root / "yarn.lock").is_file():
            runner = "yarn"
        elif (root / "bun.lockb").is_file() or (root / "bun.lock").is_file():
            runner = "bun run"
        for key in ("lint", "typecheck", "type-check", "test", "build"):
            if key in scripts:
                raw.append({"name": key, "command": f"{runner} {key}"})

    if not raw and (root / "Makefile").is_file():
        try:
            text = (root / "Makefile").read_text(encoding="utf-8")
        except OSError:
            text = ""
        targets = set(re.findall(r"^([A-Za-z0-9_-]+):", text, re.M))
        for key in ("lint", "typecheck", "test", "build"):
            if key in targets:
                raw.append({"name": key, "command": f"make {key}"})

    if not raw and (root / "pyproject.toml").is_file():
        if shutil.which("ruff"):
            raw.append({"name": "lint", "command": "ruff check ."})
        if shutil.which("pytest"):
            raw.append({"name": "test", "command": "pytest -q"})

    return _normalise(raw)


def resolve_gates(root: Path) -> tuple[list[dict], str]:
    for source, fn in (("config", from_config),
                       ("adapter", from_adapter),
                       ("discovery", discover)):
        gates = fn(root)
        if gates:
            return gates, source
    return [], "none"


# --------------------------------------------------------------------------
# execution
# --------------------------------------------------------------------------

def tail(text: str, lines: int = 40, limit: int = 4000) -> str:
    out = "\n".join(text.strip().splitlines()[-lines:])
    return out[-limit:]


def run_chain(root: Path, gates: list[dict]) -> dict:
    results = []
    failed = None
    for gate in gates:
        started = time.time()
        try:
            proc = subprocess.run(gate["command"], cwd=root, shell=True,
                                  capture_output=True, text=True,
                                  timeout=gate["timeout"])
            code, out, err = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired:
            code, out, err = 124, "", f"timed out after {gate['timeout']}s"
        except OSError as exc:
            code, out, err = 127, "", str(exc)

        result = {
            "name": gate["name"],
            "command": gate["command"],
            "blocking": gate["blocking"],
            "exit_code": code,
            "passed": code == 0,
            "seconds": round(time.time() - started, 1),
        }
        worse = False
        if not gate["blocking"] and gate.get("baseline"):
            # A ratchet: the exit code is expected to fail; the count decides.
            base = gate["baseline"]
            count = ratchet_count((out or "") + "\n" + (err or ""), base.get("read"), root)
            result["ratchet"] = {"accepted": base["accepted"], "count": count}
            worse = count is None or count > base["accepted"]
            result["passed"] = not worse
        if not result["passed"]:
            result["output"] = tail((out or "") + "\n" + (err or ""))
        results.append(result)

        if (code != 0 and gate["blocking"]) or worse:
            failed = gate["name"]
            break  # stop at the first blocking failure, or a ratchet that got worse

    return {
        "passed": failed is None,
        "failed_gate": failed,
        "gates": results,
    }


def ratchet_count(output: str, read: str | None, root: Path) -> int | None:
    """The count a ratchet compares with its baseline: the last whole number in
    the gate's output, after the baseline's `read` command has filtered it.
    None when no number can be found, which fails the ratchet: an unreadable
    count cannot prove the chain is no worse."""
    if read:
        try:
            output = subprocess.run(read, cwd=root, shell=True, input=output,
                                    capture_output=True, text=True, timeout=60).stdout
        except (subprocess.TimeoutExpired, OSError):
            return None
    numbers = re.findall(r"\d+", output)
    return int(numbers[-1]) if numbers else None


# --------------------------------------------------------------------------
# stamp
# --------------------------------------------------------------------------

def stamp_path(root: Path) -> Path:
    return config_dir(root) / GATE_DIR / STAMP_NAME


def write_stamp(root: Path, summary: dict) -> None:
    path = stamp_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    # The scratch folder ignores itself, so nothing needs adding to the
    # project's own .gitignore.
    ignore = path.parent / ".gitignore"
    if not ignore.is_file():
        ignore.write_text("*\n", encoding="utf-8")
    path.write_text(json.dumps({
        "fingerprint": summary["fingerprint"],
        "stamped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "gates": [g["name"] for g in summary["gates"]],
    }, indent=2) + "\n", encoding="utf-8")


def read_stamp(root: Path) -> dict | None:
    path = stamp_path(root)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "status", "gates"))
    parser.add_argument("--stamp", action="store_true",
                        help="write a gate stamp on a clean pass")
    args = parser.parse_args()

    root = project_dir()
    gates, source = resolve_gates(root)

    if args.command == "gates":
        print(json.dumps({"source": source, "gates": gates}, indent=2))
        return 0

    if args.command == "status":
        stamp = read_stamp(root)
        current = fingerprint(root)
        valid = bool(stamp) and stamp.get("fingerprint") == current
        print(json.dumps({
            "valid": valid,
            "fingerprint": current,
            "stamp": stamp,
        }))
        return 0 if valid else 1

    # run
    if not gates:
        cfg = config_dir(root).name   # name the directory this project uses
        print(json.dumps({
            "passed": False,
            "source": source,
            "error": "No gate chain declared and none discoverable. "
                     f"Add a ```gates block to {cfg}/pipeline-adapter.md "
                     f"or a {cfg}/pipeline-gates.json.",
        }))
        return 3

    summary = run_chain(root, gates)
    summary["source"] = source
    summary["fingerprint"] = fingerprint(root)

    if summary["passed"] and args.stamp:
        write_stamp(root, summary)
        summary["stamped"] = True

    print(json.dumps(summary, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
