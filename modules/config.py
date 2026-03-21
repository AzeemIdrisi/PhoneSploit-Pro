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
