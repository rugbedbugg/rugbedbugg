#!/usr/bin/env python3
"""Generate the surveillance-console profile panels as self-contained animated SVGs.

Each panel embeds the Departure Mono font (and, for the monitor, the dithered
headshot) as base64 so the file renders identically anywhere GitHub serves it as
an <img>. CSS keyframe animations run inside <img>, so the feeds stay live.

Run:  python assets/build.py

The generator lives in the assets/builder/ package:
  builder/config.py       identity + data-source settings
  builder/theme.py        palette and layout constants
  builder/embedded.py     base64-embedded font/avatar
  builder/svgkit.py       shared SVG primitives
  builder/github_data.py  live GitHub fetchers with fallbacks
  builder/panels/         one module per output panel
"""

from builder import github_data, upstream
from builder.panels import (
    RICES,
    SOCIALS,
    build_contribution,
    build_dossier,
    build_feed,
    build_header,
    build_label,
    build_tape_footer,
    build_tape_header,
    build_telemetry,
    build_transmission,
    build_upstream_feed,
)
from builder.svgkit import write


def main():
    print("fetching live profile data...")
    stats, repos = github_data.fetch_stats()
    langs = github_data.fetch_langs(repos)
    cal = github_data.fetch_calendar()
    contributions = upstream.fetch_upstream()
    print("  stats=%s  langs=%d  cal_cells=%d" % (stats, len(langs), len(cal)))
    write("header.svg", build_header())
    write("dossier.svg", build_dossier())
    write("telemetry.svg", build_telemetry(stats, langs, cal))
    write("contribution-latch.svg", build_contribution("latch", contributions))
    write("contribution-anyps5.svg", build_contribution("anyps5", contributions))
    write("contribution-feed.svg", build_upstream_feed(contributions))
    write("transmission.svg", build_transmission(github_data.fetch_quote()))
    write("label-uplink.svg", build_label("ESTABLISH UPLINK", "REF://CONTACT.SYS"))
    write("label-field.svg", build_label("FIELD RECORDINGS", "REF://RICINGS.VHS"))
    for number, (slug, name, distro) in enumerate(RICES, start=1):
        write(
            "rice-%s-header.svg" % slug,
            build_tape_header(number, name, distro),
        )
        write("rice-%s-footer.svg" % slug, build_tape_footer(name))
    for name, cam, icon, fxfn in SOCIALS:
        write("feed-%s.svg" % name.lower(), build_feed(name, cam, icon, fxfn))
    print("done.")


if __name__ == "__main__":
    main()
