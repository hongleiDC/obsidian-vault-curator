# Project progress persistence

Use this reference whenever work belongs to a continuing project or when a new conversation must resume prior Vault work.

## Goal

Do not use chat history as the source of truth for project progress. Persist a compact operational project state in the external private state directory so a later conversation can recover what is being done, what changed, what remains, and what should happen next.

## Private layout

```text
<state-root>/projects/
├── index.json
├── project-a.json
└── project-b.json
```

`index.json` stores the active project ID plus a lightweight project catalog. Each project file stores only operational context needed to continue work.

## Project state contract

A project state may contain:

- `project_id`, `project_name`, `aliases`;
- lifecycle `status` and current `phase`;
- `current_focus`;
- concise `completed` items;
- ordered `next_actions`;
- unresolved `blockers`;
- important `decisions` that affect future curation;
- a private `working_set` of relevant note paths/folders when useful;
- the latest successful PR number / merge commit / temporary branch for recovery;
- compact intent state: `status`, normalized `summary`, unresolved `pending_questions`, and `confirmed_at`;
- one active `modification_checklist` for the current task scope.

Do not copy entire note bodies, long conversation summaries, credentials, or irrelevant personal profile data into project state.

## Modification checklist contract

The checklist is not a second project-management system. Keep it small and operational:

```json
{
  "scope": "Fictional project folder only",
  "status": "active",
  "items": [
    {
      "id": "C001",
      "text": "Repair broken internal links",
      "status": "pending",
      "priority": "high",
      "depends_on": [],
      "note": ""
    }
  ],
  "updated_at": 0
}
```

Rules:

- `scope` must match the user-confirmed task boundary.
- item statuses are `pending`, `in_progress`, `blocked`, or `done`.
- priorities are `high`, `medium`, or `low`.
- dependencies reference earlier checklist item IDs.
- `note` is only a short verification/blocker note; never put note bodies or long reasoning there.
- the checklist-level status is derived as `empty`, `active`, or `done`.
- do not replace an unfinished checklist for a different scope unless the scope switch has been clarified.
- for GitHub mutations, mark an item `done` only after the containing PR is merged and temporary branch cleanup succeeds.

## Startup recovery

For every GitHub-backed task:

1. Load the private Vault profile.
2. Load the project index.
3. Resolve the project using this priority: explicit project named by the user → matching project alias → active project → infer from requested top-level project folder when unambiguous.
4. Read that project's state before editing any note.
5. If `intent.status` is `needs_clarification`, resume those unresolved questions before doing new mutations.
6. Combine project state with the accepted note methodology and the current remote files.
7. Run the clarification gate before execution; persist only the normalized unresolved intent, not the chat transcript.
8. After intent becomes `ready`, compare the current request scope with `modification_checklist.scope`.
9. If an unfinished checklist matches the scope, resume it. Otherwise perform a read-only diagnosis limited to the confirmed scope and create a checklist before the first mutation.
10. Show the concise checklist to the user, then process eligible items by priority/dependency order.
11. Treat remote GitHub content as source of truth for note bodies and state files as source of truth for workflow context.

If multiple project states match and the task would affect different project folders, ask only then. Do not ask the user to repeat known progress already present in private state.

## Checklist lifecycle

For each item:

1. Set `in_progress` immediately before acting on it.
2. Execute the smallest coherent change needed for that item.
3. Validate semantics, links, paths, and any item-specific acceptance condition.
4. For read-only items, set `done` after successful verification.
5. For GitHub mutation items, keep them unfinished until the PR carrying the change is merged and its temporary branch is gone; then set `done`.
6. On failure, set `blocked` and write one short reason. Do not hide the failure by marking the item complete.

When a new issue appears during execution:

- if it clearly falls inside the confirmed scope, append a new checklist item;
- if it falls outside scope, put it in `next_actions` or ask the user if it materially affects the current result;
- never silently widen the scan or mutation boundary.

## End-of-task checkpoint

After a PR is successfully merged and branch cleanup succeeds:

1. Mark checklist items represented by that PR as `done`.
2. If unfinished items remain, keep the checklist `active` and continue/resume later.
3. When all checklist items are `done`, update `completed` with the logical work just finished.
4. Update `current_focus`, `phase`, `next_actions`, and `blockers` from the actual outcome.
5. Record the merged PR number and merge commit.
6. Clear the temporary branch field after branch cleanup succeeds.
7. Persist the checkpoint atomically.

Do not mark work completed before the PR is merged. If validation or merge fails, keep the old completed state and record the blocker/next action instead. If execution has not started because clarification is incomplete, keep the task out of `completed` and persist the pending questions.

## Commands

```bash
python scripts/project_state.py init --name "Example Project" --id example-project
python scripts/project_state.py list
python scripts/project_state.py use --id example-project
python scripts/project_state.py status
python scripts/project_state.py read
python scripts/project_state.py update --focus "Current task" --next-action "Next task"
python scripts/project_state.py update --intent-status needs_clarification --intent-summary "Current interpretation" --pending-question "Unresolved point"
python scripts/project_state.py update --confirm-intent

python scripts/project_state.py checklist-start --scope "Example project only" \
  --item "Repair broken internal links" \
  --item "Normalize project Properties"
python scripts/project_state.py checklist-add --item "Verify project index" --priority low --depends-on C001
python scripts/project_state.py checklist-update --item-id C001 --status in_progress
python scripts/project_state.py checklist-update --item-id C001 --status done --note "Merged and verified"
python scripts/project_state.py checklist-status
```

Keep every checkpoint concise and operational.
