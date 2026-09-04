# Adaptive note methodology and namespace organization

Use this reference when diagnosing a Vault, selecting a note method, or deciding where a note should live.

## 1. Diagnose before redesign

Do not impose a fashionable framework first. Observe the existing Vault and answer:

- What directory depths and naming patterns already recur?
- Which Frontmatter keys/tags/links/tasks are stable?
- Which notes are capture, source, log, project, concept, decision, how-to, reference, or hub/MOC?
- Where are source material and personal synthesis mixed?
- Which project logs contain conclusions that should be promoted?
- Are folders, tags, Properties and links redundantly encoding the same taxonomy?

Use aggregate analysis whenever possible. Avoid copying private note bodies into reports.

## 2. Functional note types

Prefer a hybrid system. Typical contracts:

- **Capture**: fast intake; minimal formatting; process later.
- **Source**: preserve external evidence and citation; keep synthesis separate.
- **Log / Daily / Experiment**: preserve chronology, attempts, observations and outcomes.
- **Project**: current objective, status, next actions, decisions and blockers.
- **Concept / Evergreen**: independently reusable understanding; split only when reuse is real.
- **Decision**: context, options, choice, rationale, consequences.
- **How-to / Troubleshooting**: goal/symptom, evidence, steps, validation, failure modes.
- **Reference**: quick lookup; tables/lists often beat long prose.
- **MOC / Hub**: curated navigation across a mature cluster, not a backlink dump.

Do not force every type into the same template.

## 3. Separate organization mechanisms

Give each mechanism one main job:

- folders: coarse physical placement;
- Properties: stable structured metadata;
- tags: cross-cutting workflow/state/topic categories;
- wikilinks: semantic relations between concrete notes;
- MOCs: curated navigation and synthesis.

Avoid encoding the same hierarchy in all five.

## 4. Namespace-first shallow hierarchy

Preserve the user's established namespace grammar. Default maximum directory depth: **3 folders relative to the Vault root**.

Generic pattern:

```text
NB.<AREA>/<PREFIX>.<PROJECT>/<Note>.md
```

Optional one-level project-internal grouping:

```text
NB.<AREA>/<PREFIX>.<PROJECT>/<GROUP>/<Note>.md
```

Rules:

1. Level 1 is a stable high-level namespace such as `NB.<AREA>`.
2. Level 2 is a concrete research/work/project unit named `<PREFIX>.<ProjectName>`.
3. Multiple configured level-2 prefixes are peers by default; they identify project/research directions, not note types.
4. Never infer semantics from prefix spelling. A token that looks like `NAV` is not automatically a navigation note, MOC or Hub.
5. Prefix meaning must come from private methodology state.
6. Level 3 is optional and only for a genuinely useful project-internal group/stage/workstream.
7. Do not create a fourth folder level. Use Properties, tags, wikilinks or MOC for cross-cutting structure.
8. Preserve established spelling exactly; do not "correct" a user's namespace name.
9. Flattening an existing deep tree is a migration, not formatting. Move in coherent PR batches and verify backlinks/embeds.

## 5. Persist naming semantics privately

The public Skill should support arbitrary namespace/prefix schemes. Actual user roots, prefixes, meanings and project names belong in private `methods/note-system.json`.

Recommended private structure:

```json
{
  "schema_version": 1,
  "strategy": {
    "name": "hybrid-project-notes"
  },
  "organization": {
    "max_folder_depth": 3,
    "namespace_roots": ["NB.<AREA>"],
    "project_unit_pattern": "<PREFIX>.<ProjectName>",
    "project_prefixes": {
      "PX": "example domain A",
      "QX": "example domain B"
    },
    "third_level_policy": "optional-project-internal-group-only"
  },
  "note_types": [
    {"name": "project", "purpose": "current outcome and progress"},
    {"name": "concept", "purpose": "reusable understanding"},
    {"name": "source", "purpose": "external evidence"},
    {"name": "log", "purpose": "chronological work record"}
  ]
}
```

Use fictional prefix values in public docs/tests. Real user mappings remain private.

## 6. Project progress and note placement

A continuing project state normally maps to the level-2 project unit, regardless of prefix. The prefix is part of project identity but not a note type.

When curating a note:

1. resolve the active project state;
2. load private namespace/prefix mapping;
3. determine the note's functional type;
4. place it within that project's existing shallow structure;
5. create the optional third level only if several notes truly need that grouping;
6. prefer metadata/links over deeper folders.

## 7. Pilot before migration

Before a large restructure:

1. choose 5–15 representative notes;
2. map them to proposed functional types;
3. curate them using the proposed namespace/project structure;
4. evaluate retrieval, readability, linking and maintenance cost;
5. adjust the method;
6. only then apply to larger batches.

Never redesign hundreds of notes from one attractive template.

## 8. Persistence and drift

Persist an accepted method with `scripts/state_store.py method-write`. Future tasks load it instead of redesigning every time.

Re-run diagnosis only when:

- the user asks to redesign;
- methodology is missing;
- the Vault changes substantially;
- repeated notes no longer fit the current contracts;
- the current method causes friction;
- a new major workflow appears.

## 9. Anti-patterns

Do not:

- interpret a project prefix as a note type from its spelling;
- create a navigation/MOC note merely because a prefix resembles `NAV`;
- create deep folder trees for every subtopic;
- force all research projects into one content template;
- turn logs into polished evergreen prose;
- split sources into artificial atoms;
- create MOCs for tiny clusters;
- copy real user project names into public Skill examples or fixtures.
