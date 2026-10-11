"""Health check and system info endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "AI Audio Timestamping Platform API",
        "version": "0.1.0",
    }


@router.get("/health/live", tags=["health"])
async def liveness_probe():
    """Liveness probe for Kubernetes."""
    return {"status": "alive"}


@router.get("/health/ready", tags=["health"])
async def readiness_probe():
    """Readiness probe for Kubernetes."""
    return {"status": "ready"}
