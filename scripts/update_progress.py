#!/usr/bin/env python3
from __future__ import annotations

from repo_tools import ROOT, TRACK_LABELS, collect_solved_slugs, load_tracks

README_PATH = ROOT / "README.md"

START_MARKER = "<!-- progress:begin -->"
END_MARKER = "<!-- progress:end -->"


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
