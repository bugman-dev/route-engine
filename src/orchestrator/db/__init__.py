"""SQLAlchemy base and engine/session helpers."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from orchestrator.config import get_settings


class Base(DeclarativeBase):
    pass


_engine = None
_SessionLocal = None


def get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        settings = get_settings()
        connect_args = {}
        # SQLite needs check_same_thread=False for tests / TestClient.
        if settings.database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        _engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            connect_args=connect_args,
        )
        _SessionLocal = sessionmaker(
            bind=_engine, autocommit=False, autoflush=False
        )
    return _engine


def get_session_factory():
    get_engine()
    return _SessionLocal


def init_db() -> None:
    """Create tables if they do not exist (v1 bootstrap; Alembic later)."""
    # Import models so metadata is populated.
    from orchestrator.db import models  # noqa: F401

    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ping_db() -> bool:
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def reset_engine_for_tests() -> None:
    """Clear cached engine (used by tests that set DATABASE_URL)."""
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None
    get_settings.cache_clear()
