from dataclasses import dataclass, field


@dataclass
class AppConfig:
    operating_system: str = ""
    clear_cmd: str = "clear"
    opener: str = "xdg-open"
    screenshot_location: str = ""
    screenrecord_location: str = ""
    pull_location: str = ""
    run: bool = True
    page_number: int = 0
    # Resolved at startup (see modules.tools.resolve_external_tools)
    adb_path: str | None = None
    msfvenom_path: str | None = None
    msfconsole_path: str | None = None
    scrcpy_path: str | None = None
    nmap_path: str | None = None
