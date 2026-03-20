#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from collections.abc import Iterable
from functools import lru_cache
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

IGNORED_DIR_NAMES = IGNORED_TOP_LEVEL | {".leetcode"}

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


def normalize_slugs(values: Iterable[str]) -> set[str]:
    normalized: set[str] = set()
    for value in values:
        slug = canonical_slug(value)
        if slug:
            normalized.add(slug)
    return normalized


def load_local_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def write_text_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text() == content:
        return False
    path.write_text(content)
    return True


@lru_cache(maxsize=1)
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


def _iter_discovery_children(base: Path, *, is_root: bool) -> tuple[list[Path], list[Path]]:
    directories: list[Path] = []
    code_files: list[Path] = []
    for path in sorted(base.iterdir()):
        if path.name.startswith("."):
            if not (is_root and path.name == ".leetcode"):
                continue

        if path.is_dir():
            if path.name in IGNORED_TOP_LEVEL and is_root:
                continue
            if path.name in IGNORED_DIR_NAMES and not (is_root and path.name == ".leetcode"):
                continue
            directories.append(path)
            continue

        if path.is_file() and path.suffix.lower() in CODE_EXTENSIONS:
            code_files.append(path)

    return directories, code_files


def _iter_entry_children(base: Path) -> tuple[list[Path], list[Path]]:
    directories: list[Path] = []
    direct_solution_files: list[Path] = []
    for path in sorted(base.iterdir()):
        if path.name.startswith("."):
            continue
        if path.is_dir():
            directories.append(path)
            continue
        if path.suffix.lower() in CODE_EXTENSIONS:
            direct_solution_files.append(path)
    return directories, direct_solution_files


def _collect_solution_files(base: Path) -> list[str]:
    child_directories, direct_solution_files = _iter_entry_children(base)
    solution_paths = [str(path.relative_to(ROOT)) for path in direct_solution_files]
    for directory in child_directories:
        solution_paths.extend(_collect_solution_files(directory))
    return solution_paths


def _merge_discovered(
    target: dict[str, set[str]],
    incoming: dict[str, set[str]],
) -> None:
    for slug, paths in incoming.items():
        target.setdefault(slug, set()).update(paths)


def _discover_from_candidate_dir(directory: Path) -> dict[str, set[str]]:
    discovered: dict[str, set[str]] = {}
    child_directories, direct_solution_files = _iter_entry_children(directory)
    if direct_solution_files:
        slug = canonical_slug(directory.name)
        if not slug:
            return discovered

        solution_paths = [str(path.relative_to(ROOT)) for path in direct_solution_files]
        for child_directory in child_directories:
            solution_paths.extend(_collect_solution_files(child_directory))
        discovered.setdefault(slug, set()).update(solution_paths)
        return discovered

    for child_directory in child_directories:
        _merge_discovered(discovered, _discover_from_candidate_dir(child_directory))
    return discovered


def _discover_problem_solutions(base: Path, *, is_root: bool = False) -> dict[str, set[str]]:
    discovered: dict[str, set[str]] = {}
    directories, direct_problem_files = _iter_discovery_children(base, is_root=is_root)

    for path in direct_problem_files:
        slug = canonical_slug(path.stem)
        if not slug:
            continue
        discovered.setdefault(slug, set()).add(str(path.relative_to(ROOT)))

    for directory in directories:
        _merge_discovered(discovered, _discover_from_candidate_dir(directory))

    return discovered


@lru_cache(maxsize=1)
def discover_problem_solutions() -> dict[str, list[str]]:
    discovered = _discover_problem_solutions(ROOT, is_root=True)
    return {slug: sorted(paths) for slug, paths in discovered.items()}


def collect_solved_slugs(tracked_slugs: set[str]) -> set[str]:
    return set(discover_problem_solutions()).intersection(tracked_slugs)
