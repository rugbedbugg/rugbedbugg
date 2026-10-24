"""Dossier panel: key/value subject facts."""

from ..svgkit import esc, led, panel_frame, svg
from ..theme import C, W


def build_dossier():
    rows = [
        ("SUBJECT", [[("Oxide 1-6 — ", C["bright"]), ("@rugbedbugg", C["cyan"])]]),
        ("CLASS", [[("Arch + NixOS", C["purple"])]]),
        (
            "RIG",
            [
                # Match the five-character NixOS name to align the rig columns.
                [("Arch ", C["cyan"]), (" · 0xIde · Hyprland", C["bright"])],
                [("NixOS", C["cyan"]), (" · 0xNix · Hyprland", C["bright"])],
            ],
        ),
        (
            "DESCRIPTION",
            [
                [
                    ("watches ", C["bright"]),
                    ("YouTube", C["red"]),
                    (" from the terminal", C["bright"]),
                ]
            ],
        ),
        ("STATUS", [[("RICED", C["green"])]]),
    ]
    row_h = 36
    line_h = 22
    body_y = 28 + 16
    h = body_y + sum(row_h + (len(lines) - 1) * line_h for _, lines in rows) + 8
    b = [panel_frame(h, "SUBJECT DOSSIER", "REF://ABOUT.DAT")]
    dtx = 22
    ddx = 150
    y = body_y + 16
    for label, lines in rows:
        b.append(
            '<text x="%s" y="%s" font-size="12" letter-spacing="1" '
            'fill="%s">%s</text>' % (dtx, y, C["dim"], esc(label))
        )
        value_x = ddx
        if label == "STATUS":
            b.append(led(ddx, y - 5, color=C["green"], blink=False))
            value_x += 16
        for i, spans in enumerate(lines):
            seg = '<text x="%s" y="%s" font-size="14">' % (value_x, y + i * line_h)
            for txt, col in spans:
                seg += '<tspan fill="%s">%s</tspan>' % (col, esc(txt))
            seg += "</text>"
            b.append(seg)
        y += row_h + (len(lines) - 1) * line_h
    return svg(W, h, "", "".join(b))
