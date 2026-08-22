"""Low-level SVG primitives shared by every panel."""
import os
import xml.dom.minidom as minidom

from .embedded import FONT_FACE
from .theme import C, BC, BC2, BCH, W


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def cw(size):
    """Approximate advance width of one Departure Mono glyph (with tracking)."""
    return size * 0.6


def wrap(text, maxchars):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > maxchars:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w) if cur else w
    if cur:
        lines.append(cur)
    return lines


def led(x, y, color=None, r=4, blink=True):
    color = color or C["red"]
    cls = ' class="led"' if blink else ""
    return ('<rect x="%s" y="%s" width="8" height="8" fill="%s"%s '
            'filter="url(#glow)"/>' % (x, y - 4, color, cls))


def corners(x, y, w, h, col=BCH, s=12, inset=5):
    """Four viewfinder L-brackets."""
    L = x + inset
    R = x + w - inset
    T = y + inset
    B = y + h - inset
    p = []
    # top-left
    p.append('<path d="M%s %s v%s M%s %s h%s"/>' % (L, T + s, -s, L, T, s))
    # top-right
    p.append('<path d="M%s %s v%s M%s %s h%s"/>' % (R, T + s, -s, R, T, -s))
    # bottom-left
    p.append('<path d="M%s %s v%s M%s %s h%s"/>' % (L, B - s, s, L, B, s))
    # bottom-right
    p.append('<path d="M%s %s v%s M%s %s h%s"/>' % (R, B - s, s, R, B, -s))
    return ('<g stroke="%s" stroke-width="1" fill="none">%s</g>'
            % (col, "".join(p)))


def scanlines(x, y, w, h, op=0.18):
    return ('<rect x="%s" y="%s" width="%s" height="%s" fill="url(#scan)" '
            'opacity="%s"/>' % (x, y, w, h, op))


def defs():
    return (
        '<defs>'
        '<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
        '<rect width="4" height="2" fill="#000"/></pattern>'
        '<radialGradient id="vig" cx="50%" cy="50%" r="62%">'
        '<stop offset="55%" stop-color="#000" stop-opacity="0"/>'
        '<stop offset="100%" stop-color="#000" stop-opacity=".6"/></radialGradient>'
        '<radialGradient id="amb1" cx="24%" cy="12%" r="46%">'
        '<stop offset="0%" stop-color="#00ffff" stop-opacity=".06"/>'
        '<stop offset="100%" stop-color="#00ffff" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="amb2" cx="80%" cy="92%" r="52%">'
        '<stop offset="0%" stop-color="#a855f7" stop-opacity=".11"/>'
        '<stop offset="100%" stop-color="#a855f7" stop-opacity="0"/></radialGradient>'
        '<linearGradient id="nmfade" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#000" stop-opacity="0"/>'
        '<stop offset="100%" stop-color="#000" stop-opacity=".9"/></linearGradient>'
        '<filter id="glow" x="-60%" y="-60%" width="220%" height="220%">'
        '<feGaussianBlur stdDeviation="1.6" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
        '</defs>'
    )


def bg(w, h):
    return ('<rect width="%s" height="%s" fill="%s"/>'
            '<rect width="%s" height="%s" fill="url(#amb1)"/>'
            '<rect width="%s" height="%s" fill="url(#amb2)"/>'
            % (w, h, C["ground"], w, h, w, h))


# Shared CSS every panel starts with.
BASE_CSS = (
    FONT_FACE +
    "text,tspan{font-family:'Departure Mono',ui-monospace,Consolas,monospace;"
    "white-space:pre}"
    ".led{animation:blink 1.1s steps(1,end) infinite}"
    "@keyframes blink{0%,55%{opacity:1}56%,100%{opacity:.12}}"
)


def svg(w, h, extra_css, body, bg_on=True):
    doc = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" '
        'viewBox="0 0 %s %s" font-family="\'Departure Mono\',monospace">'
        '%s<style>%s%s</style>%s%s</svg>'
        % (w, h, w, h, defs(), BASE_CSS, extra_css,
           bg(w, h) if bg_on else "", body)
    )
    return doc


def panel_frame(h, title, ref, y0=0):
    """Outer border + label bar + corner brackets + scanline overlay."""
    parts = []
    parts.append('<rect x="1" y="%s" width="%s" height="%s" fill="%s" '
                 'stroke="%s"/>' % (y0 + 1, W - 2, h - 2, C["black"], BC))
    # label bar
    parts.append('<rect x="1" y="%s" width="%s" height="26" '
                 'fill="rgba(85,255,255,.05)"/>' % (y0 + 1, W - 2))
    parts.append('<line x1="1" y1="%s" x2="%s" y2="%s" stroke="%s"/>'
                 % (y0 + 27, W - 1, y0 + 27, BC2))
    parts.append(led(16, y0 + 14))
    parts.append('<text x="30" y="%s" font-size="9.5" letter-spacing="1.6" '
                 'fill="%s">%s</text>' % (y0 + 17.5, C["cyan"], esc(title)))
    parts.append('<text x="%s" y="%s" font-size="9.5" letter-spacing="1.6" '
                 'text-anchor="end" fill="%s">%s</text>'
                 % (W - 14, y0 + 17.5, C["gray"], esc(ref)))
    parts.append(corners(1, y0 + 1, W - 2, h - 2))
    parts.append(scanlines(2, y0 + 28, W - 4, h - 30))
    return "".join(parts)


def write(name, content):
    path = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), name)
    minidom.parseString(content)  # well-formedness check
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  ok  %-22s %6d bytes" % (name, len(content)))
