"""FastAPI application for the PhoneSploit web console."""

from __future__ import annotations

import asyncio
import shutil
import subprocess
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import anyio
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from modules.console import get_adb_executable
from modules.services.catalog import HOST_IDS, build_catalog
from modules.services.dispatch import SPECIAL_IDS, run_feature
from modules.services.operations import (
    downloads_dir,
    install_apk,
    install_splits,
    list_files,
    push_and_view,
    push_path,
    set_wallpaper,
)
from modules.services.runner import AdbError, run_bytes, validate_serial
from modules.services import operations as ops
from server.state import CONFIG, JOBS, SESSIONS, bind_loop

ROOT = Path(__file__).resolve().parent.parent
WEBUI_OUT = ROOT / "webui" / "out"

LONG_RUNNING = frozenset(
    {
        "scan_network",
        "copy_whatsapp",
        "copy_screenshots",
        "copy_camera",
        "dump_sms",
        "dump_contacts",
        "dump_call_logs",
        "screenrecord",
        "anon_screenrecord",
        "extract_apk",
        "metasploit",
        "vuln_full_audit",
        "vuln_patch_cve",
        "vuln_hardening",
        "vuln_app_surface",
        "nearby_wifi",
    }
)

MIME = {
    "open_photo": "image/jpeg",
    "open_audio": "audio/mp3",
    "open_video": "video/mp4",
}


class ActionBody(BaseModel):
    params: dict[str, Any] = Field(default_factory=dict)


class SessionBody(BaseModel):
    feature: str
    params: dict[str, Any] = Field(default_factory=dict)


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    bind_loop(asyncio.get_running_loop())
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="PhoneSploit Pro", version="2.4", lifespan=_lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    async def health() -> dict[str, Any]:
        return {
            "ok": True,
            "adb": bool(CONFIG.adb_path),
            "scrcpy": bool(CONFIG.scrcpy_path),
            "nmap": bool(CONFIG.nmap_path),
            "metasploit": bool(CONFIG.msfvenom_path and CONFIG.msfconsole_path),
            "hardax": bool(CONFIG.hardax_argv0),
            "bind": "127.0.0.1",
        }

    @app.get("/api/catalog")
    async def catalog() -> dict[str, Any]:
        return build_catalog()

    @app.get("/api/devices")
    async def devices() -> dict[str, Any]:
        return await anyio.to_thread.run_sync(ops.list_devices)

    @app.get("/api/interfaces")
    async def interfaces() -> dict[str, Any]:
        return ops.local_interfaces()

    @app.get("/api/jobs")
    async def jobs() -> dict[str, Any]:
        return {"jobs": JOBS.list()}

    @app.post("/api/jobs/{job_id}/cancel")
    async def cancel_job(job_id: str) -> dict[str, bool]:
        if not JOBS.cancel(job_id):
            raise HTTPException(404, "Job not found.")
        return {"ok": True}

    @app.get("/api/sessions")
    async def sessions() -> dict[str, Any]:
        return {"sessions": SESSIONS.list()}

    @app.post("/api/sessions")
    async def start_session(body: SessionBody, serial: str) -> dict[str, Any]:
        serial = _serial(serial)
        try:
            argv = ops.scrcpy_args(CONFIG, serial, body.feature, body.params)
        except AdbError as exc:
            raise HTTPException(400, str(exc)) from exc
        if not CONFIG.scrcpy_path:
            raise HTTPException(400, "scrcpy is not installed.")
        try:
            process = subprocess.Popen(argv)
        except OSError as exc:
            raise HTTPException(500, str(exc)) from exc
        artifact = next((part.split("=", 1)[1] for part in argv if part.startswith("--record=")), None)
        session = SESSIONS.add(body.feature, serial, process, artifact)
        return {"ok": True, "session": session.id, "artifact": artifact}

    @app.delete("/api/sessions/{session_id}")
    async def stop_session(session_id: str) -> dict[str, bool]:
        if not SESSIONS.stop(session_id):
            raise HTTPException(404, "Session not found.")
        return {"ok": True}

    @app.post("/api/actions/{feature_id}")
    async def host_action(feature_id: str, body: ActionBody) -> dict[str, Any]:
        if feature_id not in HOST_IDS:
            raise HTTPException(400, "This action needs a device.")
        return await _run(feature_id, "", body.params)

    @app.post("/api/devices/{serial}/actions/{feature_id}")
    async def device_action(serial: str, feature_id: str, body: ActionBody) -> dict[str, Any]:
        return await _run(feature_id, _serial(serial), body.params)

    @app.get("/api/devices/{serial}/files")
    async def files(serial: str, path: str = "/sdcard") -> dict[str, Any]:
        serial = _serial(serial)

        def work() -> dict[str, Any]:
            return list_files(serial, path)

        try:
            return await anyio.to_thread.run_sync(work)
        except AdbError as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.post("/api/devices/{serial}/upload")
    async def upload(
        serial: str,
        purpose: str = Form(...),
        destination: str = Form(""),
        files: list[UploadFile] = File(...),
    ) -> dict[str, Any]:
        serial = _serial(serial)
        if purpose not in {"install", "split", "push", "wallpaper", "photo", "audio", "video"}:
            raise HTTPException(400, "Unknown upload purpose.")
        saved = []
        inbox = downloads_dir() / "uploads"
        inbox.mkdir(parents=True, exist_ok=True)
        for upload_file in files:
            name = Path(upload_file.filename or "upload.bin").name
            if not name or name.startswith("."):
                raise HTTPException(400, "Invalid file name.")
            target = inbox / name
            target.write_bytes(await upload_file.read())
            saved.append(target)

        def work() -> dict[str, Any]:
            if purpose == "install":
                return install_apk(serial, saved[0])
            if purpose == "split":
                return install_splits(serial, saved)
            if purpose == "push":
                return push_path(serial, saved[0], destination)
            if purpose == "wallpaper":
                return set_wallpaper(serial, saved[0])
            return push_and_view(serial, saved[0], MIME[{"photo": "open_photo", "audio": "open_audio", "video": "open_video"}[purpose]])

        try:
            return await anyio.to_thread.run_sync(work)
        except AdbError as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.get("/api/artifacts")
    async def artifact(path: str) -> FileResponse:
        resolved = _safe_artifact(path)
        if resolved.is_dir():
            archive = await anyio.to_thread.run_sync(
                lambda: shutil.make_archive(str(resolved), "zip", root_dir=str(resolved))
            )
            return FileResponse(archive, filename=f"{resolved.name}.zip")
        return FileResponse(resolved)

    @app.websocket("/ws/devices")
    async def devices_ws(socket: WebSocket) -> None:
        await socket.accept()
        try:
            while True:
                payload = await anyio.to_thread.run_sync(ops.list_devices)
                await socket.send_json(payload.get("data") or {"devices": []})
                await asyncio.sleep(2)
        except WebSocketDisconnect:
            return

    @app.websocket("/ws/jobs")
    async def jobs_ws(socket: WebSocket) -> None:
        await socket.accept()
        queue = JOBS.subscribe()
        try:
            await socket.send_json({"jobs": JOBS.list()})
            while True:
                payload = await queue.get()
                await socket.send_json({"job": payload})
        except WebSocketDisconnect:
            return
        finally:
            JOBS.unsubscribe(queue)

    @app.websocket("/ws/devices/{serial}/screen")
    async def screen_ws(socket: WebSocket, serial: str) -> None:
        serial = _serial(serial)
        await socket.accept()

        async def pump() -> None:
            while True:
                code, data, _err = await anyio.to_thread.run_sync(
                    lambda: run_bytes(["exec-out", "screencap", "-p"], serial=serial, timeout=8)
                )
                if code == 0 and data.startswith(b"\x89PNG"):
                    await socket.send_bytes(data)
                await asyncio.sleep(0.35)

        async def read_input() -> None:
            while True:
                message = await socket.receive_json()
                kind = message.get("type")
                if kind == "tap":
                    x, y = int(message["x"]), int(message["y"])
                    await anyio.to_thread.run_sync(lambda: ops.tap(serial, x, y))
                elif kind == "swipe":
                    points = (int(message["x1"]), int(message["y1"]), int(message["x2"]), int(message["y2"]))
                    await anyio.to_thread.run_sync(lambda: ops.swipe(serial, *points))
                elif kind == "text":
                    text = str(message.get("text") or "")
                    await anyio.to_thread.run_sync(lambda: ops.key_text(serial, {"text": text}))
                elif kind == "key":
                    code = str(message.get("code") or "3")
                    await anyio.to_thread.run_sync(lambda: ops.keyevent(serial, code, "key"))

        try:
            async with anyio.create_task_group() as group:
                group.start_soon(pump)
                group.start_soon(read_input)
        except WebSocketDisconnect:
            return
        except Exception:
            await socket.close()

    @app.websocket("/ws/devices/{serial}/logcat")
    async def logcat_ws(socket: WebSocket, serial: str) -> None:
        serial = _serial(serial)
        await socket.accept()
        exe = get_adb_executable()
        if not exe:
            await socket.send_json({"line": "ADB is not available."})
            await socket.close()
            return
        process = subprocess.Popen(
            [exe, "-s", serial, "logcat", "-v", "time"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        try:
            assert process.stdout is not None
            while True:
                line = await anyio.to_thread.run_sync(process.stdout.readline)
                if not line:
                    break
                await socket.send_json({"line": line.rstrip("\n")})
        except WebSocketDisconnect:
            pass
        finally:
            process.terminate()

    @app.websocket("/ws/pty")
    async def pty_ws(socket: WebSocket, mode: str = "shell", serial: str = "") -> None:
        await socket.accept()
        argv = _pty_argv(mode, serial)
        if argv is None:
            await socket.send_text("\r\nThis terminal mode is not available.\r\n")
            await socket.close()
            return
        try:
            from server.pty_bridge import spawn

            process = spawn(argv)
        except Exception as exc:
            await socket.send_text(f"\r\nCould not start terminal: {exc}\r\n")
            await socket.close()
            return

        async def read_pty() -> None:
            while process.isalive():
                try:
                    data = await anyio.to_thread.run_sync(lambda: process.read(4096))
                except EOFError:
                    break
                except Exception:
                    break
                if data:
                    text = data.decode("utf-8", errors="replace") if isinstance(data, bytes) else str(data)
                    await socket.send_text(text)

        async def write_pty() -> None:
            while True:
                message = await socket.receive_text()
                text = message if isinstance(message, str) else message.decode("utf-8", errors="replace")
                await anyio.to_thread.run_sync(lambda: process.write(text))

        try:
            async with anyio.create_task_group() as group:
                group.start_soon(read_pty)
                group.start_soon(write_pty)
        except WebSocketDisconnect:
            pass
        finally:
            if process.isalive():
                process.terminate(force=True)

    if WEBUI_OUT.is_dir():
        app.mount("/", StaticFiles(directory=WEBUI_OUT, html=True), name="webui")

    return app


def _serial(serial: str) -> str:
    try:
        return validate_serial(serial)
    except AdbError as exc:
        raise HTTPException(400, str(exc)) from exc


def _safe_artifact(raw: str) -> Path:
    root = downloads_dir().resolve()
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        resolved = candidate.resolve()
    except OSError as exc:
        raise HTTPException(400, "Invalid path.") from exc
    if not resolved.is_relative_to(root) or not resolved.exists():
        raise HTTPException(404, "Artifact not found.")
    return resolved


async def _run(feature_id: str, serial: str, params: dict[str, Any]) -> dict[str, Any]:
    if feature_id in SPECIAL_IDS and feature_id != "metasploit":
        raise HTTPException(400, f"{feature_id} uses a dedicated endpoint.")
    if feature_id == "scan_network":
        job = JOBS.create(feature_id)

        def work() -> None:
            def on_event(event: dict[str, Any]) -> None:
                progress = event.get("progress")
                JOBS.update(
                    job,
                    status="running",
                    message=str(event.get("message") or ""),
                    progress=None if progress is None else float(progress),
                    data={"subnet": event.get("subnet"), "hosts": event.get("hosts") or []},
                )

            try:
                result = ops.scan_network(
                    CONFIG,
                    on_event=on_event,
                    should_cancel=lambda: JOBS.is_cancelled(job.id),
                )
            except (AdbError, ValueError) as exc:
                JOBS.update(job, status="error", message=str(exc))
                return
            except Exception as exc:
                JOBS.update(job, status="error", message=str(exc))
                return

            data = result.get("data")
            if isinstance(data, dict) and data.get("cancelled"):
                status = "canceled"
            elif result.get("ok"):
                status = "done"
            else:
                status = "error"
            JOBS.update(
                job,
                status=status,
                message=result.get("message") or "",
                data=data,
                artifact=result.get("artifact"),
            )

        asyncio.get_running_loop().run_in_executor(None, work)
        return {"ok": True, "job": job.to_dict(), "message": "Started."}

    if feature_id in LONG_RUNNING:
        job = JOBS.create(feature_id)

        def work() -> None:
            try:
                result = run_feature(feature_id, serial, params, CONFIG)
                JOBS.update(
                    job,
                    status="done" if result.get("ok") else "error",
                    message=result.get("message") or "",
                    artifact=result.get("artifact"),
                    data=result.get("data"),
                )
            except (AdbError, ValueError) as exc:
                JOBS.update(job, status="error", message=str(exc))
            except Exception as exc:
                JOBS.update(job, status="error", message=str(exc))

        asyncio.get_running_loop().run_in_executor(None, work)
        return {"ok": True, "job": job.to_dict(), "message": "Started."}

    def call() -> dict[str, Any]:
        return run_feature(feature_id, serial, params, CONFIG)

    try:
        return await anyio.to_thread.run_sync(call)
    except AdbError as exc:
        raise HTTPException(400, str(exc)) from exc


def _pty_argv(mode: str, serial: str) -> list[str] | None:
    exe = get_adb_executable()
    if mode == "shell":
        if not exe:
            return None
        try:
            checked = validate_serial(serial)
        except AdbError:
            return None
        return [exe, "-s", checked, "shell"]
    if mode == "metasploit":
        binary = CONFIG.msfconsole_path or "msfconsole"
        return [binary]
    return None


app = create_app()
