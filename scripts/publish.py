"""Publish changed tracked SVGs atomically through GitHub's signed commit API."""

import base64
import json
import os
import subprocess
from pathlib import Path
from xml.etree import ElementTree


def gh(*args, payload=None):
    command = ["gh", "api", *args]
    if payload is not None:
        command += ["--input", "-"]
    result = subprocess.run(
        command,
        input=json.dumps(payload) if payload is not None else None,
        text=True,
        check=True,
        capture_output=True,
    )
    result = json.loads(result.stdout)
    if isinstance(result, dict) and result.get("errors"):
        raise RuntimeError(result["errors"])
    return result


def changes():
    names = (
        subprocess.check_output(
            ["git", "diff", "--name-only", "-z", "HEAD", "--", "assets/*.svg"]
        )
        .decode()
        .split("\0")
    )
    additions = []
    for name in filter(None, names):
        path = Path(name)
        if path.parent != Path("assets") or path.suffix != ".svg" or path.is_symlink():
            raise ValueError(f"Unexpected output: {name}")
        data = path.read_bytes()
        root = ElementTree.fromstring(data)
        if root.tag != "{http://www.w3.org/2000/svg}svg":
            raise ValueError(f"Not SVG: {name}")
        additions.append({"path": name, "contents": base64.b64encode(data).decode()})
    return additions


def main():
    if os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise RuntimeError("Profile publication is restricted to main")
    additions = changes()
    if not additions:
        print("No panel changes to publish.")
        return
    repository = os.environ["GITHUB_REPOSITORY"]
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    mutation = """mutation($input: CreateCommitOnBranchInput!) {
      createCommitOnBranch(input: $input) { commit { oid signature { isValid } } }
    }"""
    result = gh(
        "graphql",
        payload={
            "query": mutation,
            "variables": {
                "input": {
                    "branch": {
                        "repositoryNameWithOwner": repository,
                        "branchName": "main",
                    },
                    "expectedHeadOid": head,
                    "message": {
                        "headline": "[Profile]: Refresh generated panels [skip ci]"
                    },
                    "fileChanges": {"additions": additions},
                }
            },
        },
    )
    commit = result["data"]["createCommitOnBranch"]["commit"]
    if not (commit.get("signature") or {}).get("isValid"):
        raise RuntimeError("Published commit signature did not verify")
    for addition in additions:
        remote = gh(
            f"repos/{repository}/contents/{addition['path']}?ref={commit['oid']}"
        )
        if base64.b64decode(remote["content"]) != base64.b64decode(
            addition["contents"]
        ):
            raise RuntimeError(f"Published bytes differ: {addition['path']}")
    print(f"Verified signed commit and {len(additions)} panels: {commit['oid']}")


if __name__ == "__main__":
    main()
