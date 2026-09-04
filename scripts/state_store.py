#!/usr/bin/env python3
"""Manage private persistent state for Obsidian Vault Curator."""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

APP_DIR = ".obsidian-vault-curator"
PROFILE_REL = Path("profiles/default.json")
METHOD_REL = Path("methods/note-system.json")
LOCK_REL = Path("locks/github-write.lock")

DEFAULT_PROFILE = {
    "schema_version": 2,
    "vault": {"repository": "", "branch": "", "root": ""},
    "write": {
        "mode": "pr_only",
        "batch_max_files": 10,
        "branch_prefix": "obsidian-curator/",
        "merge_method": "squash",
        "auto_merge_after_validation": True,
        "delete_branch_after_merge": True,
        "require_cleanup_capability": True,
        "retry_limit": 1,
        "verify_after_write": True,
        "atomic_batch_commit": True,
        "commit_prefix": "docs(obsidian)",
    },
    "safety": {
        "allow_create_notes": True,
        "allow_delete_notes": False,
        "allow_rename_or_move": False,
        "allow_binary_attachment_changes": False,
    },
}


def state_root() -> Path:
    raw = os.environ.get("OBSIDIAN_CURATOR_STATE_DIR", "").strip()
    return (Path(raw).expanduser() if raw else Path.home() / APP_DIR).resolve()


def ensure_safe_root(root: Path) -> None:
    skill_root = Path(__file__).resolve().parents[1]
    try:
        root.relative_to(skill_root)
    except ValueError:
        return
    raise ValueError("private state directory must be outside the Skill directory")


def ensure_root(root: Path) -> None:
    ensure_safe_root(root)
    root.mkdir(parents=True, exist_ok=True)
    for rel in ("profiles", "runtime", "cache", "methods", "projects", "locks"):
        (root / rel).mkdir(parents=True, exist_ok=True)
    for path in [root, *(root / x for x in ("profiles", "runtime", "cache", "methods", "projects", "locks"))]:
        try:
            path.chmod(0o700)
        except OSError:
            pass


def atomic_write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        try:
            os.chmod(tmp, 0o600)
        except OSError:
            pass
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def normalize_profile(data: dict) -> dict:
    if not data.get("vault", {}).get("repository"):
        raise ValueError("profile is missing vault.repository")
    write = data.setdefault("write", {})
    defaults = DEFAULT_PROFILE["write"]
    for key, value in defaults.items():
        write.setdefault(key, value)
    write.update({
        "mode": "pr_only",
        "merge_method": "squash",
        "auto_merge_after_validation": True,
        "delete_branch_after_merge": True,
        "require_cleanup_capability": True,
    })
    for old in ("allow_direct_write", "auto_merge_safe_batches", "auto_merge_risky_changes"):
        write.pop(old, None)
    data["schema_version"] = max(int(data.get("schema_version", 1)), 2)
    data.setdefault("safety", DEFAULT_PROFILE["safety"].copy())
    return data


def profile_path(root: Path) -> Path:
    return root / PROFILE_REL


def load_profile(root: Path) -> dict:
    return normalize_profile(read_json(profile_path(root)))


def cmd_init(args: argparse.Namespace) -> int:
    root = state_root(); ensure_root(root)
    path = profile_path(root)
    if path.exists() and not args.force:
        raise ValueError(f"profile already exists: {path}")
    data = json.loads(json.dumps(DEFAULT_PROFILE))
    data["vault"] = {
        "repository": args.repository.strip(),
        "branch": args.branch.strip(),
        "root": args.root.strip().strip("/"),
    }
    if not data["vault"]["repository"]:
        raise ValueError("repository is required")
    atomic_write(path, data)
    print(f"initialized private profile at {path}")
    return 0


def cmd_read(_: argparse.Namespace) -> int:
    root = state_root(); ensure_safe_root(root)
    print(json.dumps(load_profile(root), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = state_root(); ensure_safe_root(root)
    path = profile_path(root)
    result = {"state_root": str(root), "profile_exists": path.exists()}
    if path.exists():
        p = load_profile(root)
        repo = p["vault"].get("repository", "")
        result.update({
            "repository": repo if args.reveal_repository else "<stored privately>",
            "branch": p["vault"].get("branch") or "<repository-default>",
            "root": p["vault"].get("root", ""),
            "write_mode": p["write"].get("mode"),
            "auto_merge": p["write"].get("auto_merge_after_validation"),
            "delete_branch_after_merge": p["write"].get("delete_branch_after_merge"),
        })
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def cmd_set(args: argparse.Namespace) -> int:
    root = state_root(); ensure_root(root)
    data = load_profile(root)
    if args.repository is not None:
        data["vault"]["repository"] = args.repository.strip()
    if args.branch is not None:
        data["vault"]["branch"] = args.branch.strip()
    if args.root is not None:
        data["vault"]["root"] = args.root.strip().strip("/")
    atomic_write(profile_path(root), normalize_profile(data))
    print("updated private profile")
    return 0


def validate_methodology(data: dict) -> dict:
    if int(data.get("schema_version", 0)) < 1:
        raise ValueError("methodology requires schema_version")
    if not isinstance(data.get("strategy"), dict):
        raise ValueError("methodology requires strategy object")
    forbidden = {"repository", "token", "password", "cookie", "ssh_private_key", "note_body", "raw_content"}
    def walk(v, path=""):
        if isinstance(v, dict):
            for k, child in v.items():
                if str(k).lower() in forbidden:
                    raise ValueError(f"methodology contains forbidden field: {path}{k}")
                walk(child, f"{path}{k}.")
        elif isinstance(v, list):
            for child in v:
                walk(child, path)
    walk(data)
    if len(json.dumps(data, ensure_ascii=False).encode("utf-8")) > 262144:
        raise ValueError("methodology file is too large")
    return data


def cmd_method_read(_: argparse.Namespace) -> int:
    root = state_root(); ensure_safe_root(root)
    print(json.dumps(validate_methodology(read_json(root / METHOD_REL)), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def cmd_method_status(_: argparse.Namespace) -> int:
    root = state_root(); ensure_safe_root(root)
    path = root / METHOD_REL
    result = {"methodology_exists": path.exists()}
    if path.exists():
        d = validate_methodology(read_json(path))
        org = d.get("organization", {}) if isinstance(d.get("organization"), dict) else {}
        result.update({
            "strategy_name": d.get("strategy", {}).get("name", "<unnamed>"),
            "max_folder_depth": org.get("max_folder_depth"),
            "project_prefix_count": len(org.get("project_prefixes", {})) if isinstance(org.get("project_prefixes"), dict) else 0,
        })
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def cmd_method_write(args: argparse.Namespace) -> int:
    root = state_root(); ensure_root(root)
    source = Path(args.file).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    data = validate_methodology(read_json(source))
    atomic_write(root / METHOD_REL, data)
    print("updated private note methodology")
    return 0


def cmd_method_clear(_: argparse.Namespace) -> int:
    root = state_root(); ensure_safe_root(root)
    (root / METHOD_REL).unlink(missing_ok=True)
    print("cleared private note methodology")
    return 0


def cmd_lock_acquire(args: argparse.Namespace) -> int:
    root = state_root(); ensure_root(root)
    path = root / LOCK_REL
    now = int(time.time())
    if path.exists():
        try:
            age = now - int(read_json(path).get("created_at", now))
        except Exception:
            age = 0
        if age < args.stale_after:
            print("write lock is already active", file=sys.stderr)
            return 3
        path.unlink(missing_ok=True)
    payload = {"created_at": now, "pid": os.getpid()}
    try:
        fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        print("write lock acquisition raced with another task", file=sys.stderr)
        return 3
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(payload, fh); fh.write("\n")
    print(f"acquired write lock: {path}")
    return 0


def cmd_lock_release(_: argparse.Namespace) -> int:
    root = state_root(); ensure_safe_root(root)
    (root / LOCK_REL).unlink(missing_ok=True)
    print("released write lock")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    q = sub.add_parser("init"); q.add_argument("--repository", required=True); q.add_argument("--branch", default=""); q.add_argument("--root", default=""); q.add_argument("--force", action="store_true"); q.set_defaults(func=cmd_init)
    q = sub.add_parser("read"); q.set_defaults(func=cmd_read)
    q = sub.add_parser("status"); q.add_argument("--reveal-repository", action="store_true"); q.set_defaults(func=cmd_status)
    q = sub.add_parser("set"); q.add_argument("--repository"); q.add_argument("--branch"); q.add_argument("--root"); q.set_defaults(func=cmd_set)
    q = sub.add_parser("method-read"); q.set_defaults(func=cmd_method_read)
    q = sub.add_parser("method-status"); q.set_defaults(func=cmd_method_status)
    q = sub.add_parser("method-write"); q.add_argument("--file", required=True); q.set_defaults(func=cmd_method_write)
    q = sub.add_parser("method-clear"); q.set_defaults(func=cmd_method_clear)
    q = sub.add_parser("lock-acquire"); q.add_argument("--stale-after", type=int, default=1800); q.set_defaults(func=cmd_lock_acquire)
    q = sub.add_parser("lock-release"); q.set_defaults(func=cmd_lock_release)
    return p


def main() -> int:
    try:
        args = build_parser().parse_args()
        return int(args.func(args))
    except (ValueError, FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
