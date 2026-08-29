#!/usr/bin/env python3
"""Check that protected Obsidian constructs from an original note still exist.

The check is intentionally conservative. Additions are allowed; disappearance of
protected constructs is reported. Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

FENCE_RE = re.compile(r"(?ms)^\s*(?P<fence>```|~~~).*?^\s*(?P=fence)\s*$")
MATH_BLOCK_RE = re.compile(r"(?ms)\$\$.*?\$\$")
EMBED_RE = re.compile(r"!\[\[[^\]]+\]\]")
WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\]]+)\]\]")
TASK_RE = re.compile(r"(?m)^\s*[-*+]\s+\[[ xX]\].*$")
DATAVIEW_RE = re.compile(r"(?m)^\s*[^\n:]+::\s*.*$")
BLOCK_ID_RE = re.compile(r"(?m)(?<!\S)\^([A-Za-z0-9_-]+)\s*$")
COMMENT_RE = re.compile(r"(?s)%%.*?%%")
FOOTNOTE_DEF_RE = re.compile(r"(?m)^\[\^[^\]]+\]:.*$")

MUTABLE_FRONTMATTER_KEYS = {"tags", "aliases"}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def extract_frontmatter(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", text, re.S)
    return match.group(1) if match else None


def parse_frontmatter_blocks(frontmatter: str | None) -> dict[str, str]:
    if not frontmatter:
        return {}
    lines = frontmatter.splitlines()
    starts = []
    for i, line in enumerate(lines):
        match = re.match(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$", line)
        if match:
            starts.append((i, match.group(1)))
    result = {}
    for idx, (start, key) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        result[key] = "\n".join(lines[start:end]).strip()
    return result


def normalize_wikilink_target(raw: str) -> str:
    return raw.split("|", 1)[0].strip()


def subset_missing(original_items, curated_items):
    a = Counter(original_items)
    b = Counter(curated_items)
    missing = []
    for item, count in a.items():
        deficit = count - b[item]
        if deficit > 0:
            missing.extend([item] * deficit)
    return missing


def check(original: str, curated: str) -> dict[str, object]:
    issues = []

    fenced_before = [m.group(0) for m in FENCE_RE.finditer(original)]
    fenced_after = [m.group(0) for m in FENCE_RE.finditer(curated)]

    checks = {
        "fenced_code_blocks": (fenced_before, fenced_after),
        "math_blocks": (MATH_BLOCK_RE.findall(original), MATH_BLOCK_RE.findall(curated)),
        "embeds": (EMBED_RE.findall(original), EMBED_RE.findall(curated)),
        "tasks": (TASK_RE.findall(original), TASK_RE.findall(curated)),
        "dataview_fields": (DATAVIEW_RE.findall(original), DATAVIEW_RE.findall(curated)),
        "comments": (COMMENT_RE.findall(original), COMMENT_RE.findall(curated)),
        "footnote_definitions": (FOOTNOTE_DEF_RE.findall(original), FOOTNOTE_DEF_RE.findall(curated)),
    }

    for name, (before, after) in checks.items():
        missing = subset_missing(before, after)
        if missing:
            issues.append({"type": name, "missing": missing})

    before_links = [normalize_wikilink_target(x) for x in WIKILINK_RE.findall(original)]
    after_links = [normalize_wikilink_target(x) for x in WIKILINK_RE.findall(curated)]
    missing_links = subset_missing(before_links, after_links)
    if missing_links:
        issues.append({"type": "wikilink_targets", "missing": missing_links})

    before_blocks = BLOCK_ID_RE.findall(original)
    after_blocks = BLOCK_ID_RE.findall(curated)
    missing_blocks = subset_missing(before_blocks, after_blocks)
    if missing_blocks:
        issues.append({"type": "block_ids", "missing": missing_blocks})

    before_fm = parse_frontmatter_blocks(extract_frontmatter(original))
    after_fm = parse_frontmatter_blocks(extract_frontmatter(curated))
    for key, raw_block in before_fm.items():
        if key not in after_fm:
            issues.append({"type": "frontmatter_key", "missing": [key]})
        elif key not in MUTABLE_FRONTMATTER_KEYS and raw_block != after_fm[key]:
            issues.append({
                "type": "frontmatter_value_changed",
                "key": key,
                "before": raw_block,
                "after": after_fm[key],
            })

    return {"ok": not issues, "issues": issues}


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify protected Obsidian constructs are preserved.")
    parser.add_argument("original", type=Path)
    parser.add_argument("curated", type=Path)
    args = parser.parse_args()

    for path in (args.original, args.curated):
        if not path.is_file():
            parser.error(f"not a file: {path}")

    result = check(read(args.original), read(args.curated))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
