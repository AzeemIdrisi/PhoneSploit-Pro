"""Device control services."""

from __future__ import annotations

from modules.services.adb import ADBService, OperationResult


_DEVICE_PROPS = {
    "Model": ["getprop", "ro.product.model"],
    "Manufacturer": ["getprop", "ro.product.manufacturer"],
    "Chipset": ["getprop", "ro.product.board"],
    "Android Version": ["getprop", "ro.build.version.release"],
    "Security Patch": ["getprop", "ro.build.version.security_patch"],
    "Device": ["getprop", "ro.product.vendor.device"],
    "SIM Operator": ["getprop", "gsm.sim.operator.alpha"],
    "Encryption": ["getprop", "ro.crypto.state"],
    "Build Date": ["getprop", "ro.build.date"],
    "SDK Version": ["getprop", "ro.build.version.sdk"],
    "WiFi Interface": ["getprop", "wifi.interface"],
}


def get_device_info(adb: ADBService) -> OperationResult:
    props = {
        label: adb.output(["shell"] + cmd) for label, cmd in _DEVICE_PROPS.items()
    }
    return OperationResult(True, "Device information", data=props)


def get_battery_info(adb: ADBService) -> OperationResult:
    raw = adb.output(["shell", "dumpsys", "battery"])
    rows: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            rows[key.strip()] = value.strip()
    return OperationResult(True, "Battery information", data=rows)


def reboot(adb: ADBService, mode: str = "system") -> OperationResult:
    if mode == "system":
        r = adb.run(["reboot"])
    elif mode in ("recovery", "bootloader", "fastboot"):
        r = adb.run(["reboot", mode])
    else:
        return OperationResult(False, f"Invalid reboot mode: {mode}")
    if r.returncode == 0:
        return OperationResult(True, f"Rebooting to {mode}")
    return OperationResult(False, (r.stdout + r.stderr).strip() or "Reboot failed")


def power_off(adb: ADBService) -> OperationResult:
    r = adb.run(["shell", "reboot", "-p"])
    if r.returncode == 0:
        return OperationResult(True, "Powering off device")
    return OperationResult(False, (r.stdout + r.stderr).strip() or "Failed")


def unlock_device(adb: ADBService, password: str = "") -> OperationResult:
    adb.run(["shell", "input", "keyevent", "26"])
    adb.run(["shell", "input", "swipe", "200", "900", "200", "300", "200"])
    if password:
        adb.run(["shell", "input", "text", password])
    adb.run(["shell", "input", "keyevent", "66"])
    return OperationResult(True, "Unlock sequence sent")


def lock_device(adb: ADBService) -> OperationResult:
    adb.run(["shell", "input", "keyevent", "26"])
    return OperationResult(True, "Device locked")
