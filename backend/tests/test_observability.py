import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.observability import RequestIdMiddleware


def test_response_includes_generated_request_id(client) -> None:
    response = client.get("/health")

    assert len(response.headers["X-Request-ID"]) == 32


def test_client_request_id_is_propagated(client) -> None:
    response = client.get("/health", headers={"X-Request-ID": "trace-abc"})

    assert response.headers["X-Request-ID"] == "trace-abc"


def test_oversized_client_request_id_is_replaced(client) -> None:
    response = client.get("/health", headers={"X-Request-ID": "x" * 500})

    assert response.headers["X-Request-ID"] != "x" * 500


def test_access_log_contains_request_id(client, caplog) -> None:
    with caplog.at_level(logging.INFO, logger="golinks.access"):
        client.get("/health", headers={"X-Request-ID": "trace-log"})

    record = next(r for r in caplog.records if r.name == "golinks.access")
    assert record.request_id == "trace-log"
    assert "GET /health -> 200" in record.getMessage()


def test_unhandled_error_is_logged_and_reraised(caplog) -> None:
    app = FastAPI()
    app.add_middleware(RequestIdMiddleware)

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("boom")

    with caplog.at_level(logging.ERROR, logger="golinks.access"):
        with pytest.raises(RuntimeError):
            TestClient(app).get("/boom")

    assert any("unhandled error" in r.getMessage() for r in caplog.records)
