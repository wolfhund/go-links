"""Data access for links. Routes depend on these functions, not on SQL."""

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models import Link, LinkCreate


class SlugAlreadyExistsError(Exception):
    """Raised when creating a link whose slug is already taken."""

    def __init__(self, slug: str) -> None:
        super().__init__(f"Slug '{slug}' already exists")
        self.slug = slug


def list_links(session: Session) -> list[Link]:
    """Return all links ordered alphabetically by slug."""
    return list(session.exec(select(Link).order_by(Link.slug)).all())


def get_link(session: Session, slug: str) -> Link | None:
    """Return the link for `slug`, or None if it does not exist."""
    return session.exec(select(Link).where(Link.slug == slug)).first()


def create_link(session: Session, data: LinkCreate) -> Link:
    """Persist a new link; the DB unique constraint decides collisions."""
    link = Link(slug=data.slug, target_url=str(data.target_url))
    session.add(link)
    _commit_or_raise_conflict(session, data.slug)
    session.refresh(link)
    return link


def _commit_or_raise_conflict(session: Session, slug: str) -> None:
    # Relying on the UNIQUE constraint (instead of check-then-insert)
    # avoids a race between two concurrent creates of the same slug.
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise SlugAlreadyExistsError(slug) from error
