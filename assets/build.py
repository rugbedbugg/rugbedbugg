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


# ===========================================================================
#  HEADER
# ===========================================================================
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
    b.append(corners(fx, fy, fw, fh, col=BCH, s=11, inset=4))
    return svg(W, h, css, "".join(b), bg_on=False)


# ===========================================================================
#  DOSSIER
# ===========================================================================
def build_dossier():
    rows = [
        ("SUBJECT", [("Oxide 1-6 — ", C["bright"]),
                     ("@rugbedbugg", C["cyan"])]),
        ("ALTER EGO", [("Arsenic 1-6 — ", C["bright"]),
                       ("@mystik-krysat", C["cyan"])]),
        ("CLASS", [("Linux/Windows Power-User", C["purple"])]),
        ("RIG", [("Arch btw", C["cyan"]),
                 (" · Caelestia · Hyprland ", C["bright"]),
                 ("| ", C["dim"]),
                 ("Windows", C["cyan"]),
                 (" · WSL · Powershell", C["bright"])]),
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
    b.append(chips(["Sublime Text", "Ollama", "OpenClaw", "FreeFileSync",
                    "RealTimeSync", "PowerShell"],
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
    b.append(feed_icon(icon, 8, FH - 21))
    b.append('<text x="27" y="%s" font-size="12" letter-spacing=".6" '
             'fill="%s">%s</text>' % (FH - 11, C["bright"], esc(name.upper())))
    b.append('<text x="%s" y="%s" font-size="8.5" letter-spacing="1.4" '
             'text-anchor="end" fill="%s">CONNECT ▶</text>'
             % (FW - 8, FH - 11, C["cyan"]))
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


# ===========================================================================
#  TELEMETRY — live stats, colorblind languages, 2D calendar (self-hosted)
# ===========================================================================
USER = "rugbedbugg"
SKIP_REPOS = {"portfolio-website", "ML_SchoolAssignments"}
# Okabe-Ito colorblind-safe categorical palette, assigned by language rank.
LANG_COLORS = ["#56b4e9", "#e69f00", "#d55e00", "#cc79a7",
               "#009e73", "#f0e442", "#0072b2", "#dddddd"]
CAL_SHADES = ["rgba(85,255,255,.10)", "rgba(85,255,255,.28)",
              "rgba(85,255,255,.50)", "rgba(85,255,255,.72)", "#55ff55"]
# Fallbacks (snapshot fetched 2026-07-24) used when offline / rate-limited.
FB_STATS = {"repos": 21, "stars": 41, "followers": 23, "following": 17}
FB_LANGS = [("Python", 61.3), ("Assembly", 13.4), ("Rust", 11.7),
            ("C++", 6.1), ("Java", 4.7), ("Lua", 1.4), ("Shell", 1.1)]


def _get(url):
    import os
    import json
    import urllib.request
    headers = {"User-Agent": "oxide-build"}
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        headers["Authorization"] = "Bearer " + tok
    req = urllib.request.Request(url, headers=headers)
    return json.load(urllib.request.urlopen(req, timeout=15))


def fetch_stats():
    try:
        u = _get("https://api.github.com/users/%s" % USER)
        repos, page = [], 1
        while True:
            chunk = _get("https://api.github.com/users/%s/repos"
                         "?per_page=100&page=%d" % (USER, page))
            repos += chunk
            if len(chunk) < 100:
                break
            page += 1
        stars = sum(r["stargazers_count"] for r in repos)
        return ({"repos": u["public_repos"], "stars": stars,
                 "followers": u["followers"], "following": u["following"]}, repos)
    except Exception as e:
        print("  ..stats fetch failed (%s) -> fallback" % e)
        return dict(FB_STATS), None


def fetch_langs(repos):
    import collections
    if repos is None:
        return list(FB_LANGS)
    try:
        agg = collections.Counter()
        for r in repos:
            if r["name"] in SKIP_REPOS or r.get("fork"):
                continue
            for k, v in _get(r["languages_url"]).items():
                agg[k] += v
        tot = sum(agg.values()) or 1
        return [(k, round(100.0 * v / tot, 1)) for k, v in agg.most_common(7)]
    except Exception as e:
        print("  ..langs fetch failed (%s) -> fallback" % e)
        return list(FB_LANGS)


def fetch_calendar():
    import re
    import random
    import urllib.request
    try:
        req = urllib.request.Request(
            "https://github.com/users/%s/contributions" % USER,
            headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=15).read().decode()
        lv = [int(x) for x in re.findall(r'data-level="(\d)"', html)]
        if lv:
            return lv
        raise ValueError("no cells")
    except Exception as e:
        print("  ..calendar fetch failed (%s) -> generated" % e)
        random.seed(7)
        out = []
        for _ in range(53 * 7):
            r = random.random()
            out.append(4 if r > .93 else 3 if r > .82 else
                       2 if r > .62 else 1 if r > .4 else 0)
        return out


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


# ===========================================================================
#  SECTION LABEL STRIPS (for the field-recording video)
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
#  FIELD RECORDING — VHS still (clickable; replaces the native video chrome)
# ===========================================================================
def build_field():
    h = round(W * 9 / 16)
    pad, gap = 14, 8
    iw, ih = W - 2 * pad, h - 2 * pad
    lw = round(iw * 0.5)
    rx = pad + lw + gap
    rw = W - pad - rx
    ph = (ih - gap) / 2
    css = ("@keyframes roll{0%{transform:translateY(-20px)}"
           "100%{transform:translateY(" + str(h) + "px)}}"
           ".trk{animation:roll 6s linear infinite}"
           "@keyframes pulse{0%,100%{opacity:.8}50%{opacity:1}}"
           ".play{animation:pulse 2.5s ease-in-out infinite}")
    b = ['<rect width="%s" height="%s" fill="#0b0e14"/>' % (W, h)]

    def pane(x, y, w, hh, lines):
        s = ('<rect x="%s" y="%s" width="%s" height="%s" fill="rgba(10,7,16,.6)" '
             'stroke="%s"/>' % (x, y, w, hh, BC2))
        s += ('<rect x="%s" y="%s" width="%s" height="10" fill="#0c1418"/>'
              % (x, y, w))
        ty = y + 23
        for txt, col in lines:
            s += ('<text x="%s" y="%s" font-size="9" fill="%s">%s</text>'
                  % (x + 6, ty, col, esc(txt)))
            ty += 13
        return s

    b.append('<g opacity="0.55">')
    b.append(pane(pad, pad, lw, ih, [
        ("~/.config/hypr $ hyprctl", C["cyan"]),
        ("workspace 1 :: caelestia", C["purple"]),
        ("████░░░ 88%", C["green"]), ("> neofetch", C["dim"])]))
    b.append(pane(rx, pad, rw, ph, [
        ("btop", C["cyan"]), ("cpu ███░", C["green"]), ("mem ██░░", C["green"])]))
    b.append(pane(rx, pad + ph + gap, rw, ph, [
        ("cava", C["purple"]), ("▍▁▏▍▂▁▏", C["cyan"]), ("▏▍▂▏▎▍", C["cyan"])]))
    b.append('</g>')
    b.append('<rect width="%s" height="%s" fill="url(#scan)" opacity=".25"/>'
             % (W, h))
    b.append('<rect class="trk" x="0" y="0" width="%s" height="20" fill="#fff" '
             'opacity=".05"/>' % W)
    b.append('<rect width="%s" height="%s" fill="url(#vig)"/>' % (W, h))
    cx, cy = W / 2, h / 2
    b.append('<g class="play">')
    b.append('<rect x="%s" y="%s" width="56" height="56" '
             'fill="rgba(85,255,255,.08)" stroke="%s"/>' % (cx - 28, cy - 28, C["cyan"]))
    b.append('<path d="M%s %s l18 11 l-18 11 z" fill="%s" filter="url(#glow)"/>'
             % (cx - 6, cy - 11, C["cyan"]))
    b.append('</g>')
    b.append('<text x="14" y="26" font-size="11" fill="%s">'
             '“If it isn’t riced, it isn’t mine.”</text>' % C["purple"])
    b.append(led(W - 70, 20))
    b.append('<text x="%s" y="26" font-size="11" letter-spacing="1" '
             'text-anchor="end" fill="%s">REC</text>' % (W - 14, C["red"]))
    b.append('<text x="14" y="%s" font-size="11" letter-spacing="1.2" fill="%s">'
             'CAELESTIA // HYPRLAND</text>' % (h - 14, C["cyan"]))
    b.append('<text x="%s" y="%s" font-size="11" letter-spacing="1" '
             'text-anchor="end" fill="%s">SP · 60FPS · 00:00:37</text>'
             % (W - 14, h - 14, C["dim"]))
    b.append(corners(0, 0, W, h, col=BCH, s=14, inset=6))
    b.append('<rect x="1" y="1" width="%s" height="%s" fill="none" stroke="%s"/>'
             % (W - 2, h - 2, BC))
    return svg(W, h, css, "".join(b))


# ===========================================================================
def write(name, content):
    path = os.path.join(HERE, name)
    minidom.parseString(content)  # well-formedness check
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  ok  %-22s %6d bytes" % (name, len(content)))


QUOTES = ["Talk is cheap. Show me the code.",
          "Simplicity is prerequisite for reliability.",
          "Given enough eyeballs, all bugs are shallow.",
          "First, solve the problem. Then, write the code.",
          "Programs must be written for people to read.",
          "Linux is not an OS, it’s a lifestyle: best lived in the terminal.",
          "The computer does exactly what you tell it to. That is the terror.",
          "Weeks of coding can save you hours of planning."]


def fetch_quote():
    # Pull a random programming quote from the internet each build; fall back
    # to the built-in list if the source or network is unavailable.
    import random
    try:
        data = _get("https://raw.githubusercontent.com/skolakoda/"
                    "programming-quotes-api/master/data/quotes.json")
        picks = [q["text"].strip() for q in data
                 if q.get("text") and 20 <= len(q["text"].strip()) <= 150]
        if picks:
            return random.choice(picks)
    except Exception as e:
        print("  ..quote fetch failed (%s) -> fallback" % e)
    return random.choice(QUOTES)


def main():
    print("fetching live profile data...")
    stats, repos = fetch_stats()
    langs = fetch_langs(repos)
    cal = fetch_calendar()
    print("  stats=%s  langs=%d  cal_cells=%d"
          % (stats, len(langs), len(cal)))
    write("header.svg", build_header())
    write("dossier.svg", build_dossier())
    write("telemetry.svg", build_telemetry(stats, langs, cal))
    write("loadout.svg", build_loadout())
    write("transmission.svg", build_transmission(fetch_quote()))
    write("label-uplink.svg", build_label("ESTABLISH UPLINK", "REF://CONTACT.SYS"))
    write("label-field.svg", build_label("FIELD RECORDING", "REF://RICINGS.VHS"))
    write("field-recording.svg", build_field())
    for name, handle, cam, icon, fxfn in SOCIALS:
        write("feed-%s.svg" % name.lower(),
              build_feed(name, handle, cam, icon, fxfn))
    print("done.")


if __name__ == "__main__":
    main()
