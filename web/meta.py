"""Project metadata for the web UI."""

from __future__ import annotations

from modules.constants import VERSION

APP_NAME = "PhoneSploit Pro"
WEB_UI_LABEL = f"{VERSION} Web UI"
TAGLINE = "All-in-one Android ADB toolkit with Metasploit integration."

AUTHOR = "Azeem Idrisi"
AUTHOR_HANDLE = "AzeemIdrisi"
AUTHOR_GITHUB = f"https://github.com/{AUTHOR_HANDLE}"
GITHUB_REPO = f"https://github.com/{AUTHOR_HANDLE}/PhoneSploit-Pro"
GITHUB_ISSUES = f"{GITHUB_REPO}/issues"
GITHUB_DOCS = f"{GITHUB_REPO}#readme"
LICENSE = "GPL-3.0"
LICENSE_URL = "https://www.gnu.org/licenses/gpl-3.0.html"
COPYRIGHT_YEAR = "© 2026"

SUPPORT_LINKS: tuple[tuple[str, str], ...] = (
    ("PayPal", "https://paypal.me/AzeemIdrisi"),
    ("Buy Me a Coffee", "https://www.buymeacoffee.com/AzeemIdrisi"),
)

DISCLAIMER = (
    "For authorized security testing and education only. "
    "Do not use on devices without explicit permission."
)
