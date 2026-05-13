from __future__ import annotations

from pathlib import Path

from tenacity import retry, stop_after_attempt, wait_fixed

from docflow.core.cleaners import CleanerEngine
from docflow.core.dedup import DedupEngine
from docflow.core.output import OutputFormatter
from docflow.core.parsers import ParserRegistry
from docflow.core.quality import QualityScorer
from docflow.core.redaction import RedactionEngine
from docflow.schemas import (
    NormalizedDocument,
    ProcessedDocument,
    ProcessingAudit,
    ProcessingStep,
)
from docflow.settings import Settings
from docflow.utils.time import utc_now


class PipelineService:
    def __init__(
        self,
        *,
        settings: Settings,
        parser_registry: ParserRegistry,
        cleaner: CleanerEngine,
        dedup_engine: DedupEngine,
        redaction_engine: RedactionEngine,
        formatter: OutputFormatter,
        scorer: QualityScorer,
    ) -> None:
        self.settings = settings
        self.parser_registry = parser_registry
        self.cleaner = cleaner
        self.dedup_engine = dedup_engine
        self.redaction_engine = redaction_engine
        self.formatter = formatter
        self.scorer = scorer

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(0.5), reraise=True)
    def process_path(
        self, path: Path, tenant_id: str, corpus_records: list[dict]
    ) -> ProcessedDocument:
        steps: list[ProcessingStep] = []
        audit = ProcessingAudit()

        document = self._step(
            "parse", steps, lambda: self.parser_registry.parse_file(path, tenant_id)
        )
        document, cleaning_actions = self._step(
            "clean", steps, lambda: self.cleaner.clean(document)
        )
        audit.cleaning_actions.extend(cleaning_actions)

        document, dedup_status, dedup_relations = self._step(
            "deduplicate",
            steps,
            lambda: self.dedup_engine.evaluate(document, corpus_records),
        )
        audit.dedup_relations.extend(dedup_relations)

        document, sensitive_fields, sensitive_matches = self._step(
            "redact",
            steps,
            lambda: self._redact_document(document),
        )
        audit.sensitive_matches.extend(sensitive_matches)

        markdown_text = self._step(
            "format_markdown", steps, lambda: self.formatter.to_markdown(document)
        )
        chunk_info = self._step(
            "chunk", steps, lambda: self.formatter.build_chunk_info(markdown_text)
        )
        quality_score = self._step(
            "score",
            steps,
            lambda: self.scorer.score(
                markdown_text=markdown_text, dedup_status=dedup_status, audit=audit
            ),
        )

        output_metadata = {
            "document_id": document.document_id,
            "source": document.source,
            "doc_type": document.doc_type.value,
            "language": document.language,
            "tenant_id": document.tenant_id,
            "checksum": document.checksum,
            "dedup_status": dedup_status.value,
            "sensitive_fields": sensitive_fields,
            "processing_steps": [step.model_dump(mode="json") for step in steps],
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat(),
            "chunk_info": chunk_info.model_dump(mode="json"),
            "quality_score": quality_score,
        }

        return ProcessedDocument(
            document=document,
            markdown_text=markdown_text,
            dedup_status=dedup_status,
            sensitive_fields=sensitive_fields,
            processing_steps=steps,
            audit=audit,
            chunk_info=chunk_info,
            quality_score=quality_score,
            output_metadata=output_metadata,
        )

    def _redact_document(
        self,
        document: NormalizedDocument,
    ) -> tuple[NormalizedDocument, list[str], list]:
        updated_segments = []
        all_matches = []
        field_types: set[str] = set()
        for segment in document.segments:
            redacted_text, matches, fields = self.redaction_engine.redact(segment.text)
            updated_segments.append(segment.model_copy(update={"text": redacted_text}))
            all_matches.extend(matches)
            field_types.update(fields)
        updated_text = "\n\n".join(segment.text for segment in updated_segments)
        updated_document = document.model_copy(
            update={
                "segments": updated_segments,
                "normalized_text": updated_text,
                "updated_at": utc_now(),
            }
        )
        return updated_document, sorted(field_types), all_matches

    @staticmethod
    def _step(name: str, steps: list[ProcessingStep], operation):
        started_at = utc_now()
        step = ProcessingStep(step=name, status="running", started_at=started_at)
        steps.append(step)
        result = operation()
        steps[-1] = step.model_copy(update={"status": "completed", "finished_at": utc_now()})
        return result
