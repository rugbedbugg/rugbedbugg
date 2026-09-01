# Contributing to the rugbedbugg Profile

This repository generates the animated SVG panels used by the GitHub profile. Keep generated panels synchronized with the Python generator and preserve accessible, colorblind-safe presentation.

## Regenerate the profile

The workflow uses Python 3.12, selected locally by `.python-version`. The generator uses the standard library and accepts a GitHub token through the environment for higher API limits:

```sh
uv run python assets/build.py
```

Review the resulting `assets/*.svg` diff and open the SVGs in a browser before submitting.

## Change guidelines

- Put rendering primitives and data fetching in `assets/builder/`; keep `assets/build.py` as the orchestration entry point.
- Never embed a GitHub token or other credential in generated SVGs, logs, or commits.
- Preserve readable text alternatives, contrast, and behavior when live API data is unavailable.
- Update generator code and regenerated SVG panels together.
- Keep unrelated live-stat refresh noise out of focused design changes where possible.

## Pull requests

Explain the affected panels, include before/after screenshots for visual changes, and report the generator command and browser(s) used for verification.
