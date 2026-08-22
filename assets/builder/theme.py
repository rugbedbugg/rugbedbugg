"""Shared palette and layout constants."""

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

# Okabe-Ito colorblind-safe categorical palette, assigned by language rank.
LANG_COLORS = ["#56b4e9", "#e69f00", "#d55e00", "#cc79a7",
               "#009e73", "#f0e442", "#0072b2", "#dddddd"]
CAL_SHADES = ["rgba(85,255,255,.10)", "rgba(85,255,255,.28)",
              "rgba(85,255,255,.50)", "rgba(85,255,255,.72)", "#55ff55"]
