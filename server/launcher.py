"""Start the web console from the CLI menu."""

from __future__ import annotations

import threading
import webbrowser

import uvicorn

from modules.console import print_info, print_success


def launch_web_interface() -> None:
    url = "http://127.0.0.1:8765"
    print_info("Starting the web console on localhost. There is no login — do not expose this port.")

    def _serve() -> None:
        uvicorn.run("server.app:app", host="127.0.0.1", port=8765, log_level="warning")

    thread = threading.Thread(target=_serve, name="phonesploit-web", daemon=True)
    thread.start()
    webbrowser.open(url)
    print_success(f"Web console: {url}")
    print_info("Leave PhoneSploit Pro running. The console stops when this process exits.")
