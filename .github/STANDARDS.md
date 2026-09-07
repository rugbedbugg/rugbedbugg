# Repository standards baseline

Adapted from ReAgent's shared CI/CD/README baseline for a generated profile.

- CI: main/CI branch pushes, PRs, manual and reusable calls; read-only permissions,
  timeouts, obsolete-run cancellation, cached mise/uv setup, existing Python 3.12.
- Checks: Ruff lint/format plus offline generation of all SVG panels, XML validity,
  remote-text escaping and unavailable-network fallbacks. No live data is needed
  for validation and tests do not overwrite tracked artwork.
- Refresh: retain the three-hour schedule and manual/main triggers; require CI,
  serialize publication, validate the exact current checkout and generated XML,
  grant write permission only to refresh, and refuse stale-head updates.
- Signing: use GitHub's createCommitOnBranch API with the workflow token. GitHub
  signs the commit; the script checks signature validity and downloads each changed
  file at the returned commit to verify bytes. No additional GPG secret required.
- README: preserve the profile layout. User deferred the README pass; do not add
  application installation sections to a personal profile.

Local tasks: `mise run install`, `mise run check`, and `mise run build` (live data,
rewrites generated SVGs). Run workflow validation and require GitHub CI before
integration. No package release pipeline is relevant to this repository.

Signing reference: https://github.blog/changelog/2021-09-13-a-simpler-api-for-authoring-commits/
