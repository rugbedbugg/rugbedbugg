"""Public upstream contributions, with an explicitly dated offline snapshot."""

import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode

from . import config, github_data

RECENT_QUERY = f"is:pr is:merged is:public author:{config.USER} -user:{config.USER}"


def saved_snapshot():
    data = json.loads(Path(__file__).with_name("upstream_snapshot.json").read_text())
    data["cached"] = True
    return data


def _search(query):
    params = urlencode(
        {"q": query, "sort": "updated", "order": "desc", "per_page": 100}
    )
    result = github_data._get("https://api.github.com/search/issues?" + params)
    if result.get("incomplete_results"):
        raise ValueError("incomplete contribution search")
    return result


def _entry(item):
    repo = item["repository_url"].removeprefix("https://api.github.com/repos/")
    owner, name = repo.split("/")
    merged_at = item.get("pull_request", {}).get("merged_at")
    if (
        not merged_at
        or owner.casefold() == config.USER.casefold()
        or item["user"]["login"].casefold() != config.USER.casefold()
    ):
        return None
    datetime.fromisoformat(merged_at)
    number = int(item["number"])
    url = f"https://github.com/{owner}/{name}/pull/{number}"
    if item["html_url"] != url:
        raise ValueError("unexpected pull request URL")
    return {
        "repo": repo,
        "number": number,
        "title": item["title"],
        "merged_at": merged_at,
        "url": url,
    }


def fetch_upstream():
    try:
        latch = _search(
            f"repo:vinnovateit/latch is:pr is:merged is:public author:{config.USER}"
        )
        anyps5 = github_data._get(
            "https://api.github.com/repos/boykopovar/AnyPS5/pulls/4195"
        )
        if (
            not anyps5["merged"]
            or not anyps5["merged_at"]
            or anyps5["base"]["repo"]["private"]
            or anyps5["user"]["login"].casefold() != config.USER.casefold()
        ):
            raise ValueError("pinned upstream contribution did not verify")
        result = _search(RECENT_QUERY)
        recent = [entry for item in result["items"] if (entry := _entry(item))]
        recent.sort(key=lambda entry: entry["merged_at"], reverse=True)
        # updated_at is never earlier than merged_at. If older conversations
        # displaced a recent merge from this page, keep the verified snapshot.
        if len(result["items"]) == 100 and (
            len(recent) < 3
            or recent[2]["merged_at"] < result["items"][-1]["updated_at"]
        ):
            raise ValueError("recent merge search needs a wider result window")
        return {
            "fetched_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "latch_count": int(latch["total_count"]),
            "anyps5": {
                "number": anyps5["number"],
                "merged_at": anyps5["merged_at"],
                "url": anyps5["html_url"],
            },
            "recent": recent[:3],
            "cached": False,
        }
    except Exception as exc:
        print(f"  ..upstream fetch failed ({exc}) -> saved snapshot")
        return saved_snapshot()
