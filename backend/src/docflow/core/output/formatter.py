from __future__ import annotations

from textwrap import fill

from docflow.schemas import (
    ChunkDescriptor,
    ChunkInfo,
    DocumentSegment,
    NormalizedDocument,
    SegmentKind,
)
from docflow.settings import Settings
from docflow.utils.hashing import short_hash


class OutputFormatter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def to_markdown(self, document: NormalizedDocument) -> str:
        lines: list[str] = []
        if document.title:
            lines.append(f"# {document.title}")
            lines.append("")
        for segment in document.segments:
            lines.extend(self._segment_to_lines(segment))
        return "\n".join(line.rstrip() for line in lines).strip() + "\n"

    def build_chunk_info(self, markdown_text: str) -> ChunkInfo:
        chunk_size = self.settings.chunk_size
        overlap = self.settings.chunk_overlap
        chunks: list[ChunkDescriptor] = []
        start = 0
        while start < len(markdown_text):
            end = min(start + chunk_size, len(markdown_text))
            chunk_text = markdown_text[start:end].strip()
            if chunk_text:
                chunks.append(
                    ChunkDescriptor(
                        chunk_id=short_hash(f"{start}:{end}:{chunk_text}"),
                        start_offset=start,
                        end_offset=end,
                        text=chunk_text,
                    )
                )
            if end == len(markdown_text):
                break
            next_start = end - overlap if overlap and end - overlap > start else end
            start = next_start
        return ChunkInfo(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            chunk_count=len(chunks),
            chunks=chunks,
        )

    def _segment_to_lines(self, segment: DocumentSegment) -> list[str]:
        if segment.kind == SegmentKind.heading:
            level = min(max(segment.level or 1, 1), 6)
            return [f"{'#' * level} {segment.text}", ""]
        if segment.kind == SegmentKind.list_item:
            return [f"- {segment.text}", ""]
        if segment.kind == SegmentKind.quote:
            return [f"> {segment.text}", ""]
        if segment.kind == SegmentKind.table_row:
            return [f"| {segment.text} |", ""]
        wrapped = fill(segment.text, width=self.settings.markdown_line_width)
        return [wrapped, ""]
