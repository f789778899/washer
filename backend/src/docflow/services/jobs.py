from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import UploadFile

from docflow.db.repositories import DocumentRepository, JobRepository
from docflow.schemas import JobItem, JobRequest, JobSummary, ProcessedDocument
from docflow.services.pipeline import PipelineService
from docflow.services.storage import StorageService
from docflow.settings import Settings


class JobService:
    SUPPORTED_SUFFIXES = {
        ".pdf",
        ".docx",
        ".doc",
        ".txt",
        ".md",
        ".markdown",
        ".eml",
        ".msg",
        ".html",
        ".htm",
        ".log",
    }
    EXCLUDED_SUFFIXES = {".lnk"}

    def __init__(
        self,
        *,
        settings: Settings,
        jobs: JobRepository,
        documents: DocumentRepository,
        pipeline: PipelineService,
        storage: StorageService,
    ) -> None:
        self.settings = settings
        self.jobs = jobs
        self.documents = documents
        self.pipeline = pipeline
        self.storage = storage

    def create_job(self, paths: list[Path], tenant_id: str) -> JobSummary:
        expanded_paths = self.expand_paths(paths)
        if not expanded_paths:
            raise ValueError("No supported files were found in the provided paths.")
        request = JobRequest(
            tenant_id=tenant_id,
            items=[
                JobItem(path=str(path.resolve()), source=str(path.resolve()))
                for path in expanded_paths
            ],
        )
        return self.jobs.create_job(request)

    def save_uploads(self, files: list[UploadFile], tenant_id: str) -> list[Path]:
        tenant_dir = self.settings.upload_dir / tenant_id
        tenant_dir.mkdir(parents=True, exist_ok=True)
        saved_paths: list[Path] = []
        for file in files:
            destination = tenant_dir / file.filename
            with destination.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_paths.append(destination)
        return saved_paths

    def process_job(self, job_id: str) -> list[ProcessedDocument]:
        request = self.jobs.get_job_payload(job_id)
        if request is None:
            raise ValueError(f"Job {job_id} not found")
        return self.process_items(job_id, request.items, request.tenant_id)

    def process_items(
        self, job_id: str, items: list[JobItem], tenant_id: str
    ) -> list[ProcessedDocument]:
        processed_documents: list[ProcessedDocument] = []
        errors: list[str] = []
        corpus = self.documents.get_corpus_records(tenant_id)

        for item in items:
            path = Path(item.path)
            try:
                processed = self.pipeline.process_path(path, tenant_id, corpus)
                markdown_path, result_json_path = self.storage.persist_processed_document(processed)
                self.documents.upsert_processed_document(
                    job_id=job_id,
                    processed=processed,
                    markdown_path=markdown_path,
                    result_json_path=result_json_path,
                )
                processed_documents.append(processed)
                corpus.append(
                    {
                        "document_id": processed.document.document_id,
                        "tenant_id": tenant_id,
                        "normalized_checksum": processed.document.normalized_checksum,
                        "simhash": processed.document.simhash,
                    }
                )
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{path.name}: {exc}")

        self.jobs.finalize_job(
            job_id,
            processed_count=len(processed_documents),
            failed_count=len(errors),
            errors=errors,
        )
        return processed_documents

    @staticmethod
    def expand_paths(paths: list[Path]) -> list[Path]:
        expanded: list[Path] = []
        for path in paths:
            if path.is_dir():
                expanded.extend(
                    [
                        candidate
                        for candidate in path.rglob("*")
                        if candidate.is_file()
                        and candidate.suffix.lower() not in JobService.EXCLUDED_SUFFIXES
                        and candidate.suffix.lower() in JobService.SUPPORTED_SUFFIXES
                    ]
                )
            else:
                if (
                    path.suffix.lower() not in JobService.EXCLUDED_SUFFIXES
                    and path.suffix.lower() in JobService.SUPPORTED_SUFFIXES
                ):
                    expanded.append(path)
        return expanded

    def run_next_pending_job(self) -> str | None:
        job_id = self.jobs.claim_next_pending_job()
        if job_id is None:
            return None
        try:
            self.process_job(job_id)
        except Exception as exc:  # noqa: BLE001
            self.jobs.mark_job_failed(job_id, str(exc))
        return job_id
