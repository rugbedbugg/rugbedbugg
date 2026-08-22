"""Dossier panel: key/value subject facts."""
from ..svgkit import esc, panel_frame, svg
from ..theme import C, W


def build_dossier():
    rows = [
        ("SUBJECT", [("Oxide 1-6 — ", C["bright"]),
                     ("@rugbedbugg", C["cyan"])]),
        ("ALTER EGO", [("Arsenic 1-6 — ", C["bright"]),
                       ("@mystik-krysat", C["cyan"])]),
        ("CLASS", [("Linux/Windows Power-User", C["purple"])]),
        ("RIG", [("Arch btw", C["cyan"]),
                 (" · Caelestia · Hyprland ", C["bright"]),
                 ("| ", C["dim"]),
                 ("Windows", C["cyan"]),
                 (" · WSL · Powershell", C["bright"])]),
        ("HABIT", [("watches YouTube from the terminal", C["bright"])]),
        ("STATUS", [("● RICED", C["green"])]),
    ]
    row_h = 30
    body_y = 28 + 16
    h = body_y + len(rows) * row_h + 8
    b = [panel_frame(h, "SUBJECT DOSSIER", "REF://ABOUT.DAT")]
    dtx = 22
    ddx = 150
    y = body_y + 14
    for label, spans in rows:
        b.append('<text x="%s" y="%s" font-size="10.5" letter-spacing="1" '
                 'fill="%s">%s</text>' % (dtx, y, C["dim"], esc(label)))
        seg = '<text x="%s" y="%s" font-size="12.5">' % (ddx, y)
        for txt, col in spans:
            seg += '<tspan fill="%s">%s</tspan>' % (col, esc(txt))
        seg += '</text>'
        b.append(seg)
        y += row_h
    return svg(W, h, "", "".join(b))
