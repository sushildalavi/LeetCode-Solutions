#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README_PATH = ROOT / "README.md"
TRACKS_PATH = ROOT / "data" / "tracks.json"

START_MARKER = "<!-- progress:begin -->"
END_MARKER = "<!-- progress:end -->"

TRACK_LABELS = {
    "neetcode150": "NeetCode 150",
    "neetcode250": "NeetCode 250",
    "striverSdeSheetLeetCode": "Striver's SDE Sheet (LeetCode-backed)",
}

# Striver's sheet still contains a few legacy LeetCode URLs.
ALIASES = {
    "coin-change-2": "coin-change-ii",
    "implement-strstr": "find-the-index-of-the-first-occurrence-in-a-string",
}

IGNORE_DIRS = {
    ".git",
    ".github",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "data",
    "scripts",
    "node_modules",
    "venv",
}


def canonical_slug(slug: str) -> str:
    normalized = normalize_candidate(slug)
    return ALIASES.get(normalized, normalized)


def normalize_candidate(value: str) -> str:
    value = value.strip().lower()
    value = value.replace("_", "-")
    value = re.sub(r"^\d+[.\-_\s]+", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value


def load_tracks() -> dict[str, list[str]]:
    raw = json.loads(TRACKS_PATH.read_text())
    tracks: dict[str, list[str]] = {}
    for name, slugs in raw.items():
        deduped: list[str] = []
        seen: set[str] = set()
        for slug in slugs:
            canonical = canonical_slug(slug)
            if canonical in seen:
                continue
            seen.add(canonical)
            deduped.append(canonical)
        tracks[name] = deduped
    return tracks


def collect_solved_slugs(tracked_slugs: set[str]) -> set[str]:
    solved: set[str] = set()

    for current_root, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if dirname not in IGNORE_DIRS and not dirname.startswith(".")
        ]

        for dirname in dirnames:
            candidate = canonical_slug(dirname)
            if candidate in tracked_slugs:
                solved.add(candidate)

        for filename in filenames:
            stem = Path(filename).stem
            candidate = canonical_slug(stem)
            if candidate in tracked_slugs:
                solved.add(candidate)

    return solved


def build_progress_block(tracks: dict[str, list[str]], solved: set[str]) -> str:
    lines = [
        "| Track | Solved | Total | Progress |",
        "| --- | ---: | ---: | ---: |",
    ]

    for key in ("neetcode150", "neetcode250", "striverSdeSheetLeetCode"):
        total = len(tracks[key])
        solved_count = sum(1 for slug in tracks[key] if slug in solved)
        progress = (solved_count / total * 100) if total else 0.0
        lines.append(
            f"| {TRACK_LABELS[key]} | {solved_count} | {total} | {progress:.1f}% |"
        )

    unique_total = len(set().union(*tracks.values()))
    unique_solved = len(set().union(*tracks.values()) & solved)

    lines.extend(
        [
            "",
            f"Tracked unique problems solved across all sheets: `{unique_solved} / {unique_total}`",
        ]
    )
    return "\n".join(lines)


def update_readme(progress_block: str) -> None:
    readme = README_PATH.read_text()
    if START_MARKER not in readme or END_MARKER not in readme:
        raise RuntimeError("README markers for the progress block are missing.")

    start_index = readme.index(START_MARKER) + len(START_MARKER)
    end_index = readme.index(END_MARKER)
    updated = readme[:start_index] + "\n" + progress_block + "\n" + readme[end_index:]
    README_PATH.write_text(updated)


def main() -> int:
    tracks = load_tracks()
    tracked_slugs = set().union(*tracks.values())
    solved = collect_solved_slugs(tracked_slugs)
    update_readme(build_progress_block(tracks, solved))

    for key in ("neetcode150", "neetcode250", "striverSdeSheetLeetCode"):
        solved_count = sum(1 for slug in tracks[key] if slug in solved)
        print(f"{TRACK_LABELS[key]}: {solved_count}/{len(tracks[key])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
