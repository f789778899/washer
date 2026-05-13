from __future__ import annotations

from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from docflow.db.models import DocumentRecord, JobRecord
from docflow.schemas import DashboardSummary, JobRequest, JobStatus, JobSummary, ProcessedDocument
from docflow.utils.hashing import short_hash
from docflow.utils.time import utc_now


class JobRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory

    def create_job(self, request: JobRequest) -> JobSummary:
        now = utc_now()
        job_id = short_hash(f"{request.tenant_id}:{now.isoformat()}:{len(request.items)}", length=16)
        record = JobRecord(
            id=job_id,
            tenant_id=request.tenant_id,
            status=JobStatus.pending.value,
            source_count=len(request.items),
            processed_count=0,
            failed_count=0,
            retry_count=0,
            payload_json=request.model_dump(mode="json"),
            summary_json={},
            error_json=[],
            created_at=now,
            updated_at=now,
        )
        with self.session_factory() as session:
            session.add(record)
            session.commit()
        return JobSummary(
            job_id=job_id,
            tenant_id=request.tenant_id,
            status=JobStatus.pending,
            source_count=len(request.items),
            processed_count=0,
            failed_count=0,
            created_at=now,
            updated_at=now,
            errors=[],
        )

    def list_jobs(self, limit: int = 50) -> list[JobSummary]:
        with self.session_factory() as session:
            rows = session.scalars(select(JobRecord).order_by(JobRecord.created_at.desc()).limit(limit)).all()
            return [self._to_summary(row) for row in rows]

    def get_job(self, job_id: str) -> JobSummary | None:
        with self.session_factory() as session:
            row = session.get(JobRecord, job_id)
            return self._to_summary(row) if row else None

    def get_job_payload(self, job_id: str) -> JobRequest | None:
        with self.session_factory() as session:
            row = session.get(JobRecord, job_id)
            if not row:
                return None
            return JobRequest.model_validate(row.payload_json)

    def claim_next_pending_job(self) -> str | None:
        with self.session_factory() as session:
            row = session.scalars(
                select(JobRecord)
                .where(JobRecord.status == JobStatus.pending.value)
                .order_by(JobRecord.created_at.asc())
                .limit(1)
            ).first()
            if row is None:
                return None
            row.status = JobStatus.running.value
            row.updated_at = utc_now()
            session.commit()
            return row.id

    def finalize_job(self, job_id: str, *, processed_count: int, failed_count: int, errors: list[str]) -> None:
        with self.session_factory() as session:
            row = session.get(JobRecord, job_id)
            if row is None:
                return
            row.status = JobStatus.completed.value if failed_count == 0 else JobStatus.partial.value
            if processed_count == 0 and failed_count > 0:
                row.status = JobStatus.failed.value
            row.processed_count = processed_count
            row.failed_count = failed_count
            row.error_json = errors
            row.updated_at = utc_now()
            session.commit()

    def mark_job_failed(self, job_id: str, error: str) -> None:
        with self.session_factory() as session:
            row = session.get(JobRecord, job_id)
            if row is None:
                return
            row.failed_count = row.source_count
            row.status = JobStatus.failed.value
            row.error_json = [error]
            row.retry_count += 1
            row.updated_at = utc_now()
            session.commit()

    @staticmethod
    def _to_summary(row: JobRecord) -> JobSummary:
        return JobSummary(
            job_id=row.id,
            tenant_id=row.tenant_id,
            status=JobStatus(row.status),
            source_count=row.source_count,
            processed_count=row.processed_count,
            failed_count=row.failed_count,
            created_at=row.created_at,
            updated_at=row.updated_at,
            errors=list(row.error_json or []),
        )


class DocumentRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory

    def upsert_processed_document(
        self,
        *,
        job_id: str,
        processed: ProcessedDocument,
        markdown_path: Path,
        result_json_path: Path,
    ) -> None:
        with self.session_factory() as session:
            existing = session.scalars(
                select(DocumentRecord).where(DocumentRecord.document_id == processed.document.document_id)
            ).first()
            now = utc_now()
            payload = {
                "document_id": processed.document.document_id,
                "source": processed.document.source,
                "doc_type": processed.document.doc_type.value,
                "language": processed.document.language,
                "tenant_id": processed.document.tenant_id,
                "checksum": processed.document.checksum,
                "dedup_status": processed.dedup_status.value,
                "sensitive_fields": processed.sensitive_fields,
                "processing_steps": [step.model_dump(mode="json") for step in processed.processing_steps],
                "created_at": processed.document.created_at.isoformat(),
                "updated_at": processed.document.updated_at.isoformat(),
                "chunk_info": processed.chunk_info.model_dump(mode="json"),
                "quality_score": processed.quality_score,
            }
            if existing:
                record = existing
                record.updated_at = now
            else:
                record = DocumentRecord(
                    job_id=job_id,
                    document_id=processed.document.document_id,
                    tenant_id=processed.document.tenant_id,
                    source=processed.document.source,
                    filename=processed.document.filename,
                    doc_type=processed.document.doc_type.value,
                    language=processed.document.language,
                    checksum=processed.document.checksum,
                    normalized_checksum=processed.document.normalized_checksum,
                    simhash=processed.document.simhash,
                    dedup_status=processed.dedup_status.value,
                    quality_score=processed.quality_score,
                    sensitive_fields_json=[],
                    metadata_json={},
                    processing_steps_json=[],
                    audit_json={},
                    markdown_path=str(markdown_path),
                    result_json_path=str(result_json_path),
                    created_at=now,
                    updated_at=now,
                )
                session.add(record)

            record.job_id = job_id
            record.source = processed.document.source
            record.filename = processed.document.filename
            record.doc_type = processed.document.doc_type.value
            record.language = processed.document.language
            record.checksum = processed.document.checksum
            record.normalized_checksum = processed.document.normalized_checksum
            record.simhash = processed.document.simhash
            record.dedup_status = processed.dedup_status.value
            record.quality_score = processed.quality_score
            record.sensitive_fields_json = processed.sensitive_fields
            record.metadata_json = payload
            record.processing_steps_json = [step.model_dump(mode="json") for step in processed.processing_steps]
            record.audit_json = processed.audit.model_dump(mode="json")
            record.markdown_path = str(markdown_path)
            record.result_json_path = str(result_json_path)
            session.commit()

    def get_corpus_records(self, tenant_id: str) -> list[dict]:
        with self.session_factory() as session:
            rows = session.scalars(
                select(DocumentRecord)
                .where(DocumentRecord.tenant_id == tenant_id)
                .order_by(DocumentRecord.updated_at.desc())
                .limit(500)
            ).all()
            return [
                {
                    "document_id": row.document_id,
                    "tenant_id": row.tenant_id,
                    "normalized_checksum": row.normalized_checksum,
                    "simhash": row.simhash,
                }
                for row in rows
            ]

    def list_by_job(self, job_id: str) -> list[dict]:
        with self.session_factory() as session:
            rows = session.scalars(
                select(DocumentRecord).where(DocumentRecord.job_id == job_id).order_by(DocumentRecord.created_at.asc())
            ).all()
            return [self._to_document_summary(row) for row in rows]

    def get_document(self, document_id: str) -> dict | None:
        with self.session_factory() as session:
            row = session.scalars(
                select(DocumentRecord).where(DocumentRecord.document_id == document_id)
            ).first()
            if row is None:
                return None
            summary = self._to_document_summary(row)
            summary["markdown_path"] = row.markdown_path
            summary["result_json_path"] = row.result_json_path
            summary["metadata"] = row.metadata_json
            summary["audit"] = row.audit_json
            if Path(row.markdown_path).exists():
                summary["markdown_text"] = Path(row.markdown_path).read_text(encoding="utf-8")
            else:
                summary["markdown_text"] = ""
            return summary

    def dashboard_summary(self) -> DashboardSummary:
        with self.session_factory() as session:
            total_jobs = session.scalar(select(func.count()).select_from(JobRecord)) or 0
            completed_jobs = session.scalar(
                select(func.count()).select_from(JobRecord).where(JobRecord.status == JobStatus.completed.value)
            ) or 0
            total_documents = session.scalar(select(func.count()).select_from(DocumentRecord)) or 0
            duplicate_documents = session.scalar(
                select(func.count()).select_from(DocumentRecord).where(
                    DocumentRecord.dedup_status.in_(["exact_duplicate", "near_duplicate", "partial_duplicate"])
                )
            ) or 0
            redacted_documents = session.scalar(
                select(func.count()).select_from(DocumentRecord).where(
                    func.json_array_length(DocumentRecord.sensitive_fields_json) > 0
                )
            ) or 0
            avg_quality = session.scalar(select(func.avg(DocumentRecord.quality_score)).select_from(DocumentRecord)) or 0.0
        return DashboardSummary(
            total_jobs=total_jobs,
            completed_jobs=completed_jobs,
            total_documents=total_documents,
            duplicate_documents=duplicate_documents,
            redacted_documents=redacted_documents,
            average_quality_score=round(float(avg_quality), 2),
            last_updated_at=utc_now(),
        )

    @staticmethod
    def _to_document_summary(row: DocumentRecord) -> dict:
        return {
            "document_id": row.document_id,
            "job_id": row.job_id,
            "tenant_id": row.tenant_id,
            "source": row.source,
            "filename": row.filename,
            "doc_type": row.doc_type,
            "language": row.language,
            "dedup_status": row.dedup_status,
            "quality_score": row.quality_score,
            "sensitive_fields": row.sensitive_fields_json or [],
            "created_at": row.created_at.isoformat(),
            "updated_at": row.updated_at.isoformat(),
        }

