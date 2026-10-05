"""Request IDs and access logging.

Every request gets an X-Request-ID (propagated from the client if present),
which is echoed in the response and attached to every log line emitted while
handling that request.
"""

import logging
import time
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"
MAX_REQUEST_ID_LENGTH = 128

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
access_logger = logging.getLogger("golinks.access")


class RequestIdFilter(logging.Filter):
    """Inject the current request ID into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def configure_logging(level: str) -> None:
    """Configure root logging with a request-aware format."""
    handler = logging.StreamHandler()
    handler.addFilter(RequestIdFilter())
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s [%(request_id)s] %(name)s: %(message)s"
        )
    )
    logging.basicConfig(level=level, handlers=[handler], force=True)


def _resolve_request_id(request: Request) -> str:
    # Trust a client-supplied ID only if it is reasonably sized.
    incoming = request.headers.get(REQUEST_ID_HEADER, "")
    is_usable = 0 < len(incoming) <= MAX_REQUEST_ID_LENGTH
    return incoming if is_usable else uuid.uuid4().hex


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Assign a request ID and log one access line per request."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Each request runs in its own context, so the var needs no reset.
        request_id = _resolve_request_id(request)
        request_id_var.set(request_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            access_logger.exception(
                "%s %s -> unhandled error", request.method, request.url.path
            )
            raise
        duration_ms = (time.perf_counter() - started) * 1000
        response.headers[REQUEST_ID_HEADER] = request_id
        access_logger.info(
            "%s %s -> %d (%.1f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
