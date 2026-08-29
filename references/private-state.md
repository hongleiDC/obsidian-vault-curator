# Private persistent state

Use this reference whenever the Skill needs to remember a GitHub-backed Vault across conversations.

## Privacy boundary

User-specific state must live outside both the Skill source tree and the user's Vault repository. Never package, commit, publish, or copy private state into the Skill repository.

The state must not contain authentication secrets. GitHub authentication stays with the connector; do not store tokens, cookies, PATs, passwords, or SSH private keys.

## State root

Resolve the private state root in this order:

1. `OBSIDIAN_CURATOR_STATE_DIR` when set.
2. Otherwise `~/.obsidian-vault-curator/`.

Reject the state location when it is inside:

- the Skill source directory;
- the installed Skill package directory;
- the configured Vault repository working tree.

If the environment has no persistent writable filesystem, do not fall back to embedding the profile in `SKILL.md`, an asset, a ZIP, a public repository, or a note. Use session-only binding or a user-provided private persistent path.

## Directory layout

```text
<state-root>/
├── profiles/
│   └── default.json
├── runtime/
│   └── last-success.json
├── cache/
│   └── vault-index.json
└── locks/
    └── github-write.lock
```

### profiles/default.json

Store only operational binding and preferences:

- schema version;
- Vault repository identifier;
- base branch;
- optional Vault root relative to repository root;
- write policy;
- safety flags.

Do not store note bodies, copied attachments, access tokens, passwords, email addresses, or unrelated user profile information.

### runtime/last-success.json

May store minimal recovery metadata such as:

- last successful base ref or commit SHA;
- last successful write timestamp;
- last temporary branch or PR identifier when needed for recovery.

Do not store note content.

### cache/vault-index.json

Derived cache only. It may contain note names, paths, headings, block IDs, and link targets, so treat it as private. It must be safe to delete and rebuild.

### locks/github-write.lock

Use a lock during a GitHub write transaction when the execution environment supports it. This reduces overlapping runs that try to modify the same Vault simultaneously.

A stale lock may be reclaimed only after a reasonable timeout and only when there is no active task associated with it. Do not spin indefinitely waiting for a lock.

## State helper

Use `scripts/state_store.py` for deterministic state handling when code execution is available.

Typical operations:

```bash
python scripts/state_store.py init --repository <value>
python scripts/state_store.py read
python scripts/state_store.py set --branch <value>
python scripts/state_store.py status
python scripts/state_store.py lock-acquire
python scripts/state_store.py lock-release
```

`init` and `set` write atomically. The helper attempts private filesystem permissions where supported.

`status` is safe for user-visible diagnostics: it reports whether a profile exists and where the state root is, but redacts the repository identifier by default.

## One-time binding

When no profile exists:

1. Ask only for the missing Vault repository identifier.
2. Resolve the repository's default branch through GitHub when possible instead of asking for it.
3. Ask for a Vault subdirectory only if repository inspection shows that the Vault is not at the repository root or the user says so.
4. Persist the binding in the external state directory.
5. Validate access before reporting the binding as ready.

Do not ask for the repository again on later tasks while the private profile is readable and valid.

## Updating the binding

When the user switches Vault repositories or branches:

- update the external profile, not the Skill repository;
- validate the new target before replacing a working binding when possible;
- never include the old or new private identifier in public changelogs, examples, test fixtures, screenshots, or commits.

## Logging and diagnostics

- Keep logs minimal and disabled by default.
- Redact repository identifiers in user-visible diagnostics unless the user explicitly asks to see them.
- Never log credentials.
- Prefer error categories such as `repository unavailable`, `branch unavailable`, or `write conflict` over dumping connector payloads containing private metadata.
