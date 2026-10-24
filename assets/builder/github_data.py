"""GitHub live-data fetchers with built-in fallbacks."""

import collections
import json
import os
import random
import re
import urllib.request

from . import config


def _get(url):
    headers = {"User-Agent": "oxide-build"}
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        headers["Authorization"] = "Bearer " + tok
    req = urllib.request.Request(url, headers=headers)
    return json.load(urllib.request.urlopen(req, timeout=15))


def fetch_stats():
    try:
        u = _get("https://api.github.com/users/%s" % config.USER)
        repos, page = [], 1
        while True:
            chunk = _get(
                "https://api.github.com/users/%s/repos"
                "?per_page=100&page=%d" % (config.USER, page)
            )
            repos += chunk
            if len(chunk) < 100:
                break
            page += 1
        stars = sum(r["stargazers_count"] for r in repos)
        return (
            {
                "repos": u["public_repos"],
                "stars": stars,
                "followers": u["followers"],
                "following": u["following"],
            },
            repos,
        )
    except Exception as e:
        print("  ..stats fetch failed (%s) -> fallback" % e)
        return dict(config.FB_STATS), None


def fetch_langs(repos):
    if repos is None:
        return list(config.FB_LANGS)
    try:
        agg = collections.Counter()
        for r in repos:
            if r["name"] in config.SKIP_REPOS or r.get("fork"):
                continue
            for k, v in _get(r["languages_url"]).items():
                agg[k] += v
        tot = sum(agg.values()) or 1
        return [(k, round(100.0 * v / tot, 1)) for k, v in agg.most_common(7)]
    except Exception as e:
        print("  ..langs fetch failed (%s) -> fallback" % e)
        return list(config.FB_LANGS)


def fetch_calendar():
    try:
        req = urllib.request.Request(
            "https://github.com/users/%s/contributions" % config.USER,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        html = urllib.request.urlopen(req, timeout=15).read().decode()
        lv = [int(x) for x in re.findall(r'data-level="(\d)"', html)]
        if lv:
            return lv
        raise ValueError("no cells")
    except Exception as e:
        print("  ..calendar fetch failed (%s) -> generated" % e)
        rng = random.Random(7)
        out = []
        for _ in range(53 * 7):
            r = rng.random()
            out.append(
                4
                if r > 0.93
                else 3
                if r > 0.82
                else 2
                if r > 0.62
                else 1
                if r > 0.4
                else 0
            )
        return out


def fetch_quote():
    # Select fresh content on every build, retaining the archive's attribution.
    try:
        data = _get(config.QUOTE_URL)
        picks = []
        for record in data:
            if not isinstance(record, dict) or not isinstance(record.get("text"), str):
                continue
            text = " ".join(record["text"].split())
            if 20 <= len(text) <= 150 and any(
                topic in text.casefold() for topic in config.QUOTE_TOPICS
            ):
                quote = {"text": text}
                for key in ("author", "source"):
                    value = record.get(key)
                    if isinstance(value, str) and value.strip():
                        quote[key] = " ".join(value.split())[:160]
                picks.append(quote)
        if picks:
            return random.choice(picks)
    except Exception as e:
        print("  ..quote fetch failed (%s) -> fallback" % e)
    return random.choice(config.QUOTES)
