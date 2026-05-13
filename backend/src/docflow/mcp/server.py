from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from docflow.schemas import JobItem
from docflow.services.runtime import build_runtime

runtime = build_runtime()
mcp = FastMCP("DocFlow Studio")


@mcp.tool()
def process_document(path: str, tenant_id: str | None = None) -> dict:
    """Process a single local document path and return the structured result."""
    resolved_tenant = tenant_id or runtime.settings.default_tenant_id
    source_path = Path(path)
    if not source_path.exists():
        return {"ok": False, "error_code": "DOC_NOT_FOUND", "message": f"{path} does not exist"}
    processed = runtime.pipeline.process_path(
        source_path,
        resolved_tenant,
        runtime.documents.get_corpus_records(resolved_tenant),
    )
    markdown_path, result_json_path = runtime.storage.persist_processed_document(processed)
    runtime.documents.upsert_processed_document(
        job_id="mcp-inline",
        processed=processed,
        markdown_path=markdown_path,
        result_json_path=result_json_path,
    )
    return {
        "ok": True,
        "document_id": processed.document.document_id,
        "dedup_status": processed.dedup_status.value,
        "quality_score": processed.quality_score,
        "sensitive_fields": processed.sensitive_fields,
        "markdown_path": str(markdown_path),
        "result_json_path": str(result_json_path),
        "metadata": processed.output_metadata,
    }


@mcp.tool()
def process_batch(paths: list[str], tenant_id: str | None = None) -> dict:
    """Create a batch job for multiple local document paths."""
    resolved_tenant = tenant_id or runtime.settings.default_tenant_id
    source_paths = [Path(path) for path in paths]
    missing = [str(path) for path in source_paths if not path.exists()]
    if missing:
        return {
            "ok": False,
            "error_code": "DOC_NOT_FOUND",
            "message": "Some paths do not exist",
            "paths": missing,
        }
    job = runtime.job_service.create_job(source_paths, resolved_tenant)
    runtime.job_service.process_items(
        job.job_id,
        [JobItem(path=str(path.resolve()), source=str(path.resolve())) for path in source_paths],
        resolved_tenant,
    )
    documents = runtime.documents.list_by_job(job.job_id)
    return {"ok": True, "job": job.model_dump(mode="json"), "documents": documents}


@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """Get the status and document summaries for a previously created job."""
    job = runtime.jobs.get_job(job_id)
    if job is None:
        return {
            "ok": False,
            "error_code": "JOB_NOT_FOUND",
            "message": f"Job {job_id} was not found",
        }
    return {
        "ok": True,
        "job": job.model_dump(mode="json"),
        "documents": runtime.documents.list_by_job(job_id),
    }


@mcp.tool()
def get_document_result(document_id: str) -> dict:
    """Load a processed document result with redacted markdown and audit metadata."""
    document = runtime.documents.get_document(document_id)
    if document is None:
        return {
            "ok": False,
            "error_code": "DOC_RESULT_NOT_FOUND",
            "message": f"Document {document_id} was not found",
        }
    return {"ok": True, "document": document}


def run() -> None:
    mcp.run(transport="stdio")
