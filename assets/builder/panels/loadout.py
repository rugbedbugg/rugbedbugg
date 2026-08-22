"""Loadout panel: workflow and language chip rows."""
from ..svgkit import esc, panel_frame, svg
from ..theme import BC2, C, W


def _chips(items, y, lang=False):
    border = "rgba(192,132,252,.4)" if lang else BC2
    fillbg = "rgba(168,85,247,.07)" if lang else "rgba(85,255,255,.04)"
    txtcol = C["title"] if lang else C["text"]
    # Departure Mono advances ~0.636em and the label adds .6 letter-spacing;
    # size the box to that real width so the last glyph keeps its padding
    # instead of touching the right border.
    cpc = 11 * 0.636 + 0.6
    x = 22
    out = []
    for it in items:
        wc = len(it) * cpc + 20
        out.append('<rect x="%s" y="%s" width="%s" height="24" fill="%s" '
                   'stroke="%s"/>' % (x, y, round(wc), fillbg, border))
        out.append('<text x="%s" y="%s" font-size="11" letter-spacing=".6" '
                   'fill="%s">%s</text>'
                   % (x + 10, y + 16, txtcol, esc(it.upper())))
        x += wc + 7
    return "".join(out)


def build_loadout():
    body_y = 44
    h = body_y + 150
    b = [panel_frame(h, "DAILY LOADOUT", "REF://LOADOUT.CFG")]
    b.append('<text x="22" y="%s" font-size="10" letter-spacing="1.4" '
             'fill="%s">WORKFLOW</text>' % (body_y + 14, C["dim"]))
    b.append(_chips(["Sublime Text", "Ollama", "OpenClaw", "FreeFileSync",
                     "RealTimeSync", "PowerShell"],
                    body_y + 24))
    b.append('<text x="22" y="%s" font-size="10" letter-spacing="1.4" '
             'fill="%s">LANGUAGES</text>' % (body_y + 78, C["dim"]))
    b.append(_chips(["Rust", "C", "C++", "Python", "Java", "Assembly", "Bash"],
                    body_y + 88, lang=True))
    return svg(W, h, "", "".join(b))
