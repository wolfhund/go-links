"""The go-link redirect: GET /{slug}."""

import logging
from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app import repository
from app.db import get_session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["redirect"])


@router.get(
    "/{slug}",
    status_code=status.HTTP_302_FOUND,
    response_class=RedirectResponse,
    responses={status.HTTP_302_FOUND: {"description": "Redirect to target or to UI"}},
)
def follow_link(
    slug: str,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
) -> RedirectResponse:
    """Redirect to the link target, or to the UI create form if unknown.

    302 (not 301) so browsers don't cache it: edits take effect immediately.
    """
    normalized = slug.strip().lower()
    link = repository.get_link(session, normalized)
    target = link.target_url if link else _create_form_url(request, normalized)
    logger.info("redirect slug=%s found=%s", normalized, link is not None)
    return RedirectResponse(target, status_code=status.HTTP_302_FOUND)


def _create_form_url(request: Request, slug: str) -> str:
    frontend_url = request.app.state.settings.frontend_url
    return f"{frontend_url}/?{urlencode({'slug': slug})}"
