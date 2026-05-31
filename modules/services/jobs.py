"""Background job manager for long-running operations."""

from __future__ import annotations

import asyncio
import subprocess
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    id: str
    name: str
    status: JobStatus = JobStatus.PENDING
    output: list[str] = field(default_factory=list)
    error: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    _process: subprocess.Popen | None = field(default=None, repr=False)
    _thread: threading.Thread | None = field(default=None, repr=False)

    def append_output(self, line: str) -> None:
        self.output.append(line)
        if len(self.output) > 5000:
            self.output = self.output[-4000:]


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def list_jobs(self) -> list[Job]:
        with self._lock:
            return list(self._jobs.values())

    def get_job(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def run_subprocess(
        self,
        name: str,
        argv: list[str],
        *,
        on_complete: Callable[[Job], None] | None = None,
    ) -> Job:
        job_id = str(uuid.uuid4())[:8]
        job = Job(id=job_id, name=name, status=JobStatus.RUNNING)

        def _worker() -> None:
            try:
                proc = subprocess.Popen(
                    argv,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                job._process = proc
                if proc.stdout:
                    for line in proc.stdout:
                        job.append_output(line.rstrip())
                proc.wait()
                if job.status == JobStatus.CANCELLED:
                    return
                if proc.returncode == 0:
                    job.status = JobStatus.COMPLETED
                else:
                    job.status = JobStatus.FAILED
                    job.error = f"Exit code {proc.returncode}"
            except Exception as e:
                job.status = JobStatus.FAILED
                job.error = str(e)
            finally:
                if on_complete:
                    on_complete(job)

        thread = threading.Thread(target=_worker, daemon=True)
        job._thread = thread
        with self._lock:
            self._jobs[job_id] = job
        thread.start()
        return job

    def run_callable(self, name: str, fn: Callable[[], str]) -> Job:
        job_id = str(uuid.uuid4())[:8]
        job = Job(id=job_id, name=name, status=JobStatus.RUNNING)

        def _worker() -> None:
            try:
                result = fn()
                job.append_output(result)
                job.status = JobStatus.COMPLETED
            except Exception as e:
                job.status = JobStatus.FAILED
                job.error = str(e)

        thread = threading.Thread(target=_worker, daemon=True)
        with self._lock:
            self._jobs[job_id] = job
        thread.start()
        return job

    def cancel_job(self, job_id: str) -> bool:
        job = self.get_job(job_id)
        if not job or job.status not in (JobStatus.PENDING, JobStatus.RUNNING):
            return False
        job.status = JobStatus.CANCELLED
        if job._process and job._process.poll() is None:
            job._process.terminate()
            try:
                job._process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                job._process.kill()
        return True


# Global singleton for web UI
job_manager = JobManager()
