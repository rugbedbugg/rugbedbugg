"""Publication contract tests; no network or repository mutation."""

import base64
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import publish


class PublishTests(unittest.TestCase):
    def invoke(self, verified=True, remote=b"<svg/>"):
        content = base64.b64encode(b"<svg/>").decode()
        responses = [
            {
                "data": {
                    "createCommitOnBranch": {
                        "commit": {
                            "oid": "new-head",
                            "signature": {"isValid": verified},
                        }
                    }
                }
            },
            {"content": base64.b64encode(remote).decode()},
        ]
        with (
            patch.dict(
                "os.environ",
                {"GITHUB_REF": "refs/heads/main", "GITHUB_REPOSITORY": "owner/repo"},
            ),
            patch.object(
                publish,
                "changes",
                return_value=[{"path": "assets/header.svg", "contents": content}],
            ),
            patch.object(publish.subprocess, "check_output", return_value="old-head\n"),
            patch.object(publish, "gh", side_effect=responses) as api,
        ):
            publish.main()
        return api

    def test_publication_checks_head_signature_and_exact_remote_bytes(self):
        api = self.invoke()
        mutation = api.call_args_list[0].kwargs["payload"]["variables"]["input"]
        self.assertEqual(mutation["expectedHeadOid"], "old-head")
        self.assertEqual(mutation["branch"]["branchName"], "main")
        self.assertEqual(
            api.call_args_list[1].args[0],
            "repos/owner/repo/contents/assets/header.svg?ref=new-head",
        )

    def test_unverified_commit_fails(self):
        with self.assertRaisesRegex(RuntimeError, "signature"):
            self.invoke(verified=False)

    def test_different_remote_bytes_fail(self):
        with self.assertRaisesRegex(RuntimeError, "bytes differ"):
            self.invoke(remote=b"different")

    def test_non_main_ref_cannot_publish(self):
        with (
            patch.dict("os.environ", {"GITHUB_REF": "refs/heads/ci/test"}),
            patch.object(publish, "gh") as api,
        ):
            with self.assertRaisesRegex(RuntimeError, "restricted to main"):
                publish.main()
            api.assert_not_called()
