from __future__ import annotations

from pathlib import Path

from docflow.services.jobs import JobService


def test_expand_paths_filters_supported_types(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "a.txt").write_text("hello", encoding="utf-8")
    (nested / "b.log").write_text("2026-05-12 INFO Started", encoding="utf-8")
    (nested / "image.png").write_bytes(b"binary")

    expanded = JobService.expand_paths([nested])
    suffixes = sorted(path.suffix for path in expanded)
    assert suffixes == [".log", ".txt"]
