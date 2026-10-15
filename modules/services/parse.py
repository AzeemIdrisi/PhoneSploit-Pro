"""Pure parsers shared by the web console. No ADB calls."""

from __future__ import annotations

import re


def parse_devices_list(raw: str) -> list[dict[str, str]]:
    """Parse `adb devices -l` stdout."""
    devices: list[dict[str, str]] = []
    lines = raw.splitlines()
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        info = " ".join(parts[2:])
        transport = "wifi" if ":" in parts[0] else "usb"
        devices.append(
            {
                "serial": parts[0],
                "state": parts[1],
                "info": info,
                "transport": transport,
            }
        )
    return devices


def parse_battery(raw: str) -> dict[str, str]:
    props: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        if key:
            props[key] = value.strip()
    return props


def parse_packages(raw: str) -> list[str]:
    packages: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("package:"):
            packages.append(line.split(":", 1)[1].strip())
    return packages


def parse_ls(raw: str) -> list[dict[str, str]]:
    """Parse `ls -1p` output. Directories end with '/'."""
    entries: list[dict[str, str]] = []
    for line in raw.splitlines():
        name = line.strip()
        if not name or name in (".", ".."):
            continue
        is_dir = name.endswith("/")
        entries.append({"name": name.rstrip("/"), "kind": "dir" if is_dir else "file"})
    return entries


_LOC_RE = re.compile(r"Location\[(\w+)\s+(-?\d+\.?\d*),(-?\d+\.?\d*)", re.IGNORECASE)


def parse_location(raw: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for match in _LOC_RE.finditer(raw):
        key = (match.group(1), match.group(2), match.group(3))
        if key in seen:
            continue
        seen.add(key)
        rows.append({"provider": key[0], "latitude": key[1], "longitude": key[2]})
    for line in raw.splitlines():
        line = line.strip()
        if not any(token in line.lower() for token in ("latitude", "longitude", "lat=", "lng=")):
            continue
        lat_m = re.search(r"(?:latitude|lat)\s*[=:]\s*(-?\d+\.?\d*)", line, re.I)
        lng_m = re.search(r"(?:longitude|lng)\s*[=:]\s*(-?\d+\.?\d*)", line, re.I)
        if not lat_m or not lng_m:
            continue
        provider = line.split(":")[0].strip() if ":" in line else "location"
        key = (provider, lat_m.group(1), lng_m.group(1))
        if key in seen:
            continue
        seen.add(key)
        rows.append({"provider": provider, "latitude": key[1], "longitude": key[2]})
    return rows[:25]


def parse_usage(raw: str, cutoff_ms: int = 0) -> list[dict[str, int | str]]:
    entries: list[tuple[str, int, int]] = []
    for line in raw.splitlines():
        line = line.strip()
        if "lastTimeUsed" not in line:
            continue
        parts = line.split()
        pkg = parts[0] if parts else ""
        last_m = re.search(r"lastTimeUsed=(\d+)", line)
        if not last_m or not pkg:
            continue
        last_used = int(last_m.group(1))
        if last_used < cutoff_ms:
            continue
        fg_m = re.search(r"totalTimeInForeground=(\d+)", line)
        vis_m = re.search(r"totalTimeVisible=(\d+)", line)
        visible = int(fg_m.group(1)) if fg_m else (int(vis_m.group(1)) if vis_m else 0)
        entries.append((pkg, last_used, visible))
    entries.sort(key=lambda item: item[1], reverse=True)
    return [
        {"package": pkg, "lastUsed": last_used, "foregroundMs": visible}
        for pkg, last_used, visible in entries[:40]
    ]


def parse_content_rows(raw: str) -> list[dict[str, str]]:
    """Parse `adb shell content query` rows of the form Row: N key=value, key=value."""
    rows: list[dict[str, str]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("Row:"):
            continue
        body = line.split(" ", 2)[-1] if " " in line else line
        row: dict[str, str] = {}
        for part in body.split(", "):
            if "=" not in part:
                continue
            key, _, value = part.partition("=")
            row[key.strip()] = value.strip()
        if row:
            rows.append(row)
    return rows


def safe_artifact_relative(root_name: str, relative: str) -> bool:
    """Reject path traversal in artifact URLs."""
    if not relative or relative.startswith(("/", "\\")) or ".." in relative.replace("\\", "/").split("/"):
        return False
    return True
