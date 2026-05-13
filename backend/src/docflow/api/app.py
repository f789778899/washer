from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from docflow.api.routes import router
from docflow.services.runtime import build_runtime
from docflow.workers.runner import WorkerRunner


def create_app(start_worker: bool = True) -> FastAPI:
    runtime = build_runtime()
    worker = WorkerRunner(runtime.job_service)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.runtime = runtime
        app.state.worker = worker
        if start_worker:
            worker.start_in_background()
        yield
        worker.stop()

    app = FastAPI(title=runtime.settings.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    if runtime.settings.frontend_dist.exists():
        assets_dir = runtime.settings.frontend_dist / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @app.get("/", include_in_schema=False)
        def serve_index():
            return FileResponse(runtime.settings.frontend_dist / "index.html")

        @app.get("/{full_path:path}", include_in_schema=False)
        def serve_spa(full_path: str):
            target = runtime.settings.frontend_dist / full_path
            if target.exists() and target.is_file():
                return FileResponse(target)
            return FileResponse(runtime.settings.frontend_dist / "index.html")
    else:

        @app.get("/", include_in_schema=False)
        def root_placeholder():
            return JSONResponse(
                {
                    "message": (
                        "Frontend not built yet. Start with the API endpoints or build the "
                        "React app."
                    ),
                    "frontend_dist": str(runtime.settings.frontend_dist),
                }
            )

    return app


app = create_app()
