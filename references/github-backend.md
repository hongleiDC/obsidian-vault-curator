# GitHub-backed Vault workflow

Use this reference when the user's Obsidian vault is stored in GitHub and the Skill is expected to read and write notes through the GitHub connector.

## Persistent vault profile

The Skill supports a user-specific profile at `config/vault.yaml`.

- Treat `config/vault.yaml` as private user configuration.
- Do not commit it to the public Skill repository.
- The public repository only contains `config/vault.example.yaml`.
- Once the profile exists, read it at the start of every GitHub-backed task instead of asking for the repository again.
- Never confuse the Skill source repository with the user's note repository.

Recommended profile:

```yaml
schema_version: 1
profile_name: primary-vault

vault:
  repository: owner/repository
  branch: main
  root: ""

write:
  mode: adaptive
  direct_max_files: 1
  batch_max_files: 10
  branch_prefix: obsidian-curator/
  merge_method: squash
  auto_merge_safe_batches: true
  auto_merge_risky_changes: false
  retry_limit: 1
  verify_after_write: true
  commit_prefix: docs(obsidian)

safety:
  allow_create_notes: true
  allow_delete_notes: false
  allow_rename_or_move: false
  allow_binary_attachment_changes: false
```

`vault.root` is relative to the repository root. Use an empty string when the repository itself is the Vault root.

## Startup sequence

For every GitHub-backed task:

1. Load `config/vault.yaml` if present.
2. Resolve `vault.repository`, `vault.branch`, and `vault.root` from the profile.
3. Use the GitHub connector to retrieve repository metadata and confirm the configured branch exists.
4. Confirm the requested path belongs to the configured vault root.
5. Read the current remote file before editing. Never rely on a copy remembered from a previous conversation.
6. Choose a write strategy with the adaptive policy below.

If the profile is absent, enter one-time setup mode. Ask for the vault repository and, only when necessary, the branch and vault root. Do not ask for these values again after a persistent profile has been created.

## Adaptive write policy

### Direct write

Use a direct update on the configured base branch only when all of the following are true:

- exactly one text note is being created or updated;
- the change does not rename, move, or delete files;
- the change does not require coordinated edits to backlinks in other notes;
- no binary attachment is being changed;
- semantic-preservation checks pass.

Direct-write sequence:

1. Fetch the target file and record its blob SHA.
2. Build the complete replacement content in memory. Avoid multiple partial writes.
3. Immediately before writing, fetch the same path again.
4. If the SHA is unchanged, update with that fresh SHA.
5. If the SHA changed, discard the stale write plan, re-read the new content, re-apply the intended transformation, and retry once.
6. Fetch the written file again and verify the result when `verify_after_write` is true.

### Branch + pull request

Use a temporary branch when any of the following is true:

- two or more files are changed;
- links are coordinated across notes;
- Frontmatter or taxonomy is normalized across multiple files;
- a note is renamed or moved;
- a note is deleted;
- more than one backlink must be rewritten;
- the change is otherwise difficult to validate as one isolated file update.

Branch workflow:

1. Resolve the latest base branch state.
2. Create a unique branch under `write.branch_prefix`, for example `obsidian-curator/20260829-topic`.
3. Apply changes sequentially on that branch. Do not write the same path in parallel.
4. For every existing file, fetch the file on the temporary branch immediately before updating it and use the fresh blob SHA.
5. Validate all changed notes.
6. Open a pull request into the configured base branch.
7. For ordinary text-only curation, squash-merge automatically only when `auto_merge_safe_batches` is true and validation passed.
8. Never auto-merge rename, move, delete, attachment, or other risky changes unless `auto_merge_risky_changes` is explicitly enabled.

Squash merging keeps the base branch history readable even when several file-level commits were needed on the temporary branch.

## Batch size

Use `write.batch_max_files` as a safety ceiling, not a performance target.

- Default: at most 10 changed notes in one batch.
- Split larger vault-wide cleanup into coherent topic or directory batches.
- Do not attempt one giant whole-vault rewrite.

## Conflict and retry policy

The Skill must not enter a repeated push-error loop.

### Stale SHA / conflict

For a conflict caused by a stale file SHA or concurrently changed content:

1. Fetch the latest remote file.
2. Re-apply the intended transformation to the latest content.
3. Retry once.
4. If the second attempt fails, stop writing that path and report the conflict.

Never repeatedly submit the same stale SHA.

### Missing file / wrong operation

- If a file exists, use an update operation with its current SHA.
- If a file does not exist and creation is allowed, use a create operation.
- Do not repeatedly try `create` on an existing path or `update` on a missing path.

### Permission or authentication failure

Stop immediately. Do not retry writes when the connector lacks permission or authentication.

### Branch-name collision

Generate a different suffix once. Do not repeatedly attempt the same branch name.

### Unchanged content

If the proposed content is byte-for-byte identical to the current remote content, skip the write and do not create a no-op commit.

## Write serialization

- Never issue concurrent writes to the same path.
- Prefer one complete write per note per task.
- When the same file must be updated again after a successful write, use the newly returned content SHA or re-fetch the file first.
- Writes to different files on a temporary branch may still be performed sequentially for easier failure recovery and traceability.

## Commit conventions

Use concise commit messages with the configured prefix.

Examples:

```text
docs(obsidian): curate ROS Noetic note
docs(obsidian): normalize GNSS note properties
docs(obsidian): link three TF debugging notes
```

For branch workflows, the pull request title should describe the logical batch rather than list every file.

## Read strategy

- When the user provides an exact path, fetch that path directly.
- When the user gives a note title but not a path, search only inside the configured note repository first.
- If multiple files match the same title/stem, do not guess. Resolve the ambiguity using folder context, links, or the user's requested topic.
- Always use the configured repository as the default scope unless the user explicitly asks to work elsewhere.

## Attachments

GitHub-backed curation is text-first.

- Preserve existing attachment paths and embeds.
- Do not rename or move binary attachments by default.
- Do not attempt binary writes through a text-only file operation.
- Attachment migration is a risky multi-file operation and must use the branch workflow when supported.
