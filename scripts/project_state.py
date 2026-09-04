#!/usr/bin/env python3
"""Persist compact cross-conversation project progress outside the Skill repository."""
from __future__ import annotations
import argparse, json, os, re, tempfile, time
from pathlib import Path

APP_DIR = ".obsidian-vault-curator"

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
    for p in (root, root / "projects"):
        try: p.chmod(0o700)
        except OSError: pass

def atomic_write(path: Path, data: dict) -> None:
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n"); fh.flush(); os.fsync(fh.fileno())
        try: os.chmod(tmp, 0o600)
        except OSError: pass
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def read_json(path: Path) -> dict:
    if not path.exists(): raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict): raise ValueError("project state must be a JSON object")
    return data

def valid_id(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", value):
        raise ValueError("project id must use letters, digits, dot, underscore or hyphen")
    return value.lower()

def index_path(root: Path) -> Path: return root / "projects" / "index.json"
def project_path(root: Path, pid: str) -> Path: return root / "projects" / f"{valid_id(pid)}.json"

def load_index(root: Path) -> dict:
    p = index_path(root)
    return read_json(p) if p.exists() else {"schema_version": 1, "active_project_id": "", "projects": {}}

def save_index(root: Path, data: dict) -> None: atomic_write(index_path(root), data)

def validate_project(data: dict) -> dict:
    required = ("project_id", "project_name")
    if any(not str(data.get(k, "")).strip() for k in required): raise ValueError("project_id and project_name are required")
    forbidden = {"token", "password", "cookie", "ssh_private_key", "note_body", "raw_content"}
    def walk(v):
        if isinstance(v, dict):
            for k, c in v.items():
                if str(k).lower() in forbidden: raise ValueError(f"forbidden project-state field: {k}")
                walk(c)
        elif isinstance(v, list):
            for c in v: walk(c)
    walk(data)
    if len(json.dumps(data, ensure_ascii=False).encode()) > 262144: raise ValueError("project state is too large")
    return data

def resolve(root: Path, pid: str | None) -> str:
    idx = load_index(root); result = (pid or idx.get("active_project_id") or "").strip()
    if not result: raise ValueError("no active project")
    return valid_id(result)

def cmd_init(args):
    root = state_root(); ensure_root(root); pid = valid_id(args.id); path = project_path(root, pid)
    if path.exists() and not args.force: raise ValueError(f"project already exists: {pid}")
    now = int(time.time())
    data = {"schema_version":1,"project_id":pid,"project_name":args.name.strip(),"aliases":args.alias or [],"status":"active","phase":args.phase or "","current_focus":args.focus or "","completed":[],"next_actions":[],"blockers":[],"decisions":[],"working_set":{"note_paths":[],"folders":[]},"intent":{"status":"ready","summary":"","pending_questions":[],"confirmed_at":0},"last_github":{"pr_number":None,"merge_commit":"","branch":""},"created_at":now,"updated_at":now}
    validate_project(data); atomic_write(path, data)
    idx = load_index(root); idx.setdefault("projects", {})[pid] = {"name":data["project_name"],"aliases":data["aliases"],"status":"active","updated_at":now}; idx["active_project_id"] = pid; save_index(root, idx)
    print(f"initialized project: {pid}")

def cmd_list(args):
    root=state_root(); ensure_root(root); print(json.dumps(load_index(root), ensure_ascii=False, indent=2, sort_keys=True))

def cmd_use(args):
    root=state_root(); ensure_root(root); idx=load_index(root); pid=valid_id(args.id)
    if pid not in idx.get("projects", {}): raise ValueError(f"unknown project: {pid}")
    idx["active_project_id"] = pid; save_index(root, idx); print(f"active project: {pid}")

def cmd_read(args):
    root=state_root(); ensure_root(root); pid=resolve(root,args.id); print(json.dumps(validate_project(read_json(project_path(root,pid))), ensure_ascii=False, indent=2, sort_keys=True))

def cmd_status(args):
    root=state_root(); ensure_root(root); pid=resolve(root,args.id); d=validate_project(read_json(project_path(root,pid)))
    keys=("project_id","project_name","status","phase","current_focus","completed","next_actions","blockers","decisions","intent","last_github","updated_at")
    print(json.dumps({k:d.get(k) for k in keys}, ensure_ascii=False, indent=2, sort_keys=True))

def cmd_update(args):
    root=state_root(); ensure_root(root); pid=resolve(root,args.id); path=project_path(root,pid); d=validate_project(read_json(path))
    for key, val in (("phase",args.phase),("current_focus",args.focus),("status",args.status)):
        if val is not None: d[key] = val.strip() if isinstance(val,str) else val
    for key, vals in (("completed",args.completed),("next_actions",args.next_action),("blockers",args.blocker),("decisions",args.decision)):
        if vals: d.setdefault(key, []).extend(v.strip() for v in vals if v.strip())
    if args.clear_next: d["next_actions"]=[]
    if args.clear_blockers: d["blockers"]=[]
    intent=d.setdefault("intent", {"status":"ready","summary":"","pending_questions":[],"confirmed_at":0})
    if args.intent_status is not None: intent["status"] = args.intent_status
    if args.intent_summary is not None: intent["summary"] = args.intent_summary.strip()
    if args.clear_pending_questions: intent["pending_questions"] = []
    if args.pending_question:
        intent.setdefault("pending_questions", []).extend(v.strip() for v in args.pending_question if v.strip())
        intent["status"] = "needs_clarification"
    if args.confirm_intent:
        intent["status"] = "ready"
        intent["pending_questions"] = []
        intent["confirmed_at"] = int(time.time())
    lg=d.setdefault("last_github", {})
    if args.pr_number is not None: lg["pr_number"]=args.pr_number
    if args.merge_commit is not None: lg["merge_commit"]=args.merge_commit.strip()
    if args.branch is not None: lg["branch"]=args.branch.strip()
    d["updated_at"]=int(time.time()); validate_project(d); atomic_write(path,d)
    idx=load_index(root); idx.setdefault("projects", {})[pid]={"name":d["project_name"],"aliases":d.get("aliases",[]),"status":d.get("status","active"),"updated_at":d["updated_at"]}; idx["active_project_id"]=pid; save_index(root,idx)
    print(f"updated project: {pid}")

def parser():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest="cmd",required=True)
    q=sub.add_parser("init"); q.add_argument("--id",required=True); q.add_argument("--name",required=True); q.add_argument("--alias",action="append"); q.add_argument("--phase"); q.add_argument("--focus"); q.add_argument("--force",action="store_true"); q.set_defaults(func=cmd_init)
    q=sub.add_parser("list"); q.set_defaults(func=cmd_list)
    q=sub.add_parser("use"); q.add_argument("--id",required=True); q.set_defaults(func=cmd_use)
    for name,func in (("read",cmd_read),("status",cmd_status)):
        q=sub.add_parser(name); q.add_argument("--id"); q.set_defaults(func=func)
    q=sub.add_parser("update"); q.add_argument("--id"); q.add_argument("--phase"); q.add_argument("--focus"); q.add_argument("--status",choices=["active","paused","done","archived"]); q.add_argument("--completed",action="append"); q.add_argument("--next-action",action="append"); q.add_argument("--blocker",action="append"); q.add_argument("--decision",action="append"); q.add_argument("--clear-next",action="store_true"); q.add_argument("--clear-blockers",action="store_true"); q.add_argument("--intent-status",choices=["ready","needs_clarification"]); q.add_argument("--intent-summary"); q.add_argument("--pending-question",action="append"); q.add_argument("--clear-pending-questions",action="store_true"); q.add_argument("--confirm-intent",action="store_true"); q.add_argument("--pr-number",type=int); q.add_argument("--merge-commit"); q.add_argument("--branch"); q.set_defaults(func=cmd_update)
    return p

def main():
    try:
        args=parser().parse_args(); args.func(args); return 0
    except (ValueError,FileNotFoundError,json.JSONDecodeError,OSError) as exc:
        print(f"error: {exc}"); return 2
if __name__ == "__main__": raise SystemExit(main())
