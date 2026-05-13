from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field

from docflow.services.runtime import RuntimeContainer

router = APIRouter(prefix="/api")


def get_runtime(request: Request) -> RuntimeContainer:
    return request.app.state.runtime


class PathsRequest(BaseModel):
    tenant_id: str = Field(default="demo-tenant")
    paths: list[str]


class ExportRequest(BaseModel):
    target_dir: str
    output_format: str = Field(default="md", pattern="^(md|txt)$")


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/settings")
def get_settings_endpoint(runtime: Annotated[RuntimeContainer, Depends(get_runtime)]) -> dict:
    return {
        "app_name": runtime.settings.app_name,
        "default_tenant_id": runtime.settings.default_tenant_id,
        "api_port": runtime.settings.api_port,
        "output_dir": str(runtime.settings.output_dir),
    }


@router.get("/dashboard/summary")
def dashboard_summary(runtime: Annotated[RuntimeContainer, Depends(get_runtime)]) -> dict:
    return runtime.documents.dashboard_summary().model_dump(mode="json")


@router.post("/jobs/process-paths")
def create_job_from_paths(
    payload: PathsRequest,
    runtime: Annotated[RuntimeContainer, Depends(get_runtime)],
) -> dict:
    paths = [Path(path) for path in payload.paths]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise HTTPException(
            status_code=400, detail={"message": "Some paths do not exist", "paths": missing}
        )
    job = runtime.job_service.create_job(paths, payload.tenant_id)
    return job.model_dump(mode="json")


@router.post("/jobs/upload")
def create_job_from_uploads(
    runtime: Annotated[RuntimeContainer, Depends(get_runtime)],
    tenant_id: Annotated[str, Form()] = "demo-tenant",
    files: Annotated[list[UploadFile] | None, File()] = None,
) -> dict:
    if not files:
        raise HTTPException(status_code=400, detail={"message": "No files uploaded"})
    paths = runtime.job_service.save_uploads(files, tenant_id)
    job = runtime.job_service.create_job(paths, tenant_id)
    return job.model_dump(mode="json")


@router.get("/jobs")
def list_jobs(runtime: Annotated[RuntimeContainer, Depends(get_runtime)]) -> list[dict]:
    return [job.model_dump(mode="json") for job in runtime.jobs.list_jobs()]


@router.get("/jobs/{job_id}")
def get_job(job_id: str, runtime: Annotated[RuntimeContainer, Depends(get_runtime)]) -> dict:
    job = runtime.jobs.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail={"message": f"Job {job_id} not found"})
    return job.model_dump(mode="json")


@router.get("/jobs/{job_id}/documents")
def list_job_documents(
    job_id: str, runtime: Annotated[RuntimeContainer, Depends(get_runtime)]
) -> list[dict]:
    return runtime.documents.list_by_job(job_id)


@router.get("/documents/{document_id}")
def get_document(
    document_id: str, runtime: Annotated[RuntimeContainer, Depends(get_runtime)]
) -> dict:
    document = runtime.documents.get_document(document_id)
    if document is None:
        raise HTTPException(
            status_code=404, detail={"message": f"Document {document_id} not found"}
        )
    return document


@router.post("/documents/{document_id}/export")
def export_document(
    document_id: str,
    payload: ExportRequest,
    runtime: Annotated[RuntimeContainer, Depends(get_runtime)],
) -> dict:
    document = runtime.documents.get_document(document_id)
    if document is None:
        raise HTTPException(
            status_code=404, detail={"message": f"Document {document_id} not found"}
        )
    exported = runtime.storage.export_document(
        document=document,
        target_dir=Path(payload.target_dir),
        output_format=payload.output_format,
    )
    return {"exported_count": 1, "files": [exported]}


@router.post("/jobs/{job_id}/export")
def export_job(
    job_id: str,
    payload: ExportRequest,
    runtime: Annotated[RuntimeContainer, Depends(get_runtime)],
) -> dict:
    job = runtime.jobs.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail={"message": f"Job {job_id} not found"})

    exported_files = []
    for summary in runtime.documents.list_by_job(job_id):
        document = runtime.documents.get_document(summary["document_id"])
        if document is None:
            continue
        exported_files.append(
            runtime.storage.export_document(
                document=document,
                target_dir=Path(payload.target_dir),
                output_format=payload.output_format,
            )
        )
    return {"exported_count": len(exported_files), "files": exported_files}
