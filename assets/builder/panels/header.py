"""Header panel: status bar, namemark, boot log and surveillance feed tile."""
from ..embedded import AVATAR_B64
from ..svgkit import corners, esc, led, svg, wrap
from ..theme import BC, BC2, C, W


def build_header():
    fw, fh = 300, 225           # surveillance feed tile (4:3)
    row_y = 176
    h = row_y + fh + 16
    css = (
        "@keyframes jitter{0%,93%,100%{transform:translateX(0)}"
        "94%{transform:translateX(-3px)}96%{transform:translateX(2px)}"
        "98%{transform:translateX(-1px)}}"
        ".nm{animation:jitter 7s steps(1) infinite;transform-box:fill-box}"
        "@keyframes roll{0%{transform:translateY(-14px)}"
        "100%{transform:translateY(" + str(fh) + "px)}}"
        ".track{animation:roll 9s linear infinite}"
    )
    b = []
    # status bar
    b.append('<text x="8" y="14" font-size="10" letter-spacing="1.5" fill="%s">'
             'NODE//rugbedbugg  ·  SIG:<tspan fill="%s">STRONG</tspan>'
             '  ·  198X MODE</text>' % (C["dim"], C["green"]))
    b.append(led(W - 116, 10))
    b.append('<text x="%s" y="14" font-size="10" letter-spacing="1.5" '
             'text-anchor="end" fill="%s">REC 00:37:12</text>'
             % (W - 8, C["red"]))
    b.append('<line x1="8" y1="24" x2="%s" y2="24" stroke="%s"/>' % (W - 8, BC2))

    cx = W / 2
    b.append('<text x="%s" y="52" font-size="10.5" letter-spacing="2.4" '
             'text-anchor="middle" fill="%s" opacity=".8">'
             '[ SYSTEM :: OXIDE TERMINAL PROFILE :: 198X MODE ]</text>'
             % (cx, C["cyan"]))
    # namemark with chromatic split
    nm = "&gt; Oxide 1-6"
    for dx, col, op in ((-2, C["red"], .5), (2, C["cyan"], .55)):
        b.append('<text class="nm" x="%s" y="108" font-size="54" '
                 'letter-spacing="6" text-anchor="middle" fill="%s" '
                 'opacity="%s">%s</text>' % (cx + dx, col, op, nm))
    b.append('<text class="nm" x="%s" y="108" font-size="54" letter-spacing="6" '
             'text-anchor="middle" fill="%s" filter="url(#glow)">'
             '<tspan fill="%s">&gt;</tspan> Oxide 1-6</text>'
             % (cx, C["bright"], C["dim"]))
    b.append('<text x="%s" y="130" font-size="11" letter-spacing=".9" '
             'text-anchor="middle" fill="%s">'
             '[ Oxide 1-6 // Arsenic 1-6 // rugbedbugg ]</text>'
             % (cx, C["dim"]))
    b.append('<text x="%s" y="152" font-size="13" letter-spacing="2.6" '
             'text-anchor="middle" fill="%s">Linux Ricer '
             '<tspan fill="%s">//</tspan> Terminal Purist</text>'
             % (cx, C["cyan"], C["purple"]))

    # ---- identity row: boot log (left) + surveillance feed (right) ----
    fx = W - 8 - fw
    fy = row_y
    # boot log (left column)
    bx = 8
    bw = fx - bx - 20
    fs = 11
    maxc = int(bw / (fs * 0.72))
    b.append('<rect x="%s" y="%s" width="2" height="%s" fill="%s"/>'
             % (bx, fy + 2, fh - 40, BC))
    tx = bx + 14
    y = fy + 14
    b.append('<text x="%s" y="%s" font-size="%s" fill="%s">'
             '<tspan fill="%s">Oxide 1-6 (@rugbedbugg)</tspan> — your local '
             'daft.</text>' % (tx, y, fs, C["text"], C["cyan"]))
    y += 16
    b.append('<text x="%s" y="%s" font-size="%s" fill="%s">Welcome to my '
             'GitHub!</text>' % (tx, y, fs, C["text"]))
    y += 22
    quote = ("“Once I told the computer to do something and it did it "
             "exactly how I told it to. It was then when I felt like a god.”")
    for ql in wrap(quote, maxc):
        b.append('<text x="%s" y="%s" font-size="%s" fill="%s">%s</text>'
                 % (tx, y, fs, C["purple"], esc(ql)))
        y += 16
    y += 6
    b.append('<text x="%s" y="%s" font-size="%s" fill="%s">That’s '
             '<tspan fill="%s">Linux</tspan> for you.</text>'
             % (tx, y, fs, C["text"], C["cyan"]))
    y += 22
    b.append('<text x="%s" y="%s" font-size="%s" fill="%s">TempleOS is '
             '<tspan fill="%s">the OS</tspan> sent to earth by god'
             '</text>' % (tx, y, fs, C["text"], C["bright"]))
    y += 16
    b.append('<text x="%s" y="%s" font-size="%s" fill="%s">himself. '
             '<tspan fill="%s">R.I.P. Terry Davis</tspan></text>'
             % (tx, y, fs, C["text"], C["orange"]))

    # surveillance feed (right column) — the dithered headshot, no subject box
    iy = fy + 4
    ih = fh - 4
    bar_cols = ["#ffffff", "#ffff55", "#55ffff", "#55ff55", "#ff55ff",
                "#ff5555", "#5555ff"]
    sw = fw / len(bar_cols)
    for i, col in enumerate(bar_cols):
        b.append('<rect x="%s" y="%s" width="%s" height="4" fill="%s"/>'
                 % (fx + i * sw, fy, sw + 1, col))
    b.append('<clipPath id="hfclip"><rect x="%s" y="%s" width="%s" height="%s"/>'
             '</clipPath>' % (fx, iy, fw, ih))
    b.append('<g clip-path="url(#hfclip)">')
    b.append('<image x="%s" y="%s" width="%s" height="%s" '
             'preserveAspectRatio="xMidYMid slice" '
             'href="data:image/png;base64,%s" '
             'style="image-rendering:pixelated;filter:contrast(1.12) '
             'brightness(.9) sepia(.2) hue-rotate(150deg) saturate(1.25)"/>'
             % (fx, iy, fw, ih, AVATAR_B64))
    b.append('<rect x="%s" y="%s" width="%s" height="%s" fill="url(#scan)" '
             'opacity=".4"/>' % (fx, iy, fw, ih))
    b.append('<rect class="track" x="%s" y="%s" width="%s" height="12" '
             'fill="#fff" opacity=".10"/>' % (fx, iy, fw))
    b.append('<rect x="%s" y="%s" width="%s" height="%s" fill="url(#vig)"/>'
             % (fx, iy, fw, ih))
    b.append('</g>')
    b.append('<rect x="%s" y="%s" width="%s" height="%s" fill="none" '
             'stroke="rgba(85,255,255,.4)" stroke-width="2"/>'
             % (fx, fy, fw, fh))
    # top OSD strip
    b.append('<rect x="%s" y="%s" width="%s" height="17" fill="rgba(0,0,0,.55)"/>'
             % (fx, iy, fw))
    b.append(led(fx + 9, iy + 8.5))
    b.append('<text x="%s" y="%s" font-size="8" letter-spacing="1.2" fill="%s">'
             'CH 03 · CAM-01</text>' % (fx + 19, iy + 12, C["cyan"]))
    b.append('<text x="%s" y="%s" font-size="8" letter-spacing="1.2" '
             'text-anchor="end" fill="%s">LIVE</text>'
             % (fx + fw - 8, iy + 12, C["red"]))
    # bottom OSD
    b.append('<rect x="%s" y="%s" width="%s" height="34" fill="url(#nmfade)"/>'
             % (fx, iy + ih - 34, fw))
    b.append('<text x="%s" y="%s" font-size="8" letter-spacing=".8" fill="%s">'
             'REC <tspan fill="%s">02:41:07:14</tspan></text>'
             % (fx + 8, iy + ih - 16, C["red"], C["cyan"]))
    b.append('<text x="%s" y="%s" font-size="8" letter-spacing=".8" fill="%s">'
             '◎ 12.911210, 79.132685</text>'
             % (fx + 8, iy + ih - 6, C["cyan"]))
    b.append(corners(fx, fy, fw, fh, s=11, inset=4))
    return svg(W, h, css, "".join(b), bg_on=False)
