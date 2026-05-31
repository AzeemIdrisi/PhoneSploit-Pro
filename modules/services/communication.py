"""Communication services."""

from __future__ import annotations

from modules.services.adb import ADBService, OperationResult


def send_sms(adb: ADBService, number: str, message: str) -> OperationResult:
    if not number or not message:
        return OperationResult(False, "Number and message required")
    adb.run(
        [
            "shell",
            "service",
            "call",
            "isms",
            "5",
            "i32",
            "0",
            "s16",
            "com.android.mms.service",
            "s16",
            "null",
            "s16",
            number,
            "s16",
            "null",
            "s16",
            message,
            "s16",
            "null",
            "s16",
            "null",
            "s16",
            "null",
            "s16",
            "null",
        ]
    )
    return OperationResult(True, f"SMS sent to {number}")


def open_link(adb: ADBService, url: str) -> OperationResult:
    if not url:
        return OperationResult(False, "URL required")
    adb.run(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url])
    return OperationResult(True, f"Opened: {url}")
