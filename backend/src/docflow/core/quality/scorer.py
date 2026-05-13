from __future__ import annotations

from docflow.schemas import DedupStatus, ProcessingAudit


class QualityScorer:
    def score(
        self,
        *,
        markdown_text: str,
        dedup_status: DedupStatus,
        audit: ProcessingAudit,
    ) -> float:
        score = 100.0
        if len(markdown_text.strip()) < 120:
            score -= 15
        if len(markdown_text.strip()) < 400:
            score -= 8
        if dedup_status == DedupStatus.exact_duplicate:
            score -= 25
        elif dedup_status == DedupStatus.near_duplicate:
            score -= 15
        elif dedup_status == DedupStatus.partial_duplicate:
            score -= 6
        score -= min(len(audit.errors) * 10, 25)
        score -= min(len(audit.warnings) * 5, 15)
        if len(audit.cleaning_actions) == 0:
            score -= 3
        if len(audit.sensitive_matches) > 25:
            score -= 5
        return round(max(score, 0.0), 2)
