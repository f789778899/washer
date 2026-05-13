from __future__ import annotations

from pathlib import Path

import pytest

from docflow.settings import Settings


@pytest.fixture()
def test_settings(tmp_path: Path) -> Settings:
    settings = Settings.from_yaml()
    isolated = settings.model_copy(
        update={
            "runtime_dir": tmp_path / "runtime",
            "upload_dir": tmp_path / "runtime" / "uploads",
            "output_dir": tmp_path / "output",
            "database_path": tmp_path / "runtime" / "db" / "docflow.db",
            "log_dir": tmp_path / "runtime" / "logs",
        }
    )
    isolated.ensure_directories()
    return isolated
