# Project progress persistence

Use this reference whenever work belongs to a continuing project or when a new conversation must resume prior Vault work.

## Goal

Do not use chat history as the source of truth for project progress. Persist a compact operational project state in the external private state directory so a later conversation can recover what is being done, what changed, and what should happen next.

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
- compact intent state: `status`, normalized `summary`, unresolved `pending_questions`, and `confirmed_at`.

Do not copy entire note bodies, long conversation summaries, credentials, or irrelevant personal profile data into project state.

## Startup recovery

For every GitHub-backed task:

1. Load the private Vault profile.
2. Load the project index.
3. Resolve the project using this priority: explicit project named by the user → matching project alias → active project → infer from requested top-level project folder when unambiguous.
4. Read that project's state before editing any note.
5. If `intent.status` is `needs_clarification`, resume those unresolved questions before doing new mutations.
6. Combine project state with the accepted note methodology and the current remote files.
7. Run the clarification gate before execution; persist only the normalized unresolved intent, not the chat transcript.
8. Treat remote GitHub content as source of truth for note bodies and state files as source of truth for workflow context.

If multiple project states match and the task would affect different project folders, ask only then. Do not ask the user to repeat known progress already present in private state.

## End-of-task checkpoint

After a PR is successfully merged:

1. Update `completed` with the logical work just finished.
2. Update `current_focus`, `phase`, `next_actions`, and `blockers` from the actual outcome.
3. Record the merged PR number and merge commit.
4. Clear the temporary branch field after branch cleanup succeeds.
5. Persist the checkpoint atomically.

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
```

For larger updates, apply several `update` operations to the active project; keep each checkpoint concise and operational.
