"""Profile identity and data-source configuration."""
import os

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))

USER = "rugbedbugg"
SKIP_REPOS = {"portfolio-website", "VIT-CampusMap"}

# Fallbacks (snapshot fetched 2026-07-24) used when offline / rate-limited.
FB_STATS = {"repos": 16, "stars": 80, "followers": 29, "following": 20}
FB_LANGS = [("Python", 61.3), ("Assembly", 13.4), ("Rust", 11.7),
            ("C++", 6.1), ("Java", 4.7), ("Lua", 1.4), ("Shell", 1.1)]

QUOTES = ["Talk is cheap. Show me the code.",
          "Simplicity is prerequisite for reliability.",
          "Given enough eyeballs, all bugs are shallow.",
          "First, solve the problem. Then, write the code.",
          "Programs must be written for people to read.",
          "Linux is not an OS, it’s a lifestyle: best lived in the terminal.",
          "The computer does exactly what you tell it to. That is the terror.",
          "Weeks of coding can save you hours of planning."]
