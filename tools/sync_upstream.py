#!/usr/bin/env python3
"""Synchronize ManHuaGui source files, preserving the local random-browse patch.

This is a standalone repository, not a Git fork. The upstream build scaffold
is updated manually when needed; this script only syncs src/zh/manhuagui.
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SUBTREE = "src/zh/manhuagui"
BASE = ROOT / "tools" / "upstream-base"
URL = "https://github.com/keiyoushi/extensions-source.git"
DEFAULT_CACHE = ROOT.parent / ".keiyoushi-manhuagui-cache"


def git(*args, cwd=None):
    env = dict(os.environ)
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        env.pop(key, None)
    result = subprocess.run(
        ["git", "-c", "http.proxy=", *map(str, args)], cwd=cwd,
        env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise RuntimeError("Git failed: " + result.stderr.decode("utf-8", "replace")[-500:])
    return result.stdout


def git_tree(cache: Path, rev: str):
    names = git("ls-tree", "-r", "-z", "--name-only", rev, "--", SUBTREE, cwd=cache)
    files = [x.decode("utf-8") for x in names.split(b"\0") if x]
    return {name: git("show", rev + ":" + name, cwd=cache) for name in files}


def merge(local: Path, baseline: Path, upstream: bytes):
    local_bytes = local.read_bytes() if local.exists() else None
    base_bytes = baseline.read_bytes() if baseline.exists() else None
    if base_bytes is None:
        return upstream if local_bytes is None or local_bytes == upstream else None
    if local_bytes is None:
        return None
    if local_bytes == base_bytes:
        return upstream
    if upstream == base_bytes:
        return local_bytes
    if local.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") or b"\0" in local_bytes + base_bytes + upstream:
        return None
    with TemporaryDirectory() as tmp:
        remote_file = Path(tmp) / "upstream"
        remote_file.write_bytes(upstream)
        result = subprocess.run(
            ["git", "merge-file", "-p", "--diff3", str(local), str(baseline), str(remote_file)],
            capture_output=True,
        )
        if result.returncode:
            return None
        return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply after review; default is dry-run")
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE, help="Dedicated upstream checkout")
    parser.add_argument("--offline", action="store_true", help="Use the cache HEAD without a network request")
    args = parser.parse_args()
    cache = args.cache.resolve()
    if cache == ROOT.resolve():
        parser.error("Project cannot be its own upstream cache")
    if not (cache / ".git").is_dir():
        if args.offline:
            parser.error("--offline requires an existing upstream cache")
        if cache.exists():
            parser.error("Cache path already exists but is not a Git checkout")
        print("Cloning Keiyoushi into separate cache:", cache, flush=True)
        git("clone", "--depth", "1", "--filter=blob:none", "--sparse", URL, cache)
    origin = git("remote", "get-url", "origin", cwd=cache).decode().strip()
    if "keiyoushi/extensions-source" not in origin:
        parser.error("Refusing a cache with an unexpected remote: " + origin)
    if args.offline:
        rev = "HEAD"
    else:
        git("fetch", "--depth", "1", "origin", "main", cwd=cache)
        rev = "FETCH_HEAD"
    version = git("rev-parse", rev, cwd=cache).decode().strip()
    remote_files = git_tree(cache, rev)
    old_files = {
        p.relative_to(BASE).as_posix(): p for p in BASE.rglob("*") if p.is_file()
    }
    change_set = {}
    errors = []
    for rel in sorted(set(remote_files) | set(old_files)):
        local = ROOT / rel
        baseline = BASE / rel
        theirs = remote_files.get(rel)
        if theirs is None:
            if local.is_file() and baseline.is_file() and local.read_bytes() == baseline.read_bytes():
                result = None
            else:
                errors.append("Upstream deleted a locally changed file: " + rel)
                continue
        else:
            result = merge(local, baseline, theirs)
            if result is None:
                errors.append("Manual three-way merge needed: " + rel)
                continue
        before = local.read_bytes() if local.is_file() else None
        if before != result:
            change_set[rel] = result
            print(("delete " if result is None else "update ") + rel, flush=True)
    if errors:
        for error in errors:
            print("CONFLICT: " + error, file=sys.stderr)
        print("Nothing was overwritten. Resolve conflicts manually.", file=sys.stderr)
        return 1
    print("Upstream revision:", version)
    print("Proposed file changes:", len(change_set))
    if not args.apply:
        print("Dry-run only. Add --apply to update files.")
        return 0
    for rel, value in change_set.items():
        out = ROOT / rel
        if value is None:
            out.unlink(missing_ok=True)
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(value)
    for rel in sorted(set(remote_files) | set(old_files)):
        out = BASE / rel
        content = remote_files.get(rel)
        if content is None:
            out.unlink(missing_ok=True)
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(content)
    (ROOT / "tools" / "UPSTREAM_REVISION").write_text(version + "\n", encoding="ascii")
    print("Updated. Review diff, build, test, and commit before publishing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
