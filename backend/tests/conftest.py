from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

FRONTEND_URL = "http://ui.test"


@pytest.fixture
def client() -> Iterator[TestClient]:
    """A client against a fresh in-memory database per test."""
    settings = Settings(database_url="sqlite://", frontend_url=FRONTEND_URL)
    with TestClient(create_app(settings), follow_redirects=False) as test_client:
        yield test_client


@pytest.fixture
def create_link(client: TestClient):
    """Helper to POST a link and return the response."""

    def _create(slug: str, target_url: str = "https://example.com/"):
        return client.post("/api/links", json={"slug": slug, "target_url": target_url})

    return _create
