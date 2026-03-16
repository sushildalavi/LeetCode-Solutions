#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path

from repo_tools import (
    ROOT,
    canonical_slug,
    discover_problem_solutions,
    load_tracks,
    problem_track_memberships,
)

NOTES_DIR = ROOT / "notes" / "problems"
INDEX_PATH = ROOT / "notes" / "INDEX.md"
METADATA_CACHE_PATH = ROOT / "data" / "problem_metadata.json"

METADATA_START = "<!-- metadata:begin -->"
METADATA_END = "<!-- metadata:end -->"

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql/"
LEETCODE_QUERY = """
query q($slug: String!) {
  question(titleSlug: $slug) {
    title
    titleSlug
    difficulty
    topicTags {
      name
      slug
    }
  }
}
""".strip()


def slug_to_title(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


def note_path_for_slug(slug: str) -> Path:
    return NOTES_DIR / f"{slug}.md"


def load_metadata_cache() -> dict[str, dict[str, object]]:
    if not METADATA_CACHE_PATH.exists():
        return {}
    return json.loads(METADATA_CACHE_PATH.read_text())


def save_metadata_cache(cache: dict[str, dict[str, object]]) -> None:
    METADATA_CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n")


def fetch_problem_metadata(slug: str) -> dict[str, object]:
    payload = json.dumps(
        {
            "query": LEETCODE_QUERY,
            "variables": {"slug": slug},
        }
    ).encode()
    request = urllib.request.Request(
        LEETCODE_GRAPHQL_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(request) as response:
            raw = json.loads(response.read().decode())
    except urllib.error.URLError:
        raw = {"data": {"question": None}}

    question = raw.get("data", {}).get("question")
    if not question:
        return {
            "title": slug_to_title(slug),
            "slug": slug,
            "difficulty": "Unknown",
            "topic_tags": [],
            "url": f"https://leetcode.com/problems/{slug}/",
        }

    return {
        "title": question["title"],
        "slug": question["titleSlug"],
        "difficulty": question["difficulty"],
        "topic_tags": [tag["name"] for tag in question.get("topicTags", [])],
        "url": f"https://leetcode.com/problems/{question['titleSlug']}/",
    }


def get_problem_metadata(slug: str, cache: dict[str, dict[str, object]]) -> dict[str, object]:
    if slug not in cache:
        cache[slug] = fetch_problem_metadata(slug)
    return cache[slug]


def infer_data_structures(topic_tags: list[str]) -> list[str]:
    aliases = {
        "Array": "Array",
        "Hash Table": "Hash Map",
        "String": "String",
        "Linked List": "Linked List",
        "Tree": "Tree",
        "Binary Tree": "Binary Tree",
        "Binary Search Tree": "Binary Search Tree",
        "Graph": "Graph",
        "Heap (Priority Queue)": "Heap / Priority Queue",
        "Stack": "Stack",
        "Queue": "Queue",
        "Trie": "Trie",
        "Matrix": "Matrix",
        "Monotonic Stack": "Monotonic Stack",
        "Prefix Sum": "Prefix Sum",
    }
    inferred: list[str] = []
    for tag in topic_tags:
        value = aliases.get(tag, tag)
        if value not in inferred:
            inferred.append(value)
    return inferred


def build_metadata_block(
    slug: str,
    metadata: dict[str, object],
    solution_paths: list[str],
    memberships: list[str],
) -> str:
    topic_tags = metadata.get("topic_tags", [])
    inferred = infer_data_structures(topic_tags if isinstance(topic_tags, list) else [])

    lines = [
        METADATA_START,
        f"- LeetCode: {metadata['url']}",
        f"- Difficulty: {metadata['difficulty']}",
        f"- Topic Tags: {', '.join(topic_tags) if topic_tags else 'Unknown'}",
        f"- Tracked In: {', '.join(memberships)}",
        f"- Suggested Data Structures / Patterns: {', '.join(inferred) if inferred else 'Fill this after solving'}",
        "- Synced Solution Paths:",
    ]

    if solution_paths:
        for path in solution_paths:
            lines.append(f"  - `{path}`")
    else:
        lines.append("  - No synced solution file detected yet")

    lines.append(METADATA_END)
    return "\n".join(lines)


def default_note_body(
    metadata: dict[str, object],
    slug: str,
    solution_paths: list[str],
    memberships: list[str],
) -> str:
    metadata_block = build_metadata_block(slug, metadata, solution_paths, memberships)
    return "\n".join(
        [
            f"# {metadata['title']}",
            "",
            metadata_block,
            "",
            "## Problem Summary",
            "TODO: Summarize the question in your own words.",
            "",
            "## Data Structures Used",
            "TODO",
            "",
            "## Approach",
            "TODO",
            "",
            "## Complexity",
            "- Time: TODO",
            "- Space: TODO",
            "",
            "## Revision Notes",
            "- TODO",
            "",
        ]
    )


def update_note_file(
    slug: str,
    metadata: dict[str, object],
    solution_paths: list[str],
    memberships: list[str],
) -> None:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    note_path = note_path_for_slug(slug)
    metadata_block = build_metadata_block(slug, metadata, solution_paths, memberships)

    if not note_path.exists():
        note_path.write_text(default_note_body(metadata, slug, solution_paths, memberships))
        return

    content = note_path.read_text()
    if METADATA_START in content and METADATA_END in content:
        start = content.index(METADATA_START)
        end = content.index(METADATA_END) + len(METADATA_END)
        updated = content[:start] + metadata_block + content[end:]
        note_path.write_text(updated)
        return

    title = content.splitlines()[0] if content.startswith("# ") else f"# {metadata['title']}"
    remainder = content.split("\n", 1)[1] if "\n" in content else ""
    updated = "\n".join([title, "", metadata_block, "", remainder.lstrip("\n")])
    note_path.write_text(updated)


def note_status(note_path: Path) -> str:
    content = note_path.read_text()
    return "Needs details" if "TODO" in content else "Complete"


def update_index(
    discovered: dict[str, list[str]],
    cache: dict[str, dict[str, object]],
    tracks: dict[str, list[str]],
) -> None:
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Problem Notes Index",
        "",
        "This index is generated automatically from synced solutions.",
        "",
    ]

    if not discovered:
        lines.append("No synced solutions detected yet.")
        lines.append("")
        INDEX_PATH.write_text("\n".join(lines))
        return

    lines.extend(
        [
            "| Problem | Difficulty | Tracks | Status |",
            "| --- | --- | --- | --- |",
        ]
    )

    for slug in sorted(discovered, key=lambda value: str(cache.get(value, {}).get("title", value)).lower()):
        metadata = cache.get(slug, {"title": slug_to_title(slug), "difficulty": "Unknown"})
        memberships = ", ".join(problem_track_memberships(slug, tracks))
        relative_note = note_path_for_slug(slug).relative_to(INDEX_PATH.parent)
        status = note_status(note_path_for_slug(slug))
        lines.append(
            f"| [{metadata['title']}]({relative_note.as_posix()}) | {metadata['difficulty']} | {memberships} | {status} |"
        )

    lines.append("")
    INDEX_PATH.write_text("\n".join(lines))


def sync_problem_notes(target_slugs: set[str] | None = None) -> None:
    tracks = load_tracks()
    discovered = discover_problem_solutions()

    if target_slugs is None:
        slugs = set(discovered)
    else:
        slugs = {canonical_slug(slug) for slug in target_slugs if canonical_slug(slug)}
        for slug in slugs:
            discovered.setdefault(slug, [])

    cache = load_metadata_cache()

    for slug in sorted(slugs):
        metadata = get_problem_metadata(slug, cache)
        memberships = problem_track_memberships(slug, tracks)
        update_note_file(slug, metadata, discovered.get(slug, []), memberships)

    save_metadata_cache(cache)
    update_index(discovered, cache, tracks)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or refresh per-problem knowledge notes.")
    parser.add_argument("slugs", nargs="*", help="Optional problem slugs to sync.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_slugs = set(args.slugs) if args.slugs else None
    sync_problem_notes(target_slugs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
