# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Planned
- Orphan-note and broken-link auditing.
- Duplicate / near-duplicate note detection.
- MOC and knowledge-cluster recommendations.
- Tag-governance reporting.
- Backlink-aware rename and move workflows.
- Incremental indexing for larger vaults.

## [0.3.0] - 2026-08-29

### Added
- Adaptive Vault diagnosis before choosing a note-taking method.
- `scripts/analyze_vault_patterns.py` for privacy-preserving aggregate structural analysis.
- `references/note-methodology.md` with functional note types, method-selection rules, hybrid architecture, pilot workflow, and migration boundaries.
- Private methodology persistence at `methods/note-system.json` through new `state_store.py` method commands.
- Explicit note archetypes for capture, concept, source/reference, project, log/experiment, decision, technical how-to, MOC/hub, and structured reference notes.

### Changed
- The Skill now treats note-system design as a core capability rather than a formatting side effect.
- Future curation loads an accepted private methodology instead of re-designing the Vault on every task.
- Large migrations require a representative pilot before broad application.
- PARA, Zettelkasten, MOC, folder, tag, and link strategies are selected only when supported by the existing Vault workflow.

## [0.2.0] - 2026-08-29

### Changed
- Moved all user-specific Vault binding out of the Skill repository and Skill package.
- Added an external private state directory resolved by `OBSIDIAN_CURATOR_STATE_DIR` or `~/.obsidian-vault-curator/`.
- Removed the repository-level Vault configuration template.
- Switched the default GitHub write policy to branch-first.
- Prefer one atomic multi-file commit on temporary branches when Git Data operations are available.
- Kept stale SHA/ref retries capped at one refresh-and-retry cycle.
- Added a private write-lock workflow to reduce overlapping GitHub mutations.
- Replaced domain-specific examples with fictional, generic examples.
- Added an explicit privacy rule preventing real user note content, paths, repository identifiers, or credentials from entering public examples, fixtures, logs, changelogs, or Skill packages.

### Added
- `scripts/state_store.py` for atomic external state management and write locking.
- `references/private-state.md` for persistence and privacy boundaries.

## [0.1.0] - 2026-08-29

### Added
- Initial Obsidian Vault curation workflow.
- Single-note and multi-note organization.
- Conservative wikilink validation.
- Frontmatter / Properties merge rules.
- Protection for code, formulas, tasks, embeds, block IDs, Dataview fields, footnotes, comments, and callouts.
- Concept-patch workflow.
- Lightweight Vault indexing and preservation verification scripts.
