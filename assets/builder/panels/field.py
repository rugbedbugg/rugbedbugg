"""Compact tape labels around the two playable rice recordings."""

from ..svgkit import corners, esc, scanlines, svg
from ..theme import BC, C

TW = 356  # artwork width inside each GitHub table column
RICES = [
    ("oxide", "0xIde", "ARCH"),
    ("nix", "0xNix", "NIXOS"),
]


def _strip(h):
    return [
        '<rect x=".5" y=".5" width="%s" height="%s" fill="%s" stroke="%s"/>'
        % (TW - 1, h - 1, C["black"], BC),
        scanlines(1, 1, TW - 2, h - 2, op=0.10),
        corners(0, 0, TW, h, s=6, inset=4),
    ]


def build_tape_header(number, name, distro):
    h = 30
    b = _strip(h)
    b.append(
        '<text x="12" y="20" font-size="10.5" fill="%s">TAPE %02d / '
        '<tspan font-size="13" fill="%s">%s</tspan></text>'
        % (C["gray"], number, C["bright"], esc(name))
    )
    b.append(
        '<text x="%s" y="20" font-size="10.5" text-anchor="end" '
        'fill="%s">%s · HYPRLAND</text>' % (TW - 12, C["cyan"], esc(distro))
    )
    return svg(TW, h, "", "".join(b))


def build_tape_footer(name):
    h = 33
    b = _strip(h)
    b.append(
        '<text x="16" y="21" font-size="11" fill="%s">SOURCE://%s</text>'
        % (C["gray"], esc(name))
    )
    b.append(
        '<text x="%s" y="21" font-size="11" text-anchor="end" '
        'fill="%s">DOTFILES &gt;&gt;</text>' % (TW - 16, C["cyan"])
    )
    return svg(TW, h, "", "".join(b))
