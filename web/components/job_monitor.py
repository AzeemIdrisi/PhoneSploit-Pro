"""Background job monitor panel."""

from __future__ import annotations

from nicegui import ui

from modules.services.jobs import JobStatus
from web.helpers import io_timer
from web.state import state


def render_job_monitor(container, *, embedded: bool = False) -> None:
    with container:
        if embedded:
            outer = ui.column().classes("w-full psp-card")
        else:
            outer = ui.expansion("Job Monitor", icon="work").classes("w-full psp-card")

        with outer:
            if embedded:
                ui.label("Background jobs").classes("font-bold mb-2")
            job_table = ui.column().classes("w-full gap-2")

            @io_timer
            async def refresh_jobs() -> None:
                job_table.clear()
                jobs = state.jobs.list_jobs()
                if not jobs:
                    with job_table:
                        ui.label("No background jobs").classes("text-gray-500 text-sm")
                    return
                limit = 50 if embedded else 30
                max_h = "max-h-64" if embedded else "max-h-32"
                for job in reversed(jobs[-10:]):
                    with job_table:
                        with ui.row().classes("w-full items-center gap-2"):
                            color = {
                                JobStatus.RUNNING: "blue",
                                JobStatus.COMPLETED: "green",
                                JobStatus.FAILED: "red",
                                JobStatus.CANCELLED: "orange",
                            }.get(job.status, "grey")
                            ui.badge(job.status.value).props(f"color={color}")
                            ui.label(f"{job.name} ({job.id})").classes("text-sm")
                            if job.status == JobStatus.RUNNING:
                                ui.button(
                                    icon="stop",
                                    on_click=lambda j=job: state.jobs.cancel_job(j.id),
                                ).props("flat dense round color=negative")
                        if job.output:
                            ui.code("\n".join(job.output[-limit:])).classes(
                                f"w-full psp-mono text-xs {max_h} overflow-auto"
                            )
                        if job.error:
                            ui.label(job.error).classes("text-red-400 text-xs")

            ui.timer(2.0, refresh_jobs)
            ui.timer(0.2, refresh_jobs, once=True)
