from __future__ import annotations

import json
import re
from pathlib import Path

from docflow.schemas import ProcessedDocument
from docflow.settings import Settings


class StorageService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def persist_processed_document(self, processed: ProcessedDocument) -> tuple[Path, Path]:
        base_dir = (
            self.settings.output_dir / processed.document.tenant_id / processed.document.document_id
        )
        base_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = base_dir / "content.md"
        result_json_path = base_dir / "result.json"
        markdown_path.write_text(processed.markdown_text, encoding="utf-8")
        result_json_path.write_text(
            json.dumps(processed.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return markdown_path, result_json_path

    def export_document(
        self,
        *,
        document: dict,
        target_dir: Path,
        output_format: str = "md",
    ) -> dict:
        markdown_text = document.get("markdown_text") or ""
        filename = document.get("filename") or document.get("document_id") or "document"
        document_id = document.get("document_id") or "unknown"
        extension = ".txt" if output_format == "txt" else ".md"
        content = markdown_to_plain_text(markdown_text) if output_format == "txt" else markdown_text

        target_dir.mkdir(parents=True, exist_ok=True)
        output_path = target_dir / f"{safe_stem(filename)}__{document_id}{extension}"
        output_path.write_text(content, encoding="utf-8")
        return {
            "document_id": document_id,
            "filename": filename,
            "path": str(output_path),
            "format": output_format,
            "bytes": output_path.stat().st_size,
        }


def safe_stem(filename: str) -> str:
    stem = Path(filename).stem or "document"
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", stem).strip(" ._")
    return cleaned[:120] or "document"


def markdown_to_plain_text(markdown_text: str) -> str:
    text = re.sub(r"^#{1,6}\s+", "", markdown_text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*>\s?", "", text, flags=re.MULTILINE)
    text = re.sub(r"`{1,3}([^`]+)`{1,3}", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text.strip() + "\n" if text.strip() else ""
