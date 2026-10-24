"""Verify public contribution selection, merge chronology and offline fallbacks."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets"))
from builder import github_data, upstream
from builder.panels import build_upstream_feed


def item(repo, number, merged_at, author="rugbedbugg"):
    return {
        "repository_url": f"https://api.github.com/repos/{repo}",
        "number": number,
        "title": f"Change {number}",
        "html_url": f"https://github.com/{repo}/pull/{number}",
        "user": {"login": author},
        "pull_request": {"merged_at": merged_at},
    }


def pin(private=False):
    return {
        "number": 4195,
        "merged": True,
        "merged_at": "2026-10-13T04:47:19Z",
        "html_url": "https://github.com/boykopovar/AnyPS5/pull/4195",
        "base": {"repo": {"private": private}},
        "user": {"login": "rugbedbugg"},
    }


class UpstreamTests(unittest.TestCase):
    def test_public_upstream_items_are_sorted_by_merge_time(self):
        results = [
            item("upstream/project", 1, "2026-10-01T00:00:00Z"),
            item("rugbedbugg/project", 5, "2026-10-24T00:00:00Z"),
            item("upstream/project", 6, "2026-10-24T00:00:00Z", "someone-else"),
            item("upstream/project", 4, None),
            item("upstream/project", 3, "2026-10-23T00:00:00Z"),
            item("upstream/project", 2, "2026-10-13T00:00:00Z"),
        ]
        with patch.object(
            github_data,
            "_get",
            side_effect=[
                {"total_count": 64},
                pin(),
                {"items": results},
            ],
        ) as get:
            data = upstream.fetch_upstream()
        self.assertFalse(data["cached"])
        self.assertEqual([entry["number"] for entry in data["recent"]], [3, 2, 1])
        queries = [
            parse_qs(urlsplit(call.args[0]).query)["q"][0]
            for call in get.call_args_list
            if "/search/issues?" in call.args[0]
        ]
        self.assertTrue(all("is:public" in query for query in queries))
        self.assertIn("-user:rugbedbugg", queries[-1])

    def test_network_failure_returns_a_dated_saved_snapshot(self):
        with patch.object(github_data, "_get", side_effect=OSError("offline")):
            data = upstream.fetch_upstream()
        self.assertTrue(data["cached"])
        self.assertEqual(data["fetched_at"], upstream.saved_snapshot()["fetched_at"])
        self.assertEqual(data["recent"], upstream.saved_snapshot()["recent"])

    def test_incomplete_search_does_not_publish_partial_counts(self):
        with patch.object(
            github_data, "_get", return_value={"incomplete_results": True}
        ):
            self.assertTrue(upstream.fetch_upstream()["cached"])

    def test_private_pinned_repository_is_not_used(self):
        with patch.object(
            github_data, "_get", side_effect=[{"total_count": 64}, pin(private=True)]
        ):
            self.assertTrue(upstream.fetch_upstream()["cached"])

    def test_unexpected_entry_destination_is_not_published(self):
        entry = item("upstream/project", 1, "2026-10-01T00:00:00Z")
        entry["html_url"] = "https://example.com/unexpected"
        with self.assertRaisesRegex(ValueError, "unexpected pull request URL"):
            upstream._entry(entry)

    def test_empty_feed_has_a_readable_state(self):
        data = upstream.saved_snapshot()
        data["recent"] = []
        root = ElementTree.fromstring(build_upstream_feed(data))
        self.assertIn("No public upstream merges to display.", "".join(root.itertext()))
        self.assertIn("SAVED SNAPSHOT", "".join(root.itertext()))
