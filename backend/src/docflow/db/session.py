from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from docflow.db.models import Base
from docflow.settings import Settings


def build_engine(settings: Settings):
    return create_engine(
        f"sqlite:///{settings.database_path}",
        future=True,
        connect_args={"check_same_thread": False},
    )


def build_session_factory(settings: Settings) -> sessionmaker[Session]:
    engine = build_engine(settings)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
