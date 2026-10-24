"""Social feeds panel: three animated, clickable 4:3 tiles."""

from ..embedded import AVATAR_B64
from ..svgkit import corners, esc, led, scanlines, svg
from ..theme import BC, BC2, C, W
from .labels import label_body

FW, FH = 244, 183  # feed tile size (4:3)


def _feed_icon(kind, x, y):
    a = (
        '<g transform="translate(%s,%s) scale(.6)" fill="none" stroke="%s" '
        'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        % (x, y, C["cyan"])
    )
    p = {
        "mail": '<rect x="2.5" y="4.5" width="19" height="15"/><path d="M3 6l9 6.5L21 6"/>',
        "linkedin": '<rect x="2.5" y="2.5" width="19" height="19"/><path d="M7 10v7M7 7v.01M11 17v-4a2 2 0 0 1 4 0v4M11 17v-7"/>',
        "discord": '<path d="M7 8.5c3-1.4 7-1.4 10 0M6.5 16.5c3.2 1.6 7.8 1.6 11 0M6.5 16.5C5 14 4.7 11 5.8 8.2 7 7.3 8.4 6.9 9 6.8M17.5 16.5c1.5-2.5 1.8-5.5.7-8.3-1.2-.9-2.6-1.3-3.2-1.4"/><path d="M9.5 13v.01M14.5 13v.01" stroke-width="2.3"/>',
    }[kind]
    return a + p + "</g>"


def _preview_text(x, y, text, size=12, color=None, anchor="start"):
    return '<text x="%s" y="%s" font-size="%s" fill="%s" text-anchor="%s">%s</text>' % (
        x,
        y,
        size,
        color or C["bright"],
        anchor,
        esc(text),
    )


def _preview_frame(color, background):
    return (
        '<rect x="10" y="32" width="224" height="116" rx="3" '
        'fill="%s" stroke="%s"/>' % (background, color)
    )


def _linkedin_badge(x, y):
    """A vector mark with fixed bounds; font metrics cannot clip the 'in'."""
    return (
        '<g transform="translate(%s,%s)">'
        '<rect width="20" height="20" rx="2" fill="#0a66c2"/>'
        '<g fill="#fff"><circle cx="5.3" cy="5.3" r="1.5"/>'
        '<path d="M4 8h2.7v8H4zM9 8h2.6v1.1c.7-.9 1.6-1.4 2.8-1.4'
        " 2.5 0 3.4 1.6 3.4 4V16h-2.7v-4.1c0-1.3-.3-2-1.5-2"
        '-1.3 0-1.9.9-1.9 2.1v4H9z"/></g></g>' % (x, y)
    )


def _cursor(cls):
    return (
        '<path class="%s motion-cursor" d="M0 0v14l4-4 3 6 3-1-3-6 6-1z" '
        'fill="#fff" stroke="#080a10" stroke-width="1.2" opacity="0"/>' % cls
    )


def _fx_linkedin():
    """Profile preview: Connect, a short pending state, then a held confirmation."""
    blue = "#7ebcff"
    css = (
        "@keyframes liready{0%,24%{opacity:1}25%,100%{opacity:0}}"
        ".li-ready{animation:liready 14s steps(1,end) infinite}"
        "@keyframes lipending{0%,24%{opacity:0}25%,59%{opacity:1}60%,100%{opacity:0}}"
        ".li-pending{animation:lipending 14s steps(1,end) infinite}"
        "@keyframes lidone{0%,59%{opacity:0}60%,100%{opacity:1}}"
        ".li-done{animation:lidone 14s steps(1,end) infinite}"
        "@keyframes licursor{0%,8%{opacity:0;transform:translate(210px,133px)}"
        "13%{opacity:1;transform:translate(210px,133px)}"
        "21%,26%{opacity:1;transform:translate(161px,121px)}"
        "30%,100%{opacity:0;transform:translate(161px,121px)}}"
        ".li-cursor{animation:licursor 14s ease-in-out infinite}"
    )
    b = [_preview_frame("#273d54", "#05080d"), _linkedin_badge(18, 38)]
    b.append(_preview_text(46, 52, "Profile preview", 11.5, blue))
    b.append(
        '<image x="18" y="68" width="28" height="28" '
        'preserveAspectRatio="xMidYMid slice" href="data:image/png;base64,%s" '
        'style="image-rendering:pixelated"/>' % AVATAR_B64
    )
    b.append(_preview_text(56, 79, "Oxide 1-6", 12))
    b.append(_preview_text(56, 96, "Linux / systems", 10.5, "#9eaec1"))
    for cls, text, color, fill, opacity in [
        ("li-ready", "+ Connect", blue, "#0b2138", 0),
        ("li-pending", "Request pending", "#b8c8d9", "#101923", 0),
        ("li-done", "Connected", C["green"], "#0b1d14", 1),
    ]:
        b.append('<g class="%s" opacity="%s">' % (cls, opacity))
        b.append(
            '<rect x="18" y="110" width="208" height="26" rx="3" '
            'fill="%s" stroke="%s" stroke-opacity=".55"/>' % (fill, color)
        )
        b.append(_preview_text(FW / 2, 127, text, 11.5, color, "middle"))
        b.append("</g>")
    b.append(_cursor("li-cursor"))
    return css, "".join(b)


def _fx_email():
    """Compose preview: type a readable draft, click Send, then hold Sent."""
    teal = "#7fe3d0"
    message = "Loved your Linux setup."
    # Departure Mono's advance is 7/11 em; reveal one character per step.
    typed_w = len(message) * 12 * 7 / 11
    css = (
        "@keyframes mailtype{0%,12%{width:0}48%,100%{width:TYPE_WIDTHpx}}"
        ".mail-type{animation:mailtype 16s steps(TYPE_STEPS,end) infinite}"
        "@keyframes mailcaret{0%,12%{transform:translateX(0);opacity:1}"
        "48%,52%{transform:translateX(CARET_WIDTHpx);opacity:1}"
        "53%,100%{transform:translateX(CARET_WIDTHpx);opacity:0}}"
        ".mail-caret{animation:mailcaret 16s steps(TYPE_STEPS,end) infinite}"
        "@keyframes textcaret{0%,49%{opacity:1}50%,100%{opacity:0}}"
        ".typing-caret{animation:textcaret .9s steps(1,end) infinite}"
        "@keyframes maildraft{0%,66%{opacity:1}67%,100%{opacity:0}}"
        ".mail-draft{animation:maildraft 16s steps(1,end) infinite}"
        "@keyframes mailsending{0%,66%{opacity:0}67%,79%{opacity:1}80%,100%{opacity:0}}"
        ".mail-sending{animation:mailsending 16s steps(1,end) infinite}"
        "@keyframes mailsent{0%,79%{opacity:0}80%,100%{opacity:1}}"
        ".mail-sent{animation:mailsent 16s steps(1,end) infinite}"
        "@keyframes mailcursor{0%,54%{opacity:0;transform:translate(208px,130px)}"
        "58%{opacity:1;transform:translate(208px,130px)}"
        "64%,68%{opacity:1;transform:translate(67px,130px)}"
        "72%,100%{opacity:0;transform:translate(67px,130px)}}"
        ".mail-cursor{animation:mailcursor 16s ease-in-out infinite}"
    )
    css = (
        css.replace("TYPE_WIDTH", str(typed_w + 1))
        .replace("TYPE_STEPS", str(len(message)))
        .replace("CARET_WIDTH", str(typed_w))
    )
    b = [_preview_frame("#25443c", "#040b09")]
    b.append(_preview_text(18, 47, "New message", 11.5, teal))
    b.append(_preview_text(226, 47, "PREVIEW", 9, C["gray"], "end"))
    b.append('<path d="M11 55h222M11 91h222" stroke="#25443c"/>')
    b.append(_preview_text(18, 70, "To:", 10.5, "#a4bbb3"))
    b.append(_preview_text(46, 70, "Oxide 1-6", 11.5))
    b.append(_preview_text(18, 85, "Subject:", 10.5, "#a4bbb3"))
    b.append(_preview_text(80, 85, "GitHub contact", 11))
    b.append(_preview_text(18, 104, "Hi Oxide,", 12))
    b.append(
        '<clipPath id="mail-body"><rect class="mail-type" x="18" y="106" '
        'width="%s" height="18"/></clipPath>' % (typed_w + 1)
    )
    b.append('<g clip-path="url(#mail-body)">')
    b.append(_preview_text(18, 119, message, 12))
    b.append("</g>")
    b.append(
        '<g class="mail-caret motion-cursor"><rect class="typing-caret" '
        'x="18" y="109" width="1.5" height="12" fill="%s"/></g>' % teal
    )
    for cls, action, status, color, opacity in [
        ("mail-draft", "Send", "Draft saved", teal, 0),
        ("mail-sending", "Sending", "Sending...", teal, 0),
        ("mail-sent", "Sent", "Message sent", C["green"], 1),
    ]:
        b.append('<g class="%s" opacity="%s">' % (cls, opacity))
        b.append(
            '<rect x="18" y="126" width="68" height="18" rx="2" '
            'fill="#10261f" stroke="%s" stroke-opacity=".45"/>' % color
        )
        b.append(_preview_text(52, 139, action, 10.5, color, "middle"))
        b.append(_preview_text(226, 139, status, 10, "#a4bbb3", "end"))
        b.append("</g>")
    b.append(_cursor("mail-cursor"))
    return css, "".join(b)


def _fx_discord():
    """Conversation preview: a message, a brief typing indicator, then a reply."""
    lavender = "#c4baff"
    css = (
        "@keyframes dctyping{0%,7%{opacity:0}8%,41%{opacity:1}42%,100%{opacity:0}}"
        ".dc-typing{animation:dctyping 16s steps(1,end) infinite}"
        "@keyframes dcreply{0%,41%{opacity:0;transform:translateY(3px)}"
        "44%,100%{opacity:1;transform:translateY(0)}}"
        ".dc-reply{animation:dcreply 16s ease-out infinite}"
        "@keyframes dcdot{0%,70%,100%{opacity:.3}35%{opacity:1}}"
        ".dc-dot{animation:dcdot 1.2s ease-in-out infinite}"
    )
    b = [_preview_frame("#34334f", "#080911")]
    b.append(_preview_text(18, 47, "# linux", 11.5, lavender))
    b.append(_preview_text(226, 47, "PREVIEW", 9, C["gray"], "end"))
    b.append('<path d="M11 55h222" stroke="#34334f"/>')
    b.append('<rect x="18" y="62" width="17" height="17" rx="4" fill="#44416a"/>')
    b.append(_preview_text(26.5, 75, "v", 11, C["bright"], "middle"))
    b.append(_preview_text(44, 71, "visitor", 11, lavender))
    b.append(_preview_text(44, 89, "Nice rice!", 12))
    b.append('<g class="dc-typing" opacity="0">')
    b.append(_preview_text(18, 119, "Oxide is typing", 11, "#acacc5"))
    for i in range(3):
        b.append(
            '<circle class="dc-dot" cx="%s" cy="116" r="1.7" fill="%s" '
            'style="animation-delay:%ss"/>' % (139 + i * 7, lavender, i * 0.18)
        )
    b.append("</g>")
    b.append('<g class="dc-reply" opacity="1">')
    b.append('<rect x="18" y="101" width="17" height="17" rx="4" fill="#164348"/>')
    b.append(_preview_text(26.5, 114, "o", 11, C["cyan"], "middle"))
    b.append(_preview_text(44, 110, "Oxide 1-6", 11, C["cyan"]))
    b.append(_preview_text(44, 128, "Thanks! Arch + NixOS.", 11.5))
    b.append("</g>")
    b.append('<rect x="18" y="136" width="208" height="11" rx="2" fill="#161823"/>')
    b.append(_preview_text(23, 145, "Message #linux", 9.5, "#acacc5"))
    return css, "".join(b)


SOCIALS = [
    ("LinkedIn", "CAM-01", "linkedin", _fx_linkedin),
    ("Email", "CAM-02", "mail", _fx_email),
    ("Discord", "CAM-03", "discord", _fx_discord),
]


def build_feed(name, cam, icon, fxfn):
    css_fx, inner = fxfn()
    css = css_fx + (
        "@media(prefers-reduced-motion:reduce){*{animation:none!important}"
        ".motion-cursor,.typing-caret{display:none}}"
    )
    b = []
    b.append("<title>%s contact preview</title>" % esc(name))
    b.append("<desc>Illustrative animation. Open the contact link to connect.</desc>")
    b.append('<rect width="%s" height="%s" fill="%s"/>' % (FW, FH, C["black"]))
    b.append(
        '<clipPath id="fc"><rect x="8" y="28" width="228" height="122"/></clipPath>'
    )
    b.append('<g clip-path="url(#fc)">%s</g>' % inner)
    # Keep preview text clear of the permanent contact controls.
    b.append(
        '<rect x="0" y="153" width="%s" height="30" fill="%s"/>' % (FW, C["black"])
    )
    b.append('<line x1="1" y1="153" x2="%s" y2="153" stroke="%s"/>' % (FW - 1, BC2))
    b.append(_feed_icon(icon, 12, FH - 26))
    b.append(
        '<text x="34" y="%s" font-size="14" letter-spacing=".6" '
        'fill="%s">%s</text>' % (FH - 14, C["bright"], esc(name.upper()))
    )
    b.append(
        '<text x="%s" y="%s" font-size="9.5" letter-spacing="1.2" '
        'text-anchor="end" fill="%s">CONNECT ▶</text>' % (FW - 12, FH - 14, C["cyan"])
    )
    # Channel labels describe clickable routes, not presence or connection status.
    b.append('<rect width="%s" height="24" fill="%s"/>' % (FW, C["black"]))
    b.append('<rect width="%s" height="24" fill="rgba(85,255,255,.05)"/>' % FW)
    b.append('<line x1="1" y1="24" x2="%s" y2="24" stroke="%s"/>' % (FW - 1, BC2))
    b.append(
        '<text x="12" y="16" font-size="9.5" letter-spacing="1.2" fill="%s">'
        "%s</text>" % (C["cyan"], cam)
    )
    b.append(led(FW - 61, 12, color=C["cyan"], blink=False))
    b.append(
        '<text x="%s" y="16" font-size="9.5" letter-spacing="1.2" '
        'text-anchor="end" fill="%s">LINK</text>' % (FW - 12, C["cyan"])
    )
    b.append(scanlines(1, 1, FW - 2, FH - 2, op=0.08))
    b.append(corners(0, 0, FW, FH, s=10, inset=4))
    b.append(
        '<rect x=".5" y=".5" width="%s" height="%s" fill="none" '
        'stroke="%s"/>' % (FW - 1, FH - 1, BC)
    )
    # Each clickable tile carries a third of the common header. This keeps the
    # header attached even when its scaled height is below an HTML text line.
    column = next(i for i, social in enumerate(SOCIALS) if social[0] == name)
    slice_w = W / len(SOCIALS)
    header_h = 30 * FW / slice_w
    header = '<svg width="%s" height="%s" viewBox="%s 0 %s 30">%s</svg>' % (
        FW,
        header_h,
        column * slice_w,
        slice_w,
        label_body("ESTABLISH UPLINK", "REF://CONTACT.SYS"),
    )
    return svg(
        FW,
        FH + header_h,
        css,
        header + '<g transform="translate(0,%s)">%s</g>' % (header_h, "".join(b)),
    )
