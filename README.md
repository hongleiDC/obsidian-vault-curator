# Obsidian Vault Curator

> Curate your Obsidian vault without breaking what makes it a vault.

**Obsidian Vault Curator** is a ChatGPT Skill for safely organizing, restructuring, linking, and maintaining Obsidian Markdown notes and vaults. It focuses on improving readability and knowledge structure **without breaking Obsidian semantics** such as wikilinks, embeds, tasks, block IDs, Dataview fields, code blocks, formulas, footnotes, or custom Properties.

中文简介：这是一个用于安全整理、重构和维护 Obsidian 知识库的 ChatGPT Skill。它不仅美化 Markdown，还会优先保护双链、任务、公式、代码、附件、Properties、Dataview 字段和知识关系。

## Why this project exists

Many note-cleaning workflows treat Obsidian files as ordinary Markdown. That can make notes look cleaner while silently damaging the structures that make a vault useful.

This project follows a stricter principle:

> **Preserve semantics first. Improve structure second. Add knowledge relationships only when they are real.**

## Features

### Single-note curation

- Reorganize headings, paragraphs, lists, tables, and callouts.
- Merge existing Frontmatter / Obsidian Properties instead of replacing them.
- Preserve facts, numbers, conclusions, citations, and qualifiers.
- Keep formatting restrained and readable instead of decorative.

### Vault-aware curation

- Scan multiple notes or a complete vault before creating new links.
- Detect duplicate note stems.
- Index headings, block IDs, wikilinks, and embeds.
- Add cross-note links only when the destination actually exists and the relation is meaningful.

### Semantic protection

The Skill treats the following as protected content by default:

- YAML Frontmatter / custom Properties
- `[[wikilinks]]`, heading links, and block links
- `![[embeds]]` and attachment paths
- fenced code blocks and inline code
- LaTeX / MathJax formulas
- tasks such as `- [ ]` and `- [x]`
- Dataview fields such as `key:: value`
- block IDs such as `^reference-block`
- footnotes, quotations, comments, and callout state

### Concept patches

When a user asks what a term means, the Skill can add a small, clearly marked, collapsible explanation next to the original sentence instead of rewriting the entire note.

### Safety verification

The bundled verification script compares an original note with the curated result and reports protected constructs that disappeared or changed unexpectedly.

## Workflow

```text
Raw notes
    ↓
Protect Obsidian semantics
    ↓
Restructure content
    ↓
Validate real vault relationships
    ↓
Curated, linked, maintainable notes
    ↓
Preservation check
```

## Project structure

```text
obsidian-vault-curator/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── build_vault_index.py
│   └── verify_note_preservation.py
└── references/
    ├── formatting-rules.md
    ├── vault-linking.md
    └── examples.md
```

## Installation

Download or clone this repository and install the repository folder as a ChatGPT Skill using the Skills interface available in your ChatGPT environment.

The Skill entrypoint is:

```text
SKILL.md
```

## Example prompts

### Organize one note

```text
Use Obsidian Vault Curator to reorganize this note. Preserve all existing facts,
code, formulas, tasks, Properties, attachments, and wikilinks.
```

### Organize a vault folder

```text
Curate the notes in this Obsidian folder. Build a vault index first, preserve the
existing structure, and only add wikilinks when the destination really exists.
```

### Audit without rewriting

```text
Audit these Obsidian notes for structural problems, broken knowledge relationships,
metadata inconsistency, and unsafe formatting changes. Do not modify the files.
```

### Explain a concept in place

```text
Explain this term with a compact Obsidian concept patch. Do not reorganize the
rest of the note.
```

## Vault indexing

Build a lightweight index before multi-note or vault-wide linking:

```bash
python scripts/build_vault_index.py /path/to/vault --output /tmp/vault-index.json
```

The index includes note paths, stems, first H1 titles, headings, block IDs, wikilinks, embeds, and duplicate stems.

## Preservation verification

After curating a note, compare it with the original:

```bash
python scripts/verify_note_preservation.py original.md curated.md
```

The script returns a non-zero exit code when protected constructs appear to be missing or modified unexpectedly.

## Design principles

1. **Do not invent content.** Reorganize existing knowledge unless the user explicitly asks for additions.
2. **Do not manufacture links.** A plausible concept name is not enough to create a wikilink.
3. **Merge metadata instead of replacing it.** Unknown Properties may be important to plugins or personal workflows.
4. **Do not optimize for Graph View density.** Links should improve navigation or understanding.
5. **Avoid whole-vault rewrites by default.** Curate in small, verifiable batches.
6. **Do not automatically rename or move files.** Those operations require backlink-aware migration.
7. **Keep Markdown restrained.** Structure should clarify knowledge rather than decorate it.

## Roadmap

Potential future directions include:

- orphan-note and broken-link auditing
- duplicate / near-duplicate note detection
- MOC recommendation and knowledge-cluster discovery
- tag-governance reports
- backlink-aware note rename / move workflows
- configurable PARA, Zettelkasten, MOC, and custom taxonomy support
- larger-vault incremental indexing

## Inspiration

This project was inspired by the lightweight, restrained curation philosophy of [`qfzhao670/obsidian-curator-skill`](https://github.com/qfzhao670/obsidian-curator-skill), then independently expanded toward vault-level maintenance, semantic preservation, conservative link validation, and automated preservation checks.

## License

Licensed under the Apache License 2.0. See [`LICENSE`](LICENSE).
