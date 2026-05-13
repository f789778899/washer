from __future__ import annotations

from collections.abc import Iterable

from docflow.schemas import (
    DedupStatus,
    DocumentSegment,
    DuplicateRelation,
    NormalizedDocument,
    SegmentKind,
)
from docflow.settings import Settings
from docflow.utils.hashing import sha256_text, simhash_similarity
from docflow.utils.text import word_overlap


class DedupEngine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def evaluate(
        self,
        document: NormalizedDocument,
        corpus_records: Iterable[dict],
    ) -> tuple[NormalizedDocument, DedupStatus, list[DuplicateRelation]]:
        relations: list[DuplicateRelation] = []
        dedup_status = DedupStatus.unique

        deduped_segments, segment_relations = self._dedup_segments(document.segments)
        relations.extend(segment_relations)
        if segment_relations and dedup_status == DedupStatus.unique:
            dedup_status = DedupStatus.partial_duplicate

        for record in corpus_records:
            if record.get("tenant_id") != document.tenant_id:
                continue
            if record.get("normalized_checksum") == document.normalized_checksum:
                dedup_status = DedupStatus.exact_duplicate
                relations.append(
                    DuplicateRelation(
                        relation_type="exact_document",
                        similarity=1.0,
                        related_document_id=record.get("document_id"),
                        reason="Normalized checksum matched an existing document",
                        keep_policy=self.settings.keep_policy,
                    )
                )
                break
            similarity = simhash_similarity(record.get("simhash", ""), document.simhash)
            if similarity >= self.settings.near_similarity_threshold:
                dedup_status = DedupStatus.near_duplicate
                relations.append(
                    DuplicateRelation(
                        relation_type="near_document",
                        similarity=round(similarity, 4),
                        related_document_id=record.get("document_id"),
                        reason="Simhash similarity exceeded the near-duplicate threshold",
                        keep_policy=self.settings.keep_policy,
                    )
                )
                break

        normalized_text = "\n\n".join(segment.text for segment in deduped_segments)
        updated_document = document.model_copy(
            update={
                "segments": [
                    segment.model_copy(update={"position": index})
                    for index, segment in enumerate(deduped_segments, start=1)
                ],
                "normalized_text": normalized_text,
            }
        )
        return updated_document, dedup_status, relations

    def _dedup_segments(
        self, segments: list[DocumentSegment]
    ) -> tuple[list[DocumentSegment], list[DuplicateRelation]]:
        seen: dict[str, str] = {}
        filtered: list[DocumentSegment] = []
        relations: list[DuplicateRelation] = []
        for segment in segments:
            if segment.kind not in {SegmentKind.paragraph, SegmentKind.line, SegmentKind.list_item}:
                filtered.append(segment)
                continue
            segment_hash = sha256_text(segment.text.lower())
            if segment_hash in seen and len(segment.text) >= 32:
                relations.append(
                    DuplicateRelation(
                        relation_type="exact_segment",
                        similarity=1.0,
                        related_segment_id=seen[segment_hash],
                        reason="Repeated segment text detected within the same document",
                        keep_policy="first_occurrence",
                    )
                )
                continue
            if self._is_near_duplicate(segment.text, filtered):
                relations.append(
                    DuplicateRelation(
                        relation_type="near_segment",
                        similarity=self.settings.paragraph_similarity_threshold,
                        reason="Segment similarity exceeded the within-document threshold",
                        keep_policy="first_occurrence",
                    )
                )
                continue
            seen[segment_hash] = segment.segment_id
            filtered.append(segment)
        return filtered, relations

    def _is_near_duplicate(self, text: str, existing_segments: list[DocumentSegment]) -> bool:
        candidates = [
            segment
            for segment in existing_segments
            if segment.kind in {SegmentKind.paragraph, SegmentKind.line, SegmentKind.list_item}
        ]
        for candidate in candidates[-10:]:
            if len(candidate.text) < 32:
                continue
            if word_overlap(candidate.text, text) >= self.settings.paragraph_similarity_threshold:
                return True
        return False
