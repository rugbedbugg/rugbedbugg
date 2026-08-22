"""Binary assets embedded into every panel as base64 data URIs."""
import base64
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.dirname(HERE)

with open(os.path.join(ASSETS_DIR, "DepartureMono-Regular.woff2"), "rb") as f:
    FONT_B64 = base64.b64encode(f.read()).decode()
with open(os.path.join(ASSETS_DIR, "avatar-cga.png"), "rb") as f:
    AVATAR_B64 = base64.b64encode(f.read()).decode()

FONT_FACE = (
    "@font-face{font-family:'Departure Mono';"
    "src:url('data:font/woff2;base64,%s') format('woff2');font-display:swap}" % FONT_B64
)
