# Obsidian Vault Curator

> Curate your Obsidian vault without breaking what makes it a vault.

**Obsidian Vault Curator** is a ChatGPT Skill for safely organizing, restructuring, linking, and maintaining Obsidian Markdown notes and vaults. It is designed especially for a **GitHub-backed personal Obsidian vault**: the Skill can remember which repository is the user's vault through a private profile, read current notes from GitHub, and write changes back with a conflict-aware strategy.

中文简介：这是一个用于安全整理、重构和维护 Obsidian 知识库的 ChatGPT Skill。它特别适合把 Obsidian Vault 长期保存在 GitHub 的场景：一次绑定笔记仓库后，后续新对话可直接恢复仓库、分支和 Vault 根目录，不需要反复输入地址。

## Why this project exists

Many note-cleaning workflows treat Obsidian files as ordinary Markdown. That can make notes look cleaner while silently damaging the structures that make a vault useful.

This project follows a stricter principle:

> **Preserve semantics first. Improve structure second. Add knowledge relationships only when they are real.**

For GitHub-backed vaults, it adds another principle:

> **Always read the current remote state before writing, and never enter an unlimited push-retry loop.**

## Features

### Persistent GitHub vault binding

A user-specific `config/vault.yaml` can store:

- GitHub repository (`owner/repository`)
- default branch
- Vault root directory inside the repository
- direct-write vs branch/PR policy
- batch size and merge behavior
- safety switches for create/delete/rename/attachments

The public repository contains only [`config/vault.example.yaml`](config/vault.example.yaml). The real `config/vault.yaml` is ignored by Git so a private repository address does not need to be published with the Skill source.

Once the personal profile exists, the Skill reads it at the beginning of every GitHub-backed task instead of asking for the repository again.

### Conflict-aware GitHub writes

The default strategy is adaptive:

- **One safe text-note change** → update the configured base branch directly.
- **Two or more changed files** → temporary branch + pull request.
- **Cross-note linking or metadata normalization** → temporary branch + pull request.
- **Rename, move, delete, backlink migration, or attachment changes** → temporary branch and no automatic merge by default.

For direct writes the Skill re-fetches the file immediately before updating it and uses the fresh blob SHA. If the remote file changed, it re-applies the intended edit to the newest content and retries **once only**.

This avoids common GitHub Contents API failure loops caused by reusing a stale SHA or repeatedly calling create/update with the wrong operation.

### Single-note curation

- Reorganize headings, paragraphs, lists, tables, and callouts.
- Merge existing Frontmatter / Obsidian Properties instead of replacing them.
- Preserve facts, numbers, conclusions, citations, and qualifiers.
- Keep formatting restrained and readable instead of decorative.

### Vault-aware curation

- Work with multiple notes or a complete vault.
- Detect duplicate note stems when a local index is available.
- Validate headings, block IDs, wikilinks, and embeds.
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
Persistent vault profile
    ↓
Read current GitHub state
    ↓
Protect Obsidian semantics
    ↓
Restructure content
    ↓
Validate real vault relationships
    ↓
Choose direct write or temporary branch
    ↓
Verify remote result
```

## Project structure

```text
obsidian-vault-curator/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── config/
│   └── vault.example.yaml
├── scripts/
│   ├── build_vault_index.py
│   └── verify_note_preservation.py
└── references/
    ├── github-backend.md
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

### One-time personal vault setup

Copy the example profile to a private `config/vault.yaml` in the Skill package or working copy and fill in your own vault:

```yaml
vault:
  repository: owner/repository
  branch: main
  root: ""
```

Do **not** commit `config/vault.yaml` to this public repository if the repository name or personal setup should remain private.

## Example prompts

After the vault profile is configured, prompts no longer need the repository URL:

```text
整理我的 ROS Noetic 笔记，并保存回仓库。
```

```text
检查我最近几篇 GNSS 笔记的结构和双链，只修改确实需要整理的文件。
```

```text
把 TF debugging 相关笔记重新整理一下，多文件修改使用安全分支策略。
```

You can still use the Skill on uploaded or pasted Markdown:

```text
Use Obsidian Vault Curator to reorganize this note. Preserve all existing facts,
code, formulas, tasks, Properties, attachments, and wikilinks.
```

## GitHub write policy

Detailed GitHub behavior is documented in [`references/github-backend.md`](references/github-backend.md).

Key rules:

1. Always fetch the current remote file before editing.
2. Fetch again immediately before a direct update and use the newest SHA.
3. Never write the same path concurrently.
4. Prefer one complete update per file per task.
5. Retry stale-SHA conflicts once, then stop.
6. Skip no-op commits.
7. Use a temporary branch for coordinated multi-file changes.
8. Squash safe batches to keep the main history readable.

## Vault indexing

When the Vault is also available locally, build a lightweight index before multi-note or vault-wide linking:

```bash
python scripts/build_vault_index.py /path/to/vault --output /tmp/vault-index.json
```

The index includes note paths, stems, first H1 titles, headings, block IDs, wikilinks, embeds, and duplicate stems.

For a GitHub-only vault, use the configured repository and GitHub connector as the source of truth instead of assuming a local clone exists.

## Preservation verification

After curating a local or materialized note, compare it with the original:

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
8. **Do not reuse stale GitHub SHAs.** Re-read before writing.
9. **Do not retry forever.** One conflict refresh/retry is the default ceiling.

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

This project was inspired by the lightweight, restrained curation philosophy of [`qfzhao670/obsidian-curator-skill`](https://github.com/qfzhao670/obsidian-curator-skill), then independently expanded toward GitHub-backed vault persistence, semantic preservation, conservative link validation, and conflict-aware writes.

## License

Licensed under the Apache License 2.0. See [`LICENSE`](LICENSE).
