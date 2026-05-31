"""Global web application state."""

from __future__ import annotations

from pathlib import Path

from modules.constants import WEB_UI_HOST, WEB_UI_PORT
from modules.config import AppConfig
from modules.services.context import ServiceContext, build_context
from modules.services.jobs import JobManager, job_manager
from modules.tools import resolve_external_tools


class AppState:
    def __init__(self) -> None:
        self.config = AppConfig()
        self.active_serial: str | None = None
        self.output_dir = Path("Downloaded-Files")
        self.current_page = "home"
        self.web_host = WEB_UI_HOST
        self.web_port = WEB_UI_PORT
        self.jobs: JobManager = job_manager
        self._init_config()

    def _init_config(self) -> None:
        import platform

        self.config.operating_system = platform.system()
        if self.config.operating_system == "Windows":
            self.config.opener = "start"
        elif self.config.operating_system == "Darwin":
            self.config.opener = "open"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        resolve_external_tools(self.config)
        from modules.services.adb import set_global_adb

        set_global_adb(self.config.adb_path)

    def context(self) -> ServiceContext:
        return build_context(self.config, self.active_serial, self.output_dir)

    def tool_status(self) -> dict[str, bool]:
        c = self.config
        return {
            "ADB": bool(c.adb_path),
            "Scrcpy": bool(c.scrcpy_path),
            "Nmap": bool(c.nmap_path),
            "Metasploit": bool(c.msfvenom_path and c.msfconsole_path),
        }


state = AppState()
