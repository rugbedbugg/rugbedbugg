"""Quote metadata, topical selection and independent fallback randomness."""

import random
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets"))
from builder import config, github_data
from builder.panels import build_transmission


class QuoteTests(unittest.TestCase):
    def test_live_selection_retains_attribution_and_filters_invalid_records(self):
        expected = {
            "text": "Simple software is easier to understand.",
            "author": "An Author",
            "source": "An Archive",
        }
        records = [
            None,
            {"text": 123},
            {"text": "short"},
            {"text": "The weather has been pleasant all summer."},
            {"text": "code " * 100},
            {**expected, "author": " An   Author ", "source": "An\nArchive"},
        ]
        with patch.object(github_data, "_get", return_value=records):
            self.assertEqual(github_data.fetch_quote(), expected)

    def test_missing_attribution_does_not_invent_an_author(self):
        record = {"text": "Programs should be easy to understand.", "author": None}
        with patch.object(github_data, "_get", return_value=[record]):
            quote = github_data.fetch_quote()
        self.assertNotIn("author", quote)
        root = ElementTree.fromstring(build_transmission(quote))
        self.assertIn("PROGRAMMING QUOTES", "".join(root.itertext()))

    def test_empty_selection_uses_attributed_fallback(self):
        with patch.object(github_data, "_get", return_value=[]):
            quote = github_data.fetch_quote()
        self.assertIn(quote, config.QUOTES)
        self.assertTrue(quote["author"])

    def test_calendar_fallback_does_not_reset_quote_randomness(self):
        state = random.getstate()
        with patch.object(github_data, "_get", side_effect=OSError("offline")):
            with patch("urllib.request.urlopen", side_effect=OSError("offline")):
                github_data.fetch_calendar()
        self.assertEqual(random.getstate(), state)
