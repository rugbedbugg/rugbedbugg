"""Profile identity and data-source configuration."""

import os

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))

USER = "rugbedbugg"
SKIP_REPOS = {"portfolio-website", "VIT-CampusMap"}

# Fallbacks (snapshot fetched 2026-07-24) used when offline / rate-limited.
FB_STATS = {"repos": 16, "stars": 80, "followers": 29, "following": 20}
FB_LANGS = [
    ("Python", 61.3),
    ("Assembly", 13.4),
    ("Rust", 11.7),
    ("C++", 6.1),
    ("Java", 4.7),
    ("Lua", 1.4),
    ("Shell", 1.1),
]

QUOTE_URL = (
    "https://raw.githubusercontent.com/skolakoda/"
    "programming-quotes-api/master/data/quotes.json"
)
QUOTE_TOPICS = (
    "linux",
    "unix",
    "program",
    "software",
    "computer",
    "code",
    "system",
    "reliab",
    "simplic",
    "complex",
    "debug",
    "data structur",
)

# Attributed excerpts from the same archive used by the live quote feed.
QUOTES = [
    {"text": "Talk is cheap. Show me the code.", "author": "Linus Torvalds"},
    {
        "text": "Simplicity is prerequisite for reliability.",
        "author": "Edsger W. Dijkstra",
    },
    {
        "text": "Controlling complexity is the essence of computer programming.",
        "author": "Brian Kernighan",
    },
    {
        "text": "Programs must be written for people to read, and only incidentally for machines to execute.",
        "author": "Hal Abelson",
        "source": 'Abelson & Sussman, "Structure and Interpretation of Computer Programs"',
    },
]
