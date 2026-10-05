"""Database engine construction and per-request session dependency."""

from collections.abc import Iterator

from fastapi import Request
from sqlalchemy import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine


def build_engine(database_url: str) -> Engine:
    """Create a SQLAlchemy engine; in-memory SQLite shares one connection."""
    is_memory = database_url in {"sqlite://", "sqlite:///:memory:"}
    pool_options = {"poolclass": StaticPool} if is_memory else {}
    return create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        **pool_options,
    )


def create_tables(engine: Engine) -> None:
    """Create all tables known to SQLModel metadata (idempotent)."""
    SQLModel.metadata.create_all(engine)


def get_session(request: Request) -> Iterator[Session]:
    """FastAPI dependency yielding a session bound to the app's engine."""
    with Session(request.app.state.engine) as session:
        yield session
