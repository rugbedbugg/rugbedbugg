"""Transmission panel: a wrapped, animated-quote speech block."""
from ..svgkit import esc, panel_frame, svg, wrap
from ..theme import C, W


def build_transmission(quote):
    body_y = 44
    lines = wrap(quote, 78)
    y1 = body_y + 26
    h = body_y + 20 + len(lines) * 22 + 8
    b = [panel_frame(h, "TRANSMISSION", "REF://QUOTES.LOG")]
    b.append('<text x="22" y="%s" font-size="10.5" letter-spacing="1.4" '
             'fill="%s">INCOMING · SENSIBLE WORDS</text>'
             % (body_y + 4, C["cyan"]))
    b.append('<rect x="22" y="%s" width="2" height="%s" fill="%s"/>'
             % (y1 - 13, max(20, len(lines) * 22 - 4), C["cyan"]))
    y = y1
    for i, ln in enumerate(lines):
        txt = ("“" + ln) if i == 0 else ln
        if i == len(lines) - 1:
            txt = txt + "”"
        b.append('<text x="34" y="%s" font-size="14" fill="%s">%s</text>'
                 % (y, C["bright"], esc(txt)))
        y += 22
    return svg(W, h, "", "".join(b))
