"""Link persistence model and API schemas."""

from datetime import UTC, datetime

from pydantic import HttpUrl, field_validator
from sqlmodel import Field, SQLModel

SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"
SLUG_MAX_LENGTH = 64
# Slugs that would shadow application routes at the root path.
RESERVED_SLUGS = frozenset({"api", "health", "docs", "redoc"})


def _utc_now() -> datetime:
    return datetime.now(UTC)


class Link(SQLModel, table=True):
    """A go link: a short slug that redirects to a target URL."""

    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True, max_length=SLUG_MAX_LENGTH)
    target_url: str
    created_at: datetime = Field(default_factory=_utc_now)


class LinkCreate(SQLModel):
    """Request body for creating a link."""

    slug: str = Field(min_length=1, max_length=SLUG_MAX_LENGTH, pattern=SLUG_PATTERN)
    target_url: HttpUrl

    @field_validator("slug", mode="before")
    @classmethod
    def normalize_slug(cls, value: object) -> object:
        """Trim and lowercase so `OnCall` and `oncall` are the same link."""
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("slug")
    @classmethod
    def reject_reserved_slug(cls, value: str) -> str:
        """Prevent slugs that collide with application routes."""
        if value in RESERVED_SLUGS:
            raise ValueError(f"'{value}' is reserved")
        return value


class LinkRead(SQLModel):
    """Public representation of a link."""

    slug: str
    target_url: str
    created_at: datetime
