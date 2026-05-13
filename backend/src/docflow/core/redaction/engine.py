from __future__ import annotations

import re
from dataclasses import dataclass

from docflow.schemas import SensitiveMatch
from docflow.settings import Settings


@dataclass(frozen=True)
class RegexRule:
    rule_id: str
    field_type: str
    pattern: re.Pattern[str]


class RedactionEngine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.rules = self._build_rules(settings.redaction_rules)

    def redact(self, text: str) -> tuple[str, list[SensitiveMatch], list[str]]:
        redacted = text
        matches: list[SensitiveMatch] = []
        field_hits: list[str] = []
        counters: dict[str, int] = {}
        mappings: dict[tuple[str, str], str] = {}

        for rule in self.rules:

            def replacer(match: re.Match[str], current_rule: RegexRule = rule) -> str:
                value = (match.groupdict().get("value") or match.group(0)).strip()
                key = (current_rule.field_type, value)
                if key not in mappings:
                    counters[current_rule.field_type] = (
                        counters.get(current_rule.field_type, 0) + 1
                    )
                    mappings[key] = self._placeholder(
                        current_rule.field_type,
                        counters[current_rule.field_type],
                    )
                placeholder = mappings[key]
                field_hits.append(current_rule.field_type)
                matches.append(
                    SensitiveMatch(
                        field_type=current_rule.field_type,
                        rule_id=current_rule.rule_id,
                        placeholder=placeholder,
                        original_excerpt=value[:120],
                        span_start=match.start(),
                        span_end=match.end(),
                    )
                )
                if "value" in match.groupdict():
                    return match.group(0).replace(value, placeholder, 1)
                return placeholder

            redacted = rule.pattern.sub(replacer, redacted)

        return redacted, matches, sorted(set(field_hits))

    def _placeholder(self, field_type: str, index: int) -> str:
        label = field_type.upper()
        if self.settings.placeholder_style == "bracketed":
            return f"[{label}_{index}]"
        return f"<{label}_{index}>"

    @staticmethod
    def _build_rules(enabled_rules: list[str]) -> list[RegexRule]:
        configured = set(enabled_rules)
        rules = [
            RegexRule(
                rule_id="person_name",
                field_type="person_name",
                pattern=re.compile(
                    r"(?P<label>(?:\u59d3\u540d|\u8054\u7cfb\u4eba|\u5ba2\u6237|"
                    r"\u6536\u4ef6\u4eba|Name|Contact)\s*[:\uff1a]\s*)"
                    r"(?P<value>[\u4e00-\u9fa5A-Za-z\u00b7]{2,30})"
                ),
            ),
            RegexRule(
                rule_id="email",
                field_type="email",
                pattern=re.compile(r"(?P<value>[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"),
            ),
            RegexRule(
                rule_id="address",
                field_type="address",
                pattern=re.compile(
                    r"(?P<label>(?:\u5730\u5740|Address)\s*[:\uff1a]\s*)"
                    r"(?P<value>[^\n]{6,120})"
                ),
            ),
            RegexRule(
                rule_id="id_number",
                field_type="id_number",
                pattern=re.compile(r"(?P<value>\b\d{17}[0-9Xx]\b|\b[A-Z]{1,2}\d{6,12}\b)"),
            ),
            RegexRule(
                rule_id="account",
                field_type="account",
                pattern=re.compile(
                    r"(?P<label>(?:\u8d26\u53f7|\u8d26\u6237|Account)\s*[:\uff1a#]?\s*)"
                    r"(?P<value>[A-Za-z0-9_-]{6,32})"
                ),
            ),
            RegexRule(
                rule_id="order_number",
                field_type="order_number",
                pattern=re.compile(
                    r"(?P<label>(?:\u8ba2\u5355\u53f7|Order(?: Number| No\.)?)\s*[:\uff1a#]?\s*)"
                    r"(?P<value>[A-Za-z0-9-]{6,40})",
                    re.IGNORECASE,
                ),
            ),
            RegexRule(
                rule_id="ip_address",
                field_type="ip_address",
                pattern=re.compile(r"(?P<value>\b(?:\d{1,3}\.){3}\d{1,3}\b)"),
            ),
            RegexRule(
                rule_id="access_token",
                field_type="access_token",
                pattern=re.compile(
                    r"(?P<label>(?:token|access_token|bearer)\s*[:= ]\s*)"
                    r"(?P<value>[A-Za-z0-9._\-]{16,})",
                    re.IGNORECASE,
                ),
            ),
            RegexRule(
                rule_id="secret_key",
                field_type="secret_key",
                pattern=re.compile(
                    r"(?P<label>(?:api[_-]?key|secret|secret[_-]?key|\u5bc6\u7801|Password)"
                    r"\s*[:= ]\s*)(?P<value>[^\s\"';]{8,64})",
                    re.IGNORECASE,
                ),
            ),
            RegexRule(
                rule_id="cookie",
                field_type="cookie",
                pattern=re.compile(
                    r"(?P<label>cookie\s*[:=]\s*)(?P<value>[^\n]{8,200})",
                    re.IGNORECASE,
                ),
            ),
            RegexRule(
                rule_id="phone",
                field_type="phone",
                pattern=re.compile(
                    r"(?P<value>\b(?:\+?86[- ]?)?1[3-9]\d{9}\b|"
                    r"\b(?:\+?\d{1,3}[- ]?)?(?:\d{3,4}[- ]?){2,3}\d{3,4}\b)"
                ),
            ),
            RegexRule(
                rule_id="contract_number",
                field_type="contract_number",
                pattern=re.compile(
                    r"(?P<label>(?:\u5408\u540c\u7f16\u53f7|Contract(?: Number| No\.)?)"
                    r"\s*[:\uff1a#]?\s*)(?P<value>[A-Za-z0-9-]{6,40})",
                    re.IGNORECASE,
                ),
            ),
        ]
        if not configured:
            return rules
        return [rule for rule in rules if rule.rule_id in configured]
