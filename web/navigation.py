"""
Navigation registry — single source of truth for sidebar structure.

CLI action map (1–63):
  Home: overview only
  Devices/Connect: 1–3 | Discover: 4 | ADB Server: 37 | Device Info: 27–28
  Screen/Live: 5,62 | Capture: 6–7,21–22 | Audio: 40–43 | Play: 24–26
  Remote/Input: 39 | Lock&Power: 29–32,38 | Messaging: 17,23
  Console/Terminal: 14,50 | Console/Jobs: msfconsole, scans
  Apps/Installed: 10,12–13 | Install: 11,52 | Manage: 36,45–46,48–49
  Files/Manager: 8–9,16 | Bulk: 18–20 | Personal: 33–35
  Network/Forward: 44 | WiFi: 56–58,60 | Connectivity: 51,59
  Exploit: 15
  System/Logs: 47 | Config: 53–55 | Security: 61
  CLI 63: Launch Web UI | Settings: web sidebar
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TabMeta:
    id: str
    label: str
    description: str


@dataclass(frozen=True)
class PageMeta:
    id: str
    label: str
    icon: str
    section: str
    page_description: str
    tabs: tuple[TabMeta, ...] = ()


NAV_SECTIONS: list[tuple[str, list[PageMeta]]] = [
    (
        "OVERVIEW",
        [
            PageMeta(
                id="home",
                label="Home",
                icon="dashboard",
                section="OVERVIEW",
                page_description="Status at a glance and quick navigation.",
            ),
        ],
    ),
    (
        "CONNECT",
        [
            PageMeta(
                id="devices",
                label="Devices",
                icon="devices",
                section="CONNECT",
                page_description="Connect, discover, and inspect Android devices.",
                tabs=(
                    TabMeta("connect", "Connect", "Pair over Wi‑Fi and manage the device list."),
                    TabMeta("discover", "Discover", "Scan the LAN for ADB hosts and connect."),
                    TabMeta("adb", "ADB Server", "Disconnect sessions or stop the ADB server."),
                    TabMeta("info", "Device Info", "Hardware, OS, and battery details."),
                ),
            ),
        ],
    ),
    (
        "OPERATE",
        [
            PageMeta(
                id="screen",
                label="Screen & Audio",
                icon="videocam",
                section="OPERATE",
                page_description="Mirror, capture, stream, and play media on the device.",
                tabs=(
                    TabMeta("live", "Live View", "Real-time mirror and camera via scrcpy."),
                    TabMeta("capture", "Capture", "Screenshots and screen recordings saved to PC."),
                    TabMeta("audio", "Audio", "Stream or record microphone and device audio."),
                    TabMeta("play", "Play on Device", "Push a file and open it on the device."),
                ),
            ),
            PageMeta(
                id="remote",
                label="Remote Control",
                icon="gamepad",
                section="OPERATE",
                page_description="Send input, control power state, and message the device.",
                tabs=(
                    TabMeta("input", "Input", "Keycodes and text input."),
                    TabMeta("power", "Lock & Power", "Lock, unlock, reboot, and power off."),
                    TabMeta("messaging", "Messaging", "Send SMS and open URLs."),
                ),
            ),
        ],
    ),
    (
        "MANAGE",
        [
            PageMeta(
                id="apps",
                label="Applications",
                icon="apps",
                section="MANAGE",
                page_description="Browse, install, and manage installed apps.",
                tabs=(
                    TabMeta("installed", "Installed", "List, launch, and uninstall apps."),
                    TabMeta("install", "Install", "Deploy APK or split APK bundles."),
                    TabMeta("manage", "Manage", "Force-stop, clear data, permissions, extract APK."),
                ),
            ),
            PageMeta(
                id="files",
                label="Files & Data",
                icon="folder",
                section="MANAGE",
                page_description="Transfer files and export personal data from the device.",
                tabs=(
                    TabMeta("manager", "File Manager", "Browse /sdcard/, pull, and push files."),
                    TabMeta("bulk", "Bulk Export", "Copy WhatsApp, screenshots, and camera rolls."),
                    TabMeta("personal", "Personal Data", "Export SMS, contacts, and call logs."),
                ),
            ),
        ],
    ),
    (
        "INFRASTRUCTURE",
        [
            PageMeta(
                id="network",
                label="Network Tools",
                icon="wifi",
                section="INFRASTRUCTURE",
                page_description="Port forwarding, WiFi controls, and connectivity checks.",
                tabs=(
                    TabMeta("forward", "Port Forward", "ADB TCP forward and reverse rules."),
                    TabMeta("wifi", "WiFi", "Status, toggle, saved networks, and WLAN IP."),
                    TabMeta("connectivity", "Connectivity", "Network snapshot and ping from device."),
                ),
            ),
            PageMeta(
                id="console",
                label="Console",
                icon="terminal",
                section="INFRASTRUCTURE",
                page_description="ADB shell, live logcat, and background job output.",
                tabs=(
                    TabMeta("terminal", "Terminal", "Interactive shell and live logcat stream."),
                    TabMeta("jobs", "Job Monitor", "Metasploit handlers, scans, and long tasks."),
                ),
            ),
        ],
    ),
    (
        "ADVANCED",
        [
            PageMeta(
                id="exploit",
                label="Exploit",
                icon="security",
                section="ADVANCED",
                page_description="Metasploit meterpreter attack flow (authorized testing only).",
            ),
            PageMeta(
                id="system",
                label="System",
                icon="bug_report",
                section="ADVANCED",
                page_description="Logs, developer settings, and security heuristics.",
                tabs=(
                    TabMeta("logs", "Logs", "Save logcat snippets; live stream on Console page."),
                    TabMeta("config", "Configuration", "Developer settings, locale, screen stay-on."),
                    TabMeta("security", "Security Check", "Root and build heuristics."),
                ),
            ),
        ],
    ),
    (
        "CONFIG",
        [
            PageMeta(
                id="settings",
                label="Settings",
                icon="settings",
                section="CONFIG",
                page_description="Output folder, appearance, and dependencies.",
            ),
        ],
    ),
]


def all_pages() -> dict[str, PageMeta]:
    pages: dict[str, PageMeta] = {}
    for _, section_pages in NAV_SECTIONS:
        for page in section_pages:
            pages[page.id] = page
    return pages
