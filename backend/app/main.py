"""Application factory and ASGI entrypoint."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import Settings, load_settings
from app.db import build_engine, create_tables
from app.routes import links, redirect


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build a configured FastAPI app (tests pass their own settings)."""
    resolved = settings or load_settings()
    engine = build_engine(resolved.database_url)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        create_tables(engine)
        yield
        engine.dispose()

    app = FastAPI(title="Go Links", version="0.1.0", lifespan=lifespan)
    app.state.settings = resolved
    app.state.engine = engine
    app.include_router(links.router)
    # Catch-all /{slug} must be registered last so it never shadows other routes.
    app.include_router(redirect.router)
    return app


app = create_app()
