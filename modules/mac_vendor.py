"""Offline IEEE OUI lookup shared by device and Wi-Fi features."""

from __future__ import annotations

import re
from typing import Any

MAC_RE = re.compile(r"(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}")

_lookup: Any = None
_lookup_failed = False


def lookup_mac_vendor(mac: str) -> str | None:
    """Resolve a MAC/BSSID to a manufacturer name. None if unknown or lib missing."""
    global _lookup, _lookup_failed
    mac = (mac or "").strip()
    if not mac or _lookup_failed:
        return None
    if _lookup is None:
        try:
            from mac_vendor_lookup import MacLookup

            _lookup = MacLookup()
        except Exception:
            _lookup_failed = True
            return None
    try:
        return _lookup.lookup(mac)
    except Exception:
        return None


def annotate_macs(text: str) -> str:
    def _repl(match: re.Match[str]) -> str:
        mac = match.group(0)
        vendor = lookup_mac_vendor(mac)
        return f"{mac} ({vendor})" if vendor else mac

    return MAC_RE.sub(_repl, text)
