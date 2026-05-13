from __future__ import annotations

import uvicorn

from docflow.mcp.server import run as run_mcp_server
from docflow.services.runtime import build_runtime
from docflow.settings import get_settings
from docflow.workers.runner import WorkerRunner


def run_api() -> None:
    settings = get_settings()
    uvicorn.run(
        "docflow.api.app:app",
        host="127.0.0.1",
        port=settings.api_port,
        reload=False,
        factory=False,
    )


def run_worker() -> None:
    runtime = build_runtime()
    runner = WorkerRunner(runtime.job_service)
    runner.run_forever()


def run_mcp() -> None:
    run_mcp_server()
