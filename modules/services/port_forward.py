"""Port forwarding services."""

from __future__ import annotations

from modules.services.adb import ADBService, OperationResult


def forward_port(adb: ADBService, local_port: int, remote_port: int) -> OperationResult:
    r = adb.run(
        ["forward", f"tcp:{local_port}", f"tcp:{remote_port}"],
        host_level=True,
    )
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        return OperationResult(
            True,
            out or f"Forwarded tcp:{local_port} → device tcp:{remote_port}",
        )
    return OperationResult(False, out or "forward failed")


def reverse_port(adb: ADBService, device_port: int, host_port: int) -> OperationResult:
    r = adb.run(
        ["reverse", f"tcp:{device_port}", f"tcp:{host_port}"],
        host_level=True,
    )
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        return OperationResult(
            True,
            out or f"Reverse tcp:{device_port} → host tcp:{host_port}",
        )
    return OperationResult(False, out or "reverse failed")


def list_forwards(adb: ADBService) -> OperationResult:
    r = adb.run(["forward", "--list"], host_level=True)
    text = (r.stdout + r.stderr).strip()
    return OperationResult(True, text or "(no rules)", data=text)


def remove_forward(adb: ADBService, spec: str) -> OperationResult:
    r = adb.run(["forward", "--remove", spec], host_level=True)
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        return OperationResult(True, out or "Removed")
    return OperationResult(False, out or "remove failed")


def remove_all_forwards(adb: ADBService) -> OperationResult:
    r = adb.run(["forward", "--remove-all"], host_level=True)
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        return OperationResult(True, out or "All forwarding rules removed")
    return OperationResult(False, out or "failed")
