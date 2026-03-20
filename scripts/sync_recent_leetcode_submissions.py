#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from repo_tools import ROOT, canonical_slug

SUBMISSIONS_API_URL = "https://leetcode.com/api/submissions/"
STATE_PATH = ROOT / "data" / "leetcode_sync_state.json"
SYNC_ROOT = ROOT / ".leetcode"

LANGUAGE_EXTENSIONS = {
    "bash": ".sh",
    "c": ".c",
    "cpp": ".cpp",
    "csharp": ".cs",
    "dart": ".dart",
    "elixir": ".ex",
    "erlang": ".erl",
    "golang": ".go",
    "html": ".html",
    "java": ".java",
    "javascript": ".js",
    "kotlin": ".kt",
    "mssql": ".sql",
    "mysql": ".sql",
    "oraclesql": ".sql",
    "php": ".php",
    "python": ".py",
    "python3": ".py",
    "pythondata": ".py",
    "pythonml": ".py",
    "racket": ".rkt",
    "ruby": ".rb",
    "rust": ".rs",
    "scala": ".scala",
    "swift": ".swift",
    "typescript": ".ts",
}


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


def build_cookie_header() -> str | None:
    cookies = os.getenv("LEETCODE_COOKIES", "").strip()
    if cookies:
        return cookies

    session = os.getenv("LEETCODE_SESSION", "").strip()
    csrftoken = os.getenv("LEETCODE_CSRFTOKEN", "").strip()
    if session and csrftoken:
        return f"csrftoken={csrftoken}; LEETCODE_SESSION={session};"
    return None


def language_extension(lang: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "", lang.lower())
    return LANGUAGE_EXTENSIONS.get(normalized, f".{normalized or 'txt'}")


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {"recent_submission_ids": [], "last_synced_timestamp": 0}
    return json.loads(STATE_PATH.read_text())


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def fetch_submissions(offset: int, limit: int, cookie_header: str) -> dict[str, Any]:
    query = urllib.parse.urlencode({"offset": offset, "limit": limit})
    request = urllib.request.Request(
        f"{SUBMISSIONS_API_URL}?{query}",
        headers={
            "Cookie": cookie_header,
            "Referer": "https://leetcode.com/submissions/",
            "User-Agent": "Mozilla/5.0",
            "X-CSRFToken": extract_csrftoken(cookie_header),
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode())


def extract_csrftoken(cookie_header: str) -> str:
    match = re.search(r"(?:^|;\s*)csrftoken=([^;]+)", cookie_header)
    return match.group(1) if match else ""


def iter_new_accepted_submissions(cookie_header: str, state: dict[str, Any]) -> list[dict[str, Any]]:
    recent_ids = {int(value) for value in state.get("recent_submission_ids", [])}
    last_synced_timestamp = int(state.get("last_synced_timestamp", 0))
    found: list[dict[str, Any]] = []

    offset = 0
    limit = 20
    while True:
        payload = fetch_submissions(offset, limit, cookie_header)
        submissions = payload.get("submissions_dump") or []
        if not submissions:
            break

        reached_old = False
        for submission in submissions:
            submission_id = int(submission["id"])
            submission_timestamp = int(submission["timestamp"])
            if submission_timestamp < last_synced_timestamp:
                reached_old = True
                break

            if (
                submission.get("status_display") == "Accepted"
                and (submission_timestamp > last_synced_timestamp or submission_id not in recent_ids)
            ):
                found.append(submission)

        if reached_old or not payload.get("has_next"):
            break
        offset += limit

    return found


def submission_folder(slug: str) -> Path:
    return SYNC_ROOT / canonical_slug(slug)


def write_submission_files(submission: dict[str, Any]) -> None:
    slug = canonical_slug(str(submission["title_slug"]))
    folder = submission_folder(slug)
    folder.mkdir(parents=True, exist_ok=True)

    extension = language_extension(str(submission.get("lang", "")))
    code = str(submission.get("code") or "")
    title = str(submission.get("title") or slug)
    submission_id = int(submission["id"])
    runtime = str(submission.get("runtime") or "Unknown")
    memory = str(submission.get("memory") or "Unknown")
    timestamp = int(submission.get("timestamp") or 0)
    submitted_at = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()

    solution_path = folder / f"{slug}{extension}"
    solution_path.write_text(code)

    readme = "\n".join(
        [
            f"# {title}",
            "",
            f"- LeetCode: https://leetcode.com/problems/{slug}/",
            f"- Submission ID: {submission_id}",
            f"- Submitted At: {submitted_at}",
            f"- Runtime: {runtime}",
            f"- Memory: {memory}",
            "",
        ]
    )
    (folder / "README.md").write_text(readme)


def main() -> int:
    load_local_env()
    cookie_header = build_cookie_header()
    if not cookie_header:
        print("LeetCode cookie secret not configured; skipping direct sync.")
        return 0

    state = load_state()

    try:
        new_submissions = iter_new_accepted_submissions(cookie_header, state)
    except urllib.error.HTTPError as exc:
        print(f"LeetCode sync failed with HTTP {exc.code}; skipping.")
        return 0
    except urllib.error.URLError as exc:
        print(f"LeetCode sync failed: {exc}")
        return 0

    if not new_submissions:
        print("No new accepted submissions found.")
        return 0

    newest_timestamp = int(state.get("last_synced_timestamp", 0))
    recent_ids = {int(value) for value in state.get("recent_submission_ids", [])}

    for submission in sorted(new_submissions, key=lambda value: int(value["timestamp"])):
        write_submission_files(submission)
        newest_timestamp = max(newest_timestamp, int(submission["timestamp"]))
        recent_ids.add(int(submission["id"]))
        print(f"Synced {submission['title_slug']} ({submission['lang']})")

    state["last_synced_timestamp"] = newest_timestamp
    state["recent_submission_ids"] = sorted(recent_ids, reverse=True)[:200]
    save_state(state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
