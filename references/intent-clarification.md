# Intent clarification gate

Use this reference whenever the user's instruction is long/complex **or** may have more than one materially different interpretation.

## Goal

Do not start changing notes merely because one interpretation seems plausible. For long/complex requests, validate the interpretation even when it appears clear. The objective is **execution-ready understanding**: no remaining reasonable alternative interpretation would materially change the project, files, scope, semantics, structure, preservation boundary, or write action.

## Resolve before asking

Before asking the user, inspect the information already available:

1. the current user message and preceding messages in the active conversation;
2. the private Vault profile;
3. the accepted private note methodology, including namespace/prefix semantics;
4. the current project's persisted progress and decisions;
5. the current remote Vault structure and exact target files when available.

Do not ask the user to repeat recoverable facts. Use the three questions to validate **interpretation and execution boundaries**, not to request information already known verbatim.

## Mandatory triggers

Enter the three-question gate when **either** condition is true.

### A. Long or complex instruction

Treat an instruction as long/complex when any of these apply:

- it contains three or more independent requirements or steps;
- it spans multiple files, folders, projects, batches, or output targets;
- it combines analysis, restructuring, migration, validation, and/or write-back in one request;
- it has several interacting constraints where a mistaken assumption could change the result.

A request can be complex even when it is short in word count. Long/complex requests must go through at least one three-question round even if the current interpretation seems clear.

### B. Material uncertainty

Stop execution and ask when unresolved uncertainty could materially alter the result, including:

- a pronoun or shorthand such as “this”, “that”, “the previous one”, or “continue” maps to multiple plausible targets;
- several projects, folders, or notes have similar names;
- an unfamiliar acronym, prefix, naming convention, or domain term could mean different things;
- the requested scope could reasonably be one note, one project unit, one namespace, or the whole Vault;
- a new request conflicts with a persisted methodology, project decision, or prior explicit preference;
- the user appears to correct a previous interpretation but the corrected boundary is still incomplete;
- rename, move, delete, merge, split, attachment migration, or broad taxonomy changes lack a precise target;
- preserving versus removing content depends on an unstated preference;
- the requested output/write-back form has multiple materially different possibilities.

Do not trigger this gate for a simple, exact request whose target, scope, operation, and expected result are already unique and explicit.

## Fixed three-question round

Every clarification round must contain **exactly three questions**.

Choose the three highest-information dimensions, usually from:

1. goal / target interpretation;
2. scope / inclusion-exclusion boundary;
3. preservation, destructive-operation, output, write-back, or priority boundary.

For each question:

- state the question concretely;
- immediately provide **My proposed answer**: the interpretation currently believed most likely to be correct;
- treat that proposed answer only as a hypothesis awaiting user correction;
- do not start mutation or checklist execution before the user answers.

Preferred visible pattern:

```text
1. Question: Which project boundary should this apply to?
   My proposed answer: Only the explicitly named project; neighboring projects are out of scope.
2. Question: Should existing note meaning and unknown Properties be preserved?
   My proposed answer: Yes; restructure without deleting unknown metadata or semantic content.
3. Question: What write-back result is intended?
   My proposed answer: Apply the validated changes through the normal PR-only workflow.
```

Do not pad the round with low-value trivia. If only one ambiguity is obvious, use the other two questions to validate the highest-impact execution assumptions rather than asking known factual questions.

## Mandatory correction review after the user answers

Do **not** proceed immediately after receiving answers.

1. Compare each user answer against the corresponding proposed answer.
2. Mark the prior interpretation as correct or needing correction.
3. Rewrite every incorrect assumption according to the user's answer.
4. Produce one compact **Corrected execution understanding** covering target, scope, key semantics, and allowed operation boundary.
5. Re-evaluate the request using the corrected understanding and all available state.
6. If any material uncertainty remains, start another round of exactly three questions, each again with a proposed answer.
7. Only when no material uncertainty remains may the intent become `ready`.

The correction review is not a ceremonial confirmation. It exists to force the Skill to notice and repair its own wrong assumptions before acting.

## Persist unresolved clarification

When the project is known, persist only compact normalized intent state outside the Skill repository:

```json
{
  "intent": {
    "status": "needs_clarification",
    "summary": "Concise current interpretation",
    "pending_questions": [
      "Q1: Question 1 | Proposed: Proposed answer 1",
      "Q2: Question 2 | Proposed: Proposed answer 2",
      "Q3: Question 3 | Proposed: Proposed answer 3"
    ],
    "confirmed_at": 0
  }
}
```

`pending_questions` must normally contain exactly three compact entries while clarification is pending; each entry carries both the question and its proposed answer. Do not store full user messages, chat transcripts, or hidden reasoning.

If the conversation switches before clarification is complete, the next conversation should load the three combined question/proposed-answer entries and resume the same round instead of silently guessing or starting unrelated work.

After correction is complete and intent becomes ready:

- set `intent.status` to `ready`;
- replace `intent.summary` with the corrected compact execution understanding;
- clear `pending_questions`;
- record `confirmed_at`;
- then begin read-only diagnosis and checklist construction.

## Examples

### Complex request: ask even if it looks understandable

Fictional user request: “Review the project folder, reorganize the notes, fix links, then push the result through GitHub.”

This has multiple independent steps, so ask exactly three validation questions with proposed answers before execution.

### Short but ambiguous request: ask

User: “Move those notes into the new project.”

If several targets or projects are plausible, ask exactly three questions. One can resolve the target ambiguity; the other two should validate scope and preservation/write-back boundaries.

### Ask again after a partial answer

If the user resolves the project but leaves the note group or destructive boundary unclear, first perform the correction review, then ask a new three-question round with new proposed answers.

### Simple exact request: do not ask

User names one exact note path, requests one formatting-only edit, explicitly says to preserve content, and the accepted methodology already defines the output. Proceed without forcing a three-question round.

### Do not guess prefix semantics

If a prefix is unknown, load its private mapping. If no mapping exists and different meanings would change placement or behavior, include that uncertainty in the three-question round. Never infer meaning from English spelling alone.
