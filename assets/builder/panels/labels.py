"""Section label strips (thin title bars between README sections)."""
from ..svgkit import esc, led, svg
from ..theme import BC, C, W


def build_label(title, ref):
    h = 30
    b = []
    b.append('<rect x="1" y="1" width="%s" height="%s" '
             'fill="rgba(85,255,255,.05)" stroke="%s"/>' % (W - 2, h - 2, BC))
    b.append(led(16, 15))
    b.append('<text x="30" y="19" font-size="10" letter-spacing="1.6" '
             'fill="%s">%s</text>' % (C["cyan"], esc(title)))
    b.append('<text x="%s" y="19" font-size="10" letter-spacing="1.6" '
             'text-anchor="end" fill="%s">%s</text>'
             % (W - 14, C["gray"], esc(ref)))
    return svg(W, h, "", "".join(b))
