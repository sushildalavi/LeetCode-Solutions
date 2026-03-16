#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re

from repo_tools import canonical_slug
from sync_problem_notes import note_path_for_slug, sync_problem_notes


def replace_section(content: str, heading: str, body: str) -> str:
    pattern = rf"(## {re.escape(heading)}\n)(.*?)(?=\n## |\Z)"
    replacement = rf"\1{body.strip()}\n"
    updated, count = re.subn(pattern, replacement, content, flags=re.S)
    if count == 0:
        raise RuntimeError(f"Section '{heading}' not found in note.")
    return updated


def replace_complexity(content: str, time_value: str | None, space_value: str | None) -> str:
    pattern = r"(## Complexity\n)(.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, flags=re.S)
    if not match:
        raise RuntimeError("Section 'Complexity' not found in note.")

    body = match.group(2)
    if time_value is not None:
        body = re.sub(r"^- Time:.*$", f"- Time: {time_value}", body, flags=re.M)
    if space_value is not None:
        body = re.sub(r"^- Space:.*$", f"- Space: {space_value}", body, flags=re.M)

    return content[: match.start(2)] + body + content[match.end(2) :]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fill your own summary and approach into a problem note.")
    parser.add_argument("slug", help="Problem slug, for example: two-sum")
    parser.add_argument("--summary", help="Your summary of the question.")
    parser.add_argument("--data-structures", help="The data structures you used.")
    parser.add_argument("--approach", help="Your approach in your own words.")
    parser.add_argument("--time", help="Time complexity, for example O(n).")
    parser.add_argument("--space", help="Space complexity, for example O(1).")
    parser.add_argument("--notes", help="Revision notes or mistakes to remember.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    slug = canonical_slug(args.slug)
    sync_problem_notes({slug})

    note_path = note_path_for_slug(slug)
    content = note_path.read_text()

    if args.summary:
        content = replace_section(content, "Problem Summary", args.summary)
    if args.data_structures:
        content = replace_section(content, "Data Structures Used", args.data_structures)
    if args.approach:
        content = replace_section(content, "Approach", args.approach)
    if args.time is not None or args.space is not None:
        content = replace_complexity(content, args.time, args.space)
    if args.notes:
        notes_body = args.notes if args.notes.lstrip().startswith("-") else f"- {args.notes}"
        content = replace_section(content, "Revision Notes", notes_body)

    note_path.write_text(content)
    print(f"Updated {note_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
