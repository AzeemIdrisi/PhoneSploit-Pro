"""WebSocket streaming terminal (shell + logcat)."""

from __future__ import annotations

import asyncio
import subprocess

from urllib.parse import quote

from fastapi import WebSocket, WebSocketDisconnect
from nicegui import app, ui

from web.state import state


def _ws_base() -> str:
    return f"ws://{state.web_host}:{state.web_port}"

_active_streams: dict[str, subprocess.Popen] = {}
_logcat_stop: asyncio.Event | None = None


def stop_logcat_stream() -> None:
    global _logcat_stop
    serial = state.active_serial or "default"
    stream_id = f"logcat-{serial}"
    proc = _active_streams.get(stream_id)
    if proc and proc.poll() is None:
        proc.terminate()
    if _logcat_stop is not None:
        _logcat_stop.set()


async def _stream_process(
    websocket: WebSocket,
    proc: subprocess.Popen,
    stream_id: str,
    stop_event: asyncio.Event | None = None,
) -> None:
    _active_streams[stream_id] = proc
    try:
        if proc.stdout:
            while True:
                if stop_event and stop_event.is_set():
                    break
                line = await asyncio.get_event_loop().run_in_executor(
                    None, proc.stdout.readline
                )
                if not line:
                    break
                await websocket.send_text(line.rstrip("\n\r"))
    except WebSocketDisconnect:
        pass
    finally:
        if proc.poll() is None:
            proc.terminate()
        _active_streams.pop(stream_id, None)


def register_terminal_routes() -> None:
    @app.websocket("/ws/logcat")
    async def logcat_ws(websocket: WebSocket) -> None:
        global _logcat_stop
        await websocket.accept()
        serial = websocket.query_params.get("serial") or state.active_serial
        if not state.config.adb_path:
            await websocket.send_text("[error] ADB not available")
            await websocket.close()
            return

        cmd = [state.config.adb_path]
        if serial:
            cmd.extend(["-s", serial])
        cmd.extend(["logcat", "-v", "time"])
        filt = websocket.query_params.get("filter", "")
        if filt:
            cmd.append(filt)

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        stop_event = asyncio.Event()
        _logcat_stop = stop_event
        await _stream_process(websocket, proc, f"logcat-{serial}", stop_event)

    @app.websocket("/ws/shell")
    async def shell_ws(websocket: WebSocket) -> None:
        await websocket.accept()
        serial = websocket.query_params.get("serial") or state.active_serial
        if not state.config.adb_path:
            await websocket.send_text("[error] ADB not available")
            await websocket.close()
            return

        cmd = [state.config.adb_path]
        if serial:
            cmd.extend(["-s", serial])
        cmd.append("shell")

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        async def read_stdout() -> None:
            if proc.stdout:
                while True:
                    line = await asyncio.get_event_loop().run_in_executor(
                        None, proc.stdout.readline
                    )
                    if not line:
                        break
                    await websocket.send_text(line.rstrip("\n\r"))

        async def read_stdin() -> None:
            try:
                while True:
                    data = await websocket.receive_text()
                    if proc.stdin and proc.poll() is None:
                        proc.stdin.write(data + "\n")
                        proc.stdin.flush()
            except WebSocketDisconnect:
                pass

        try:
            await asyncio.gather(read_stdout(), read_stdin())
        finally:
            if proc.poll() is None:
                proc.terminate()


def render_terminal_panel(container, *, embedded: bool = False) -> None:
    logcat_task: dict[str, asyncio.Task | None] = {"task": None}

    with container:
        if embedded:
            outer = ui.column().classes("w-full psp-card")
        else:
            outer = ui.expansion("Terminal", icon="terminal").classes("w-full psp-card")

        with outer:
            ui.label(
                "Interactive ADB shell and live logcat. Select a device in the top bar first."
            ).classes("text-xs text-gray-500 mb-2")

            term_height = "min-h-[420px]" if embedded else ""

            with ui.tabs().classes("w-full") as tabs:
                ui.tab("logcat", label="Live Logcat")
                ui.tab("shell", label="ADB Shell")

            with ui.tab_panels(tabs, value="logcat").classes("w-full"):
                with ui.tab_panel("logcat"):
                    log_output = ui.log(max_lines=1000 if embedded else 500).classes(
                        f"w-full psp-terminal {term_height}"
                    )
                    filter_input = ui.input(
                        "Filter (optional)", placeholder="*:W or TAG:S"
                    ).classes("w-full")

                    async def start_logcat() -> None:
                        import websockets

                        serial = state.active_serial or ""
                        filt = filter_input.value or ""
                        url = (
                            f"{_ws_base()}/ws/logcat"
                            f"?serial={quote(serial)}&filter={quote(filt)}"
                        )
                        log_output.push("[info] Starting logcat stream…")
                        try:
                            async with websockets.connect(url) as ws:
                                async for msg in ws:
                                    log_output.push(msg)
                        except asyncio.CancelledError:
                            log_output.push("[info] Logcat stream stopped.")
                        except Exception as e:
                            log_output.push(f"[error] {e}")

                    def start_logcat_task() -> None:
                        if logcat_task["task"] and not logcat_task["task"].done():
                            log_output.push("[warning] Stream already running.")
                            return
                        logcat_task["task"] = asyncio.create_task(start_logcat())

                    def stop_logcat_task() -> None:
                        stop_logcat_stream()
                        task = logcat_task.get("task")
                        if task and not task.done():
                            task.cancel()
                        logcat_task["task"] = None
                        log_output.push("[info] Stop requested.")

                    with ui.row().classes("gap-2"):
                        ui.button("Start Logcat", on_click=start_logcat_task).props("color=cyan")
                        ui.button("Stop", on_click=stop_logcat_task).props("outline color=negative")
                        ui.button("Clear", on_click=lambda: log_output.clear()).props("flat")

                with ui.tab_panel("shell"):
                    shell_output = ui.log(max_lines=1000 if embedded else 500).classes(
                        f"w-full psp-terminal {term_height}"
                    )
                    shell_input = ui.input("Command").classes("w-full").props(
                        "dark outlined dense"
                    )

                    async def send_shell_cmd() -> None:
                        import websockets

                        cmd = shell_input.value
                        if not cmd:
                            return
                        serial = state.active_serial or ""
                        url = f"{_ws_base()}/ws/shell?serial={quote(serial)}"
                        try:
                            async with websockets.connect(url) as ws:
                                await ws.send(cmd)
                                msg = await asyncio.wait_for(ws.recv(), timeout=10)
                                shell_output.push(f"$ {cmd}")
                                shell_output.push(msg)
                        except Exception as e:
                            shell_output.push(f"[error] {e}")
                        shell_input.value = ""

                    shell_input.on("keydown.enter", send_shell_cmd)
                    ui.button("Send", on_click=send_shell_cmd).props("color=cyan")
