# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project follows Semantic Versioning.

## [Unreleased]

### Planned
- Broken-link and orphan-note auditing.
- Duplicate / near-duplicate note detection.
- MOC and knowledge-cluster recommendations.
- Tag-governance reporting.
- Backlink-aware rename and move workflows.
- Incremental indexing for larger vaults.

## [0.1.0] - 2026-08-29

### Added
- Initial `obsidian-vault-curator` ChatGPT Skill.
- Single-note curation workflow.
- Multi-note and vault-aware curation workflow.
- Conservative wikilink validation rules.
- Frontmatter / Properties merge rules.
- Protection rules for code, formulas, tasks, embeds, block IDs, Dataview fields, footnotes, comments, and callouts.
- Concept-patch workflow for local explanations.
- `build_vault_index.py` for lightweight vault indexing.
- `verify_note_preservation.py` for semantic-preservation checks.
- Formatting, linking, and usage reference documents.
