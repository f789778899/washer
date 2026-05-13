from __future__ import annotations

import re
from collections import Counter

from docflow.schemas import CleaningAction, DocumentSegment, NormalizedDocument, SegmentKind
from docflow.settings import Settings
from docflow.utils.text import normalize_text

PAGE_NUMBER_RE = re.compile(r"^(page\s+\d+(\s+of\s+\d+)?|\d+/\d+|\d+)$", re.IGNORECASE)
EMAIL_QUOTE_RE = re.compile(r"^on .+ wrote:$", re.IGNORECASE)


class CleanerEngine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def clean(
        self, document: NormalizedDocument
    ) -> tuple[NormalizedDocument, list[CleaningAction]]:
        actions: list[CleaningAction] = []
        segments = list(document.segments)

        if self.settings.remove_repeated_headers:
            segments, removed = self._remove_repeated_short_segments(segments)
            if removed:
                actions.append(
                    CleaningAction(
                        action="remove_repeated_headers",
                        detail="Removed recurring short segments",
                        count=removed,
                    )
                )

        segments, removed_numbers = self._remove_page_numbers(segments)
        if removed_numbers:
            actions.append(
                CleaningAction(
                    action="remove_page_numbers",
                    detail="Removed page-number-only lines",
                    count=removed_numbers,
                )
            )

        if document.doc_type.value == "email" and self.settings.trim_quote_threads:
            segments, trimmed = self._trim_email_quotes(segments)
            if trimmed:
                actions.append(
                    CleaningAction(
                        action="trim_email_quotes",
                        detail="Trimmed quoted email thread tail",
                        count=trimmed,
                    )
                )

        if document.doc_type.value == "log":
            segments, deduped = self._squash_repeated_log_lines(segments)
            if deduped:
                actions.append(
                    CleaningAction(
                        action="squash_repeated_log_lines",
                        detail="Collapsed repeated log lines",
                        count=deduped,
                    )
                )

        cleaned_segments: list[DocumentSegment] = []
        whitespace_changes = 0
        for position, segment in enumerate(segments, start=1):
            cleaned_text = normalize_text(
                segment.text, remove_control_chars=self.settings.remove_control_chars
            )
            if not cleaned_text:
                continue
            if cleaned_text != segment.text:
                whitespace_changes += 1
            cleaned_segments.append(
                segment.model_copy(update={"text": cleaned_text, "position": position})
            )
        if whitespace_changes:
            actions.append(
                CleaningAction(
                    action="normalize_whitespace",
                    detail="Normalized spacing and control characters",
                    count=whitespace_changes,
                )
            )

        normalized_text = "\n\n".join(segment.text for segment in cleaned_segments)
        cleaned_document = document.model_copy(
            update={
                "segments": cleaned_segments,
                "normalized_text": normalized_text,
                "updated_at": document.updated_at,
            }
        )
        return cleaned_document, actions

    @staticmethod
    def _remove_repeated_short_segments(
        segments: list[DocumentSegment],
    ) -> tuple[list[DocumentSegment], int]:
        repeated_candidates = Counter(
            segment.text.strip()
            for segment in segments
            if segment.kind in {SegmentKind.paragraph, SegmentKind.line}
            and 1 < len(segment.text.strip()) <= 40
        )
        blacklist = {
            text
            for text, count in repeated_candidates.items()
            if count >= 3 and not PAGE_NUMBER_RE.match(text)
        }
        filtered = [segment for segment in segments if segment.text.strip() not in blacklist]
        return filtered, len(segments) - len(filtered)

    @staticmethod
    def _remove_page_numbers(segments: list[DocumentSegment]) -> tuple[list[DocumentSegment], int]:
        filtered = [
            segment for segment in segments if not PAGE_NUMBER_RE.match(segment.text.strip())
        ]
        return filtered, len(segments) - len(filtered)

    @staticmethod
    def _trim_email_quotes(segments: list[DocumentSegment]) -> tuple[list[DocumentSegment], int]:
        cutoff = None
        for index, segment in enumerate(segments):
            text = segment.text.strip()
            if EMAIL_QUOTE_RE.match(text) or text.startswith(">"):
                cutoff = index
                break
        if cutoff is None:
            return segments, 0
        trimmed = segments[:cutoff]
        return trimmed, len(segments) - len(trimmed)

    @staticmethod
    def _squash_repeated_log_lines(
        segments: list[DocumentSegment],
    ) -> tuple[list[DocumentSegment], int]:
        filtered: list[DocumentSegment] = []
        last_text = None
        removed = 0
        for segment in segments:
            if segment.text == last_text:
                removed += 1
                continue
            filtered.append(segment)
            last_text = segment.text
        return filtered, removed
