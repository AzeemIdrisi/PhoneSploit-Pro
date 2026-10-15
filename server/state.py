"""Process-wide config, jobs, and host-launched scrcpy sessions."""

from __future__ import annotations

import asyncio
import subprocess
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any

from modules.config import AppConfig
from modules.console import set_adb_executable
from modules.tools import resolve_external_tools

import platform


def load_config() -> AppConfig:
    config = AppConfig()
    config.operating_system = platform.system()
    resolve_external_tools(config)
    set_adb_executable(config.adb_path)
    return config


CONFIG = load_config()


@dataclass
class Job:
    id: str
    name: str
    status: str = "running"
    message: str = ""
    artifact: str | None = None
    data: Any = None
    progress: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "artifact": self.artifact,
            "data": self.data,
            "progress": self.progress,
        }


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._cancel_events: dict[str, threading.Event] = {}
        self._lock = threading.Lock()
        self._subscribers: list[asyncio.Queue] = []

    def create(self, name: str) -> Job:
        job = Job(id=uuid.uuid4().hex[:12], name=name)
        with self._lock:
            self._jobs[job.id] = job
            self._cancel_events[job.id] = threading.Event()
        return job

    def list(self) -> list[dict[str, Any]]:
        with self._lock:
            return [job.to_dict() for job in reversed(list(self._jobs.values()))]

    def update(self, job: Job, **changes: Any) -> None:
        for key, value in changes.items():
            setattr(job, key, value)
        payload = job.to_dict()
        loop = _loop_holder.get("loop")
        if loop is not None and loop.is_running():
            loop.call_soon_threadsafe(self._publish, payload)
        else:
            self._publish(payload)

    def cancel(self, job_id: str) -> bool:
        with self._lock:
            event = self._cancel_events.get(job_id)
        if event is None:
            return False
        event.set()
        return True

    def is_cancelled(self, job_id: str) -> bool:
        with self._lock:
            event = self._cancel_events.get(job_id)
        return event is not None and event.is_set()

    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    def _publish(self, payload: dict[str, Any]) -> None:
        for queue in list(self._subscribers):
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                pass


JOBS = JobStore()


@dataclass
class Session:
    id: str
    feature: str
    serial: str
    process: subprocess.Popen[bytes]
    artifact: str | None = None


class Sessions:
    def __init__(self) -> None:
        self._items: dict[str, Session] = {}
        self._lock = threading.Lock()

    def add(self, feature: str, serial: str, process: subprocess.Popen[bytes], artifact: str | None = None) -> Session:
        session = Session(id=uuid.uuid4().hex[:10], feature=feature, serial=serial, process=process, artifact=artifact)
        with self._lock:
            self._items[session.id] = session
        return session

    def list(self) -> list[dict[str, Any]]:
        with self._lock:
            rows = []
            for session in self._items.values():
                code = session.process.poll()
                rows.append(
                    {
                        "id": session.id,
                        "feature": session.feature,
                        "serial": session.serial,
                        "running": code is None,
                        "exitCode": code,
                        "artifact": session.artifact,
                    }
                )
            return rows

    def stop(self, session_id: str) -> bool:
        with self._lock:
            session = self._items.get(session_id)
        if session is None:
            return False
        if session.process.poll() is None:
            session.process.terminate()
        return True


SESSIONS = Sessions()
_loop_holder: dict[str, asyncio.AbstractEventLoop] = {}


def bind_loop(loop: asyncio.AbstractEventLoop) -> None:
    _loop_holder["loop"] = loop


def schedule(coro: Any) -> None:
    loop = _loop_holder.get("loop")
    if loop is not None:
        asyncio.run_coroutine_threadsafe(coro, loop)
