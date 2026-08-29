# Obsidian formatting and preservation rules

Use this reference when handling complex Obsidian Markdown, Properties, code, formulas, tasks, or plugin fields.

## 1. Headings and paragraphs

- Keep an existing reasonable H1.
- Add one H1 from content or filename only when the note lacks a title.
- Prefer `##` and `###`; use deeper levels only for real hierarchy.
- Use paragraphs for continuous reasoning and lists for parallel points, steps, conditions, pros/cons, or checklists.
- Improve readability without changing causality, scope, probability, negation, numbers, or units.

## 2. Properties / Frontmatter

Generic example:

```yaml
---
tags:
  - software/testing
aliases:
  - 测试策略
source: existing-source
custom_field: keep-existing-value
---
```

Rules:

- Read existing Frontmatter before changing it.
- Preserve unknown fields.
- Deduplicate multi-value fields while preserving meaningful order.
- Do not infer `created`, `modified`, `author`, or `source` values.
- Do not replace a user's schema with a template.

## 3. Tags and aliases

Good generic tag categories:

- stable topic: `software/testing`, `database/indexing`;
- long-running workspace: `project/example`;
- workflow state: `status/to-review`.

Avoid:

- turning every noun into a tag;
- producing many one-off tags;
- creating duplicate synonyms unless the Vault already uses them.

Aliases should represent real abbreviations, common alternate names, translations, or historical names.

## 4. Wikilinks and embeds

Common forms:

```markdown
[[Note]]
[[Note|Display text]]
[[Note#Heading]]
[[Note#^block-id]]
[[#Local heading]]
![[image.png]]
![[image.png|420]]
![[Note#Heading]]
```

Protection rules:

- Treat embeds as references; do not change their targets during ordinary curation.
- Do not rewrite existing link targets without a verified reason.
- Heading renames can break deep links; avoid them without Vault-wide context.
- Preserve block IDs exactly.

## 5. Callouts

```markdown
> [!note] Title
> Content
```

Collapsed patch:

```markdown
> [!question]- 补丁：术语是什么？
> 解释
```

Use callouts only for clear semantics such as a note, tip, warning, question, summary, or isolated example. Preserve existing `+` / `-` collapse state.

## 6. Code and formulas

- Preserve fenced code block content byte-for-byte when practical, including indentation and comments.
- Do not rewrite inline code such as commands, paths, parameters, function names, or identifiers as prose.
- Preserve `$...$`, `$$...$$`, LaTeX environments, symbols, subscripts, units, and custom macros.

## 7. Tasks, Dataview, and block IDs

Protect structures such as:

```markdown
- [ ] pending item
- [x] completed item
status:: active
priority:: high
^reference-block
```

- Task state is data.
- Dataview keys, `::`, and values may be queried.
- DataviewJS blocks are code.
- Block IDs must remain exact.

## 8. Quotes, footnotes, and comments

Protect:

```markdown
> quoted text
[^1]: footnote body
term[^1]
%% Obsidian comment %%
```

Do not flatten quoted material into ordinary prose when that would erase source boundaries. Keep footnote references paired with definitions. Keep Obsidian comments private and do not expand them into visible text.

## 9. Tables and emphasis

- Use tables only for real multi-column comparison or structured data.
- Preserve meaningful `==highlight==`.
- Add bold sparingly.
- Do not add decorative emoji, colored HTML, or CSS by default.

## 10. Forbidden transformations by default

Do not automatically:

- rename notes;
- move attachments;
- manufacture unverified wikilinks;
- mass-rename headings;
- delete unfamiliar Properties;
- remove tasks, footnotes, comments, block IDs, or Dataview fields;
- rewrite code, commands, paths, or LaTeX;
- invent sources, URLs, numbers, citations, or conclusions;
- copy private user content into Skill examples, tests, logs, changelogs, or repository documentation.
