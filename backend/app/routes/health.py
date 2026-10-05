"""Liveness endpoint for operators and load balancers."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Report that the process is up."""
    return {"status": "ok"}
