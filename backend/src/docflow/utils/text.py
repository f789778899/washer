from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from collections.abc import Iterable

from ftfy import fix_text
from langdetect import DetectorFactory, detect

DetectorFactory.seed = 0


WHITESPACE_RE = re.compile(r"[ \t]+")
BLANK_LINES_RE = re.compile(r"\n{3,}")
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


def normalize_text(text: str, remove_control_chars: bool = True) -> str:
    normalized = fix_text(text or "")
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = unicodedata.normalize("NFKC", normalized)
    if remove_control_chars:
        normalized = CONTROL_CHARS_RE.sub("", normalized)
    normalized = "\n".join(WHITESPACE_RE.sub(" ", line).strip() for line in normalized.splitlines())
    normalized = BLANK_LINES_RE.sub("\n\n", normalized)
    return normalized.strip()


def detect_language(text: str) -> str:
    try:
        if not text.strip():
            return "unknown"
        return detect(text)
    except Exception:
        return "unknown"


def word_overlap(a: str, b: str) -> float:
    left = set(re.findall(r"\w+", a.lower()))
    right = set(re.findall(r"\w+", b.lower()))
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def split_into_paragraphs(text: str) -> list[str]:
    return [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]


def shingle_text(text: str, size: int = 5) -> list[str]:
    compact = re.sub(r"\s+", " ", text.lower()).strip()
    if len(compact) <= size:
        return [compact] if compact else []
    return [compact[index : index + size] for index in range(len(compact) - size + 1)]


def cosine_counter_similarity(left: Counter[str], right: Counter[str]) -> float:
    shared = set(left) & set(right)
    numerator = sum(left[token] * right[token] for token in shared)
    left_magnitude = math.sqrt(sum(value * value for value in left.values()))
    right_magnitude = math.sqrt(sum(value * value for value in right.values()))
    if not left_magnitude or not right_magnitude:
        return 0.0
    return numerator / (left_magnitude * right_magnitude)


def token_counter(text: str) -> Counter[str]:
    return Counter(re.findall(r"\w+", text.lower()))


def most_repeated_lines(text: str, min_count: int = 2) -> list[str]:
    counts = Counter(line.strip() for line in text.splitlines() if line.strip())
    return [line for line, count in counts.items() if count >= min_count]


def remove_lines(text: str, lines_to_remove: Iterable[str]) -> str:
    blacklist = {line.strip() for line in lines_to_remove if line.strip()}
    kept = [line for line in text.splitlines() if line.strip() not in blacklist]
    return "\n".join(kept).strip()
