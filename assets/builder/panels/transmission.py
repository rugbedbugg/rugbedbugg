"""A periodically refreshed quote log, with readable text and attribution."""

from textwrap import wrap

from ..svgkit import esc, panel_frame, scanlines, svg
from ..theme import C, W


def build_transmission(quote):
    lines = wrap(quote["text"], 78, break_on_hyphens=False)
    author = quote.get("author", "")
    source = quote.get("source", "PROGRAMMING QUOTES")
    attribution = ("— " + author + " · ") if author else ""
    captions = wrap(attribution + source, 92, break_on_hyphens=False)
    first_y = 58
    last_y = first_y + (len(lines) - 1) * 22
    caption_y = last_y + 26
    h = caption_y + (len(captions) - 1) * 16 + 22
    b = [panel_frame(h, "INCOMING TRANSMISSIONS", "REF://QUOTES.LOG")]
    b.append(
        "<desc>Quote attribution as supplied by the programming-quotes archive.</desc>"
    )
    b.append(
        '<rect x="22" y="%s" width="2" height="%s" fill="%s"/>'
        % (first_y - 12, last_y - first_y + 16, C["cyan"])
    )
    for i, line in enumerate(lines):
        text = ("“" if i == 0 else "") + line
        if i == len(lines) - 1:
            text += "”"
        b.append(
            '<text x="36" y="%s" font-size="14" fill="%s">%s</text>'
            % (first_y + i * 22, C["bright"], esc(text))
        )
    for i, line in enumerate(captions):
        b.append(
            '<text x="36" y="%s" font-size="11" fill="%s">%s</text>'
            % (caption_y + i * 16, C["gray"], esc(line))
        )
    b.append(scanlines(2, 28, W - 4, h - 30, op=0.10))
    return svg(W, h, "", "".join(b))
