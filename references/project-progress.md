# Project progress persistence

Use this reference whenever work belongs to a continuing project or a new conversation must resume prior Vault work.

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
- latest successful PR number, merge commit and temporary branch state.

Do not copy entire note bodies, long conversation summaries, credentials or irrelevant personal profile data into project state.

## Startup recovery

For every GitHub-backed task:
1. Load the private Vault profile.
2. Load the project index.
3. Resolve the project using this priority: explicit project named by the user → matching project alias → active project → infer from requested top-level project folder when unambiguous.
4. Read that project's state before editing any note.
5. Combine project state with the accepted note methodology and current remote files.
6. Treat remote GitHub content as source of truth for note bodies and project state as source of truth for workflow context.

If multiple project states match and the task would affect different projects, ask only then. Do not ask the user to repeat known progress already present in private state.

## End-of-task checkpoint

Checkpoint only after the GitHub outcome is known.

After a PR is successfully merged and the temporary branch is deleted:
1. add the logical work just finished to `completed`;
2. refresh `current_focus`, `phase`, `next_actions` and `blockers` from the actual outcome;
3. record PR number and merge commit;
4. clear the temporary branch field;
5. persist the checkpoint atomically.

If validation or merge fails, do not mark the work completed. Preserve the old completed state and record the blocker and next action instead.

## Project switching

When the user explicitly names another project, switch the active project and load its state. Do not overwrite one project's progress with another's. Project IDs are stable internal keys; aliases can match natural names used by the user.

## Commands

```bash
python scripts/project_state.py init --id example-project --name "Example Project"
python scripts/project_state.py list
python scripts/project_state.py use --id example-project
python scripts/project_state.py status
python scripts/project_state.py read
python scripts/project_state.py update --focus "Current task" --next-action "Next task"
```

Keep checkpoints concise and operational. The goal is continuity, not a duplicate project journal.
