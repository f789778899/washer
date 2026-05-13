from __future__ import annotations

import threading
import time

from docflow.services.jobs import JobService


class WorkerRunner:
    def __init__(self, job_service: JobService, poll_interval: float = 1.0) -> None:
        self.job_service = job_service
        self.poll_interval = poll_interval
        self.stop_event = threading.Event()

    def start_in_background(self) -> threading.Thread:
        thread = threading.Thread(target=self.run_forever, daemon=True, name="docflow-worker")
        thread.start()
        return thread

    def run_forever(self) -> None:
        while not self.stop_event.is_set():
            claimed = self.job_service.run_next_pending_job()
            if claimed is None:
                time.sleep(self.poll_interval)

    def stop(self) -> None:
        self.stop_event.set()
