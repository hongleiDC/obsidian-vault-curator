#!/usr/bin/env python3
"""Persist compact cross-conversation project progress outside the Skill repository."""
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
import time
from pathlib import Path

APP_DIR = ".obsidian-vault-curator"
CHECKLIST_STATUSES = ("pending", "in_progress", "blocked", "done")
CHECKLIST_PRIORITIES = ("high", "medium", "low")


def state_root() -> Path:
    raw = os.environ.get("OBSIDIAN_CURATOR_STATE_DIR", "").strip()
    return (Path(raw).expanduser() if raw else Path.home() / APP_DIR).resolve()


def ensure_root(root: Path) -> None:
    skill_root = Path(__file__).resolve().parents[1]
    try:
        root.relative_to(skill_root)
        raise ValueError("private project state must be outside the Skill directory")
    except ValueError as exc:
        if str(exc).startswith("private project state"):
            raise
    root.mkdir(parents=True, exist_ok=True)
    (root / "projects").mkdir(parents=True, exist_ok=True)
    for path in (root, root / "projects"):
        try:
            path.chmod(0o700)
        except OSError:
            pass


def atomic_write(path: Path, data: dict) -> None:
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
        raise ValueError("project state must be a JSON object")
    return data


def valid_id(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", value):
        raise ValueError("project id must use letters, digits, dot, underscore or hyphen")
    return value.lower()


def index_path(root: Path) -> Path:
    return root / "projects" / "index.json"


def project_path(root: Path, pid: str) -> Path:
    return root / "projects" / f"{valid_id(pid)}.json"


def load_index(root: Path) -> dict:
    path = index_path(root)
    return read_json(path) if path.exists() else {"schema_version": 1, "active_project_id": "", "projects": {}}


def save_index(root: Path, data: dict) -> None:
    atomic_write(index_path(root), data)


def empty_checklist() -> dict:
    return {"scope": "", "status": "empty", "items": [], "updated_at": 0}


def ensure_checklist(data: dict) -> dict:
    checklist = data.setdefault("modification_checklist", empty_checklist())
    checklist.setdefault("scope", "")
    checklist.setdefault("status", "empty")
    checklist.setdefault("items", [])
    checklist.setdefault("updated_at", 0)
    if not isinstance(checklist["items"], list):
        raise ValueError("modification_checklist.items must be a list")
    return checklist


def refresh_checklist_status(checklist: dict) -> None:
    items = checklist.get("items", [])
    if not items:
        checklist["status"] = "empty"
    elif all(item.get("status") == "done" for item in items):
        checklist["status"] = "done"
    else:
        checklist["status"] = "active"
    checklist["updated_at"] = int(time.time())


def next_checklist_id(checklist: dict) -> str:
    highest = 0
    for item in checklist.get("items", []):
        match = re.fullmatch(r"C(\d{3,})", str(item.get("id", "")))
        if match:
            highest = max(highest, int(match.group(1)))
    return f"C{highest + 1:03d}"


def checklist_item(checklist: dict, item_id: str) -> dict:
    wanted = item_id.strip().upper()
    for item in checklist.get("items", []):
        if str(item.get("id", "")).upper() == wanted:
            return item
    raise ValueError(f"unknown checklist item: {item_id}")


def add_checklist_item(checklist: dict, text: str, priority: str = "medium", depends_on: list[str] | None = None) -> dict:
    clean = text.strip()
    if not clean:
        raise ValueError("checklist item text is required")
    deps = []
    for dep in depends_on or []:
        dep_id = dep.strip().upper()
        checklist_item(checklist, dep_id)
        if dep_id not in deps:
            deps.append(dep_id)
    item = {
        "id": next_checklist_id(checklist),
        "text": clean,
        "status": "pending",
        "priority": priority,
        "depends_on": deps,
        "note": "",
    }
    checklist.setdefault("items", []).append(item)
    refresh_checklist_status(checklist)
    return item


def validate_project(data: dict) -> dict:
    required = ("project_id", "project_name")
    if any(not str(data.get(key, "")).strip() for key in required):
        raise ValueError("project_id and project_name are required")
    forbidden = {"token", "password", "cookie", "ssh_private_key", "note_body", "raw_content"}

    def walk(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if str(key).lower() in forbidden:
                    raise ValueError(f"forbidden project-state field: {key}")
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    ensure_checklist(data)
    walk(data)
    if len(json.dumps(data, ensure_ascii=False).encode()) > 262144:
        raise ValueError("project state is too large")
    return data


def resolve(root: Path, pid: str | None) -> str:
    index = load_index(root)
    result = (pid or index.get("active_project_id") or "").strip()
    if not result:
        raise ValueError("no active project")
    return valid_id(result)


def save_project(root: Path, pid: str, data: dict) -> None:
    data["updated_at"] = int(time.time())
    validate_project(data)
    atomic_write(project_path(root, pid), data)
    index = load_index(root)
    index.setdefault("projects", {})[pid] = {
        "name": data["project_name"],
        "aliases": data.get("aliases", []),
        "status": data.get("status", "active"),
        "updated_at": data["updated_at"],
    }
    index["active_project_id"] = pid
    save_index(root, index)


def load_project(root: Path, pid: str) -> dict:
    return validate_project(read_json(project_path(root, pid)))


def cmd_init(args):
    root = state_root()
    ensure_root(root)
    pid = valid_id(args.id)
    path = project_path(root, pid)
    if path.exists() and not args.force:
        raise ValueError(f"project already exists: {pid}")
    now = int(time.time())
    data = {
        "schema_version": 1,
        "project_id": pid,
        "project_name": args.name.strip(),
        "aliases": args.alias or [],
        "status": "active",
        "phase": args.phase or "",
        "current_focus": args.focus or "",
        "completed": [],
        "next_actions": [],
        "blockers": [],
        "decisions": [],
        "working_set": {"note_paths": [], "folders": []},
        "intent": {"status": "ready", "summary": "", "pending_questions": [], "confirmed_at": 0},
        "modification_checklist": empty_checklist(),
        "last_github": {"pr_number": None, "merge_commit": "", "branch": ""},
        "created_at": now,
        "updated_at": now,
    }
    validate_project(data)
    atomic_write(path, data)
    index = load_index(root)
    index.setdefault("projects", {})[pid] = {
        "name": data["project_name"],
        "aliases": data["aliases"],
        "status": "active",
        "updated_at": now,
    }
    index["active_project_id"] = pid
    save_index(root, index)
    print(f"initialized project: {pid}")


def cmd_list(args):
    root = state_root()
    ensure_root(root)
    print(json.dumps(load_index(root), ensure_ascii=False, indent=2, sort_keys=True))


def cmd_use(args):
    root = state_root()
    ensure_root(root)
    index = load_index(root)
    pid = valid_id(args.id)
    if pid not in index.get("projects", {}):
        raise ValueError(f"unknown project: {pid}")
    index["active_project_id"] = pid
    save_index(root, index)
    print(f"active project: {pid}")


def cmd_read(args):
    root = state_root()
    ensure_root(root)
    pid = resolve(root, args.id)
    print(json.dumps(load_project(root, pid), ensure_ascii=False, indent=2, sort_keys=True))


def cmd_status(args):
    root = state_root()
    ensure_root(root)
    pid = resolve(root, args.id)
    data = load_project(root, pid)
    keys = (
        "project_id",
        "project_name",
        "status",
        "phase",
        "current_focus",
        "completed",
        "next_actions",
        "blockers",
        "decisions",
        "intent",
        "modification_checklist",
        "last_github",
        "updated_at",
    )
    print(json.dumps({key: data.get(key) for key in keys}, ensure_ascii=False, indent=2, sort_keys=True))


def cmd_update(args):
    root = state_root()
    ensure_root(root)
    pid = resolve(root, args.id)
    data = load_project(root, pid)
    for key, value in (("phase", args.phase), ("current_focus", args.focus), ("status", args.status)):
        if value is not None:
            data[key] = value.strip() if isinstance(value, str) else value
    for key, values in (
        ("completed", args.completed),
        ("next_actions", args.next_action),
        ("blockers", args.blocker),
        ("decisions", args.decision),
    ):
        if values:
            data.setdefault(key, []).extend(value.strip() for value in values if value.strip())
    if args.clear_next:
        data["next_actions"] = []
    if args.clear_blockers:
        data["blockers"] = []

    intent = data.setdefault("intent", {"status": "ready", "summary": "", "pending_questions": [], "confirmed_at": 0})
    if args.intent_status is not None:
        intent["status"] = args.intent_status
    if args.intent_summary is not None:
        intent["summary"] = args.intent_summary.strip()
    if args.clear_pending_questions:
        intent["pending_questions"] = []
    if args.pending_question:
        intent.setdefault("pending_questions", []).extend(value.strip() for value in args.pending_question if value.strip())
        intent["status"] = "needs_clarification"
    if args.confirm_intent:
        intent["status"] = "ready"
        intent["pending_questions"] = []
        intent["confirmed_at"] = int(time.time())

    github = data.setdefault("last_github", {})
    if args.pr_number is not None:
        github["pr_number"] = args.pr_number
    if args.merge_commit is not None:
        github["merge_commit"] = args.merge_commit.strip()
    if args.branch is not None:
        github["branch"] = args.branch.strip()

    save_project(root, pid, data)
    print(f"updated project: {pid}")


def cmd_checklist_start(args):
    root = state_root()
    ensure_root(root)
    pid = resolve(root, args.id)
    data = load_project(root, pid)
    current = ensure_checklist(data)
    unfinished = [item for item in current.get("items", []) if item.get("status") != "done"]
    if unfinished and not args.force:
        raise ValueError("unfinished modification checklist exists; resume it or use --force only after task-scope clarification")
    checklist = empty_checklist()
    checklist["scope"] = args.scope.strip()
    if not checklist["scope"]:
        raise ValueError("checklist scope is required")
    for text in args.item:
        add_checklist_item(checklist, text, priority="medium")
    data["modification_checklist"] = checklist
    save_project(root, pid, data)
    print(json.dumps(checklist, ensure_ascii=False, indent=2, sort_keys=True))


def cmd_checklist_add(args):
    root = state_root()
    ensure_root(root)
    pid = resolve(root, args.id)
    data = load_project(root, pid)
    checklist = ensure_checklist(data)
    if not checklist.get("scope"):
        raise ValueError("no active modification checklist; start one first")
    item = add_checklist_item(checklist, args.item, args.priority, args.depends_on)
    save_project(root, pid, data)
    print(json.dumps(item, ensure_ascii=False, indent=2, sort_keys=True))


def cmd_checklist_update(args):
    root = state_root()
    ensure_root(root)
    pid = resolve(root, args.id)
    data = load_project(root, pid)
    checklist = ensure_checklist(data)
    item = checklist_item(checklist, args.item_id)
    if args.status is not None:
        if args.status == "done":
            unfinished_deps = []
            for dep_id in item.get("depends_on", []):
                dep = checklist_item(checklist, dep_id)
                if dep.get("status") != "done":
                    unfinished_deps.append(dep_id)
            if unfinished_deps:
                raise ValueError(f"cannot mark {item['id']} done; unfinished dependencies: {', '.join(unfinished_deps)}")
        item["status"] = args.status
    if args.note is not None:
        item["note"] = args.note.strip()
    refresh_checklist_status(checklist)
    save_project(root, pid, data)
    print(json.dumps(item, ensure_ascii=False, indent=2, sort_keys=True))


def cmd_checklist_status(args):
    root = state_root()
    ensure_root(root)
    pid = resolve(root, args.id)
    data = load_project(root, pid)
    print(json.dumps(ensure_checklist(data), ensure_ascii=False, indent=2, sort_keys=True))


def parser():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    command = sub.add_parser("init")
    command.add_argument("--id", required=True)
    command.add_argument("--name", required=True)
    command.add_argument("--alias", action="append")
    command.add_argument("--phase")
    command.add_argument("--focus")
    command.add_argument("--force", action="store_true")
    command.set_defaults(func=cmd_init)

    command = sub.add_parser("list")
    command.set_defaults(func=cmd_list)

    command = sub.add_parser("use")
    command.add_argument("--id", required=True)
    command.set_defaults(func=cmd_use)

    for name, func in (("read", cmd_read), ("status", cmd_status)):
        command = sub.add_parser(name)
        command.add_argument("--id")
        command.set_defaults(func=func)

    command = sub.add_parser("update")
    command.add_argument("--id")
    command.add_argument("--phase")
    command.add_argument("--focus")
    command.add_argument("--status", choices=["active", "paused", "done", "archived"])
    command.add_argument("--completed", action="append")
    command.add_argument("--next-action", action="append")
    command.add_argument("--blocker", action="append")
    command.add_argument("--decision", action="append")
    command.add_argument("--clear-next", action="store_true")
    command.add_argument("--clear-blockers", action="store_true")
    command.add_argument("--intent-status", choices=["ready", "needs_clarification"])
    command.add_argument("--intent-summary")
    command.add_argument("--pending-question", action="append")
    command.add_argument("--clear-pending-questions", action="store_true")
    command.add_argument("--confirm-intent", action="store_true")
    command.add_argument("--pr-number", type=int)
    command.add_argument("--merge-commit")
    command.add_argument("--branch")
    command.set_defaults(func=cmd_update)

    command = sub.add_parser("checklist-start")
    command.add_argument("--id")
    command.add_argument("--scope", required=True)
    command.add_argument("--item", action="append", required=True)
    command.add_argument("--force", action="store_true")
    command.set_defaults(func=cmd_checklist_start)

    command = sub.add_parser("checklist-add")
    command.add_argument("--id")
    command.add_argument("--item", required=True)
    command.add_argument("--priority", choices=CHECKLIST_PRIORITIES, default="medium")
    command.add_argument("--depends-on", action="append")
    command.set_defaults(func=cmd_checklist_add)

    command = sub.add_parser("checklist-update")
    command.add_argument("--id")
    command.add_argument("--item-id", required=True)
    command.add_argument("--status", choices=CHECKLIST_STATUSES)
    command.add_argument("--note")
    command.set_defaults(func=cmd_checklist_update)

    command = sub.add_parser("checklist-status")
    command.add_argument("--id")
    command.set_defaults(func=cmd_checklist_status)
    return parser


def main():
    try:
        args = parser().parse_args()
        args.func(args)
        return 0
    except (ValueError, FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        print(f"error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
