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

from repo_tools import ROOT, canonical_slug, discover_problem_solutions
from sync_problem_notes import (
    get_problem_metadata,
    load_metadata_cache,
    note_path_for_slug,
    save_metadata_cache,
    sync_problem_notes,
)
from update_problem_note import replace_complexity, replace_section

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-5-mini"
SYSTEM_INSTRUCTIONS = """
You generate concise LeetCode study notes from a problem statement and an accepted solution.
Return only valid JSON with this exact shape:
{
  "summary": "string",
  "data_structures": ["string"],
  "approach": "string",
  "time_complexity": "string",
  "space_complexity": "string",
  "revision_notes": ["string"]
}

Requirements:
- Ground the explanation in the provided solution code, not a generic textbook answer.
- Keep the summary to 1-2 short sentences.
- Keep the approach to one short paragraph.
- `data_structures` should be short labels like "Hash Map" or "Two Pointers".
- Complexities must be asymptotic Big-O values.
- `revision_notes` should be 1-3 brief bullets about key invariants, edge cases, or why the approach works.
- Do not wrap the JSON in markdown fences.
""".strip()


def load_local_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def extract_section_body(content: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, flags=re.S)
    if not match:
        raise RuntimeError(f"Section '{heading}' not found in note.")
    return match.group(1).strip()


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
            "reasoning": {"effort": "low"},
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


def apply_ai_draft(note_path: Path, draft: dict[str, Any]) -> bool:
    content = note_path.read_text()
    updated = content
    data_structures = draft.get("data_structures")
    revision_notes = draft.get("revision_notes")

    updated = replace_section(updated, "Problem Summary", str(draft.get("summary") or "TODO"))
    updated = replace_section(
        updated,
        "Data Structures Used",
        format_bullets(data_structures if isinstance(data_structures, list) else [], "TODO"),
    )
    updated = replace_section(updated, "Approach", str(draft.get("approach") or "TODO"))
    updated = replace_complexity(
        updated,
        str(draft.get("time_complexity") or "TODO"),
        str(draft.get("space_complexity") or "TODO"),
    )
    updated = replace_section(
        updated,
        "Revision Notes",
        format_bullets(revision_notes if isinstance(revision_notes, list) else [], "- TODO"),
    )

    if updated != content:
        note_path.write_text(updated)
        return True
    return False


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
    discovered = discover_problem_solutions()
    target_slugs = (
        {canonical_slug(slug) for slug in args.slugs if canonical_slug(slug)}
        if args.slugs
        else set(discovered)
    )

    if not target_slugs:
        print("No synced problems found.")
        return 0

    sync_problem_notes(target_slugs)
    cache = load_metadata_cache()

    updated_count = 0
    for slug in sorted(target_slugs):
        solution_paths = discovered.get(slug)
        if not solution_paths:
            continue

        note_path = note_path_for_slug(slug)
        if not note_path.exists():
            continue

        metadata = get_problem_metadata(slug, cache)
        prompt = build_prompt(slug, metadata, solution_paths)

        try:
            draft = request_note_draft(prompt, api_key, model)
        except (RuntimeError, urllib.error.URLError, json.JSONDecodeError) as exc:
            print(f"Skipping {slug}: {exc}")
            continue

        if apply_ai_draft(note_path, draft):
            updated_count += 1
            print(f"Updated {note_path}")

    save_metadata_cache(cache)
    print(f"AI-generated drafts updated: {updated_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
