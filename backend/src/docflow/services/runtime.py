from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session, sessionmaker

from docflow.core.cleaners import CleanerEngine
from docflow.core.dedup import DedupEngine
from docflow.core.output import OutputFormatter
from docflow.core.parsers import ParserRegistry
from docflow.core.quality import QualityScorer
from docflow.core.redaction import RedactionEngine
from docflow.db.repositories import DocumentRepository, JobRepository
from docflow.db.session import build_session_factory
from docflow.services.jobs import JobService
from docflow.services.pipeline import PipelineService
from docflow.services.storage import StorageService
from docflow.settings import Settings, get_settings
from docflow.utils.logging import configure_logging


@dataclass
class RuntimeContainer:
    settings: Settings
    session_factory: sessionmaker[Session]
    jobs: JobRepository
    documents: DocumentRepository
    storage: StorageService
    pipeline: PipelineService
    job_service: JobService


def build_runtime(settings: Settings | None = None) -> RuntimeContainer:
    resolved_settings = settings or get_settings()
    resolved_settings.ensure_directories()
    configure_logging(resolved_settings)

    session_factory = build_session_factory(resolved_settings)
    jobs = JobRepository(session_factory)
    documents = DocumentRepository(session_factory)
    storage = StorageService(resolved_settings)
    pipeline = PipelineService(
        settings=resolved_settings,
        parser_registry=ParserRegistry(),
        cleaner=CleanerEngine(resolved_settings),
        dedup_engine=DedupEngine(resolved_settings),
        redaction_engine=RedactionEngine(resolved_settings),
        formatter=OutputFormatter(resolved_settings),
        scorer=QualityScorer(),
    )
    job_service = JobService(
        settings=resolved_settings,
        jobs=jobs,
        documents=documents,
        pipeline=pipeline,
        storage=storage,
    )
    return RuntimeContainer(
        settings=resolved_settings,
        session_factory=session_factory,
        jobs=jobs,
        documents=documents,
        storage=storage,
        pipeline=pipeline,
        job_service=job_service,
    )
