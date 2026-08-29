#!/usr/bin/env python3
"""Analyze structural patterns in an Obsidian Vault without copying note bodies.

The report contains aggregate metrics that help the Skill recommend a note system.
By default it does not emit note titles, file paths, frontmatter values, or text excerpts.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Iterable

SKIP_DIRS = {".git", ".obsidian", ".trash", "node_modules", ".venv", "venv"}
DATE_NAME_RE = re.compile(r"(?:^|[^0-9])(20\d{2})[-_.]?(0[1-9]|1[0-2])[-_.]?([0-2]\d|3[01])(?:[^0-9]|$)")
WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\]]+)\]\]")
EMBED_RE = re.compile(r"!\[\[([^\]]+)\]\]")
TASK_RE = re.compile(r"(?m)^\s*[-*+]\s+\[[ xX-]\]\s+")
CALLOUT_RE = re.compile(r"(?m)^\s*>\s*\[![^\]]+\][+-]?")
CODE_FENCE_RE = re.compile(r"(?m)^\s*```|^\s*~~~")
DATAVIEW_RE = re.compile(r"(?m)^\s*[A-Za-z0-9_\- .]+::\s*.+$")
EXT_LINK_RE = re.compile(r"\[[^\]]+\]\(https?://[^)]+\)|https?://\S+")
INLINE_TAG_RE = re.compile(r"(?<![\w/])#([\w\-]+(?:/[\w\-]+)*)")
HEADING_RE = re.compile(r"(?m)^(#{1,6})\s+.+$")
LIST_RE = re.compile(r"(?m)^\s*(?:[-*+] |\d+[.)] )")
TABLE_RE = re.compile(r"(?m)^\s*\|.*\|\s*$")
MATH_BLOCK_RE = re.compile(r"\$\$[\s\S]*?\$\$")
FRONTMATTER_RE = re.compile(r"\A---\s*\n([\s\S]*?)\n---\s*(?:\n|\Z)")


def iter_markdown(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            yield path


def percentile(values: list[int], p: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    idx = max(0, min(len(ordered) - 1, math.ceil(p * len(ordered)) - 1))
    return ordered[idx]


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    block = match.group(1)
    data: dict[str, object] = {}
    current_key: str | None = None
    current_list: list[str] | None = None
    for raw in block.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        list_match = re.match(r"^\s+-\s+(.+?)\s*$", line)
        if list_match and current_key and current_list is not None:
            current_list.append(list_match.group(1).strip().strip('"\''))
            continue
        kv = re.match(r"^([A-Za-z0-9_.-]+)\s*:\s*(.*)$", line)
        if not kv:
            current_key = None
            current_list = None
            continue
        key, value = kv.group(1), kv.group(2).strip()
        current_key = key
        if value == "":
            current_list = []
            data[key] = current_list
        elif value.startswith("[") and value.endswith("]"):
            items = [x.strip().strip('"\'') for x in value[1:-1].split(",") if x.strip()]
            data[key] = items
            current_list = None
        else:
            data[key] = value.strip('"\'')
            current_list = None
    return data, text[match.end():]


def classify_shape(features: dict[str, int | bool]) -> list[str]:
    signals: list[tuple[str, int]] = []
    chars = int(features["chars"])
    tasks = int(features["tasks"])
    links = int(features["wikilinks"])
    external = int(features["external_links"])
    headings = int(features["headings"])
    list_lines = int(features["list_lines"])
    tables = int(features["table_lines"])
    code = int(features["code_fences"])
    dated = bool(features["dated_filename"])
    has_source = bool(features["has_source_field"])
    has_status = bool(features["has_status_field"])

    if dated:
        signals.append(("chronological-log", 3))
    if tasks >= 2 or (tasks >= 1 and has_status):
        signals.append(("action-project", 3))
    if has_source or external >= 3:
        signals.append(("source-reference", 3))
    if links >= 8 and list_lines >= 6 and chars < 5000:
        signals.append(("hub-moc", 3))
    if chars <= 2500 and tasks == 0 and not has_source and 0 <= headings <= 4:
        signals.append(("atomic-concept", 2))
    if code >= 2 or (code >= 1 and headings >= 2):
        signals.append(("technical-howto", 2))
    if tables >= 3 and chars < 6000:
        signals.append(("structured-reference", 2))
    if chars >= 8000 and headings >= 5:
        signals.append(("longform-synthesis", 2))
    if not signals:
        signals.append(("general-note", 1))
    return [name for name, _ in sorted(signals, key=lambda x: (-x[1], x[0]))[:3]]


def analyze(root: Path, include_folder_names: bool = False) -> dict:
    files = list(iter_markdown(root))
    chars: list[int] = []
    heading_counts: Counter[int] = Counter()
    fm_keys: Counter[str] = Counter()
    feature_notes: Counter[str] = Counter()
    shape_counts: Counter[str] = Counter()
    folder_depths: Counter[int] = Counter()
    folder_names: Counter[str] = Counter()
    total = Counter()

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        fm, body = parse_frontmatter(text)
        rel = path.relative_to(root)
        depth = max(0, len(rel.parts) - 1)
        folder_depths[depth] += 1
        if include_folder_names and depth:
            folder_names[str(rel.parent)] += 1

        body_chars = len(body.strip())
        chars.append(body_chars)
        headings = [len(m.group(1)) for m in HEADING_RE.finditer(body)]
        for level in headings:
            heading_counts[level] += 1
        for key in fm:
            fm_keys[key] += 1

        features = {
            "chars": body_chars,
            "headings": len(headings),
            "tasks": len(TASK_RE.findall(body)),
            "wikilinks": len(WIKILINK_RE.findall(body)),
            "embeds": len(EMBED_RE.findall(body)),
            "callouts": len(CALLOUT_RE.findall(body)),
            "code_fences": len(CODE_FENCE_RE.findall(body)) // 2,
            "dataview_fields": len(DATAVIEW_RE.findall(body)),
            "external_links": len(EXT_LINK_RE.findall(body)),
            "inline_tags": len(INLINE_TAG_RE.findall(body)),
            "list_lines": len(LIST_RE.findall(body)),
            "table_lines": len(TABLE_RE.findall(body)),
            "math_blocks": len(MATH_BLOCK_RE.findall(body)),
            "dated_filename": bool(DATE_NAME_RE.search(path.stem)),
            "has_source_field": any(k.lower() in {"source", "url", "doi", "citation", "reference"} for k in fm),
            "has_status_field": any(k.lower() in {"status", "state", "stage"} for k in fm),
        }
        for key, value in features.items():
            if isinstance(value, bool):
                if value:
                    feature_notes[key] += 1
            elif isinstance(value, int):
                total[key] += value
                if value > 0:
                    feature_notes[key] += 1
        for shape in classify_shape(features):
            shape_counts[shape] += 1

    n = len(files)
    coverage = lambda count: round((count / n * 100.0), 1) if n else 0.0
    report = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "privacy": {
            "contains_note_bodies": False,
            "contains_note_titles_or_paths": bool(include_folder_names),
            "aggregate_only_by_default": True,
        },
        "vault_shape": {
            "markdown_files": n,
            "folder_depth_distribution": {str(k): v for k, v in sorted(folder_depths.items())},
            "note_length_chars": {
                "median": int(median(chars)) if chars else 0,
                "p90": percentile(chars, 0.90),
                "max": max(chars) if chars else 0,
                "short_le_1200_pct": coverage(sum(1 for x in chars if x <= 1200)),
                "long_ge_8000_pct": coverage(sum(1 for x in chars if x >= 8000)),
            },
            "heading_level_counts": {str(k): v for k, v in sorted(heading_counts.items())},
        },
        "metadata": {
            "frontmatter_present_pct": coverage(sum(1 for p in files if FRONTMATTER_RE.match(p.read_text(encoding="utf-8", errors="replace")))),
            "common_frontmatter_keys": fm_keys.most_common(20),
        },
        "feature_coverage_pct": {key: coverage(count) for key, count in sorted(feature_notes.items())},
        "feature_totals": {key: int(value) for key, value in sorted(total.items())},
        "structural_archetype_signals": [
            {"archetype": name, "note_count": count, "coverage_pct": coverage(count)}
            for name, count in shape_counts.most_common()
        ],
        "interpretation_hints": [
            "Use structural_archetype_signals as evidence, not as final classification.",
            "Prefer a hybrid note system when multiple archetypes have material coverage.",
            "Do not infer subject matter or identity from this aggregate report.",
        ],
    }
    if include_folder_names:
        report["vault_shape"]["folder_names"] = folder_names.most_common(50)
    return report


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("vault_root", type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--include-folder-names", action="store_true", help="include folder names; off by default for privacy")
    return p


def main() -> int:
    args = build_parser().parse_args()
    root = args.vault_root.expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"vault root is not a directory: {root}")
    report = analyze(root, include_folder_names=args.include_folder_names)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
