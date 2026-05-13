from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class DocumentType(StrEnum):
    pdf = "pdf"
    docx = "docx"
    txt = "txt"
    markdown = "markdown"
    email = "email"
    html = "html"
    chat = "chat"
    log = "log"
    unknown = "unknown"


class SegmentKind(StrEnum):
    heading = "heading"
    paragraph = "paragraph"
    list_item = "list_item"
    table_row = "table_row"
    quote = "quote"
    metadata = "metadata"
    line = "line"


class DedupStatus(StrEnum):
    unique = "unique"
    exact_duplicate = "exact_duplicate"
    near_duplicate = "near_duplicate"
    partial_duplicate = "partial_duplicate"


class JobStatus(StrEnum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    partial = "partial"


class DocumentSegment(BaseModel):
    segment_id: str
    kind: SegmentKind
    text: str
    level: int | None = None
    page: int | None = None
    position: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class DuplicateRelation(BaseModel):
    relation_type: str
    similarity: float
    related_document_id: str | None = None
    related_segment_id: str | None = None
    reason: str
    keep_policy: str


class SensitiveMatch(BaseModel):
    field_type: str
    rule_id: str
    placeholder: str
    original_excerpt: str
    span_start: int
    span_end: int


class CleaningAction(BaseModel):
    action: str
    detail: str
    count: int = 1


class ProcessingStep(BaseModel):
    step: str
    status: str
    detail: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class ChunkDescriptor(BaseModel):
    chunk_id: str
    start_offset: int
    end_offset: int
    text: str


class ChunkInfo(BaseModel):
    chunk_size: int
    chunk_overlap: int
    chunk_count: int
    chunks: list[ChunkDescriptor]


class ProcessingAudit(BaseModel):
    cleaning_actions: list[CleaningAction] = Field(default_factory=list)
    dedup_relations: list[DuplicateRelation] = Field(default_factory=list)
    sensitive_matches: list[SensitiveMatch] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class NormalizedDocument(BaseModel):
    document_id: str
    source: str
    filename: str
    doc_type: DocumentType
    tenant_id: str
    title: str | None = None
    language: str = "unknown"
    checksum: str
    normalized_checksum: str
    simhash: str
    raw_text: str
    normalized_text: str
    segments: list[DocumentSegment]
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class ProcessedDocument(BaseModel):
    document: NormalizedDocument
    markdown_text: str
    dedup_status: DedupStatus
    sensitive_fields: list[str]
    processing_steps: list[ProcessingStep]
    audit: ProcessingAudit
    chunk_info: ChunkInfo
    quality_score: float
    output_metadata: dict[str, Any]


class JobItem(BaseModel):
    path: str
    source: str | None = None


class JobRequest(BaseModel):
    tenant_id: str
    items: list[JobItem]


class JobSummary(BaseModel):
    job_id: str
    tenant_id: str
    status: JobStatus
    source_count: int
    processed_count: int
    failed_count: int
    created_at: datetime
    updated_at: datetime
    errors: list[str] = Field(default_factory=list)


class DashboardSummary(BaseModel):
    total_jobs: int
    completed_jobs: int
    total_documents: int
    duplicate_documents: int
    redacted_documents: int
    average_quality_score: float
    last_updated_at: datetime
