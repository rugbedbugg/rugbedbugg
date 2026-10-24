"""Panel registry: every generated output, in README order."""

from .contributions import build_contribution, build_upstream_feed
from .dossier import build_dossier
from .feeds import SOCIALS, build_feed
from .field import RICES, build_tape_footer, build_tape_header
from .header import build_header
from .labels import build_label
from .telemetry import build_telemetry
from .transmission import build_transmission

__all__ = [
    "build_contribution",
    "build_dossier",
    "build_feed",
    "build_header",
    "build_label",
    "build_tape_footer",
    "build_tape_header",
    "build_telemetry",
    "build_transmission",
    "build_upstream_feed",
    "SOCIALS",
    "RICES",
]
