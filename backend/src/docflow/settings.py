from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

def is_frozen_app() -> bool:
    return bool(getattr(sys, "frozen", False))


def get_bundle_root() -> Path:
    if is_frozen_app():
        return Path(getattr(sys, "_MEIPASS")).resolve()
    return Path(__file__).resolve().parents[3]


def get_data_root() -> Path:
    if is_frozen_app():
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "DocFlowStudio"
        return Path.home() / ".docflow-studio"
    return get_bundle_root()


BUNDLE_ROOT = get_bundle_root()
DATA_ROOT = get_data_root()
DEFAULT_CONFIG_PATH = BUNDLE_ROOT / "config" / "default.yaml"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DOCFLOW_", extra="ignore")

    app_name: str = "DocFlow Studio"
    environment: str = "local"
    default_tenant_id: str = "demo-tenant"
    max_workers: int = 2
    retry_attempts: int = 2
    api_port: int = 8765
    desktop_title: str = "DocFlow Studio"

    exact_similarity: float = 1.0
    near_similarity_threshold: float = 0.9
    paragraph_similarity_threshold: float = 0.93
    keep_policy: str = "first_seen"

    collapse_blank_lines: bool = True
    remove_repeated_headers: bool = True
    remove_page_numbers: bool = True
    remove_control_chars: bool = True
    trim_quote_threads: bool = True

    placeholder_style: str = "bracketed"
    redaction_rules: list[str] = Field(default_factory=list)

    chunk_size: int = 1200
    chunk_overlap: int = 150
    markdown_line_width: int = 100

    repo_root: Path = BUNDLE_ROOT
    runtime_dir: Path = DATA_ROOT / "data" / "runtime"
    upload_dir: Path = DATA_ROOT / "data" / "runtime" / "uploads"
    output_dir: Path = DATA_ROOT / "data" / "output"
    database_path: Path = DATA_ROOT / "data" / "runtime" / "db" / "docflow.db"
    frontend_dist: Path = BUNDLE_ROOT / "frontend" / "dist"
    log_dir: Path = DATA_ROOT / "data" / "runtime" / "logs"

    @classmethod
    def from_yaml(cls, config_path: Path | None = None) -> Settings:
        config_file = config_path or DEFAULT_CONFIG_PATH
        if not config_file.exists():
            raise FileNotFoundError(
                f"DocFlow configuration file was not found: {config_file}"
            )
        data = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
        flattened = flatten_settings(data)
        return cls(**flattened)

    def ensure_directories(self) -> None:
        for directory in [
            self.runtime_dir,
            self.upload_dir,
            self.output_dir,
            self.database_path.parent,
            self.log_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


def flatten_settings(data: dict[str, Any]) -> dict[str, Any]:
    app = data.get("app", {})
    dedup = data.get("dedup", {})
    cleaning = data.get("cleaning", {})
    redaction = data.get("redaction", {})
    output = data.get("output", {})
    return {
        "app_name": app.get("name", "DocFlow Studio"),
        "environment": app.get("environment", "local"),
        "default_tenant_id": app.get("default_tenant_id", "demo-tenant"),
        "max_workers": app.get("max_workers", 2),
        "retry_attempts": app.get("retry_attempts", 2),
        "api_port": app.get("api_port", 8765),
        "desktop_title": app.get("desktop_title", "DocFlow Studio"),
        "exact_similarity": dedup.get("exact_similarity", 1.0),
        "near_similarity_threshold": dedup.get("near_similarity_threshold", 0.9),
        "paragraph_similarity_threshold": dedup.get("paragraph_similarity_threshold", 0.93),
        "keep_policy": dedup.get("keep_policy", "first_seen"),
        "collapse_blank_lines": cleaning.get("collapse_blank_lines", True),
        "remove_repeated_headers": cleaning.get("remove_repeated_headers", True),
        "remove_page_numbers": cleaning.get("remove_page_numbers", True),
        "remove_control_chars": cleaning.get("remove_control_chars", True),
        "trim_quote_threads": cleaning.get("trim_quote_threads", True),
        "placeholder_style": redaction.get("placeholder_style", "bracketed"),
        "redaction_rules": redaction.get("rules", []),
        "chunk_size": output.get("chunk_size", 1200),
        "chunk_overlap": output.get("chunk_overlap", 150),
        "markdown_line_width": output.get("markdown_line_width", 100),
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings.from_yaml()
    settings.ensure_directories()
    return settings
