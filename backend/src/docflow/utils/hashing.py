from __future__ import annotations

import hashlib
from collections import Counter

from docflow.utils.text import shingle_text


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def short_hash(text: str, length: int = 12) -> str:
    return sha256_text(text)[:length]


def simhash64(text: str) -> str:
    shingles = shingle_text(text, size=5)
    if not shingles:
        return "0" * 16
    vector = [0] * 64
    counts = Counter(shingles)
    for shingle, weight in counts.items():
        digest = hashlib.blake2b(shingle.encode("utf-8"), digest_size=8).digest()
        fingerprint = int.from_bytes(digest, "big")
        for index in range(64):
            bit = 1 if fingerprint & (1 << index) else -1
            vector[index] += bit * weight
    value = 0
    for index, score in enumerate(vector):
        if score >= 0:
            value |= 1 << index
    return f"{value:016x}"


def simhash_similarity(left: str, right: str) -> float:
    try:
        left_value = int(left, 16)
        right_value = int(right, 16)
    except ValueError:
        return 0.0
    distance = (left_value ^ right_value).bit_count()
    return 1 - (distance / 64)
