# Intent clarification gate

Use this reference whenever the user's instruction may have more than one materially different interpretation.

## Goal

Do not start changing notes merely because one interpretation seems plausible. Resolve material ambiguity first. The objective is **execution-ready understanding**: no remaining reasonable alternative interpretation would materially change the project, files, scope, semantics, structure, or write action.

## Resolve before asking

Before asking the user, inspect the information already available:

1. the current user message and preceding messages in the active conversation;
2. the private Vault profile;
3. the accepted private note methodology, including namespace/prefix semantics;
4. the current project's persisted progress and decisions;
5. the current remote Vault structure and exact target files when available.

Do not ask the user to repeat facts already recoverable from these sources.

## Material ambiguity triggers

Stop execution and ask when any unresolved ambiguity could materially alter the result, including:

- a pronoun or shorthand such as “this”, “that”, “the previous one”, or “continue” maps to multiple plausible targets;
- several projects, folders, or notes have similar names;
- an unfamiliar acronym, prefix, naming convention, or domain term could mean different things;
- the requested scope could reasonably be one note, one project unit, one namespace, or the whole Vault;
- a new request conflicts with a persisted methodology, project decision, or prior explicit preference;
- the user appears to correct a previous interpretation but the corrected boundary is still incomplete;
- rename, move, delete, merge, split, attachment migration, or broad taxonomy changes lack a precise target;
- preserving versus removing content depends on an unstated preference;
- the requested output form has multiple materially different possibilities and the choice affects the work itself.

Do not stop for trivial wording uncertainty that does not change the result.

## Multi-round clarification loop

1. State the specific ambiguity briefly.
2. Ask only the highest-information 1–3 questions for that round.
3. Prefer contrastive questions when useful, e.g. “Do you mean A or B?”
4. After the user answers, update the working interpretation.
5. Re-evaluate all material ambiguities.
6. If any remain, ask another short round.
7. When none remain, proceed immediately. Do not ask for ceremonial confirmation unless the user explicitly wants it.

Avoid dumping a long checklist of questions. Progressive clarification is easier for the user and reduces mistaken assumptions.

## Persist unresolved clarification

When the project is known, persist only a compact normalized intent state outside the Skill repository:

```json
{
  "intent": {
    "status": "needs_clarification",
    "summary": "Concise current interpretation",
    "pending_questions": ["One unresolved question"],
    "confirmed_at": 0
  }
}
```

Do not store full user messages or chat transcripts.

If the conversation switches before clarification is complete, the next conversation should load this state and continue with the unresolved question instead of starting the task or asking unrelated questions.

After clarification is complete:

- set `intent.status` to `ready`;
- keep a concise summary if it helps future continuity;
- clear `pending_questions`;
- record `confirmed_at`;
- then begin the actual curation/write workflow.

## Examples

### Ask

User: “Move the experiment notes into the new project.”

If two active projects exist, ask which project is intended before moving anything.

### Ask again after a partial answer

User clarifies the project but there are two experiment folders with the same stem. Ask which folder or whether both are in scope.

### Do not ask

User names an exact note path, requests a formatting-only edit, and the requested structure is already defined by the accepted methodology. Proceed without a confirmation round.

### Do not guess prefix semantics

If a prefix is unknown, load its private mapping. If no mapping exists and different meanings would change placement or behavior, ask. Never infer meaning from the English spelling alone.
