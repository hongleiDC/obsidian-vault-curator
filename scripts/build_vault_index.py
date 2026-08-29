#!/usr/bin/env python3
"""Build a lightweight JSON index for an Obsidian vault.

Uses only the Python standard library. The index is intended for link validation
and conservative batch curation, not for fully parsing Obsidian Markdown.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

SKIP_DIRS = {".obsidian", ".git", ".trash", "node_modules"}

FENCE_RE = re.compile(r"(?ms)^\s*(```|~~~).*?^\s*\1\s*$")
WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\]]+)\]\]")
EMBED_RE = re.compile(r"!\[\[([^\]]+)\]\]")
HEADING_RE = re.compile(r"(?m)^(#{1,6})\s+(.+?)\s*$")
BLOCK_ID_RE = re.compile(r"(?m)(?<!\S)\^([A-Za-z0-9_-]+)\s*$")


def strip_fenced_code(text: str) -> str:
    return FENCE_RE.sub("", text)


def normalize_target(raw: str) -> str:
    target = raw.split("|", 1)[0].strip()
    return target


def first_h1(headings: list[dict[str, object]], fallback: str) -> str:
    for item in headings:
        if item["level"] == 1:
            return str(item["text"])
    return fallback


def iter_markdown_files(root: Path):
    for path in root.rglob("*.md"):
        rel_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in rel_parts[:-1]):
            continue
        yield path


def parse_note(path: Path, root: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    scan_text = strip_fenced_code(text)

    headings = []
    for match in HEADING_RE.finditer(scan_text):
        headings.append({"level": len(match.group(1)), "text": match.group(2).strip()})

    links = [normalize_target(m.group(1)) for m in WIKILINK_RE.finditer(scan_text)]
    embeds = [normalize_target(m.group(1)) for m in EMBED_RE.finditer(scan_text)]
    block_ids = [m.group(1) for m in BLOCK_ID_RE.finditer(scan_text)]

    rel = path.relative_to(root).as_posix()
    stem = path.stem
    return {
        "path": rel,
        "stem": stem,
        "title": first_h1(headings, stem),
        "headings": headings,
        "block_ids": block_ids,
        "wikilink_targets": links,
        "embed_targets": embeds,
    }


def build_index(root: Path) -> dict[str, object]:
    notes = [parse_note(path, root) for path in sorted(iter_markdown_files(root))]

    by_stem: dict[str, list[str]] = defaultdict(list)
    for note in notes:
        by_stem[str(note["stem"])].append(str(note["path"]))

    duplicate_stems = {stem: paths for stem, paths in by_stem.items() if len(paths) > 1}

    return {
        "vault_root": str(root.resolve()),
        "note_count": len(notes),
        "duplicate_stems": duplicate_stems,
        "notes": notes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a lightweight Obsidian vault index.")
    parser.add_argument("vault_root", type=Path, help="Path to the Obsidian vault root")
    parser.add_argument("--output", type=Path, help="Write JSON to this file instead of stdout")
    args = parser.parse_args()

    root = args.vault_root.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"vault_root is not a directory: {root}")

    index = build_index(root)
    payload = json.dumps(index, ensure_ascii=False, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
