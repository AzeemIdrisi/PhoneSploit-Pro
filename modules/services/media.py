"""Media capture and scrcpy services."""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

from modules.config import AppConfig
from modules.services.adb import ADBService, OperationResult
from modules.services.context import ServiceContext
from modules.tools import scrcpy_argv


def _timestamp() -> str:
    now = datetime.now()
    return f"{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}-{now.second}"


def get_android_version(adb: ADBService) -> int | None:
    raw = adb.output(["shell", "getprop", "ro.build.version.release"])
    try:
        return int(raw.split(".")[0])
    except (ValueError, IndexError):
        return None


def take_screenshot(ctx: ServiceContext, anonymous: bool = False) -> OperationResult:
    file_name = f"screenshot-{_timestamp()}.png"
    remote = f"/sdcard/{file_name}"
    out_dir = ctx.ensure_output_dir()

    ctx.adb.run(["shell", "screencap", "-p", remote])
    result = ctx.adb.run(["pull", remote, str(out_dir)])
    if anonymous:
        ctx.adb.run(["shell", "rm", remote])

    local_path = out_dir / file_name
    if result.returncode == 0:
        return OperationResult(True, f"Saved to: {local_path}", data=str(local_path))
    return OperationResult(False, (result.stdout + result.stderr).strip())


def screen_record(ctx: ServiceContext, duration_sec: int, anonymous: bool = False) -> OperationResult:
    if duration_sec < 1:
        return OperationResult(False, "Duration must be at least 1 second")

    file_name = f"vid-{_timestamp()}.mp4"
    remote = f"/sdcard/{file_name}"
    out_dir = ctx.ensure_output_dir()
    adb = ctx.adb

    if not adb.available():
        return OperationResult(False, "ADB not available")

    cmd = adb._build_cmd(
        ["shell", "screenrecord", "--time-limit", str(duration_sec), remote]
    )
    rec = subprocess.run(cmd, capture_output=True, text=True)
    if rec.returncode != 0:
        detail = (rec.stdout + rec.stderr).strip() or f"exit code {rec.returncode}"
        return OperationResult(False, f"screenrecord failed: {detail}")

    result = adb.run(["pull", remote, str(out_dir)])
    if anonymous:
        adb.run(["shell", "rm", remote])

    local_path = out_dir / file_name
    if result.returncode == 0:
        return OperationResult(True, f"Saved to: {local_path}", data=str(local_path))
    return OperationResult(False, (result.stdout + result.stderr).strip())


def push_and_open_media(
    adb: ADBService,
    local_path: Path,
    intent_type: str,
) -> OperationResult:
    if not local_path.is_file():
        return OperationResult(False, "File not found")
    adb.run(["push", str(local_path), "/sdcard/"])
    fn = local_path.name
    adb.run(
        [
            "shell",
            "am",
            "start",
            "-a",
            "android.intent.action.VIEW",
            "-d",
            f"file:///sdcard/{fn}",
            "-t",
            intent_type,
        ]
    )
    return OperationResult(True, f"Opened: {fn}")


def launch_scrcpy(
    config: AppConfig,
    extra_args: list[str] | None = None,
) -> OperationResult:
    if not config.scrcpy_path:
        return OperationResult(False, "Scrcpy not available")
    args = scrcpy_argv(config, extra_args or [])
    subprocess.Popen(args)
    return OperationResult(True, "Scrcpy launched in native window")


def mirror_mode(config: AppConfig, mode: str, **kwargs: str) -> OperationResult:
    if mode == "default":
        return launch_scrcpy(config, [])
    if mode == "fast":
        return launch_scrcpy(config, ["-m", "1024", "-b", "1M"])
    if mode == "custom":
        extra: list[str] = []
        if kwargs.get("size"):
            extra += ["-m", kwargs["size"]]
        if kwargs.get("bitrate"):
            extra += ["-b", f"{kwargs['bitrate']}M"]
        if kwargs.get("fps"):
            extra += [f"--max-fps={kwargs['fps']}"]
        return launch_scrcpy(config, extra)
    return OperationResult(False, "Invalid mirror mode")


def camera_live(
    config: AppConfig,
    adb: ADBService,
    facing: str = "front",
    orientation: str = "0",
    mode: str = "default",
    **kwargs: str,
) -> OperationResult:
    ver = get_android_version(adb)
    if ver is None:
        return OperationResult(False, "No connected device")
    if ver < 12:
        return OperationResult(False, "Camera Live requires Android 12+")

    args = [
        "--video-source=camera",
        f"--camera-facing={facing}",
        f"--capture-orientation={orientation}",
        "--no-audio",
        "--no-control",
        f"--window-title=PhoneSploit Camera Live ({facing})",
    ]
    if mode == "fast":
        args += ["--camera-size=1280x720", "--camera-fps=15", "-b", "4M"]
    elif mode == "custom":
        if kwargs.get("size"):
            args.append(f"--camera-size={kwargs['size']}")
        if kwargs.get("fps"):
            args.append(f"--camera-fps={kwargs['fps']}")
        if kwargs.get("bitrate"):
            args += ["-b", f"{kwargs['bitrate']}M"]

    if not config.scrcpy_path:
        return OperationResult(False, "Scrcpy not available")
    subprocess.Popen(scrcpy_argv(config, args))
    return OperationResult(True, "Camera live launched")


def stream_audio(config: AppConfig, mode: str) -> OperationResult:
    if not config.scrcpy_path:
        return OperationResult(False, "Scrcpy not available")
    args = ["--no-video"]
    if mode == "mic":
        args.append("--audio-source=mic")
    subprocess.Popen(scrcpy_argv(config, args))
    return OperationResult(True, f"Audio stream ({mode}) launched")


def record_audio(
    config: AppConfig,
    ctx: ServiceContext,
    mode: str,
    record_only: bool = False,
) -> OperationResult:
    adb = ctx.adb
    ver = get_android_version(adb)
    if ver is None:
        return OperationResult(False, "No connected device")
    if ver < 11:
        return OperationResult(False, "Requires Android 11+")

    out_dir = ctx.ensure_output_dir()
    if mode == "mic":
        file_name = f"mic-audio-{_timestamp()}.opus"
        audio_flag = "--audio-source=mic"
    else:
        file_name = f"device-audio-{_timestamp()}.opus"
        audio_flag = ""

    save_path = str(out_dir / file_name)
    cmd_args = ["--no-video", f"--record={save_path}"]
    if record_only:
        cmd_args.insert(1, "--no-playback")
    if audio_flag:
        cmd_args.append(audio_flag)

    if not config.scrcpy_path:
        return OperationResult(False, "Scrcpy not available")
    subprocess.Popen(scrcpy_argv(config, cmd_args))
    return OperationResult(True, f"Recording to {save_path}", data=save_path)
