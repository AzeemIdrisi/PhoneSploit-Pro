"""Root heuristics service."""

from __future__ import annotations

from modules.root_check import _verdict
from modules.services.adb import ADBService, OperationResult


def root_heuristics(adb: ADBService) -> OperationResult:
    props = {
        "ro.build.type": adb.output(["shell", "getprop", "ro.build.type"]),
        "ro.build.tags": adb.output(["shell", "getprop", "ro.build.tags"]),
        "ro.debuggable": adb.output(["shell", "getprop", "ro.debuggable"]),
        "ro.secure": adb.output(["shell", "getprop", "ro.secure"]),
        "service.adb.root": adb.output(["shell", "getprop", "service.adb.root"]),
        "ro.boot.flash.locked": adb.output(["shell", "getprop", "ro.boot.flash.locked"]),
        "ro.boot.verifiedbootstate": adb.output(
            ["shell", "getprop", "ro.boot.verifiedbootstate"]
        ),
    }

    shell_uid = adb.output(["shell", "sh", "-c", "id 2>/dev/null | head -1"])
    which_su = adb.output(["shell", "sh", "-c", "which su 2>/dev/null"])
    su_bin = adb.output(
        ["shell", "sh", "-c", "ls -l /system/xbin/su /system/bin/su 2>/dev/null | head -2"]
    )
    magisk_bins = adb.output(
        [
            "shell",
            "sh",
            "-c",
            "ls /data/adb/magisk/magisk 2>/dev/null; "
            "ls /sbin/magisk 2>/dev/null; which magisk 2>/dev/null",
        ]
    )
    r_pkg = adb.run(["shell", "pm", "path", "com.topjohnwu.magisk"])
    magisk_pkg = (r_pkg.stdout + r_pkg.stderr).strip()

    verdict, detail = _verdict(props, which_su, su_bin, magisk_bins, magisk_pkg)

    return OperationResult(
        True,
        verdict,
        data={
            "props": props,
            "shell_uid": shell_uid,
            "which_su": which_su,
            "su_bin": su_bin,
            "magisk_bins": magisk_bins,
            "magisk_pkg": magisk_pkg,
            "verdict": verdict,
            "detail": detail,
        },
    )
