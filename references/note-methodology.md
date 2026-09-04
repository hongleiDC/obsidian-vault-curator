# Adaptive note methodology and Vault architecture

Use this reference when the Skill needs to understand an existing Vault before deciding how to organize it.

## Principle

Do not force one fashionable system onto every Vault. First inspect the user's real data shape and workflows, then choose the smallest useful hybrid method.

## Diagnosis

Before major restructuring, inspect aggregate structural signals:
- note count and length distribution;
- directory depth and recurring top-level folders;
- date-based filenames and daily/log patterns;
- Frontmatter keys and Properties consistency;
- tags and aliases;
- wikilinks, embeds, headings and block IDs;
- tasks and status fields;
- source/url/reference patterns;
- code, formulas, tables, callouts and Dataview;
- recurring project, meeting, experiment, decision, how-to or reference structures.

When a materialized Vault is available, use:

```bash
python scripts/analyze_vault_patterns.py <vault-root> --output <private-report.json>
```

The report should contain aggregate structure metrics by default, not raw note bodies.

## Diagnose workflow friction, not just inconsistent formatting

Look for problems such as:
- source material mixed with the user's own conclusions;
- project logs treated as permanent concept notes;
- useful conclusions trapped in daily notes;
- folder, tag and link systems redundantly encoding the same classification;
- project context disappearing when conversations change;
- excessive nesting making navigation harder than search/linking;
- MOCs that are only backlink dumps;
- templates that create fields nobody maintains.

## Functional note types

Use note types as functional contracts, not rigid templates.

- **Capture**: fast intake; minimal structure.
- **Source / Literature**: external evidence, citation and extraction; keep synthesis separate.
- **Log / Daily / Experiment**: preserve chronology, observations, attempts and outcomes.
- **Project**: current goal, status, workstream, actions, decisions and progress.
- **Concept / Evergreen**: reusable understanding with independent long-term value.
- **Decision record**: choice, alternatives, evidence and why it was made.
- **How-to / Troubleshooting**: symptom/goal, evidence, steps, verification and failure modes.
- **Reference**: fast lookup; tables/lists may be better than prose.
- **MOC / Hub**: navigation for a real mature knowledge cluster, not a raw backlink list.

A Vault may use several of these at once.

## Project-first shallow directory policy

The default directory strategy should support real work without creating deep trees.

Directory depth is counted relative to the Vault root. Target depth should normally be **no more than 3 folders**.

Preferred default:

```text
<Project>/<Category>/<Note>.md
```

Use a third folder only when a real phase/workstream is large enough to justify it:

```text
<Project>/<Category>/<Workstream>/<Note>.md
```

Rules:
- project-bound work should usually use a stable project name as the first folder level;
- the second level should be one of a small number of useful functional categories, for example `Notes`, `Meetings`, `Sources`, `Experiments`, `Decisions`, `Reference`;
- the third level is exceptional, not routine;
- do not create folders to mirror every tag, month, note type or heading;
- use Properties, tags, wikilinks and MOCs for cross-cutting classification instead of deeper folders;
- a note does not need to move just because a different taxonomy could theoretically fit it;
- when the current Vault is deeper than three levels, propose a shallow target first and migrate in coherent PR batches with backlink verification; never flatten the whole Vault destructively in one pass.

## Project context and note method must cooperate

Project progress state tells the Skill **where the work currently is**. Note methodology tells it **how each kind of note should be structured**.

For project tasks:
1. load project state first;
2. identify the note's functional type;
3. apply the appropriate note contract;
4. keep the directory structure shallow and project-oriented;
5. update project progress only after the GitHub PR lifecycle succeeds.

Do not turn project progress files into notes inside the Vault unless the user explicitly requests a human-readable project dashboard note. The private project state exists to preserve agent workflow context across conversations.

## Folder / Properties / tags / links / MOC division of labor

Prefer clear responsibilities:
- **folders**: stable ownership/context, especially project and broad category;
- **Properties**: structured metadata needed for filtering/querying;
- **tags**: small set of stable cross-cutting themes or workflow states;
- **wikilinks**: semantic relationships between real notes;
- **MOC / Hub**: curated navigation where a cluster genuinely needs a map.

Avoid encoding the same hierarchy in all five systems.

## Method selection

Prefer the smallest viable hybrid system. Do not recommend PARA, Zettelkasten, Johnny Decimal or another branded method only because it is popular. Borrow useful ideas only when they solve observed friction.

## Pilot before migration

Before applying a new method broadly:
1. choose 5–15 representative notes across important note types;
2. curate them using the proposed method;
3. check retrieval, readability, maintenance cost, link quality and project usefulness;
4. adjust the method;
5. only then expand to a larger batch.

Do not start with a whole-vault rewrite.

## Persist accepted methodology

After the user accepts the method, save it only in external private `methods/note-system.json` using `state_store.py`. Future tasks load it instead of redesigning the system every time.

Re-diagnose only when:
- the user asks for a redesign;
- the methodology is missing;
- the Vault has materially drifted;
- repeated real-use failures show the current method is no longer useful.

## Preserve heterogeneity when it is useful

Do not force every note into the same headings or metadata. A troubleshooting note, meeting log, paper note and evergreen concept have different jobs. Consistency is valuable only where it reduces cognitive load or improves retrieval.
