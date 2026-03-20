#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACKS_PATH = ROOT / "data" / "tracks.json"

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

IGNORED_TOP_LEVEL = {
    ".git",
    ".github",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "data",
    "notes",
    "node_modules",
    "scripts",
    "venv",
}

CODE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".kts",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scala",
    ".sql",
    ".swift",
    ".ts",
    ".tsx",
}


def normalize_candidate(value: str) -> str:
    value = value.strip().lower()
    value = value.replace("_", "-")
    value = re.sub(r"^\d+[.\-_\s]+", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value


def canonical_slug(slug: str) -> str:
    normalized = normalize_candidate(slug)
    return ALIASES.get(normalized, normalized)


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


def problem_track_memberships(slug: str, tracks: dict[str, list[str]] | None = None) -> list[str]:
    tracks = tracks or load_tracks()
    memberships = [
        TRACK_LABELS[name]
        for name, slugs in tracks.items()
        if slug in slugs
    ]
    return memberships or ["General Practice"]


def _top_level_problem_entries() -> list[Path]:
    entries: list[Path] = []
    for path in sorted(ROOT.iterdir()):
        if path.name.startswith(".") and path.name not in {".leetcode"}:
            continue
        if path.name in IGNORED_TOP_LEVEL:
            continue
        if path.is_dir():
            entries.append(path)
            continue
        if path.is_file() and path.suffix.lower() in CODE_EXTENSIONS:
            entries.append(path)
    return entries


def _solution_files_for_entry(entry: Path) -> list[str]:
    if entry.is_file():
        return [str(entry.relative_to(ROOT))]

    solution_paths: list[str] = []
    for path in sorted(entry.rglob("*")):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(entry).parts
        if any(part.startswith(".") for part in relative_parts):
            continue
        if path.suffix.lower() not in CODE_EXTENSIONS:
            continue
        solution_paths.append(str(path.relative_to(ROOT)))
    return solution_paths


def discover_problem_solutions() -> dict[str, list[str]]:
    discovered: dict[str, set[str]] = {}
    for root_entry in _top_level_problem_entries():
        entries = [root_entry]
        if root_entry.is_dir() and root_entry.name == ".leetcode":
            entries = [
                path
                for path in sorted(root_entry.iterdir())
                if not path.name.startswith(".")
                and (path.is_dir() or (path.is_file() and path.suffix.lower() in CODE_EXTENSIONS))
            ]

        for entry in entries:
            slug_source = entry.stem if entry.is_file() else entry.name
            slug = canonical_slug(slug_source)
            if not slug:
                continue
            discovered.setdefault(slug, set()).update(_solution_files_for_entry(entry))

    return {slug: sorted(paths) for slug, paths in discovered.items()}


def collect_solved_slugs(tracked_slugs: set[str]) -> set[str]:
    return set(discover_problem_solutions()).intersection(tracked_slugs)
