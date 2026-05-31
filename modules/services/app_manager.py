"""App management services."""

from __future__ import annotations

from pathlib import Path

from modules.services.adb import ADBService, OperationResult
from modules.services.context import ServiceContext


def list_third_party_apps(adb: ADBService) -> list[str]:
    raw = adb.output(["shell", "pm", "list", "packages", "-3"])
    return [line.replace("package:", "").strip() for line in raw.splitlines() if line.strip()]


def list_all_apps(adb: ADBService) -> list[str]:
    raw = adb.output(["shell", "pm", "list", "packages"])
    return [line.replace("package:", "").strip() for line in raw.splitlines() if line.strip()]


def list_apps(adb: ADBService, third_party_only: bool = True) -> OperationResult:
    apps = list_third_party_apps(adb) if third_party_only else list_all_apps(adb)
    return OperationResult(True, f"{len(apps)} package(s)", data=apps)


def install_app(adb: ADBService, apk_path: Path) -> OperationResult:
    if not apk_path.is_file():
        return OperationResult(False, "APK file not found", error="missing file")
    result = adb.run(["install", "-r", str(apk_path)])
    output = (result.stdout + result.stderr).strip()
    if "Success" in output:
        return OperationResult(True, f"Installed: {apk_path.name}")
    return OperationResult(False, f"Installation failed: {output}", error=output)


def uninstall_app(adb: ADBService, package_name: str) -> OperationResult:
    result = adb.run(["uninstall", package_name])
    output = (result.stdout + result.stderr).strip()
    if "Success" in output:
        return OperationResult(True, f"Uninstalled: {package_name}")
    return OperationResult(False, f"Uninstall failed: {output}", error=output)


def launch_app(adb: ADBService, package_name: str) -> OperationResult:
    adb.run(["shell", "monkey", "-p", package_name, "1"])
    return OperationResult(True, f"Launched: {package_name}")


def extract_apk(ctx: ServiceContext, package_name: str) -> OperationResult:
    adb = ctx.adb
    out_dir = ctx.ensure_output_dir()
    file_name = package_name.replace(".", "_") + ".apk"
    dest = out_dir / file_name

    path_output = adb.output(["shell", "pm", "path", package_name])
    lines = [l.strip() for l in path_output.splitlines() if l.strip().startswith("package:")]
    paths = [l.replace("package:", "").strip() for l in lines]
    if not paths:
        return OperationResult(False, f"App not found: {package_name}")

    apk_path = None
    for p in paths:
        if p.endswith("base.apk") or "/base.apk" in p:
            apk_path = p
            break
    if apk_path is None:
        apk_path = paths[0]

    pull_result = adb.run(["pull", apk_path])
    if pull_result.returncode != 0:
        return OperationResult(
            False,
            (pull_result.stdout + pull_result.stderr).strip() or "adb pull failed",
        )

    pulled_name = Path(apk_path).name
    src = Path(pulled_name)
    if not src.is_file() and Path("base.apk").is_file():
        src = Path("base.apk")

    try:
        if src.is_file():
            src.rename(dest)
            return OperationResult(True, f"Saved to: {dest}", data=str(dest))
        return OperationResult(False, "Pulled APK not found after adb pull")
    except FileExistsError:
        return OperationResult(False, f"APK already exists at {dest}")
    except OSError as e:
        return OperationResult(False, str(e))


def force_stop_app(adb: ADBService, package_name: str) -> OperationResult:
    r = adb.run(["shell", "am", "force-stop", package_name])
    if r.returncode == 0:
        return OperationResult(True, f"Force-stopped: {package_name}")
    return OperationResult(False, (r.stdout + r.stderr).strip() or "failed")


def clear_app_data(adb: ADBService, package_name: str) -> OperationResult:
    r = adb.run(["shell", "pm", "clear", package_name])
    out = (r.stdout + r.stderr).strip()
    if "Success" in out or r.returncode == 0:
        return OperationResult(True, out or "Cleared")
    return OperationResult(False, out or "failed")


def restart_app(adb: ADBService, package_name: str) -> OperationResult:
    adb.run(["shell", "am", "force-stop", package_name])
    r = adb.run(
        [
            "shell",
            "monkey",
            "-p",
            package_name,
            "-c",
            "android.intent.category.LAUNCHER",
            "1",
        ]
    )
    if r.returncode == 0:
        return OperationResult(True, f"Restarted: {package_name}")
    return OperationResult(False, (r.stdout + r.stderr).strip() or "launch failed")


def install_split_apks(adb: ADBService, paths: list[Path]) -> OperationResult:
    for p in paths:
        if not p.is_file():
            return OperationResult(False, f"Not a file: {p}")
    args = ["install-multiple", "-r"] + [str(p) for p in paths]
    r = adb.run(args)
    out = (r.stdout + r.stderr).strip()
    if "Success" in out:
        return OperationResult(True, out)
    return OperationResult(False, out or "failed")
