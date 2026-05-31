"""Input / keycode services."""

from __future__ import annotations

from modules.services.adb import ADBService, OperationResult

KEYCODES: dict[str, list[str]] = {
    "home": ["shell", "input", "keyevent", "3"],
    "back": ["shell", "input", "keyevent", "4"],
    "recents": ["shell", "input", "keyevent", "187"],
    "power": ["shell", "input", "keyevent", "26"],
    "dpad_up": ["shell", "input", "keyevent", "19"],
    "dpad_down": ["shell", "input", "keyevent", "20"],
    "dpad_left": ["shell", "input", "keyevent", "21"],
    "dpad_right": ["shell", "input", "keyevent", "22"],
    "delete": ["shell", "input", "keyevent", "67"],
    "enter": ["shell", "input", "keyevent", "66"],
    "volume_up": ["shell", "input", "keyevent", "24"],
    "volume_down": ["shell", "input", "keyevent", "25"],
    "media_play": ["shell", "input", "keyevent", "126"],
    "media_pause": ["shell", "input", "keyevent", "127"],
    "tab": ["shell", "input", "keyevent", "61"],
    "esc": ["shell", "input", "keyevent", "111"],
}


def send_keycode(adb: ADBService, name: str) -> OperationResult:
    args = KEYCODES.get(name)
    if not args:
        return OperationResult(False, f"Unknown keycode: {name}")
    adb.run(args)
    return OperationResult(True, name.replace("_", " ").title())


def send_text(adb: ADBService, text: str) -> OperationResult:
    adb.run(["shell", "input", "text", text])
    return OperationResult(True, f'Entered: "{text}"')
