# GitHub-backed Vault workflow

Use this reference whenever the Vault is stored in GitHub. Private Vault binding comes only from the external state directory described in `private-state.md`.

## Startup

1. Load the private Vault profile.
2. Load current project progress before editing.
3. Resolve repository, base branch and optional Vault root.
4. Confirm repository and base branch access.
5. Restrict reads and writes to the configured Vault root unless the user explicitly expands scope.
6. Fetch current remote content; never trust a body or SHA remembered from another conversation.
7. Acquire the private write lock when supported.
8. Build and validate the complete change set before mutation.

## Mandatory policy: PR-only

Every GitHub mutation must use a temporary branch and pull request. Direct writes to the base branch are forbidden, including single-note edits.

### PR workflow

1. Resolve the latest base head.
2. Create a unique temporary branch from that exact head.
3. Read target files from a consistent snapshot when possible.
4. Produce final contents in memory.
5. Run preservation and link checks.
6. Prefer one atomic batch commit when Git Data operations are available; otherwise update files sequentially on the temporary branch.
7. Open a PR into the base branch.
8. Re-check mergeability and relevant conflicts.
9. If validation passes and the PR is mergeable, automatically squash-merge it.
10. After merge succeeds, delete the temporary head branch and verify it no longer exists.
11. Release the write lock.
12. Only then checkpoint project progress.

Risky rename, move, delete or attachment operations may need stricter validation, but they still use this same PR lifecycle.

## Atomic batch commit

When Git Data operations are available:

1. Build one final change set.
2. Create blobs for changed text files.
3. Create one tree using the current base tree.
4. Create one commit with the expected parent.
5. Move the temporary branch ref once.

This reduces commit noise, stale-SHA races and partial updates.

If unavailable, fall back to sequential writes on the temporary branch:
- fetch each path immediately before updating it;
- use the fresh blob SHA;
- write each path at most once per logical batch;
- never write the same path concurrently.

## Automatic merge and branch cleanup

After opening a PR:

- do not wait for another conversation to finish ordinary validated work;
- if the PR is mergeable and validation passes, squash-merge automatically;
- after merge, delete the head branch automatically;
- verify branch deletion before marking cleanup complete;
- never intentionally leave merged temporary branches;
- if the available GitHub capability cannot delete the branch, report cleanup as incomplete and never reuse that branch.

Project progress is not marked completed before merge. After cleanup, record the PR and merge commit and clear the temporary branch field in private project state.

## Conflict and retry limits

### Stale SHA or content changed
1. Refresh latest remote content.
2. Re-apply the intended transformation.
3. Retry once.
4. On second failure, stop that path or batch and report the blocker.

### Temporary branch ref moved unexpectedly
- do not force-update;
- create one fresh branch from the intended base and rebuild once;
- on a second failure, stop.

### Base branch changed during work
Before merge, check PR mergeability. Never force-merge a conflict. If a clean automatic update is unavailable, keep the PR unmerged and report the blocking paths.

### Permission/authentication failure
Stop immediately; do not retry without a real authorization change.

### Branch-name collision
Generate one alternate suffix only. If it also collides, stop.

### Unchanged content
Skip it; do not create empty commits or no-op PRs.

## Batch size

Treat the configured batch maximum as a safety ceiling, not a target. Prefer coherent project/workstream batches; do not start with a whole-vault rewrite.

## Commit and PR naming

Use concise generic messages that describe the operation without leaking private note names when avoidable, for example:

```text
docs(obsidian): curate project note batch
docs(obsidian): normalize metadata and links
```

PR titles should describe the logical batch, not enumerate private filenames.

## Read strategy

- Exact path: fetch it directly.
- Note title without path: search only in the bound Vault first.
- Multiple matches: resolve with project state, folder context or links; do not guess.
- Never broaden to unrelated repositories unless explicitly asked.

## Attachments

Preserve existing attachment targets. Do not rename/move binary attachments by default or write binary data through text-only operations. Attachment migration is a PR-based high-risk workflow.
