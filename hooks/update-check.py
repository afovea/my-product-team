#!/usr/bin/env python3
"""SessionStart hook: say once a day when a newer product-team release exists.

Wired from hooks/hooks.json for new sessions only. Compares the installed
plugin's version with the newest `vX.Y.Z` release tag on the plugin's GitHub
repository, and shows one line when the release is newer. It never blocks,
never changes anything, and reads nothing from the remote but tag names.

  checked at most once every 24 hours; the answer is kept in
    $XDG_CACHE_HOME/product-team/update-check.json (default ~/.cache/...)
  silent when offline, when git is missing, when up to date, and in CI
  switched off with PRODUCT_TEAM_NO_UPDATE_CHECK=1

Exit 0 always: a failed check must never get in the way of a session.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

CHECK_EVERY = 24 * 60 * 60     # seconds between remote checks
TIMEOUT = 5                    # seconds to wait for the remote
MARKETPLACE = "productteam-skills"
FALLBACK_REPO = "https://github.com/afovea/my-product-team"
TAG = re.compile(r"refs/tags/v(\d+)\.(\d+)\.(\d+)$")


def plugin_root() -> Path:
    for var in ("CLAUDE_PLUGIN_ROOT", "PLUGIN_ROOT"):
        root = os.environ.get(var)
        if root and Path(root).is_dir():
            return Path(root)
    return Path(__file__).resolve().parent.parent


def installed(root: Path) -> tuple[tuple[int, int, int] | None, str]:
    """The installed version, and the repository page to point people at."""
    version, repo = None, FALLBACK_REPO
    for manifest in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
        try:
            data = json.loads((root / manifest).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        version = version or parse(data.get("version", ""))
        if str(data.get("homepage", "")).startswith("https://github.com/"):
            repo = data["homepage"].rstrip("/")
    return version, repo


def parse(text: str) -> tuple[int, int, int] | None:
    m = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", str(text).strip())
    return tuple(int(x) for x in m.groups()) if m else None


def newest_tag(ls_remote_output: str) -> tuple[int, int, int] | None:
    found = [tuple(int(x) for x in m.groups())
             for m in (TAG.search(line) for line in ls_remote_output.splitlines()) if m]
    return max(found) if found else None


def remote_latest(repo: str) -> tuple[int, int, int] | None:
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_ASKPASS="true")
    try:
        proc = subprocess.run(["git", "ls-remote", "--tags", "--refs", repo + ".git"],
                              capture_output=True, text=True, timeout=TIMEOUT, env=env)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return newest_tag(proc.stdout) if proc.returncode == 0 else None


def cache_file() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "product-team" / "update-check.json"


def latest(repo: str, now: float) -> tuple[int, int, int] | None:
    """The newest release, from the cache when it is under a day old."""
    path = cache_file()
    try:
        cached = json.loads(path.read_text(encoding="utf-8"))
        if cached.get("repo") == repo and now - float(cached.get("checkedAt", 0)) < CHECK_EVERY:
            return parse(cached.get("latest") or "")
    except (OSError, ValueError, json.JSONDecodeError):
        pass
    found = remote_latest(repo)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        # A failed check is cached too, so an offline machine is not retried every session.
        path.write_text(json.dumps({"checkedAt": now, "repo": repo,
                                    "latest": ".".join(map(str, found)) if found else None}),
                        encoding="utf-8")
    except OSError:
        pass
    return found


def message(have: tuple[int, int, int], new: tuple[int, int, int], repo: str) -> str:
    h, n = ".".join(map(str, have)), ".".join(map(str, new))
    return (f"product-team {n} is available (you have {h}). In Claude Code, run "
            f"/plugin marketplace update {MARKETPLACE}, then update product-team from /plugin. "
            f"What changed: {repo}/tags. Turn this reminder off with PRODUCT_TEAM_NO_UPDATE_CHECK=1.")


def main() -> int:
    if os.environ.get("PRODUCT_TEAM_NO_UPDATE_CHECK") or os.environ.get("CI"):
        return 0
    have, repo = installed(plugin_root())
    if not have:
        return 0
    new = latest(repo, time.time())
    if new and new > have:
        sys.stdout.write(json.dumps({"systemMessage": message(have, new, repo)}))
    return 0


def _selfcheck() -> None:
    out = "abc\trefs/tags/v1.1.0\ndef\trefs/tags/v1.8.0\nghi\trefs/tags/v1.10.0\njkl\trefs/tags/release-2\n"
    assert newest_tag(out) == (1, 10, 0), "versions compare as numbers, not text"
    assert newest_tag("") is None and parse("1.8.0") == (1, 8, 0) and parse("v2.0.1") == (2, 0, 1)
    assert parse("1.8") is None
    assert "1.9.0" in message((1, 8, 0), (1, 9, 0), FALLBACK_REPO)


if __name__ == "__main__":
    try:
        _selfcheck()
        sys.exit(main())
    except Exception:  # noqa: BLE001 - a broken check must never break a session
        sys.exit(0)
