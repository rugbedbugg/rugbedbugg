"""One contribution panel, sliced into independently clickable README regions."""

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


def _divider(y):
    return '<line x1="22" y1="%s" x2="%s" y2="%s" stroke="%s"/>' % (
        y + 0.5,
        W - 22,
        y + 0.5,
        BC2,
    )


def _project(project, data, top):
    if project == "latch":
        name = "VinnovateIT / Latch"
        status = f"{data['latch_count']} MERGED PRS"
        description = "Kotlin Multiplatform core, CLI, credential safety, IPC and release engineering."
        action = "VIEW MERGED PRS >>"
    else:
        name = "AnyPS5 / C++ shader compiler"
        status = f"MERGED #{data['anyps5']['number']}"
        description = (
            "Fixed unsigned integer narrowing semantics in shader constant folding."
        )
        action = "VIEW UPSTREAM PR >>"
    b = [_text(22, top + 28, name, 14)]
    b.append(_text(W - 22, top + 28, status, 12, C["green"], "end"))
    y = top + 54
    for line in _lines(description, 86):
        b.append(_text(22, y, line, 13, C["text"]))
        y += 20
    b.append(_text(W - 22, y + 4, action, 10.5, C["title"], "end"))
    return "".join(b), y + 26


def _recent(data, top):
    date = datetime.fromisoformat(data["fetched_at"]).strftime("%Y-%m-%d")
    state = "SAVED SNAPSHOT" if data["cached"] else "FETCHED"
    b = [_text(22, top + 28, "RECENT PUBLIC MERGES", 12, C["cyan"])]
    b.append(_text(W - 22, top + 28, f"{state} {date} UTC", 10.5, C["gray"], "end"))
    y = top + 56
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
    b.append(_divider(y - 10))
    b.append(_text(22, y + 10, "PUBLIC UPSTREAM / MERGED", 10.5, C["gray"]))
    b.append(_text(W - 22, y + 10, "OPEN FULL MERGE FEED >>", 10.5, C["title"], "end"))
    return "".join(b), y + 32


def _panel(data):
    b, ranges = [], {}
    top = 28
    for project in ("latch", "anyps5"):
        if project != "latch":
            b.append(_divider(top))
        content, bottom = _project(project, data, top)
        b.append(content)
        ranges[project] = (0 if project == "latch" else top, bottom)
        top = bottom
    b.append(_divider(top))
    content, h = _recent(data, top)
    b.append(content)
    ranges["recent"] = (top, h)
    body = panel_frame(h, "COLLABORATIVE ENGINEERING", "REF://UPSTREAM.PRS")
    body += "".join(b) + scanlines(2, 28, W - 4, h - 30, op=0.10)
    return svg(W, h, "", body), ranges, h


def _slice(data, region):
    # SVG links inside a GitHub <img> are inactive. Crop the same framed panel
    # into contiguous viewports, each wrapped in its existing README hyperlink.
    document, ranges, total_h = _panel(data)
    top, bottom = ranges[region]
    h = bottom - top
    return document.replace(f'height="{total_h}"', f'height="{h}"', 1).replace(
        f'viewBox="0 0 {W} {total_h}"', f'viewBox="0 {top} {W} {h}"', 1
    )


def build_contribution(project, data):
    if project not in ("latch", "anyps5"):
        raise ValueError(f"Unknown contribution: {project}")
    return _slice(data, project)


def build_upstream_feed(data):
    return _slice(data, "recent")
