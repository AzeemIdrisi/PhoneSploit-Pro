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
    return_to_main: bool = False
    adb_path: str | None = None
    msfvenom_path: str | None = None
    msfconsole_path: str | None = None
    scrcpy_path: str | None = None
    nmap_path: str | None = None
    hardax_argv0: list[str] | None = None
    lockknife_path: str | None = None
    drozer_path: str | None = None
    frida_path: str | None = None
    objection_path: str | None = None
    aleapp_argv0: list[str] | None = None
    mobsf_url: str = "http://127.0.0.1:8000"
    mobsf_api_key: str | None = None
    ext_target_package: str | None = None
    lockknife_case_dir: str | None = None
