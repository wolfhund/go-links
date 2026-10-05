"""REST endpoints for managing links."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app import repository
from app.db import get_session
from app.models import Link, LinkCreate, LinkRead

router = APIRouter(prefix="/api/links", tags=["links"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("", response_model=list[LinkRead])
def list_links(session: SessionDep) -> list[Link]:
    """List every link, ordered by slug."""
    return repository.list_links(session)


@router.post(
    "",
    response_model=LinkRead,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"description": "Slug already exists"}},
)
def create_link(payload: LinkCreate, session: SessionDep) -> Link:
    """Create a new link. Returns 409 if the slug is taken."""
    try:
        link = repository.create_link(session, payload)
    except repository.SlugAlreadyExistsError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(error)) from error
    return link
