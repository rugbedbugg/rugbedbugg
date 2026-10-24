"""Loadout panel: side-by-side workflow and language inventories."""

from ..svgkit import esc, panel_frame, scanlines, svg
from ..theme import BC2, C, W


def _inventory(items, left, y, width, columns, lang=False):
    marker = C["purple"] if lang else C["cyan"]
    txtcol = C["title"] if lang else C["bright"]
    row_h = 28
    column_w = width / columns
    out = []
    for i, it in enumerate(items):
        x = left + (i % columns) * column_w
        baseline = y + (i // columns) * row_h
        out.append(
            '<rect x="%s" y="%s" width="4" height="4" fill="%s"/>'
            % (x, baseline - 7, marker)
        )
        out.append(
            '<text x="%s" y="%s" font-size="14" letter-spacing=".3" '
            'fill="%s">%s</text>' % (x + 14, baseline, txtcol, esc(it))
        )
    rows = (len(items) + columns - 1) // columns
    bottom = y + max(0, rows - 1) * row_h + 4
    return "".join(out), bottom


def build_loadout():
    cy = 60
    pad, section_gap = 22, 44
    section_w = (W - 2 * pad - section_gap) / 2
    right_x = pad + section_w + section_gap
    b = []
    b.append(
        '<text x="22" y="%s" font-size="12" letter-spacing="1.2" '
        'fill="%s"><tspan fill="%s">&gt; </tspan>WORKFLOW</text>'
        % (cy, C["cyan"], C["dim"])
    )
    inventory, workflow_bottom = _inventory(
        [
            "Foot",
            "Fish",
            "Vim",
            "lf",
            "Fuzzel",
            "btop",
            "rmpc",
            "direnv",
        ],
        left=pad,
        y=cy + 30,
        width=section_w,
        columns=3,
    )
    b.append(inventory)
    b.append(
        '<text x="%s" y="%s" font-size="12" letter-spacing="1.2" '
        'fill="%s"><tspan fill="%s">&gt; </tspan>LANGUAGES</text>'
        % (right_x, cy, C["cyan"], C["dim"])
    )
    inventory, bottom = _inventory(
        ["Python", "C", "C++", "Java", "Rust", "Shell", "Nix", "Lua"],
        left=right_x,
        y=cy + 30,
        width=section_w,
        columns=3,
        lang=True,
    )
    b.append(inventory)
    bottom = max(workflow_bottom, bottom)
    b.append(
        '<line x1="%s" y1="44" x2="%s" y2="%s" stroke="%s"/>'
        % (W / 2, W / 2, bottom, BC2)
    )
    h = bottom + 22
    out = [panel_frame(h, "DAILY LOADOUT", "REF://LOADOUT.CFG"), "".join(b)]
    out.append(scanlines(2, 28, W - 4, h - 30, op=0.10))
    return svg(W, h, "", "".join(out))
