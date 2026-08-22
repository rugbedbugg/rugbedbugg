"""Telemetry panel: live stats, colorblind-safe languages, contribution calendar."""
from ..svgkit import cw, esc, panel_frame, svg
from ..theme import BC2, CAL_SHADES, C, LANG_COLORS, W


def build_telemetry(stats, langs, cal):
    label_h, pad = 28, 14
    card_x, card_w = 16, W - 32
    ipad = 14
    ix = card_x + ipad
    iw = card_w - 2 * ipad
    card_top = label_h + pad
    hd_h = 26
    css = (".cur{animation:blink 1s steps(1,end) infinite}"
           ".sec::before{content:'> '}")
    c = []
    cy = card_top + hd_h + 20
    # prompt
    c.append('<text x="%s" y="%s" font-size="12.5" fill="%s">'
             '<tspan fill="%s">~/rugbedbugg</tspan> '
             '<tspan fill="%s">(main)</tspan> <tspan fill="%s">$</tspan> '
             '<tspan fill="%s">./metrics --generate</tspan>'
             '<tspan class="cur" fill="%s">█</tspan></text>'
             % (ix, cy, C["text"], C["cyan"], C["purple"], C["dim"],
                C["bright"], C["cyan"]))
    cy += 24

    def seclabel(txt, right=None):
        s = ('<text x="%s" y="%s" font-size="10.5" letter-spacing="1.4" '
             'fill="%s"><tspan fill="%s">&gt; </tspan>%s</text>'
             % (ix, cy, C["cyan"], C["dim"], esc(txt)))
        if right:
            s += ('<text x="%s" y="%s" font-size="9.5" text-anchor="end" '
                  'fill="%s">%s</text>' % (ix + iw, cy, C["dim"], esc(right)))
        return s

    # core stats
    c.append(seclabel("core stats"))
    cy += 12
    boxes = [(stats["repos"], "REPOS"), (stats["stars"], "STARS"),
             (stats["followers"], "FOLLOWERS"), (stats["following"], "FOLLOWING")]
    bw = (iw - 3 * 8) / 4
    for i, (n, lab) in enumerate(boxes):
        bx = ix + i * (bw + 8)
        c.append('<rect x="%s" y="%s" width="%s" height="42" '
                 'fill="rgba(85,255,255,.03)" stroke="rgba(85,255,255,.16)"/>'
                 % (bx, cy, bw))
        c.append('<text x="%s" y="%s" font-size="17" fill="%s" '
                 'filter="url(#glow)">%s</text>'
                 % (bx + 9, cy + 22, C["cyan"], n))
        c.append('<text x="%s" y="%s" font-size="9" letter-spacing=".8" '
                 'fill="%s">%s</text>' % (bx + 9, cy + 34, C["dim"], lab))
    cy += 42 + 18

    # languages
    c.append(seclabel("most used languages", "colorblind-safe"))
    cy += 12
    shown = list(langs)
    ssum = sum(p for _, p in shown)
    if ssum < 99.0:
        shown = shown + [("Other", round(100 - ssum, 1))]
    total = sum(p for _, p in shown) or 1
    colmap = {}
    x = ix
    barw = iw
    c.append('<rect x="%s" y="%s" width="%s" height="12" fill="none" '
             'stroke="rgba(255,255,255,.14)"/>' % (ix, cy, barw))
    for i, (name, pct) in enumerate(shown):
        col = "#8a8a8a" if name == "Other" else LANG_COLORS[i % len(LANG_COLORS)]
        colmap[name] = col
        segw = barw * pct / total
        c.append('<rect x="%s" y="%s" width="%s" height="12" fill="%s"/>'
                 % (x, cy, segw, col))
        x += segw
    cy += 26
    # legend (flow with wrap)
    lx, lrow_h = ix, 18
    for name, pct in shown:
        item = "%s %s%%" % (name, pct)
        wpx = 15 + len(item) * cw(11) + 16
        if lx + wpx > ix + iw:
            lx = ix
            cy += lrow_h
        c.append('<rect x="%s" y="%s" width="9" height="9" fill="%s"/>'
                 % (lx, cy - 9, colmap[name]))
        c.append('<text x="%s" y="%s" font-size="11" fill="%s">%s '
                 '<tspan fill="%s">%s%%</tspan></text>'
                 % (lx + 14, cy, C["bright"], esc(name), C["dim"], pct))
        lx += wpx
    cy += 22

    # contribution calendar (2D)
    c.append(seclabel("contribution activity · last year"))
    cy += 12
    cols = (len(cal) + 6) // 7
    gap = 2
    cell = (iw - (cols - 1) * gap) / cols
    cell = min(cell, 11)
    for idx, lv in enumerate(cal):
        col_i, row_i = idx // 7, idx % 7
        gx = ix + col_i * (cell + gap)
        gy = cy + row_i * (cell + gap)
        c.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>'
                 % (round(gx, 1), round(gy, 1), round(cell, 1), round(cell, 1),
                    CAL_SHADES[max(0, min(4, lv))]))
    cy += 7 * (cell + gap) + 6
    # calkey
    kx = ix + iw - 12 - 5 * 12 - 30
    c.append('<text x="%s" y="%s" font-size="10" fill="%s">less</text>'
             % (kx, cy, C["dim"]))
    for i, sh in enumerate(CAL_SHADES):
        c.append('<rect x="%s" y="%s" width="9" height="9" fill="%s"/>'
                 % (kx + 26 + i * 12, cy - 8, sh))
    c.append('<text x="%s" y="%s" font-size="10" fill="%s">more</text>'
             % (kx + 26 + 5 * 12 + 4, cy, C["dim"]))
    cy += 10

    card_bottom = cy + 6
    card_h = card_bottom - card_top
    h = card_bottom + pad

    out = [panel_frame(h, "TELEMETRY", "REF://METRICS.SYS")]
    out.append('<rect x="%s" y="%s" width="%s" height="%s" fill="#08060e" '
               'stroke="%s"/>' % (card_x, card_top, card_w, card_h, BC2))
    out.append('<rect x="%s" y="%s" width="%s" height="%s" fill="#0b0912" '
               'stroke="%s"/>' % (card_x, card_top, card_w, hd_h, BC2))
    for i, dc in enumerate(["#2f4a44", "#3a2f4a", "#ff5555"]):
        out.append('<rect x="%s" y="%s" width="8" height="8" fill="%s"/>'
                   % (card_x + 12 + i * 12, card_top + 9, dc))
    out.append('<text x="%s" y="%s" font-size="10" letter-spacing="1.4" '
               'fill="%s">RUGBEDBUGG@GITHUB — METRICS</text>'
               % (card_x + 54, card_top + 17, C["cyan"]))
    out.append("".join(c))
    return svg(W, h, css, "".join(out))
