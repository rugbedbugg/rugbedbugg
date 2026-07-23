#!/usr/bin/env python3
"""Generate the surveillance-console profile panels as self-contained animated SVGs.

Each panel embeds the Departure Mono font (and, for the monitor, the dithered
headshot) as base64 so the file renders identically anywhere GitHub serves it as
an <img>. CSS keyframe animations run inside <img>, so the feeds stay live.

Run:  python assets/build.py
"""
import base64
import os
import xml.dom.minidom as minidom

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- embedded assets -------------------------------------------------------
with open(os.path.join(HERE, "DepartureMono-Regular.woff2"), "rb") as f:
    FONT_B64 = base64.b64encode(f.read()).decode()
with open(os.path.join(HERE, "avatar-cga.png"), "rb") as f:
    AVATAR_B64 = base64.b64encode(f.read()).decode()

W = 780  # full panel width

# ---- palette ---------------------------------------------------------------
C = dict(
    ground="#050308", black="#000000", text="#aaaaaa", dim="#6f6478",
    gray="#8a8a8a", bright="#e6fbfb", cyan="#55ffff", cyand="#33aacc",
    green="#55ff55", red="#ff5555", yellow="#ffff55", purple="#c084fc",
    title="#d8b4fe", orange="#ffb454",
)
BC = "rgba(85,255,255,.30)"
BC2 = "rgba(85,255,255,.18)"
BCH = "rgba(85,255,255,.60)"

FONT_FACE = (
    "@font-face{font-family:'Departure Mono';"
    "src:url('data:font/woff2;base64,%s') format('woff2');font-display:swap}" % FONT_B64
)

# Shared CSS every panel starts with.
BASE_CSS = (
    FONT_FACE +
    "text,tspan{font-family:'Departure Mono',ui-monospace,Consolas,monospace;"
    "white-space:pre}"
    ".led{animation:blink 1.1s steps(1,end) infinite}"
    "@keyframes blink{0%,55%{opacity:1}56%,100%{opacity:.12}}"
)


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


def svg(w, h, extra_css, body):
    doc = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" '
        'viewBox="0 0 %s %s" font-family="\'Departure Mono\',monospace">'
        '%s<style>%s%s</style>%s%s</svg>'
        % (w, h, w, h, defs(), BASE_CSS, extra_css, bg(w, h), body)
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


# ===========================================================================
#  HEADER
# ===========================================================================
def build_header():
    h = 312
    css = (
        "@keyframes jitter{0%,93%,100%{transform:translateX(0)}"
        "94%{transform:translateX(-3px)}96%{transform:translateX(2px)}"
        "98%{transform:translateX(-1px)}}"
        ".nm{animation:jitter 7s steps(1) infinite;transform-box:fill-box}"
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

    # boot log box
    bx, bw, by = (W - 520) / 2, 520, 176
    b.append('<rect x="%s" y="%s" width="2" height="106" fill="%s"/>'
             % (bx, by, BC))
    tx = bx + 16
    lines = [
        ('<tspan fill="%s">Oxide 1-6 (@rugbedbugg)</tspan> — your local '
         'daft. Welcome to my GitHub!' % C["cyan"], C["text"]),
    ]
    y = by + 12
    fs = 12
    b.append('<text x="%s" y="%s" font-size="%s" fill="%s">%s</text>'
             % (tx, y, fs, lines[0][1], lines[0][0]))
    y += 22
    quote = ("“Once I told the computer to do something and it did it "
             "exactly how I told it to. It was then when I felt like a god.”")
    for ql in wrap(quote, 64):
        b.append('<text x="%s" y="%s" font-size="%s" fill="%s">%s</text>'
                 % (tx, y, fs, C["purple"], esc(ql)))
        y += 18
    y += 4
    b.append('<text x="%s" y="%s" font-size="%s" fill="%s">That’s '
             '<tspan fill="%s">Linux</tspan> for you.</text>'
             % (tx, y, fs, C["text"], C["cyan"]))
    y += 20
    b.append('<text x="%s" y="%s" font-size="%s" fill="%s">TempleOS is '
             '<tspan fill="%s">the OS</tspan> sent to earth by god himself. '
             '<tspan fill="%s">R.I.P. Terry Davis</tspan></text>'
             % (tx, y, fs, C["text"], C["bright"], C["orange"]))
    return svg(W, h, css, "".join(b))


# ===========================================================================
#  MONITOR (hero)
# ===========================================================================
def build_monitor():
    pad = 14
    ix = pad
    iw = W - 2 * pad
    tt_w = 210
    gap = 12
    feed_w = iw - tt_w - gap
    feed_h = round(feed_w * 3 / 4)
    head_h = 26
    bars_y = pad + head_h + 6
    body_y = bars_y + 12
    foot_y = body_y + feed_h + 16
    h = foot_y + 20

    css = (
        "@keyframes roll{0%{transform:translateY(-14px)}"
        "100%{transform:translateY(" + str(feed_h + 4) + "px)}}"
        ".track{animation:roll 9s linear infinite}"
    )
    b = []
    b.append('<rect x="2" y="2" width="%s" height="%s" fill="#000" '
             'stroke="%s" stroke-width="2"/>' % (W - 4, h - 4, "rgba(85,255,255,.4)"))
    # monhead
    hy = pad
    b.append('<rect x="%s" y="%s" width="%s" height="%s" '
             'fill="rgba(85,255,255,.06)" stroke="%s"/>'
             % (ix, hy, iw, head_h, BC))
    b.append(led(ix + 10, hy + head_h / 2))
    b.append('<text x="%s" y="%s" font-size="9.5" letter-spacing="1.6" '
             'fill="%s">[LIVE] · 480i</text>'
             % (ix + 24, hy + 16.5, C["red"]))
    b.append('<text x="%s" y="%s" font-size="9.5" letter-spacing="1.6" '
             'text-anchor="middle" fill="%s">MEMORY REBOOT — VØJ '
             '(SLOWED)</text>' % (W / 2, hy + 16.5, C["gray"]))
    b.append('<text x="%s" y="%s" font-size="9.5" letter-spacing="1.6" '
             'text-anchor="end" fill="%s">02:41:07</text>'
             % (ix + iw - 8, hy + 16.5, C["cyan"]))
    # SMPTE bars
    bar_cols = ["#ffffff", "#ffff55", "#55ffff", "#55ff55", "#ff55ff",
                "#ff5555", "#5555ff"]
    bw = iw / len(bar_cols)
    for i, col in enumerate(bar_cols):
        b.append('<rect x="%s" y="%s" width="%s" height="5" fill="%s"/>'
                 % (ix + i * bw, bars_y, bw + 1, col))
    # feed
    fx, fy = ix, body_y
    b.append('<clipPath id="fclip"><rect x="%s" y="%s" width="%s" height="%s"/>'
             '</clipPath>' % (fx, fy, feed_w, feed_h))
    b.append('<g clip-path="url(#fclip)">')
    b.append('<image x="%s" y="%s" width="%s" height="%s" '
             'preserveAspectRatio="xMidYMid slice" '
             'href="data:image/png;base64,%s" '
             'style="image-rendering:pixelated;filter:contrast(1.12) '
             'brightness(.9) sepia(.2) hue-rotate(150deg) saturate(1.25)"/>'
             % (fx, fy, feed_w, feed_h, AVATAR_B64))
    b.append('<rect x="%s" y="%s" width="%s" height="%s" fill="url(#scan)" '
             'opacity=".4"/>' % (fx, fy, feed_w, feed_h))
    b.append('<rect class="track" x="%s" y="%s" width="%s" height="12" '
             'fill="#fff" opacity=".10"/>' % (fx, fy, feed_w))
    b.append('<rect x="%s" y="%s" width="%s" height="%s" fill="url(#vig)"/>'
             % (fx, fy, feed_w, feed_h))
    b.append('</g>')
    b.append('<rect x="%s" y="%s" width="%s" height="%s" fill="none" '
             'stroke="%s"/>' % (fx, fy, feed_w, feed_h, BC))
    # OSD rec
    b.append('<rect x="%s" y="%s" width="128" height="14" fill="rgba(0,0,0,.6)"/>'
             % (fx + 6, fy + 6))
    b.append(led(fx + 14, fy + 13))
    b.append('<text x="%s" y="%s" font-size="8" letter-spacing=".8" fill="%s">'
             'REC <tspan fill="%s">02:41:07:14</tspan></text>'
             % (fx + 24, fy + 16.5, C["red"], C["cyan"]))
    # OSD channel
    b.append('<text x="%s" y="%s" font-size="8" letter-spacing="1.4" '
             'text-anchor="end" fill="%s">CH 03 · CAM-01 LIVE</text>'
             % (fx + feed_w - 8, fy + 16.5, C["cyan"]))
    # OSD geo
    b.append('<text x="%s" y="%s" font-size="8" letter-spacing=".8" fill="%s">'
             'THU 23 JUL 2026 <tspan fill="%s">LCL</tspan> 02:41:07</text>'
             % (fx + 8, fy + feed_h - 18, "#ddffee", C["cyan"]))
    b.append('<text x="%s" y="%s" font-size="8" letter-spacing=".8" fill="%s">'
             '◎ 12.911210, 79.132685</text>'
             % (fx + 8, fy + feed_h - 8, C["cyan"]))
    b.append(corners(fx, fy, feed_w, feed_h, s=12, inset=4))
    # teletext
    tx = ix + feed_w + gap
    tt = [("SUBJECT FILE :: CH 04", C["yellow"]),
          ("--------------------", BC2)]
    rows = [("ID     : ", "OXIDE 1-6", C["bright"]),
            ("CLASS  : ", "LINUX RICER", C["cyan"]),
            ("WM     : ", "HYPRLAND", C["cyan"]),
            ("SHELL  : ", "CAELESTIA", C["cyan"]),
            ("STATUS : ", "RICED", C["green"]),
            ("LOC    : ", "12°54'40\"N 79°07'57\"E", C["cyan"])]
    tt_h = 20 + (len(tt) + len(rows)) * 20
    b.append('<rect x="%s" y="%s" width="%s" height="%s" '
             'fill="rgba(85,255,255,.04)" stroke="%s"/>'
             % (tx, fy, tt_w, tt_h, BC2))
    ty = fy + 22
    for txt, col in tt:
        b.append('<text x="%s" y="%s" font-size="10" letter-spacing=".8" '
                 'fill="%s">%s</text>' % (tx + 13, ty, col, esc(txt)))
        ty += 20
    for lbl, val, col in rows:
        b.append('<text x="%s" y="%s" font-size="10" letter-spacing=".8" '
                 'fill="%s">%s<tspan fill="%s">%s</tspan></text>'
                 % (tx + 13, ty, C["cyan"], esc(lbl), col, esc(val)))
        ty += 20
    # footer
    b.append('<text x="%s" y="%s" font-size="9.5" letter-spacing="1.6" '
             'fill="%s">● REC · PLAYBACK</text>'
             % (ix, foot_y, C["cyan"]))
    b.append('<text x="%s" y="%s" font-size="9.5" letter-spacing="1.6" '
             'text-anchor="end" fill="%s">SECURITY TAPE · SP 60FPS</text>'
             % (ix + iw, foot_y, C["cyand"]))
    return svg(W, h, css, "".join(b))


# ===========================================================================
#  DOSSIER
# ===========================================================================
def build_dossier():
    rows = [
        ("SUBJECT", [("Oxide 1-6 — ", C["bright"]),
                     ("@rugbedbugg", C["cyan"])]),
        ("ALTER EGO", [("Arsenic 1-6 — ", C["bright"]),
                       ("@mystik-krysat", C["cyan"])]),
        ("CLASS", [("Linux Power-User", C["purple"])]),
        ("RIG", [("Arch btw", C["cyan"]),
                 (" · Caelestia · Hyprland", C["bright"])]),
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


# ===========================================================================
#  LOADOUT
# ===========================================================================
def build_loadout():
    def chips(items, y, lang=False):
        border = "rgba(192,132,252,.4)" if lang else BC2
        fillbg = "rgba(168,85,247,.07)" if lang else "rgba(85,255,255,.04)"
        txtcol = C["title"] if lang else C["text"]
        x = 22
        out = []
        for it in items:
            wc = len(it) * cw(11) + 20
            out.append('<rect x="%s" y="%s" width="%s" height="24" fill="%s" '
                       'stroke="%s"/>' % (x, y, round(wc), fillbg, border))
            out.append('<text x="%s" y="%s" font-size="11" letter-spacing=".6" '
                       'fill="%s">%s</text>'
                       % (x + 10, y + 16, txtcol, esc(it.upper())))
            x += wc + 7
        return "".join(out)

    body_y = 44
    h = body_y + 150
    b = [panel_frame(h, "DAILY LOADOUT", "REF://LOADOUT.CFG")]
    b.append('<text x="22" y="%s" font-size="10" letter-spacing="1.4" '
             'fill="%s">WORKFLOW</text>' % (body_y + 14, C["dim"]))
    b.append(chips(["ChatGPT", "LibreOffice", "Ollama", "Zed", "OpenClaw"],
                   body_y + 24))
    b.append('<text x="22" y="%s" font-size="10" letter-spacing="1.4" '
             'fill="%s">LANGUAGES</text>' % (body_y + 78, C["dim"]))
    b.append(chips(["Rust", "C", "C++", "Python", "Java", "Assembly", "Bash"],
                   body_y + 88, lang=True))
    return svg(W, h, "", "".join(b))


# ===========================================================================
#  SOCIAL FEEDS (6 clickable tiles)
# ===========================================================================
FW, FH = 244, 183  # feed tile size (4:3)


def feed_icon(kind, x, y):
    a = ('<g transform="translate(%s,%s) scale(.6)" fill="none" stroke="%s" '
         'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
         % (x, y, C["cyan"]))
    p = {
        "mail": '<rect x="2.5" y="4.5" width="19" height="15"/><path d="M3 6l9 6.5L21 6"/>',
        "linkedin": '<rect x="2.5" y="2.5" width="19" height="19"/><path d="M7 10v7M7 7v.01M11 17v-4a2 2 0 0 1 4 0v4M11 17v-7"/>',
        "instagram": '<rect x="3" y="3" width="18" height="18"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.2" cy="6.8" r=".9" fill="%s"/>' % C["cyan"],
        "youtube": '<rect x="2.5" y="6" width="19" height="12"/><path d="M10.5 9.2l4.5 2.8-4.5 2.8z" fill="%s" stroke="none"/>' % C["cyan"],
        "discord": '<path d="M7 8.5c3-1.4 7-1.4 10 0M6.5 16.5c3.2 1.6 7.8 1.6 11 0M6.5 16.5C5 14 4.7 11 5.8 8.2 7 7.3 8.4 6.9 9 6.8M17.5 16.5c1.5-2.5 1.8-5.5.7-8.3-1.2-.9-2.6-1.3-3.2-1.4"/><path d="M9.5 13v.01M14.5 13v.01" stroke-width="2.3"/>',
        "github": '<path d="M4 7l4 4-4 4M11 16h7"/>',
    }[kind]
    return a + p + '</g>'


def fx_github():
    L = ['$ git push origin main', 'Enumerating: 24, done', 'Compressing 100%',
         'Writing objects 100%', 'a1f4e HEAD -> main', '$ git commit -am fix',
         '[main 9c2b7] patch', '2 files changed, +48']
    lh = 14
    seth = len(L) * lh
    rows = []
    for rep in range(2):
        for i, t in enumerate(L):
            col = C["cyan"] if ('HEAD' in t or ']' in t) else C["green"]
            rows.append('<text x="9" y="%s" font-size="8" fill="%s">%s</text>'
                        % (rep * seth + (i + 1) * lh, col, esc(t)))
    css = ("@keyframes vroll{from{transform:translateY(0)}"
           "to{transform:translateY(-%dpx)}}"
           ".rl{animation:vroll 5s linear infinite}" % seth)
    inner = ('<g class="rl">%s</g>' % "".join(rows))
    return css, inner


def fx_scroll(color, round_av):
    rowh = 18
    n = 6
    seth = n * rowh
    rc = "5.5" if round_av else "0"
    rows = []
    for rep in range(2):
        for i in range(n):
            yy = rep * seth + i * rowh + 8
            rows.append('<rect x="8" y="%s" width="11" height="11" rx="%s" '
                        'fill="%s"/>' % (yy, rc, color))
            rows.append('<rect x="24" y="%s" width="88%%" height="3" fill="%s" '
                        'opacity=".5"/>' % (yy + 1, color))
            rows.append('<rect x="24" y="%s" width="56%%" height="3" fill="%s" '
                        'opacity=".5"/>' % (yy + 6, color))
    css = ("@keyframes vroll{from{transform:translateY(0)}"
           "to{transform:translateY(-%dpx)}}"
           ".rl{animation:vroll 5.5s linear infinite}" % seth)
    return css, '<g class="rl">%s</g>' % "".join(rows)


def fx_insta():
    cells = []
    css = ("@keyframes igflk{0%,100%{opacity:.4}50%{opacity:.95}}"
           ".ig i{animation:igflk 3s ease-in-out infinite}")
    gw = (FW - 8) / 3
    gh = (FH - 8) / 3
    grads = []
    out = ['<g class="ig">']
    for i in range(9):
        hh = (i * 40) % 360
        gid = "ig%d" % i
        grads.append('<linearGradient id="%s" x1="0" y1="0" x2="1" y2="1">'
                     '<stop offset="0" stop-color="hsl(%d,75%%,58%%)"/>'
                     '<stop offset="1" stop-color="hsl(%d,75%%,46%%)"/>'
                     '</linearGradient>' % (gid, hh, (hh + 50) % 360))
        cx = 3 + (i % 3) * gw
        cy = 3 + (i // 3) * gh
        out.append('<rect x="%s" y="%s" width="%s" height="%s" fill="url(#%s)" '
                   'style="animation-delay:%.2fs"/>'
                   % (cx, cy, gw - 2, gh - 2, gid, i * 0.22))
    out.append('</g>')
    return css, '<defs>%s</defs>%s' % ("".join(grads), "".join(out))


def fx_youtube():
    cx = FW / 2
    css = ("@keyframes eq{from{height:3px}to{height:20px}}"
           ".eq i{animation:eq .8s ease-in-out infinite alternate}"
           "@keyframes ytfill{from{width:4px}to{width:120px}}"
           ".ytf{animation:ytfill 4s linear infinite}")
    out = []
    out.append('<path d="M%s %s l16 9 l-16 9 z" fill="%s"/>'
               % (cx - 8, FH / 2 - 34, C["red"]))
    bx = cx - 27
    for i in range(9):
        out.append('<rect class="i" x="%s" y="%s" width="3" height="20" '
                   'fill="%s" style="transform-box:fill-box;'
                   'transform-origin:bottom;animation-delay:%.2fs"/>'
                   % (bx + i * 6, FH / 2 - 8, C["red"], i * 0.07))
    barw = FW * 0.7
    out.append('<rect x="%s" y="%s" width="%s" height="4" '
               'fill="rgba(255,255,255,.18)"/>'
               % (cx - barw / 2, FH / 2 + 26, barw))
    out.append('<clipPath id="ytc"><rect x="%s" y="%s" width="%s" height="4"/>'
               '</clipPath>' % (cx - barw / 2, FH / 2 + 26, barw))
    out.append('<rect class="ytf" clip-path="url(#ytc)" x="%s" y="%s" '
               'height="4" fill="%s"/>' % (cx - barw / 2, FH / 2 + 26, C["red"]))
    return css, "".join(out)


def fx_linkedin():
    edges = [[50, 40, 18, 16], [50, 40, 82, 18], [50, 40, 16, 64],
             [50, 40, 84, 62], [50, 40, 50, 10], [18, 16, 50, 10],
             [82, 18, 84, 62]]
    nodes = [[50, 40, True], [18, 16, False], [82, 18, False], [16, 64, False],
             [84, 62, False], [50, 10, False]]
    css = ("@keyframes lidash{to{stroke-dashoffset:-8}}"
           ".edge{animation:lidash 1.6s linear infinite}"
           "@keyframes linode{0%,100%{opacity:.6}50%{opacity:1}}"
           ".node{animation:linode 2.4s ease-in-out infinite}")
    sc = 'scale(%f,%f)' % (FW / 100.0, FH / 80.0)
    out = ['<g transform="%s">' % sc]
    for g in edges:
        out.append('<line class="edge" x1="%s" y1="%s" x2="%s" y2="%s" '
                   'stroke="#4d9fff" stroke-width=".7" opacity=".55" '
                   'stroke-dasharray="4 4"/>' % tuple(g))
    for i, g in enumerate(nodes):
        col = C["cyan"] if g[2] else "#7cc2ff"
        r = 3.4 if g[2] else 2.6
        out.append('<circle class="node" cx="%s" cy="%s" r="%s" fill="%s" '
                   'style="animation-delay:%.2fs"/>' % (g[0], g[1], r, col, i * 0.3))
    out.append('</g>')
    return css, "".join(out)


def fx_discord():
    avs = ["#5865f2", "#57f287", "#eb459e", "#fee75c"]
    css = ("@keyframes dcpop{0%{opacity:0}12%,82%{opacity:1}100%{opacity:.12}}"
           ".msg{animation:dcpop 4.5s ease-out infinite}"
           "@keyframes tping{0%,60%,100%{opacity:.3}30%{opacity:1}}"
           ".tp{animation:tping 1.2s infinite}")
    out = []
    for i in range(4):
        yy = 14 + i * 26
        out.append('<g class="msg" style="animation-delay:%.2fs">' % (i * 0.55))
        out.append('<circle cx="14" cy="%s" r="5.5" fill="%s"/>'
                   % (yy, avs[i % 4]))
        out.append('<rect x="24" y="%s" width="42%%" height="3" fill="#b3a4ff"/>'
                   % (yy - 5))
        out.append('<rect x="24" y="%s" width="%s%%" height="3" fill="#7d7da8"/>'
                   % (yy, 58 + (i * 17) % 34))
        out.append('</g>')
    ty = 14 + 4 * 26
    out.append('<circle cx="14" cy="%s" r="5.5" fill="#5865f2"/>' % ty)
    for j in range(3):
        out.append('<circle class="tp" cx="%s" cy="%s" r="2" fill="#b3a4ff" '
                   'style="animation-delay:%.2fs"/>'
                   % (26 + j * 8, ty, j * 0.2))
    return css, "".join(out)


SOCIALS = [
    ("GitHub", "rugbedbugg", "CAM-01", "github", fx_github),
    ("LinkedIn", "partha-gogoi", "CAM-02", "linkedin", fx_linkedin),
    ("Email", "yes.par781", "CAM-03", "mail", lambda: fx_scroll("#7fe3d0", False)),
    ("Instagram", "_boyin_paradise", "CAM-04", "instagram", fx_insta),
    ("YouTube", "@rknif781", "CAM-05", "youtube", fx_youtube),
    ("Discord", "oxide 1-6", "CAM-06", "discord", fx_discord),
]


def build_feed(name, handle, cam, icon, fxfn):
    css_fx, inner = fxfn()
    css = ("@keyframes snow{0%{transform:translate(0,0)}"
           "100%{transform:translate(-14px,-9px)}}" + css_fx)
    b = []
    b.append('<rect width="%s" height="%s" fill="#020104"/>' % (FW, FH))
    b.append('<clipPath id="fc"><rect width="%s" height="%s"/></clipPath>' % (FW, FH))
    b.append('<g clip-path="url(#fc)">%s</g>' % inner)
    b.append('<rect width="%s" height="%s" fill="url(#scan)" opacity=".28"/>'
             % (FW, FH))
    # bottom name gradient
    b.append('<rect x="0" y="%s" width="%s" height="40" fill="url(#nmfade)"/>'
             % (FH - 40, FW))
    b.append(feed_icon(icon, 8, FH - 24))
    b.append('<text x="26" y="%s" font-size="11.5" letter-spacing=".5" '
             'fill="%s">%s</text>' % (FH - 14, C["bright"], esc(name.upper())))
    b.append('<text x="26" y="%s" font-size="9" fill="%s">%s</text>'
             % (FH - 5, C["cyan"], esc(handle)))
    b.append('<text x="%s" y="%s" font-size="8.5" letter-spacing="1.4" '
             'text-anchor="end" fill="%s">CONNECT ▶</text>'
             % (FW - 8, FH - 8, C["cyan"]))
    # cam / live (dark strip keeps labels legible over the animated feed)
    b.append('<rect x="0" y="0" width="%s" height="19" fill="rgba(0,0,0,.55)"/>'
             % FW)
    b.append('<text x="7" y="13" font-size="8" letter-spacing="1.2" fill="%s">'
             '%s</text>' % (C["cyan"], cam))
    b.append(led(FW - 34, 10))
    b.append('<text x="%s" y="13" font-size="8" text-anchor="end" fill="%s">'
             'LIVE</text>' % (FW - 8, C["red"]))
    b.append(corners(0, 0, FW, FH, col=BCH, s=10, inset=4))
    b.append('<rect x=".5" y=".5" width="%s" height="%s" fill="none" '
             'stroke="%s"/>' % (FW - 1, FH - 1, BC2))
    return svg(FW, FH, css, "".join(b))


# ===========================================================================
#  TRANSMISSION
# ===========================================================================
def build_transmission():
    quotes = ["Talk is cheap. Show me the code.",
              "Simplicity is prerequisite for reliability.",
              "Given enough eyeballs, all bugs are shallow.",
              "First, solve the problem. Then, write the code.",
              "Programs must be written for people to read."]
    body_y = 44
    h = body_y + 168
    b = [panel_frame(h, "TRANSMISSION", "REF://QUOTES.LOG")]
    n = len(quotes)
    dur = n * 2.6
    # cycling quote (stacked, opacity keyframes)
    css = []
    y1 = body_y + 22
    b.append('<text x="22" y="%s" font-size="10.5" letter-spacing="1.4" '
             'fill="%s">INCOMING · SENSIBLE WORDS</text>'
             % (body_y + 4, C["cyan"]))
    b.append('<rect x="22" y="%s" width="2" height="20" fill="%s"/>'
             % (y1 - 14, C["cyan"]))
    step = 100.0 / n
    for i, q in enumerate(quotes):
        a = i * step
        vis1, vis2 = a + step * 0.08, a + step * 0.92
        nb = ((i + 1) % n) * step
        kf = ("@keyframes q%d{0%%{opacity:0}%.1f%%{opacity:0}%.1f%%{opacity:1}"
              "%.1f%%{opacity:1}%.1f%%{opacity:0}100%%{opacity:0}}"
              % (i, max(a - 1, 0), vis1, vis2, nb))
        css.append(kf)
        b.append('<text x="34" y="%s" font-size="14" fill="%s" opacity="0" '
                 'style="animation:q%d %.1fs linear infinite">“%s”'
                 '</text>' % (y1, C["bright"], i, dur, esc(q)))
    b.append('<text x="34" y="%s" font-size="11" fill="%s">— auto-rotated '
             'on every load</text>' % (y1 + 18, C["dim"]))
    # custom quote
    y2 = y1 + 62
    b.append('<text x="22" y="%s" font-size="10.5" letter-spacing="1.4" '
             'fill="%s">OPERATIVE LOG · CUSTOM</text>' % (y2, C["cyan"]))
    b.append('<rect x="22" y="%s" width="2" height="40" fill="%s"/>'
             % (y2 + 10, C["purple"]))
    b.append('<text x="34" y="%s" font-size="14" fill="%s">“Linux is not '
             'an OS, it’s a lifestyle: best lived in the terminal.”'
             '</text>' % (y2 + 26, C["title"]))
    b.append('<text x="34" y="%s" font-size="11" fill="%s">— Oxide 1-6'
             '</text>' % (y2 + 44, C["dim"]))
    return svg(W, h, "".join(css), "".join(b))


# ===========================================================================
#  SECTION LABEL STRIPS (for telemetry card + field-recording video)
# ===========================================================================
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


# ===========================================================================
#  FOOTER
# ===========================================================================
def build_footer():
    h = 60
    b = []
    b.append('<line x1="0" y1="14" x2="%s" y2="14" stroke="%s"/>' % (W, BC2))
    b.append('<text x="%s" y="30" font-size="10" letter-spacing="2" '
             'text-anchor="middle" fill="%s">// end of transmission · '
             'oxide 1-6 · arch btw //</text>' % (W / 2, C["dim"]))
    b.append('<text x="%s" y="48" font-size="10" letter-spacing="1.4" '
             'text-anchor="middle" fill="%s">[ <tspan fill="%s">●</tspan> '
             'NEW SUBJECT · TRACE INITIATED ]</text>'
             % (W / 2, C["gray"], C["red"]))
    return svg(W, h, "", "".join(b))


# ===========================================================================
def write(name, content):
    path = os.path.join(HERE, name)
    minidom.parseString(content)  # well-formedness check
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  ok  %-22s %6d bytes" % (name, len(content)))


def main():
    write("header.svg", build_header())
    write("monitor.svg", build_monitor())
    write("dossier.svg", build_dossier())
    write("loadout.svg", build_loadout())
    write("transmission.svg", build_transmission())
    write("label-telemetry.svg", build_label("TELEMETRY", "REF://METRICS.SYS"))
    write("label-uplink.svg", build_label("ESTABLISH UPLINK", "REF://CONTACT.SYS"))
    write("label-field.svg", build_label("FIELD RECORDING", "REF://RICINGS.VHS"))
    write("footer.svg", build_footer())
    for name, handle, cam, icon, fxfn in SOCIALS:
        write("feed-%s.svg" % name.lower(),
              build_feed(name, handle, cam, icon, fxfn))
    print("done.")


if __name__ == "__main__":
    main()
