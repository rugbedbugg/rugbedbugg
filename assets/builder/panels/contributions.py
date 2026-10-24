"""Pinned contribution evidence and a chronological feed of upstream merges."""

from datetime import datetime
from textwrap import wrap

from ..svgkit import esc, panel_frame, scanlines, svg
from ..theme import BC2, C, W


def _text(x, y, text, size=13, color=None, anchor="start"):
    return '<text x="%s" y="%s" font-size="%s" fill="%s" text-anchor="%s">%s</text>' % (
        x,
        y,
        size,
        color or C["bright"],
        anchor,
        esc(text),
    )


def _lines(text, width):
    return wrap(text, width=width, break_on_hyphens=False) or [""]


def build_contribution(project, data):
    if project == "latch":
        title, ref = "PINNED / LATCH", "REF://VINNOVATEIT/LATCH"
        name = "VinnovateIT / Latch"
        status = f"{data['latch_count']} MERGED PRS"
        description = "Kotlin Multiplatform core, CLI, credential safety, IPC and release engineering."
        evidence = "EVIDENCE: #85 / #171 / #173 / #137 / #186"
        action = "VIEW MERGED PRS >>"
    elif project == "anyps5":
        title, ref = "PINNED / ANYPS5", "REF://BOYKOPOVAR/ANYPS5"
        name = "AnyPS5 / C++ shader compiler"
        status = f"MERGED #{data['anyps5']['number']}"
        description = (
            "Fixed unsigned integer narrowing semantics in shader constant folding."
        )
        evidence = "EVIDENCE: PR #4195 / 975 REGRESSION CASES"
        action = "VIEW UPSTREAM PR >>"
    else:
        raise ValueError(f"Unknown contribution: {project}")

    b = [_text(22, 56, name, 14)]
    b.append(_text(W - 22, 56, status, 12, C["green"], "end"))
    y = 82
    for line in _lines(description, 86):
        b.append(_text(22, y, line, 13, C["text"]))
        y += 20
    b.append(
        '<line x1="22" y1="%s" x2="%s" y2="%s" stroke="%s"/>'
        % (y - 6, W - 22, y - 6, BC2)
    )
    b.append(_text(22, y + 14, evidence, 10.5, C["cyan"]))
    b.append(_text(W - 22, y + 14, action, 10.5, C["title"], "end"))
    h = y + 36
    out = [panel_frame(h, title, ref), "".join(b)]
    out.append(scanlines(2, 28, W - 4, h - 30, op=0.10))
    return svg(W, h, "", "".join(out))


def build_upstream_feed(data):
    date = datetime.fromisoformat(data["fetched_at"]).strftime("%Y-%m-%d")
    state = "SAVED SNAPSHOT" if data["cached"] else "FETCHED"
    b = [_text(22, 60, "LATEST PUBLIC MERGES", 12, C["cyan"])]
    b.append(_text(W - 22, 60, f"{state} {date} UTC", 10.5, C["gray"], "end"))
    y = 88
    recent = sorted(data["recent"], key=lambda entry: entry["merged_at"], reverse=True)
    for i, entry in enumerate(recent):
        lines = _lines(entry["title"], 76)
        metadata = _lines(f"{entry['repo']} / #{entry['number']}", 82)
        title_y = y + 24 + (len(metadata) - 1) * 16
        next_y = title_y + 24 + (len(lines) - 1) * 20
        if i < len(recent) - 1:
            b.append(
                '<line x1="25" y1="%s" x2="25" y2="%s" stroke="%s"/>'
                % (y, next_y + 16, BC2)
            )
        b.append(
            '<rect x="22" y="%s" width="6" height="6" fill="%s"/>' % (y - 7, C["green"])
        )
        for j, line in enumerate(metadata):
            b.append(_text(44, y + j * 16, line, 11, C["cyan"]))
        merged = datetime.fromisoformat(entry["merged_at"]).strftime("%Y-%m-%d")
        b.append(_text(W - 22, y, merged, 11, C["gray"], "end"))
        for j, line in enumerate(lines):
            b.append(_text(44, title_y + j * 20, line, 14))
        y = next_y + 20

    if not recent:
        b.append(_text(22, y, "No public upstream merges to display.", 14, C["text"]))
        y += 44
    b.append(
        '<line x1="22" y1="%s" x2="%s" y2="%s" stroke="%s"/>'
        % (y - 10, W - 22, y - 10, BC2)
    )
    b.append(_text(22, y + 10, "PUBLIC UPSTREAM / MERGED", 10.5, C["gray"]))
    b.append(_text(W - 22, y + 10, "OPEN FULL MERGE FEED >>", 10.5, C["title"], "end"))
    h = y + 32
    out = [panel_frame(h, "RECENT MERGES", "REF://UPSTREAM.FEED"), "".join(b)]
    out.append(scanlines(2, 28, W - 4, h - 30, op=0.10))
    return svg(W, h, "", "".join(out))
