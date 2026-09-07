"""Exercise every panel offline without replacing checked-in artwork."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets"))
import build
from builder import config, github_data


class BuildTests(unittest.TestCase):
    def test_all_panels_render_with_escaped_remote_text(self):
        panels = {}

        def capture(name, content):
            panels[name] = ElementTree.fromstring(content)

        with (
            patch.object(
                github_data, "fetch_stats", return_value=(config.FB_STATS, [])
            ),
            patch.object(github_data, "fetch_langs", return_value=config.FB_LANGS),
            patch.object(
                github_data, "fetch_calendar", return_value=[0, 1, 2, 3, 4] * 75
            ),
            patch.object(github_data, "fetch_quote", return_value='A < B & "quoted"'),
            patch.object(build, "write", side_effect=capture),
            patch(
                "urllib.request.urlopen",
                side_effect=AssertionError("unexpected network"),
            ),
        ):
            build.main()
        self.assertEqual(
            set(panels),
            {
                "header.svg",
                "dossier.svg",
                "telemetry.svg",
                "loadout.svg",
                "transmission.svg",
                "label-uplink.svg",
                "label-field.svg",
                "field-recording.svg",
                "feed-linkedin.svg",
                "feed-discord.svg",
                "feed-email.svg",
            },
        )
        for root in panels.values():
            self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
            self.assertIn("viewBox", root.attrib)
        self.assertIn(
            'A < B & "quoted"', "".join(panels["transmission.svg"].itertext())
        )

    def test_fetchers_handle_network_failure(self):
        with patch("urllib.request.urlopen", side_effect=OSError("offline")):
            stats, repos = github_data.fetch_stats()
            self.assertEqual(stats, config.FB_STATS)
            self.assertIsNone(repos)
            self.assertEqual(github_data.fetch_langs(repos), config.FB_LANGS)
            calendar = github_data.fetch_calendar()
            self.assertEqual(len(calendar), 371)
            self.assertTrue(set(calendar) <= set(range(5)))
            self.assertIn(github_data.fetch_quote(), config.QUOTES)
