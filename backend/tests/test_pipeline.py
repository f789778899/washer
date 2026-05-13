from __future__ import annotations

from pathlib import Path

from docflow.core.cleaners import CleanerEngine
from docflow.core.dedup import DedupEngine
from docflow.core.output import OutputFormatter
from docflow.core.parsers import ParserRegistry
from docflow.core.quality import QualityScorer
from docflow.core.redaction import RedactionEngine
from docflow.schemas import DedupStatus
from docflow.services.pipeline import PipelineService
from docflow.settings import Settings


def build_pipeline(settings: Settings) -> PipelineService:
    return PipelineService(
        settings=settings,
        parser_registry=ParserRegistry(),
        cleaner=CleanerEngine(settings),
        dedup_engine=DedupEngine(settings),
        redaction_engine=RedactionEngine(settings),
        formatter=OutputFormatter(settings),
        scorer=QualityScorer(),
    )


def test_pipeline_redacts_and_deduplicates(test_settings: Settings, tmp_path: Path) -> None:
    input_path = tmp_path / "customer-thread.txt"
    input_path.write_text(
        "\n".join(
            [
                "客户投诉升级通知",
                "",
                "姓名：张三",
                "手机号：13800138000",
                "邮箱：zhangsan@example.com",
                "订单号：ORD-2026-0001",
                "Token=abc1234567890123456789",
                "",
                "该客户要求在 24 小时内回电。",
                "",
                "该客户要求在 24 小时内回电。",
            ]
        ),
        encoding="utf-8",
    )

    pipeline = build_pipeline(test_settings)
    processed = pipeline.process_path(input_path, "tenant-a", corpus_records=[])

    assert processed.quality_score > 0
    assert processed.sensitive_fields
    assert "[PHONE_1]" in processed.markdown_text
    assert "[EMAIL_1]" in processed.markdown_text
    assert "[ACCESS_TOKEN_1]" in processed.markdown_text
    assert processed.dedup_status in {DedupStatus.partial_duplicate, DedupStatus.unique}
    assert processed.chunk_info.chunk_count >= 1


def test_pipeline_marks_near_duplicate(test_settings: Settings, tmp_path: Path) -> None:
    input_path = tmp_path / "faq.txt"
    input_path.write_text(
        "RAG 数据接入说明\n\n系统支持 PDF、Word、TXT 与邮件导入。系统支持 PDF、Word、TXT 与邮件导入。",
        encoding="utf-8",
    )
    pipeline = build_pipeline(test_settings)
    corpus = [
        {
            "document_id": "existing-doc",
            "tenant_id": "tenant-a",
            "normalized_checksum": "different",
            "simhash": "ffffffffffffffff",
        }
    ]
    processed = pipeline.process_path(input_path, "tenant-a", corpus_records=corpus)
    assert processed.document.document_id
    assert processed.markdown_text.startswith("#")


def test_pipeline_processes_eml_headers(test_settings: Settings, tmp_path: Path) -> None:
    input_path = tmp_path / "thread.eml"
    input_path.write_text(
        "\n".join(
            [
                "From: Demo User <demo@example.com>",
                "To: ops@example.com",
                "Subject: Incident",
                'Content-Type: text/plain; charset="utf-8"',
                "",
                "姓名：张三",
                "邮箱：demo@example.com",
            ]
        ),
        encoding="utf-8",
    )
    pipeline = build_pipeline(test_settings)
    processed = pipeline.process_path(input_path, "tenant-a", corpus_records=[])
    assert processed.document.doc_type.value == "email"
    assert "[EMAIL_1]" in processed.markdown_text
