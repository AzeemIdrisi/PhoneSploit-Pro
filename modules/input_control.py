from modules.config import AppConfig
from modules.console import (
    console,
    print_success,
    print_error,
    adb,
    ask,
)


def _keyevent(config: AppConfig, code: str, label: str) -> None:
    adb(["shell", "input", "keyevent", code])
    print_success(label)


def keycode_text(config: AppConfig) -> None:
    text = ask("[bold cyan]Text[/bold cyan]> ")
    adb(["shell", "input", "text", text])
    print_success(f'Entered: "{text}"')


def keycode(config: AppConfig, code: str, label: str) -> None:
    _keyevent(config, code, label)


KEYCODE_MAP = {
    "keycode_home": ("3", "Home"),
    "keycode_back": ("4", "Back"),
    "keycode_recent": ("187", "Recent apps"),
    "keycode_power": ("26", "Power"),
    "keycode_dpad_up": ("19", "DPAD up"),
    "keycode_dpad_down": ("20", "DPAD down"),
    "keycode_dpad_left": ("21", "DPAD left"),
    "keycode_dpad_right": ("22", "DPAD right"),
    "keycode_delete": ("67", "Delete"),
    "keycode_enter": ("66", "Enter"),
    "keycode_vol_up": ("24", "Volume up"),
    "keycode_vol_down": ("25", "Volume down"),
    "keycode_media_play": ("126", "Media play"),
    "keycode_media_pause": ("127", "Media pause"),
    "keycode_tab": ("61", "Tab"),
    "keycode_esc": ("111", "Esc"),
}


def _keycode_handler(config: AppConfig, code: str, label: str) -> None:
    _keyevent(config, code, label)