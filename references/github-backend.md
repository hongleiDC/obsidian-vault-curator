# GitHub-backed Vault workflow

Use this reference for any GitHub-backed Vault mutation.

## Startup

1. Load private Vault profile, methodology and project progress.
2. Resolve repository, base branch, Vault root and active project.
3. Fetch current remote content; never trust a body/SHA from another conversation.
4. Acquire the private write lock.
5. Build and validate the complete change set before sending writes.

## Mandatory PR-only policy

Every GitHub mutation uses a temporary branch and PR. Direct base-branch writes are forbidden, including one-note edits.

## Cleanup preflight

Before creating a temporary branch, confirm at least one cleanup path exists:

- the current GitHub capability can explicitly delete the head branch/ref; or
- repository setting `delete_branch_on_merge` is enabled.

If neither exists, do not create another branch. Report a configuration blocker first. This prevents accumulated merged branches.

## PR transaction

1. Resolve latest base head.
2. Create a unique temporary branch from that exact commit.
3. Read targets from a consistent base snapshot when possible.
4. Produce complete final contents in memory.
5. Run preservation/link/path checks.
6. Prefer one atomic commit for the whole batch.
7. Open PR into base branch.
8. Re-check mergeability and conflicts.
9. If validation passes and PR is mergeable, automatically squash-merge.
10. Delete the temporary branch after merge and confirm it no longer exists.
11. Update private project progress only after successful merge + cleanup.
12. Release the write lock on success or handled failure.

Risky rename/move/delete/attachment changes require explicit permission before preparing the mutation. Once authorized and validated, they use the same automatic merge and cleanup transaction.

## Atomic batch commit

When Git Data operations are available:

1. create blobs for all final text contents;
2. create one tree from the current base tree;
3. create one commit with the expected parent;
4. move the temporary branch ref once.

If unavailable, update files sequentially on the temporary branch using fresh SHAs; never write the same path concurrently or more than once per logical batch.

## Batch size

Default safety ceiling: 10 changed files. Split larger work into coherent project/topic batches. Do not begin with a whole-Vault rewrite.

## Conflict/retry policy

- stale SHA/ref: refresh and rebuild once; second failure stops the batch;
- branch collision: generate one new suffix; second collision stops;
- base changed: re-check PR mergeability; never force-merge conflict;
- missing path: create only when note creation is allowed;
- permission/auth failure: stop immediately;
- unchanged content: no commit/no PR;
- merged but branch not cleaned: report transaction incomplete and never reuse that branch.

## Commit/PR conventions

Use generic operation descriptions and avoid private note titles when possible:

```text
docs(obsidian): curate project notes
docs(obsidian): normalize note metadata batch
docs(obsidian): refresh validated vault links
```

## Read strategy

- exact path: fetch directly;
- title without path: search inside configured Vault only;
- multiple matches: resolve from project/folder/link context, do not guess;
- do not broaden to unrelated repositories without explicit request.

## Attachments

Text-first by default. Preserve embed targets. Do not rename/move binary attachments unless the user explicitly authorized a risky migration.
