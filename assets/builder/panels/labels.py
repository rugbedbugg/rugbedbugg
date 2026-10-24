"""Section label strips (thin title bars between README sections)."""

from ..svgkit import corners, scanlines, svg, title_bar
from ..theme import BC, C, W


def label_body(title, ref):
    """Shared artwork, also embedded in panels to avoid HTML line-height gaps."""
    h = 30
    b = []
    b.append(
        '<rect x="1" y="1" width="%s" height="%s" '
        'fill="%s" stroke="%s"/>' % (W - 2, h - 2, C["black"], BC)
    )
    b.append(title_bar(title, ref))
    b.append(scanlines(2, 2, W - 4, h - 4, op=0.10))
    b.append(corners(1, 1, W - 2, h - 2, s=6))
    return "".join(b)


def build_label(title, ref):
    return svg(W, 30, "", label_body(title, ref))
