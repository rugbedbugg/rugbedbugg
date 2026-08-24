# Profile README stabilization via GitHub Actions + lowlighter/metrics

**Date:** 2026-07-23
**Repo:** `rugbedbugg/rugbedbugg` (GitHub profile README)

## Problem

The profile README renders several dynamic cards by hot-linking third-party
Vercel apps that generate the image *live, every time the profile is viewed*:

| Element | Host | Status (2026-07-23) |
|---|---|---|
| Stats card + top languages | `github-readme-stats-vert-eight-34.vercel.app` (own deployment) | 200 |
| Activity graph | `github-readme-activity-graph.vercel.app` (public) | 200 |
| Quote ("Sensible Words") | `quotes-github-readme.vercel.app` (public) | 200 |
| Trophies | `github-profile-trophy-kannan.vercel.app` | 404 (deployment deleted) |

The trophy host has already died (404), and the official trophy host returns
402 (usage cap). Any of the remaining hosts can 404 / 402 / rate-limit with no
warning, because rendering happens at page-view time. The class problem is the
runtime dependency on external services, not any single dead host.

## Goal

Remove the view-time dependency on external render hosts by generating profile
graphics on a schedule with GitHub Actions and committing the result into the
repo as a static file. GitHub then serves a static image that cannot 404/402.

## Non-goals

- Rewriting the README's static content (badges, socials, header, video).
- Shrinking git history (the deleted 12 MB demo video still lives in history;
  out of scope here).
- Preserving the exact current visual style; a new metrics-style card is
  acceptable (decided during brainstorming).

## Design

### Generator

Use `lowlighter/metrics` — a GitHub Action that queries the GitHub API and
renders a self-contained SVG, then commits it back to the repo. All rendering
happens during the Action run; nothing renders at view-time.

### Output layout — Approach A (single combined image)

One file, `github-metrics.svg`, containing four stacked sections:

1. **Core stats** (base plugin) — commits, PRs, issues, stars, followers,
   contributions. Replaces the current stats card.
2. **Top languages** (`languages` plugin) — excluding `portfolio-website` and
   `ML_SchoolAssignments`, matching the current `exclude_repo` list.
3. **Achievements** (`achievements` plugin) — native replacement for the dead
   trophy card.
4. **Activity calendar** (`isocalendar` plugin) — replacement for the
   activity-graph card.

Rationale: a single committed file is the fewest moving parts and the most
stable/low-maintenance option. The side-by-side arrangement of the current
layout is intentionally traded away for simplicity.

### Authentication

- A **fine-grained personal access token** scoped to only `rugbedbugg/rugbedbugg`
  with **Contents: read & write** (needed so the Action can commit the generated
  SVG). Public profile stats are readable without additional scopes.
- Stored as the repository secret `METRICS_TOKEN`.
- Least privilege: the token cannot modify the user's other repositories.
- This is the one manual step only the user can perform (token creation +
  secret storage). Exact click-by-click steps to be provided during
  implementation.

### Workflow — `.github/workflows/metrics.yml`

- **Triggers:**
  - `schedule`: daily at `0 0 * * *` (00:00 UTC).
  - `workflow_dispatch`: manual on-demand runs.
  - `push` on `main` limited to the workflow file (so config changes re-render).
- **Permissions:** `contents: write`.
- **Step:** `lowlighter/metrics@latest` configured with the four plugins above,
  `token: ${{ secrets.METRICS_TOKEN }}`, `filename: github-metrics.svg`,
  transient-error `retries` enabled, and default `output_action: commit`.

### Theming

Metrics ships no tokyonight template, but accepts custom colors. Tune toward the
existing palette (`#1a1b26` background, `#7aa2f7` accent) so the card does not
clash with the shields.io badges, which remain tokyonight-styled.

### README changes

- Replace the three `<p align="left">` blocks (stats+langs, trophies, activity)
  with a single `![Metrics](./github-metrics.svg)`.
- **Keep unchanged:** header text, "About Me", Daily Workflow badges,
  Programming Languages badges, all Socials, the Screenshots video, and the
  "Sensible Words" quote card (its host is currently live; kept as the one
  remaining dynamic element — low risk, flavor only).

### Error handling / stability properties

- If a scheduled run fails (API hiccup, expired token), the previously committed
  `github-metrics.svg` remains in place — the profile never shows a broken
  image. The next scheduled run retries.
- `retries` on the metrics step absorbs transient GitHub API errors within a run.

## Success criteria

- `github-metrics.svg` exists in the repo and renders on the profile.
- Profile loads with no dependency on `*-trophy-*` or other live render hosts
  for the four migrated sections.
- The workflow runs on schedule and on manual dispatch, committing an updated
  image without manual intervention.
- Temporarily breaking the token or network does not blank the profile image.

## Manual steps required from the user

1. Create the fine-grained PAT (scoped to this repo, Contents R/W).
2. Add it as repo secret `METRICS_TOKEN`.
3. (Optional) Trigger the first run via `workflow_dispatch` to verify.
