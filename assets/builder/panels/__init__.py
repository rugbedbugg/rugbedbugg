"""Panel registry: every generated output, in README order."""
from .dossier import build_dossier
from .feeds import SOCIALS, build_feed
from .field import build_field
from .header import build_header
from .labels import build_label
from .loadout import build_loadout
from .telemetry import build_telemetry
from .transmission import build_transmission

__all__ = [
    "build_dossier", "build_feed", "build_field", "build_header",
    "build_label", "build_loadout", "build_telemetry", "build_transmission",
    "SOCIALS",
]
