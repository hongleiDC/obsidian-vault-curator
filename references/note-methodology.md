# Adaptive note methodology and Vault architecture

Use this reference when the user asks how their current notes should be organized, wants a better note-taking method, or asks the Skill to infer a suitable structure from the existing Vault.

## Contents

1. Core principle
2. Diagnosis workflow
3. What to measure
4. Note archetypes
5. Method selection
6. Hybrid architecture
7. Pilot before migration
8. Persistent methodology profile
9. Re-analysis and drift
10. Anti-patterns

## 1. Core principle

Do not force a fashionable system such as PARA or Zettelkasten onto every Vault.

The correct sequence is:

```text
observe existing data
      ↓
identify recurring note shapes and workflows
      ↓
separate capture, source, thinking, action and navigation needs
      ↓
choose the smallest useful set of note types
      ↓
pilot on a small sample
      ↓
persist the accepted method privately
      ↓
use it consistently in later curation
```

Prefer a hybrid system when the Vault contains several materially different kinds of notes.

## 2. Diagnosis workflow

### Phase A: inventory

Inspect the Vault without rewriting it.

Collect structural evidence such as:

- number and length distribution of Markdown files;
- folder depth and whether folders carry stable meaning;
- filename conventions and date-based notes;
- common Frontmatter keys;
- tags and aliases usage;
- wikilink and embed density;
- task density;
- callouts, code, formulas, Dataview fields and tables;
- source / URL / citation metadata;
- ratio of short fragmented notes to long synthesis notes;
- repeated note shapes across the Vault.

When a local/materialized Vault is available, run:

```bash
python scripts/analyze_vault_patterns.py <vault-root> --output <private-report.json>
```

The default report is aggregate-only and does not emit note titles, paths or text excerpts.

For a GitHub-only Vault, reproduce the same evidence from repository metadata plus a stratified sample. Do not download or echo the entire Vault merely to classify it.

### Phase B: identify friction

Look for operational problems, not only formatting inconsistencies:

- one note mixes capture, source quotations, personal conclusions and tasks;
- many notes are long but have no stable navigation layer;
- many tiny notes exist but rarely link to each other;
- project logs are being mistaken for permanent knowledge;
- source notes and the user's own synthesis are mixed without boundaries;
- daily notes contain valuable conclusions that never get promoted;
- folders, tags and links all attempt to represent the same taxonomy;
- MOCs are absent where the Vault has grown too large for direct search;
- duplicated metadata exists without being used by queries or workflows.

### Phase C: recommend a method

Recommend the smallest set of note types that solves the observed friction. Explain why each type is needed and which existing notes should map to it.

Do not propose a full Vault migration immediately.

## 3. What to measure

The deterministic analyzer produces evidence, not truth. Interpret signals conservatively.

Useful high-level signals:

| Signal | Likely need |
| --- | --- |
| many date-named notes | chronological log / daily workflow |
| many tasks + status fields | project/action notes |
| source/url fields + external links | source/reference notes |
| short notes + moderate wikilinks | atomic/evergreen concept notes |
| high wikilink + list density | MOC / hub notes |
| code blocks + procedural headings | technical how-to / troubleshooting notes |
| many tables, compact prose | structured reference notes |
| very long notes + many headings | synthesis / chapter-like notes |
| several strong signals at once | hybrid system, not one universal template |

Do not infer subject matter, identity or profession from structural metrics alone.

## 4. Note archetypes

Use these as functional contracts, not rigid templates.

### A. Capture / Inbox

Purpose: record quickly before classification.

Characteristics:
- minimal formatting;
- temporary status;
- should eventually be processed, linked, promoted or archived.

Do not beautify capture notes so heavily that capture becomes slow.

### B. Atomic / Evergreen concept

Purpose: preserve one reusable idea that can stand on its own.

Good for:
- definitions;
- mechanisms;
- principles;
- reusable explanations;
- conclusions that are expected to remain useful beyond one project.

Typical structure:

```markdown
# Concept

One-sentence core idea.

## Explanation
...

## Relationships
Natural wikilinks in context.
```

Do not split notes into atoms merely because they are long. Split only when the resulting notes have independent reuse value.

### C. Source / Literature / Reference

Purpose: keep what an external source says distinct from the user's synthesis.

Suggested separation:
- bibliographic/source metadata;
- factual notes or quotations;
- user's annotations clearly marked;
- links to synthesis/evergreen notes where conclusions are developed.

A source note should not automatically become the final knowledge note.

### D. Project / Outcome note

Purpose: coordinate active work toward an outcome.

Typical content:
- goal / scope;
- current state;
- next actions;
- decisions;
- links to supporting knowledge;
- results or deliverables.

Do not convert project status into permanent knowledge until it becomes reusable.

### E. Log / Daily / Experiment journal

Purpose: preserve chronology and evidence.

Typical content:
- timestamp/date;
- what happened;
- observations;
- decisions;
- next step.

Logs are append-oriented. Do not repeatedly rewrite history to make them look like evergreen notes. Promote important conclusions out of the log instead.

### F. Decision record

Purpose: preserve why a consequential choice was made.

Suggested fields:
- context;
- options;
- decision;
- rationale;
- consequences;
- revisit condition.

Useful when the same decision would otherwise be re-litigated later.

### G. Technical how-to / Troubleshooting

Purpose: make a procedure reproducible.

Suggested structure:
- symptom / goal;
- environment or prerequisites only when relevant;
- checks / evidence;
- procedure;
- verification;
- known failure modes.

Protect commands and code verbatim.

### H. MOC / Hub

Purpose: provide curated navigation over a topic, project or domain.

A hub should organize and explain relationships. It is not merely a dump of every backlink.

Use MOCs when direct search and backlinks are no longer enough, not because every topic needs one.

### I. Structured reference

Purpose: fast lookup of stable facts, commands, parameters or comparisons.

Prefer tables, lists or compact sections. Avoid turning reference material into unnecessary prose.

## 5. Method selection

Select a system based on dominant workflows:

### Mostly learning / conceptual knowledge

Use:
- source notes;
- atomic/evergreen concepts;
- synthesis notes;
- topic MOCs when clusters grow.

This is Zettelkasten-like only where atomicity and linking create real reuse value.

### Mostly projects and active work

Use:
- project/outcome notes;
- logs;
- decision records;
- supporting reference/knowledge notes.

A PARA-like folder layer may help for lifecycle management, but do not use folders as the only knowledge relation.

### Mostly research / source-heavy work

Use:
- source/literature notes;
- experiment/log notes;
- synthesis/claim notes;
- MOCs or research hubs;
- explicit separation between evidence and interpretation.

### Mostly operational / technical notes

Use:
- how-to/troubleshooting notes;
- structured references;
- decision records;
- project notes for active implementation;
- hubs for system-level navigation.

### Mixed Vault

Default to a note-type-based hybrid. Do not demand one universal template.

## 6. Hybrid architecture

A useful default architecture is functional rather than topic-specific:

```text
Capture  → temporary input
Source   → what external material says
Log      → what happened over time
Project  → what is being done now
Concept  → reusable understanding
Decision → why a choice was made
Reference→ fast lookup
MOC      → navigation and synthesis
```

Folders, tags, Properties and wikilinks should have distinct jobs:

- **folders**: coarse storage/lifecycle boundaries when useful;
- **Properties**: machine-queryable state/type/source metadata;
- **tags**: broad cross-cutting categories or workflow state;
- **wikilinks**: semantic relationships between concrete notes;
- **MOCs**: curated navigation and explanation across a cluster.

Avoid using all four to encode the same taxonomy.

## 7. Pilot before migration

Before changing a large Vault:

1. choose 5–15 representative notes from the relevant scope;
2. map each to a proposed note type;
3. curate them with the proposed contracts;
4. evaluate retrieval, readability, linking and maintenance cost;
5. adjust the method;
6. only then apply to a larger batch.

Never redesign hundreds of notes based only on one attractive template.

## 8. Persistent methodology profile

Once a method is accepted, persist only the method and structural preferences in the external private state directory:

```text
<state-root>/methods/note-system.json
```

Use:

```bash
python scripts/state_store.py method-write --file <methodology.json>
python scripts/state_store.py method-read
python scripts/state_store.py method-status
```

Recommended private schema:

```json
{
  "schema_version": 1,
  "strategy": {
    "name": "hybrid-note-types",
    "principles": [
      "separate source from synthesis",
      "preserve logs chronologically",
      "promote reusable conclusions to concept notes"
    ]
  },
  "note_types": [
    {
      "name": "concept",
      "purpose": "reusable understanding",
      "preferred_sections": ["core idea", "explanation", "relationships"]
    }
  ],
  "organization": {
    "folders_role": "coarse lifecycle only",
    "tags_role": "cross-cutting state/categories",
    "links_role": "semantic relationships",
    "moc_role": "curated navigation"
  },
  "curation_rules": {
    "split_long_notes_only_when_independently_reusable": true,
    "preserve_log_chronology": true
  }
}
```

Do not store raw note bodies, copied excerpts, credentials or repository identifiers in the methodology file.

At the start of future curation tasks, load the methodology profile after the Vault binding. Use it as the default organization policy unless the current note clearly belongs to a different functional type.

## 9. Re-analysis and drift

Do not re-analyze the whole Vault every time.

Re-run diagnosis when:
- the user asks to redesign the note system;
- the methodology file is absent;
- the Vault changed substantially;
- repeated notes do not fit the current types;
- the user says the current method feels cumbersome;
- a new major workflow appears.

Otherwise apply the existing private methodology profile.

## 10. Anti-patterns

Do not:
- force every note into the same section template;
- equate short notes with good atomic notes;
- split source material into dozens of artificial atoms;
- turn daily logs into polished evergreen prose;
- create MOCs for tiny clusters;
- create tags and wikilinks for every noun;
- migrate the entire Vault before testing the method;
- infer a user's profession or identity from note structure;
- persist private content in public Skill source or examples.
