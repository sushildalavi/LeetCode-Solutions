#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from repo_tools import (
    ROOT,
    canonical_slug,
    discover_problem_solutions,
    load_local_env,
    load_tracks,
    normalize_slugs,
)
from sync_problem_notes import (
    get_problem_metadata,
    load_metadata_cache,
    save_metadata_cache,
    sync_problem_notes,
)

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-4o-mini"
LEETCODE_DIR = ROOT / ".leetcode"
SYSTEM_INSTRUCTIONS = """
You generate concise LeetCode study notes from a problem statement and an accepted solution.
Return only valid JSON with this exact shape:
{
  "approach": "string",
  "time_complexity": "string",
  "space_complexity": "string",
  "revision_notes": ["string"]
}

Requirements:
- Ground the explanation in the provided solution code, not a generic textbook answer.
- Keep the approach to one short paragraph.
- Complexities must be asymptotic Big-O values.
- `revision_notes` should be 1-3 brief bullets about key invariants, edge cases, or why the approach works.
- Do not wrap the JSON in markdown fences.
""".strip()


def format_bullets(values: list[str], fallback: str) -> str:
    cleaned = [value.strip() for value in values if value and value.strip()]
    if not cleaned:
        return fallback
    return "\n".join(f"- {value}" for value in cleaned)


def strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```[a-zA-Z0-9_-]*\n", "", stripped)
        stripped = re.sub(r"\n```$", "", stripped)
    return stripped.strip()


def extract_response_text(payload: dict[str, Any]) -> str:
    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    texts: list[str] = []
    for item in payload.get("output", []):
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if not isinstance(content, dict):
                continue
            if content.get("type") not in {"output_text", "text"}:
                continue
            text = content.get("text")
            if isinstance(text, str) and text.strip():
                texts.append(text.strip())
                continue
            if isinstance(text, dict):
                value = text.get("value")
                if isinstance(value, str) and value.strip():
                    texts.append(value.strip())
    return "\n".join(texts).strip()


def request_note_draft(prompt: str, api_key: str, model: str) -> dict[str, Any]:
    payload = json.dumps(
        {
            "model": model,
            "instructions": SYSTEM_INSTRUCTIONS,
            "input": prompt,
        }
    ).encode()
    request = urllib.request.Request(
        OPENAI_RESPONSES_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "LeetCode-Solutions-AI-Notes/1.0",
        },
    )

    with urllib.request.urlopen(request, timeout=90) as response:
        raw = json.loads(response.read().decode())

    text = extract_response_text(raw)
    if not text:
        raise RuntimeError("OpenAI response did not contain output text.")

    parsed = json.loads(strip_code_fences(text))
    if not isinstance(parsed, dict):
        raise RuntimeError("OpenAI response was not a JSON object.")
    return parsed


def read_solution_context(solution_paths: list[str]) -> str:
    snippets: list[str] = []
    total_chars = 0

    for relative_path in solution_paths[:3]:
        path = ROOT / relative_path
        content = path.read_text()
        snippet = content[:6000]
        snippets.append(f"Path: {relative_path}\n```text\n{snippet}\n```")
        total_chars += len(snippet)
        if total_chars >= 12000:
            break

    return "\n\n".join(snippets)


def build_prompt(slug: str, metadata: dict[str, Any], solution_paths: list[str]) -> str:
    topic_tags = ", ".join(metadata.get("topic_tags", [])) or "Unknown"
    hints = metadata.get("hints", [])
    hint_lines = "\n".join(f"- {hint}" for hint in hints[:3]) if hints else "- None"
    example_testcases = str(metadata.get("example_testcases") or "").strip()
    if not example_testcases:
        example_testcases = "None"

    problem_statement = str(metadata.get("content_markdown") or "").strip()
    if len(problem_statement) > 10000:
        problem_statement = problem_statement[:10000].rstrip() + "\n..."

    return f"""
Problem slug: {slug}
Title: {metadata["title"]}
Difficulty: {metadata["difficulty"]}
Topic tags: {topic_tags}
LeetCode URL: {metadata["url"]}

Problem statement:
{problem_statement}

Example testcases:
{example_testcases}

Hints:
{hint_lines}

Accepted solution files:
{read_solution_context(solution_paths)}
""".strip()


def readme_path_for_slug(slug: str) -> Path:
    return LEETCODE_DIR / slug / "README.md"


def has_ai_content(content: str) -> bool:
    """Return True if the README already has a real (non-TODO) Approach section."""
    match = re.search(r"## Approach\n(.*?)(?=\n## |\Z)", content, re.S)
    return bool(match and match.group(1).strip() and "TODO" not in match.group(1))


def apply_ai_to_readme(readme_path: Path, draft: dict[str, Any]) -> bool:
    content = readme_path.read_text()

    if has_ai_content(content):
        return False

    approach = str(draft.get("approach") or "TODO").strip()
    time_c = str(draft.get("time_complexity") or "TODO")
    space_c = str(draft.get("space_complexity") or "TODO")
    revision_notes = draft.get("revision_notes")
    notes_text = format_bullets(revision_notes if isinstance(revision_notes, list) else [], "- TODO")

    # Strip any existing (empty/TODO) AI sections so we don't duplicate them
    if "## Approach" in content:
        pos = content.find("## Approach")
        content = content[:pos].rstrip()

    ai_block = (
        f"\n\n## Approach\n{approach}"
        f"\n\n## Complexity\n- Time: {time_c}\n- Space: {space_c}"
        f"\n\n## Revision Notes\n{notes_text}\n"
    )

    readme_path.write_text(content + ai_block)
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate AI note drafts for synced LeetCode solutions.")
    parser.add_argument("slugs", nargs="*", help="Optional problem slugs to target.")
    return parser.parse_args()


def main() -> int:
    load_local_env()
    args = parse_args()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set; skipping AI note generation.")
        return 0

    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    tracks = load_tracks()
    discovered = discover_problem_solutions()
    cache = load_metadata_cache()
    target_slugs = (
        normalize_slugs(args.slugs)
        if args.slugs
        else set(discovered)
    )

    if not target_slugs:
        print("No synced problems found.")
        return 0

    sync_problem_notes(target_slugs, discovered=discovered, tracks=tracks, cache=cache)

    updated_count = 0
    for slug in sorted(target_slugs):
        solution_paths = discovered.get(slug)
        if not solution_paths:
            continue

        readme_path = readme_path_for_slug(slug)
        if not readme_path.exists():
            continue

        if has_ai_content(readme_path.read_text()):
            print(f"Skipping {slug}: AI content already present.")
            continue

        metadata = get_problem_metadata(slug, cache)
        prompt = build_prompt(slug, metadata, solution_paths)

        try:
            draft = request_note_draft(prompt, api_key, model)
        except (RuntimeError, urllib.error.URLError, json.JSONDecodeError) as exc:
            print(f"Skipping {slug}: {exc}")
            continue

        if apply_ai_to_readme(readme_path, draft):
            updated_count += 1
            print(f"Updated {readme_path}")

    save_metadata_cache(cache)
    print(f"AI-generated drafts updated: {updated_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
