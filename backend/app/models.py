"""Link persistence model and API schemas."""

from socket import socket
import ipaddress
from datetime import UTC, datetime

from pydantic import BaseModel, HttpUrl, field_validator
from pydantic import Field as SchemaField
from sqlmodel import Field, SQLModel

SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"
SLUG_MAX_LENGTH = 64
# Slugs that would shadow application routes at the root path.
RESERVED_SLUGS = frozenset({"api", "health", "docs", "redoc"})


def _utc_now() -> datetime:
    return datetime.now(UTC)

def is_block_ip(ip_str: str) -> bool:
    blocked = True
    try:
        ip = ipaddress.ip_address(ip_str)
    
        if ip.version == 6 and ip.ipv4_mapped is not None:
            ip = ip.ipv4_mapped
    
        blocked = (
            ip.is_loopback,
            ip.is_private,
            ip.is_link_local,
            ip.is_reserved,
        )
    except ValueError:
        blocked = False
    
    return blocked

def validate_safe_target_url(url: HttpUrl) -> HttpUrl:
    hostname = url.host

    if not hostname:
        raise ValueError("URL must include a hostname")
    
    # ask DNS
    try:
        answers = socket.getaddrinfo(hostname.strip("[]"), None)
    except socket.gaierror as e:
        raise ValueError(f"DNS resolution failed: {hostname}")

    # check all resolved IPs
    for answer in answers:
        if is_block_ip(answer[4][0]):
            raise ValueError(f"URL is not safe: {hostname} resolves to blocked IP {answer[4][0]}")
        
    return url


class Link(SQLModel, table=True):
    """A go link: a short slug that redirects to a target URL."""

    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True, max_length=SLUG_MAX_LENGTH)
    target_url: str
    created_at: datetime = Field(default_factory=_utc_now)


class LinkCreate(BaseModel):
    """Request body for creating a link."""

    slug: str = SchemaField(
        min_length=1, max_length=SLUG_MAX_LENGTH, pattern=SLUG_PATTERN
    )
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
    
    @field_validator("target_url")
    @classmethod
    def reject_internal_target(cls, value: HttpUrl) -> HttpUrl:
        result = validate_safe_target_url(value)
        return result
        

class LinkRead(BaseModel):
    """Public representation of a link."""

    model_config = {"from_attributes": True}

    slug: str
    target_url: str
    created_at: datetime
