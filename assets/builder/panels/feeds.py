"""Social feeds panel: three animated, clickable 4:3 tiles."""
from ..svgkit import corners, esc, led, svg
from ..theme import BC2, BCH, C

FW, FH = 244, 183  # feed tile size (4:3)


def _feed_icon(kind, x, y):
    a = ('<g transform="translate(%s,%s) scale(.6)" fill="none" stroke="%s" '
         'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
         % (x, y, C["cyan"]))
    p = {
        "mail": '<rect x="2.5" y="4.5" width="19" height="15"/><path d="M3 6l9 6.5L21 6"/>',
        "linkedin": '<rect x="2.5" y="2.5" width="19" height="19"/><path d="M7 10v7M7 7v.01M11 17v-4a2 2 0 0 1 4 0v4M11 17v-7"/>',
        "discord": '<path d="M7 8.5c3-1.4 7-1.4 10 0M6.5 16.5c3.2 1.6 7.8 1.6 11 0M6.5 16.5C5 14 4.7 11 5.8 8.2 7 7.3 8.4 6.9 9 6.8M17.5 16.5c1.5-2.5 1.8-5.5.7-8.3-1.2-.9-2.6-1.3-3.2-1.4"/><path d="M9.5 13v.01M14.5 13v.01" stroke-width="2.3"/>',
    }[kind]
    return a + p + '</g>'


def _li_avatar(x, y, r, col, glow=False):
    """Small avatar node: ring with a head + shoulders silhouette."""
    return ('<g transform="translate(%s,%s)">'
            '<circle r="%s" fill="#0a1830" stroke="%s" stroke-width="1.2"%s/>'
            '<circle cy="%s" r="%s" fill="%s"/>'
            '<path d="M%s %s a%s %s 0 0 1 %s 0" fill="%s"/></g>'
            % (x, y, r, col, ' filter="url(#glow)"' if glow else '',
               -r * 0.18, r * 0.34, col,
               -r * 0.5, r * 0.62, r * 0.5, r * 0.42, r, col))


def _fx_linkedin():
    """Professional network: hub avatar, orbiting connections, marching-ant
    links, incoming connection pulses and a new-connection ping."""
    BLU, LT = "#4d9fff", "#a9d4ff"
    cx, cy = FW / 2, FH / 2 + 3
    sats = [(40, 44), (FW - 40, 46), (30, FH - 46), (FW - 32, FH - 44),
            (cx, 30), (34, cy + 6), (FW - 28, cy)]
    pulse_idx = [0, 3, 4, 6]

    css = ("@keyframes lidash{to{stroke-dashoffset:-18}}"
           ".edge{animation:lidash 1.5s linear infinite}"
           "@keyframes linode{0%,100%{opacity:.5}50%{opacity:1}}"
           ".node{animation:linode 3s ease-in-out infinite}"
           "@keyframes lispin{to{transform:rotate(360deg)}}"
           ".ring{animation:lispin 24s linear infinite;"
           "transform-box:fill-box;transform-origin:center}"
           "@keyframes lireach{0%{transform:scale(.5);opacity:.85}"
           "100%{transform:scale(1.7);opacity:0}}"
           ".reach{animation:lireach 3.2s ease-out infinite;"
           "transform-box:fill-box;transform-origin:center}")
    for k in pulse_idx:
        sx, sy = sats[k]
        dx, dy = round(cx - sx, 1), round(cy - sy, 1)
        css += ("@keyframes lip" + str(k) + "{0%{transform:translate(0px,0px);"
                "opacity:0}14%{opacity:1}86%{opacity:1}100%{transform:translate("
                + str(dx) + "px," + str(dy) + "px);opacity:0}}"
                ".lip" + str(k) + "{animation:lip" + str(k)
                + " 2.8s linear infinite;animation-delay:" + str(round(k * 0.5, 2))
                + "s}")

    out = ['<circle class="ring" cx="%s" cy="%s" r="52" fill="none" stroke="%s" '
           'stroke-width="1" stroke-dasharray="2 9" opacity=".3"/>'
           % (cx, cy, BLU)]
    for sx, sy in sats:
        out.append('<line class="edge" x1="%s" y1="%s" x2="%s" y2="%s" '
                   'stroke="%s" stroke-width="1" opacity=".45" '
                   'stroke-dasharray="4 5"/>' % (cx, cy, sx, sy, BLU))
    for i, (sx, sy) in enumerate(sats):
        out.append('<g class="node" style="animation-delay:%.2fs">%s</g>'
                   % (i * 0.4, _li_avatar(sx, sy, 8.5, "#7cc2ff")))
    for k in pulse_idx:
        sx, sy = sats[k]
        out.append('<circle class="lip%d" cx="%s" cy="%s" r="2.6" fill="%s" '
                   'filter="url(#glow)"/>' % (k, sx, sy, C["cyan"]))
    sx, sy = sats[1]
    out.append('<circle class="reach" cx="%s" cy="%s" r="12" fill="none" '
               'stroke="%s" stroke-width="1.5"/>' % (sx, sy, C["green"]))
    out.append(_li_avatar(cx, cy, 15, LT, glow=True))
    out.append('<rect x="%s" y="%s" width="13" height="13" rx="2.5" fill="%s"/>'
               % (cx + 6, cy + 3, BLU))
    out.append('<text x="%s" y="%s" font-size="9.5" fill="#00142c">in</text>'
               % (cx + 8, cy + 12.5))
    return css, "".join(out)


def _fx_email():
    """Inbox: unread rows, an envelope dropping in, a sent paper-plane sweep
    and a blinking compose caret."""
    TEAL, TEAL2, DIMT = "#7fe3d0", "#39b39a", "#2b4d47"
    css = ("@keyframes mdrop{0%{transform:translateY(-40px);opacity:0}"
           "16%{opacity:1}64%{transform:translateY(0);opacity:1}"
           "80%,100%{transform:translateY(0);opacity:0}}"
           ".drop{animation:mdrop 4.4s ease-in infinite}"
           "@keyframes unread{0%,100%{opacity:.3}50%{opacity:1}}"
           ".un{animation:unread 1.6s ease-in-out infinite}"
           "@keyframes plane{0%{transform:translate(-34px,6px);opacity:0}"
           "22%,78%{opacity:.95}100%{transform:translate(250px,-14px);opacity:0}}"
           ".plane{animation:plane 5.2s ease-in-out infinite}"
           "@keyframes caret{0%,50%{opacity:1}51%,100%{opacity:0}}"
           ".caret{animation:caret 1s steps(1) infinite}")
    out = []
    for i, ry in enumerate((30, 60, 90)):
        out.append('<rect x="10" y="%s" width="224" height="24" rx="3" '
                   'fill="#08201c" stroke="rgba(127,227,208,.25)" '
                   'stroke-width="1"/>' % ry)
        out.append('<circle class="un" cx="22" cy="%s" r="3.4" fill="%s" '
                   'style="animation-delay:%.2fs"/>' % (ry + 12, TEAL, i * 0.4))
        out.append('<g transform="translate(32,%s)" stroke="%s" stroke-width="1" '
                   'fill="none"><rect width="15" height="11" rx="1.5"/>'
                   '<path d="M0 1l7.5 5.5L15 1"/></g>' % (ry + 6, TEAL))
        out.append('<rect x="54" y="%s" width="%s" height="3.5" fill="%s"/>'
                   % (ry + 7, 70 + i * 14, TEAL))
        out.append('<rect x="54" y="%s" width="%s" height="3" fill="%s" '
                   'opacity=".6"/>' % (ry + 14, 150 - i * 20, DIMT))
    out.append('<g class="drop"><g transform="translate(105,16)" stroke="%s" '
               'stroke-width="1.4" fill="#08201c"><rect width="34" height="24" '
               'rx="2.5"/><path d="M0 2l17 13L34 2" fill="none"/></g></g>' % TEAL)
    out.append('<path class="plane" d="M0 0l20 8-7 2-2 7z" fill="%s" '
               'transform="translate(0,116)"/>' % TEAL)
    out.append('<text x="12" y="132" font-size="9" letter-spacing="1" '
               'fill="%s">&gt; compose message</text>' % TEAL2)
    out.append('<rect class="caret" x="130" y="124" width="6" height="10" '
               'fill="%s"/>' % TEAL)
    return css, "".join(out)


def _fx_discord():
    """Server chat + voice: messages popping in, a reaction pill, a typing
    indicator, a speaking voice avatar and a member list with status dots."""
    BLURPLE, GRN, PNK, YEL, RED = ("#5865f2", "#57f287", "#eb459e",
                                   "#fee75c", "#ed4245")
    TXT, SUB = "#c9c6ff", "#8d8db0"
    css = ("@keyframes dcpop{0%{opacity:0;transform:translateY(6px)}"
           "12%,84%{opacity:1;transform:translateY(0)}100%{opacity:.1}}"
           ".msg{animation:dcpop 5s ease-out infinite}"
           "@keyframes tping{0%,60%,100%{opacity:.3}30%{opacity:1}}"
           ".tp{animation:tping 1.2s infinite}"
           "@keyframes vspeak{0%{transform:scale(1);opacity:.7}"
           "100%{transform:scale(1.9);opacity:0}}"
           ".vs{animation:vspeak 1.8s ease-out infinite;"
           "transform-box:fill-box;transform-origin:center}"
           "@keyframes react{0%{transform:scale(0);opacity:0}"
           "18%{transform:scale(1.25)}32%{transform:scale(1)}"
           "86%{opacity:1}100%{opacity:0}}"
           ".rx{animation:react 5s ease-out infinite;"
           "transform-box:fill-box;transform-origin:center}"
           "@keyframes stat{0%,100%{opacity:.5}50%{opacity:1}}"
           ".st{animation:stat 2.4s ease-in-out infinite}")
    out = []
    avs = (BLURPLE, GRN, PNK)
    for i in range(3):
        yy = 30 + i * 32
        out.append('<g class="msg" style="animation-delay:%.2fs">' % (i * 0.7))
        out.append('<circle cx="18" cy="%s" r="7" fill="%s"/>' % (yy, avs[i]))
        out.append('<rect x="30" y="%s" width="%s" height="4" rx="1" fill="%s"/>'
                   % (yy - 7, 40 + i * 10, TXT))
        out.append('<rect x="30" y="%s" width="%s" height="3.5" rx="1" fill="%s" '
                   'opacity=".7"/>' % (yy - 1, 96 - i * 16, SUB))
        if i == 1:
            out.append('<rect x="30" y="%s" width="46" height="3.5" rx="1" '
                       'fill="%s" opacity=".7"/>' % (yy + 5, SUB))
        out.append('</g>')
    # reaction pill on the first message
    out.append('<g class="rx"><rect x="108" y="21" width="27" height="13" '
               'rx="6.5" fill="#232447" stroke="%s" stroke-width="1"/>'
               '<circle cx="116" cy="27.5" r="3" fill="%s"/>'
               '<rect x="122" y="26" width="8" height="3" rx="1.5" fill="%s"/>'
               '</g>' % (PNK, PNK, "#b3a4ff"))
    # typing indicator
    ty = 126
    out.append('<circle cx="18" cy="%s" r="7" fill="%s"/>' % (ty, YEL))
    out.append('<rect x="30" y="%s" width="58" height="13" rx="6.5" '
               'fill="#232447"/>' % (ty - 6))
    for j in range(3):
        out.append('<circle class="tp" cx="%s" cy="%s" r="2.2" fill="#b3a4ff" '
                   'style="animation-delay:%.2fs"/>' % (42 + j * 12, ty, j * 0.2))
    # right column: voice avatar + member list
    out.append('<line x1="162" y1="26" x2="162" y2="118" stroke="%s" '
               'stroke-width="1" opacity=".22"/>' % BLURPLE)
    vx, vy = 200, 42
    out.append('<circle class="vs" cx="%s" cy="%s" r="12" fill="none" '
               'stroke="%s" stroke-width="1.6"/>' % (vx, vy, GRN))
    out.append('<circle cx="%s" cy="%s" r="12" fill="%s"/>' % (vx, vy, BLURPLE))
    out.append('<circle cx="%s" cy="%s" r="3.2" fill="#e9e9ff"/>' % (vx, vy - 2))
    out.append('<path d="M%s %s a6 5 0 0 1 12 0" fill="#e9e9ff"/>'
               % (vx - 6, vy + 6))
    for i, sc in enumerate((GRN, YEL, RED, GRN)):
        my = 74 + i * 14
        out.append('<circle cx="182" cy="%s" r="5" fill="#3a3c66"/>' % my)
        out.append('<circle class="st" cx="186" cy="%s" r="2.4" fill="%s" '
                   'style="animation-delay:%.2fs"/>' % (my + 3, sc, i * 0.5))
        out.append('<rect x="192" y="%s" width="%s" height="3.5" rx="1" '
                   'fill="%s" opacity=".7"/>' % (my - 2, 34 - i * 4, SUB))
    return css, "".join(out)


SOCIALS = [
    ("LinkedIn", "CAM-01", "linkedin", _fx_linkedin),
    ("Email", "CAM-02", "mail", _fx_email),
    ("Discord", "CAM-03", "discord", _fx_discord),
]


def build_feed(name, cam, icon, fxfn):
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
    b.append(_feed_icon(icon, 8, FH - 21))
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
    b.append(corners(0, 0, FW, FH, s=10, inset=4))
    b.append('<rect x=".5" y=".5" width="%s" height="%s" fill="none" '
             'stroke="%s"/>' % (FW - 1, FH - 1, BC2))
    return svg(FW, FH, css, "".join(b))
