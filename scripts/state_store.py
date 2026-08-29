#!/usr/bin/env python3
"""Manage private persistent state for Obsidian Vault Curator.

The state directory is intentionally outside the Skill repository. This helper
uses only the Python standard library and never stores authentication secrets.
"""

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
LOCK_REL = Path("locks/github-write.lock")
METHOD_REL = Path("methods/note-system.json")

DEFAULT_PROFILE = {
    "schema_version": 1,
    "vault": {"repository": "", "branch": "", "root": ""},
    "write": {
        "mode": "branch_pr",
        "batch_max_files": 10,
        "branch_prefix": "obsidian-curator/",
        "merge_method": "squash",
        "auto_merge_safe_batches": True,
        "auto_merge_risky_changes": False,
        "allow_direct_write": False,
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
    root = Path(raw).expanduser() if raw else Path.home() / APP_DIR
    return root.resolve()


def ensure_safe_state_root(root: Path) -> None:
    skill_root = Path(__file__).resolve().parents[1]
    try:
        root.relative_to(skill_root)
    except ValueError:
        return
    raise ValueError("private state directory must be outside the Skill directory")


def ensure_root(root: Path) -> None:
    ensure_safe_state_root(root)
    root.mkdir(parents=True, exist_ok=True)
    try:
        root.chmod(0o700)
    except OSError:
        pass
    for rel in ("profiles", "runtime", "cache", "methods", "locks"):
        path = root / rel
        path.mkdir(parents=True, exist_ok=True)
        try:
            path.chmod(0o700)
        except OSError:
            pass


def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        try:
            os.chmod(tmp_name, 0o600)
        except OSError:
            pass
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def load_profile(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"profile not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict) or not data.get("vault", {}).get("repository"):
        raise ValueError("profile is missing vault.repository")
    return data


def redact_repo(value: str) -> str:
    return "<stored privately>" if value else "<not-bound>"


def cmd_init(args: argparse.Namespace) -> int:
    root = state_root()
    ensure_root(root)
    profile_path = root / PROFILE_REL
    if profile_path.exists() and not args.force:
        print(f"profile already exists: {profile_path}", file=sys.stderr)
        return 2
    profile = json.loads(json.dumps(DEFAULT_PROFILE))
    profile["vault"]["repository"] = args.repository.strip()
    profile["vault"]["branch"] = args.branch.strip()
    profile["vault"]["root"] = args.root.strip().strip("/")
    atomic_write_json(profile_path, profile)
    print(f"initialized private profile at {profile_path}")
    return 0


def cmd_read(_: argparse.Namespace) -> int:
    root = state_root()
    ensure_safe_state_root(root)
    profile = load_profile(root / PROFILE_REL)
    print(json.dumps(profile, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = state_root()
    ensure_safe_state_root(root)
    profile_path = root / PROFILE_REL
    result = {"state_root": str(root), "profile_exists": profile_path.exists()}
    if profile_path.exists():
        try:
            profile = load_profile(profile_path)
            repo = profile["vault"].get("repository", "")
            result["repository"] = repo if args.reveal_repository else redact_repo(repo)
            result["branch"] = profile["vault"].get("branch", "") or "<repository-default>"
            result["root"] = profile["vault"].get("root", "")
        except Exception as exc:
            result["profile_error"] = str(exc)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def cmd_set(args: argparse.Namespace) -> int:
    root = state_root()
    ensure_safe_state_root(root)
    path = root / PROFILE_REL
    profile = load_profile(path)
    if args.repository is not None:
        profile["vault"]["repository"] = args.repository.strip()
    if args.branch is not None:
        profile["vault"]["branch"] = args.branch.strip()
    if args.root is not None:
        profile["vault"]["root"] = args.root.strip().strip("/")
    if args.allow_direct_write is not None:
        profile["write"]["allow_direct_write"] = args.allow_direct_write
    atomic_write_json(path, profile)
    print("updated private profile")
    return 0


def validate_methodology(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValueError("methodology must be a JSON object")
    if int(data.get("schema_version", 0)) < 1:
        raise ValueError("methodology is missing a valid schema_version")
    strategy = data.get("strategy")
    if not isinstance(strategy, dict) or not strategy:
        raise ValueError("methodology is missing strategy")
    forbidden = {"repository", "token", "password", "cookie", "ssh_private_key", "note_body", "raw_content"}

    def walk(value, path=""):
        if isinstance(value, dict):
            for key, child in value.items():
                key_l = str(key).lower()
                if key_l in forbidden:
                    raise ValueError(f"methodology contains forbidden field: {path + str(key)}")
                walk(child, path + str(key) + ".")
        elif isinstance(value, list):
            for child in value:
                walk(child, path)

    walk(data)
    encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
    if len(encoded) > 262144:
        raise ValueError("methodology file is too large")
    return data


def cmd_method_read(_: argparse.Namespace) -> int:
    root = state_root()
    ensure_safe_state_root(root)
    path = root / METHOD_REL
    if not path.exists():
        raise FileNotFoundError(f"methodology not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = validate_methodology(json.load(fh))
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def cmd_method_status(_: argparse.Namespace) -> int:
    root = state_root()
    ensure_safe_state_root(root)
    path = root / METHOD_REL
    result = {"methodology_exists": path.exists()}
    if path.exists():
        try:
            data = validate_methodology(json.loads(path.read_text(encoding="utf-8")))
            result["schema_version"] = data.get("schema_version")
            result["strategy_name"] = data.get("strategy", {}).get("name", "<unnamed>")
            result["note_type_count"] = len(data.get("note_types", [])) if isinstance(data.get("note_types", []), list) else 0
        except Exception as exc:
            result["methodology_error"] = str(exc)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def cmd_method_write(args: argparse.Namespace) -> int:
    root = state_root()
    ensure_root(root)
    source = Path(args.file).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"methodology input not found: {source}")
    with source.open("r", encoding="utf-8") as fh:
        data = validate_methodology(json.load(fh))
    atomic_write_json(root / METHOD_REL, data)
    print("updated private note methodology")
    return 0


def cmd_method_clear(_: argparse.Namespace) -> int:
    root = state_root()
    ensure_safe_state_root(root)
    (root / METHOD_REL).unlink(missing_ok=True)
    print("cleared private note methodology")
    return 0


def cmd_lock_acquire(args: argparse.Namespace) -> int:
    root = state_root()
    ensure_root(root)
    lock_path = root / LOCK_REL
    now = int(time.time())
    if lock_path.exists():
        try:
            age = now - int(json.loads(lock_path.read_text(encoding="utf-8")).get("created_at", now))
        except Exception:
            age = 0
        if age < args.stale_after:
            print("write lock is already active", file=sys.stderr)
            return 3
        lock_path.unlink(missing_ok=True)
    payload = {"created_at": now, "pid": os.getpid()}
    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        print("write lock acquisition raced with another task", file=sys.stderr)
        return 3
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)
        fh.write("\n")
    print(f"acquired write lock: {lock_path}")
    return 0


def cmd_lock_release(_: argparse.Namespace) -> int:
    root = state_root()
    ensure_safe_state_root(root)
    lock_path = root / LOCK_REL
    lock_path.unlink(missing_ok=True)
    print("released write lock")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="create the external private profile")
    p.add_argument("--repository", required=True)
    p.add_argument("--branch", default="")
    p.add_argument("--root", default="")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("read", help="print the full private profile for Skill use")
    p.set_defaults(func=cmd_read)

    p = sub.add_parser("status", help="show redacted state diagnostics")
    p.add_argument("--reveal-repository", action="store_true")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("set", help="update selected private profile fields")
    p.add_argument("--repository")
    p.add_argument("--branch")
    p.add_argument("--root")
    p.add_argument("--allow-direct-write", dest="allow_direct_write", action="store_true")
    p.add_argument("--no-direct-write", dest="allow_direct_write", action="store_false")
    p.set_defaults(allow_direct_write=None, func=cmd_set)

    p = sub.add_parser("method-read", help="print the private note methodology")
    p.set_defaults(func=cmd_method_read)

    p = sub.add_parser("method-status", help="show redacted note methodology status")
    p.set_defaults(func=cmd_method_status)

    p = sub.add_parser("method-write", help="replace the private note methodology from a JSON file")
    p.add_argument("--file", required=True)
    p.set_defaults(func=cmd_method_write)

    p = sub.add_parser("method-clear", help="remove the private note methodology")
    p.set_defaults(func=cmd_method_clear)

    p = sub.add_parser("lock-acquire", help="acquire the private GitHub write lock")
    p.add_argument("--stale-after", type=int, default=1800)
    p.set_defaults(func=cmd_lock_acquire)

    p = sub.add_parser("lock-release", help="release the private GitHub write lock")
    p.set_defaults(func=cmd_lock_release)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.func(args))
    except (FileNotFoundError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
