#!/usr/bin/env python3
"""PhoneSploit Pro — Web UI entry point."""

from modules.constants import WEB_UI_HOST, WEB_UI_PORT
from web.app import run

if __name__ == "__main__":
    run(host=WEB_UI_HOST, port=WEB_UI_PORT)
