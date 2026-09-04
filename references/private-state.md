# Private persistent state

Use this reference whenever the Skill needs to remember a GitHub-backed Vault, accepted note methodology, or project progress across conversations.

## Privacy boundary

User-specific state must live outside both the Skill source tree and the user's Vault repository. Never package, commit, publish, or copy private state into the Skill repository.

Never store authentication secrets. GitHub authentication stays with the connector; do not store tokens, cookies, PATs, passwords, or SSH private keys.

## State root

Resolve in this order:
1. `OBSIDIAN_CURATOR_STATE_DIR` when set.
2. Otherwise `~/.obsidian-vault-curator/`.

Reject a state location inside the Skill source tree, installed Skill package, or configured Vault repository working tree.

If the environment has no persistent writable filesystem, do not fall back to embedding private state in `SKILL.md`, a ZIP, public repository, or note. Use session-only binding or a user-provided private persistent location and clearly state the limitation.

## Directory layout

```text
<state-root>/
├── profiles/
│   └── default.json
├── methods/
│   └── note-system.json
├── projects/
│   ├── index.json
│   └── <project-id>.json
├── runtime/
│   └── last-success.json
├── cache/
│   ├── vault-index.json
│   └── vault-patterns.json
└── locks/
    └── github-write.lock
```

### profiles/default.json

Store only operational Vault binding and preferences: schema version, repository identifier, base branch, optional Vault root, batch size and safety flags. A legacy `allow_direct_write` value, if present in an older profile, must be ignored: current Skill policy is PR-only.

### methods/note-system.json

Store the accepted note methodology and structural preferences. It may include note-type contracts, folder/tag/link roles, shallow directory policy, curation rules, and a small aggregate analysis summary. Do not store raw note bodies, credentials or unnecessary personal profile data.

### projects/index.json

Store the active project ID and a lightweight catalog of known project IDs/names/aliases. This is the starting point for cross-conversation recovery.

### projects/<project-id>.json

Store only operational context needed to continue work:
- project name and aliases;
- status and phase;
- current focus;
- concise completed work;
- ordered next actions;
- blockers;
- important decisions;
- relevant private note paths/folders when useful;
- latest successful PR number, merge commit and temporary branch state.

Do not copy entire note bodies or long chat transcripts into project state.

Use `scripts/project_state.py` for project state operations.

### runtime/last-success.json

May store minimal recovery metadata such as last successful base ref or write timestamp. It is not a substitute for project progress files.

### cache/*

Derived private cache only. It may contain note paths/headings/link targets, so never publish it. It must be safe to delete and rebuild.

### locks/github-write.lock

Use a write lock during GitHub mutations when supported. Reclaim stale locks only after a reasonable timeout and never spin indefinitely waiting for one.

## One-time binding

When no profile exists:
1. Ask only for the missing Vault repository identifier.
2. Resolve the default branch through GitHub when possible.
3. Ask for a Vault subdirectory only when needed.
4. Persist the binding externally.
5. Validate access before reporting it ready.

Do not ask for the repository again while the private profile remains readable and valid.

## Project recovery

At the start of every GitHub-backed project task:
1. load the Vault profile;
2. load `projects/index.json`;
3. resolve the project by explicit name, alias, active project, or unambiguous top-level project folder;
4. load that project's JSON state;
5. combine project progress with the accepted note methodology and current remote files.

Do not ask the user to repeat progress already persisted in project state.

## Checkpoint timing

Checkpoint project progress only after the GitHub outcome is known:
- PR merged and branch cleanup succeeded → add completed work, refresh focus/next actions/blockers, record PR and merge commit, clear branch field;
- validation or merge failed → do not mark completed; record blocker and next action instead.

## State helpers

Vault binding and methodology:

```bash
python scripts/state_store.py init --repository <value>
python scripts/state_store.py status
python scripts/state_store.py method-status
python scripts/state_store.py method-read
python scripts/state_store.py method-write --file <methodology.json>
python scripts/state_store.py lock-acquire
python scripts/state_store.py lock-release
```

Project progress:

```bash
python scripts/project_state.py init --id example --name "Example Project"
python scripts/project_state.py list
python scripts/project_state.py use --id example
python scripts/project_state.py status
python scripts/project_state.py read
python scripts/project_state.py update --focus "Current task" --next-action "Next task"
```

All state writes should be atomic and use private filesystem permissions where supported.

## Logging and diagnostics

Keep logs minimal and disabled by default. Redact repository identifiers unless the user explicitly requests them. Prefer categories such as `repository unavailable`, `branch unavailable`, `write conflict`, or `project state unavailable` over dumping connector payloads.
