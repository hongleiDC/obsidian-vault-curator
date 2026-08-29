# Obsidian Vault Curator

> Curate an Obsidian vault without publishing the private state that locates it.

Obsidian Vault Curator is a ChatGPT Skill for safely organizing, restructuring, linking, and maintaining Obsidian Markdown notes. It is designed for Vaults stored in GitHub while keeping all user-specific repository bindings **outside the public Skill repository and outside the Skill package**.

## Core idea

The project separates three things that should never be mixed:

```text
Public Skill source
      │
      ├── generic instructions, scripts and fictional examples
      │
External private state directory
      │
      ├── Vault repository binding and write preferences
      │
Private GitHub Vault
      └── the actual Obsidian notes and attachments
```

The public project never needs a real Vault repository identifier, real note path, copied private note, or credential.

## Features

- Single-note and multi-note curation.
- Frontmatter / Properties merge instead of destructive replacement.
- Conservative wikilink validation.
- Protection for embeds, tasks, block IDs, Dataview fields, code, formulas, footnotes, comments, and callout state.
- External private state directory for persistent Vault binding.
- GitHub branch-first write strategy with finite retries.
- Atomic multi-file commit strategy when Git Data operations are available.
- Semantic-preservation verification scripts.
- Vault indexing for safer cross-note linking.

## Private persistent state

The Skill resolves a private state directory in this order:

1. `OBSIDIAN_CURATOR_STATE_DIR` if configured.
2. Otherwise `~/.obsidian-vault-curator/`.

The private directory is intentionally **not part of this repository** and must not be placed inside the installed Skill package or the Vault repository.

Typical local layout:

```text
~/.obsidian-vault-curator/
├── profiles/default.json
├── runtime/last-success.json
├── cache/vault-index.json
└── locks/github-write.lock
```

Initialize a binding only in the private state directory:

```bash
python scripts/state_store.py init --repository <your-private-value>
```

The repository value above is supplied at runtime; it is never stored in this public source tree.

Check state without exposing the repository identifier:

```bash
python scripts/state_store.py status
```

The helper uses atomic writes and attempts private filesystem permissions where supported. Authentication tokens are never stored; GitHub authentication remains with the connector.

> Persistence depends on the execution environment providing a persistent writable directory. If it does not, the Skill must not fall back to embedding private binding data in the Skill ZIP or public repository.

## GitHub write strategy

The default policy is **branch-first**:

```text
latest base branch
      ↓
unique temporary branch
      ↓
build + validate complete change set
      ↓
one atomic commit when possible
      ↓
pull request
      ↓
mergeability/conflict check
      ↓
squash merge for safe text-only changes
```

This avoids repeatedly writing the same path with stale SHAs and reduces partial multi-file updates.

Direct writes to the base branch are disabled by default and can only be enabled through the private state profile.

The Skill also enforces:

- no concurrent writes to the same path;
- one refresh-and-retry for stale SHA/ref conflicts;
- no repeated permission/auth retries;
- no empty commits;
- no force merge for conflicted PRs;
- risky rename/move/delete/attachment changes require explicit permission and are not auto-merged by default.

## Project structure

```text
obsidian-vault-curator/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── build_vault_index.py
│   ├── state_store.py
│   └── verify_note_preservation.py
└── references/
    ├── examples.md
    ├── formatting-rules.md
    ├── github-backend.md
    ├── private-state.md
    └── vault-linking.md
```

There is deliberately no user `config/` directory in the project.

## Example prompts

```text
Curate the note I named from my bound Vault. Preserve all existing semantics and use the safe GitHub write policy.
```

```text
Audit this folder of notes for broken structure and unverified links, but do not write anything yet.
```

```text
Explain this term as a compact Obsidian concept patch without reorganizing the rest of the note.
```

## Vault indexing

For a locally materialized Vault:

```bash
python scripts/build_vault_index.py /path/to/vault --output /tmp/vault-index.json
```

The index is derived private data. Store persistent indexes only in the external private state directory, never in this public repository.

## Preservation verification

```bash
python scripts/verify_note_preservation.py original.md curated.md
```

A non-zero exit code indicates protected constructs may have disappeared or changed unexpectedly.

## Design principles

1. Preserve semantics before improving appearance.
2. Never invent knowledge relationships.
3. Merge metadata instead of replacing unknown fields.
4. Keep private binding and private note content out of Skill source, packages, fixtures, and examples.
5. Prefer a temporary branch and one logical commit over repeated file-by-file pushes.
6. Retry conflicts at most once after refreshing state.
7. Do not force risky operations through automation.
8. Keep Markdown restrained and readable.

## Inspiration

The project was inspired by the restrained curation philosophy of `qfzhao670/obsidian-curator-skill`, then independently expanded toward semantic preservation, vault-level validation, external private state, and safer GitHub write workflows.

## License

Apache-2.0.
