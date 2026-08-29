# GitHub-backed Vault workflow

Use this reference when the Vault is stored in GitHub and the Skill is expected to read and write notes through a connected GitHub capability.

Private Vault binding is loaded from the external state directory described in `private-state.md`; never from the Skill repository.

## Startup sequence

1. Load the private profile from the external state directory.
2. Resolve repository, base branch, and optional Vault root.
3. Fetch repository metadata and confirm the base branch exists.
4. Restrict reads and writes to the configured Vault root unless the user explicitly expands scope.
5. Fetch current remote content before editing. Never rely on a body or SHA remembered from a previous conversation.
6. Acquire the write lock before mutation when supported.
7. Build and validate a complete change set before sending writes.

## Default policy: branch-first

The default write mode is `branch_pr` because a Vault may also be synchronized by a desktop client or another device. Do not write directly to the base branch unless private settings explicitly enable direct writes.

### Branch-first workflow

1. Resolve the latest base branch head.
2. Create a unique temporary branch from that exact head.
3. Read all target files from a consistent base snapshot when possible.
4. Produce the complete final contents in memory.
5. Run semantic-preservation checks.
6. Commit the batch to the temporary branch.
7. Open a pull request into the base branch.
8. Re-check mergeability and relevant conflicts.
9. Auto squash-merge only ordinary text-only changes when private settings allow it and validation passes.
10. Release the write lock.

Rename, move, delete, attachment, and other risky changes are never auto-merged by default.

## Prefer one atomic batch commit

When GitHub Git Data operations are available, avoid one commit per file.

For a batch:

1. Build one final change set first.
2. Create blobs for changed text files.
3. Create one tree using the current base tree.
4. Create one commit with the expected parent commit.
5. Move the temporary branch ref once.

This reduces API calls, commit noise, stale-SHA races, and partial multi-file updates.

If atomic Git Data operations are not available, fall back to sequential file updates on the temporary branch:

- fetch each path immediately before updating it;
- use the fresh blob SHA;
- write each path at most once per logical batch;
- never write the same path concurrently.

## Optional direct write

Direct base-branch updates are opt-in. Use them only when all conditions are true:

- private policy explicitly enables direct write;
- exactly one text note is created or updated;
- there is no rename, move, delete, attachment change, or coordinated backlink change;
- preservation validation passes.

Direct sequence:

1. Fetch the target and record the current SHA.
2. Build complete replacement content.
3. Fetch the target again immediately before writing.
4. If SHA is unchanged, update using the fresh SHA.
5. If SHA changed, re-apply the intended transformation to the latest content and retry once.
6. Re-read and verify the result.

## Batch size

Treat the configured batch maximum as a safety ceiling, not a performance target.

- Default maximum: 10 changed notes.
- Split larger work into coherent directory or topic batches.
- Never start with a whole-vault rewrite.

## Conflict and retry policy

The Skill must not enter a repeated push-error loop.

### Stale SHA or changed content

1. Refresh the latest remote content.
2. Re-apply the intended transformation.
3. Retry once.
4. If it fails again, stop that path or batch and report a conflict.

Never submit the same stale SHA repeatedly.

### Temporary branch ref conflict

A temporary branch should be owned by one task. If its ref moves unexpectedly:

- do not force-update it;
- create one fresh branch from the newest intended base and rebuild once;
- on a second failure, stop.

### Base branch changed during work

A newer base commit is normal. Before merge:

- check PR mergeability;
- identify whether touched paths conflict;
- never force-merge a conflicted PR;
- if a clean automatic update/rebase is not available, leave the PR unmerged and report the blocking paths.

### Missing file or wrong operation

- Existing path: update using its current state.
- Missing path: create only when creation is allowed.
- Do not loop between create and update attempts.

### Permission or authentication failure

Stop immediately. Do not retry writes without a change in authorization state.

### Branch-name collision

Generate one new suffix. If the retry also collides, stop.

### Unchanged content

Skip byte-identical changes. Do not create empty commits or no-op PRs.

## Write serialization

- Use the private write lock when available.
- Never issue concurrent writes to the same path.
- Prefer one complete write per note per task.
- Prefer one atomic commit for each multi-file batch.
- Release locks on both success and handled failure.

## Commit conventions

Use concise generic messages that describe the operation, not private note details when avoidable.

Examples:

```text
docs(obsidian): curate one note
docs(obsidian): normalize note metadata batch
docs(obsidian): refresh validated vault links
```

PR titles should describe the logical operation rather than list private filenames.

## Read strategy

- Exact path: fetch it directly.
- Note title without path: search only inside the configured private Vault first.
- Multiple matches: resolve using folder context or links; do not guess.
- Never broaden to unrelated repositories unless the user explicitly asks.

## Attachments

GitHub-backed curation is text-first.

- Preserve existing attachment targets and embeds.
- Do not rename or move binary attachments by default.
- Do not write binary content through text-only file operations.
- Attachment migration is a risky branch workflow and requires explicit permission.
