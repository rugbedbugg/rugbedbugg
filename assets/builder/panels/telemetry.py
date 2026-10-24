"""Telemetry panel: profile snapshot, language breakdown and contribution calendar."""

from ..svgkit import esc, led, panel_frame, scanlines, svg
from ..theme import BC2, CAL_SHADES, C, LANG_COLORS, W


def build_telemetry(stats, langs, cal):
    ix, pad = 22, 22
    iw = W - 2 * ix
    css = ".cur{animation:blink 1s steps(1,end) infinite}"
    c = []

    # Recorder-style strip; the data is a periodic snapshot, not a live feed.
    c.append(
        '<rect x="%s" y="44" width="%s" height="26" '
        'fill="rgba(85,255,255,.03)"/>' % (ix, iw)
    )
    c.append(led(ix + 10, 57, color=C["cyan"], blink=False))
    c.append(
        '<text x="%s" y="61" font-size="10" letter-spacing="1.4" '
        'fill="%s">GITHUB // METRICS</text>' % (ix + 26, C["cyan"])
    )
    c.append(
        '<text x="%s" y="61" font-size="10" letter-spacing="1.4" '
        'text-anchor="end" fill="%s">SNAPSHOT</text>' % (ix + iw - 10, C["gray"])
    )

    cy = 96
    c.append(
        '<text x="%s" y="%s" font-size="14" fill="%s">'
        '<tspan fill="%s">~/rugbedbugg</tspan> '
        '<tspan fill="%s">(main)</tspan> <tspan fill="%s">$</tspan> '
        '<tspan fill="%s">./metrics --generate</tspan>'
        '<tspan class="cur" fill="%s">█</tspan></text>'
        % (ix, cy, C["text"], C["cyan"], C["purple"], C["dim"], C["bright"], C["cyan"])
    )
    cy += 30

    def seclabel(txt, right=None):
        s = (
            '<text x="%s" y="%s" font-size="12" letter-spacing="1.2" '
            'fill="%s"><tspan fill="%s">&gt; </tspan>%s</text>'
            % (ix, cy, C["cyan"], C["dim"], esc(txt))
        )
        if right:
            s += (
                '<text x="%s" y="%s" font-size="11" text-anchor="end" '
                'fill="%s">%s</text>' % (ix + iw, cy, C["gray"], esc(right))
            )
        return s

    c.append(seclabel("core stats"))
    cy += 16
    boxes = [
        (stats["repos"], "REPOS"),
        (stats["stars"], "STARS"),
        (stats["followers"], "FOLLOWERS"),
        (stats["following"], "FOLLOWING"),
    ]
    bw = (iw - 3 * 12) / 4
    for i, (n, lab) in enumerate(boxes):
        bx = ix + i * (bw + 12)
        c.append(
            '<rect x="%s" y="%s" width="%s" height="62" '
            'fill="rgba(85,255,255,.03)" stroke="%s"/>' % (bx, cy, bw, BC2)
        )
        c.append(
            '<text x="%s" y="%s" font-size="24" fill="%s" '
            'filter="url(#glow)">%s</text>' % (bx + 12, cy + 29, C["cyan"], n)
        )
        c.append(
            '<text x="%s" y="%s" font-size="12" letter-spacing=".8" '
            'fill="%s">%s</text>' % (bx + 12, cy + 49, C["gray"], lab)
        )
    cy += 62 + 32

    c.append(seclabel("most used languages", "colorblind-safe"))
    cy += 18
    shown = list(langs)
    ssum = sum(p for _, p in shown)
    if ssum < 99.0:
        shown.append(("Other", round(100 - ssum, 1)))
    total = sum(p for _, p in shown) or 1
    colmap = {}
    x = ix
    for i, (name, pct) in enumerate(shown):
        col = C["gray"] if name == "Other" else LANG_COLORS[i % len(LANG_COLORS)]
        colmap[name] = col
        segw = iw * pct / total
        c.append(
            '<rect x="%s" y="%s" width="%s" height="14" fill="%s"/>'
            % (x, cy, segw, col)
        )
        if i:
            c.append(
                '<line x1="%s" y1="%s" x2="%s" y2="%s" '
                'stroke="%s"/>' % (x, cy, x, cy + 14, C["black"])
            )
        x += segw
    c.append(
        '<rect x="%s" y="%s" width="%s" height="14" fill="none" '
        'stroke="rgba(255,255,255,.14)"/>' % (ix, cy, iw)
    )
    cy += 14 + 28

    # Two fixed columns keep names and percentages aligned at a readable size.
    legend_gap, legend_row_h = 32, 26
    legend_w = (iw - legend_gap) / 2
    for i, (name, pct) in enumerate(shown):
        lx = ix + (i % 2) * (legend_w + legend_gap)
        ly = cy + (i // 2) * legend_row_h
        c.append(
            '<rect x="%s" y="%s" width="10" height="10" fill="%s"/>'
            % (lx, ly - 10, colmap[name])
        )
        c.append(
            '<text x="%s" y="%s" font-size="14" fill="%s">%s</text>'
            % (lx + 20, ly, C["bright"], esc(name))
        )
        c.append(
            '<text x="%s" y="%s" font-size="14" text-anchor="end" '
            'fill="%s">%s%%</text>' % (lx + legend_w, ly, C["gray"], pct)
        )
    legend_rows = (len(shown) + 1) // 2
    cy += max(0, legend_rows - 1) * legend_row_h + 32

    c.append(seclabel("contribution activity · last year"))
    cy += 20
    cols = max(1, (len(cal) + 6) // 7)
    gap = 2
    cell = min((iw - (cols - 1) * gap) / cols, 12)
    for idx, lv in enumerate(cal):
        col_i, row_i = idx // 7, idx % 7
        gx = ix + col_i * (cell + gap)
        gy = cy + row_i * (cell + gap)
        c.append(
            '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>'
            % (
                round(gx, 2),
                round(gy, 2),
                round(cell, 2),
                round(cell, 2),
                CAL_SHADES[max(0, min(4, lv))],
            )
        )
    cy += 7 * cell + 6 * gap + 24
    kx = ix + iw - 154
    c.append(
        '<text x="%s" y="%s" font-size="12" fill="%s">less</text>' % (kx, cy, C["gray"])
    )
    for i, shade in enumerate(CAL_SHADES):
        c.append(
            '<rect x="%s" y="%s" width="10" height="10" fill="%s"/>'
            % (kx + 42 + i * 14, cy - 10, shade)
        )
    c.append(
        '<text x="%s" y="%s" font-size="12" fill="%s">more</text>'
        % (kx + 118, cy, C["gray"])
    )

    h = round(cy + pad)
    out = [panel_frame(h, "TELEMETRY", "REF://METRICS.SYS"), "".join(c)]
    # Draw after the content so opaque chart fills do not hide the VHS texture.
    out.append(scanlines(2, 28, W - 4, h - 30, op=0.10))
    return svg(W, h, css, "".join(out))
