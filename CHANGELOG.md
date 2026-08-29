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
