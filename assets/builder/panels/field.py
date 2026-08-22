"""Field recording panel: VHS still of the ricing setup (clickable)."""
from ..svgkit import corners, esc, led, svg
from ..theme import BC, BC2, C, W


def _pane(x, y, w, hh, lines):
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

    b.append('<g opacity="0.55">')
    b.append(_pane(pad, pad, lw, ih, [
        ("~/.config/hypr $ hyprctl", C["cyan"]),
        ("workspace 1 :: caelestia", C["purple"]),
        ("████░░░ 88%", C["green"]), ("> neofetch", C["dim"])]))
    b.append(_pane(rx, pad, rw, ph, [
        ("btop", C["cyan"]), ("cpu ███░", C["green"]), ("mem ██░░", C["green"])]))
    b.append(_pane(rx, pad + ph + gap, rw, ph, [
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
    b.append(corners(0, 0, W, h, s=14, inset=6))
    b.append('<rect x="1" y="1" width="%s" height="%s" fill="none" stroke="%s"/>'
             % (W - 2, h - 2, BC))
    return svg(W, h, css, "".join(b))
