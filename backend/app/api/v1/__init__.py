"""API v1 routes."""

from fastapi import APIRouter

from app.api.v1.endpoints import audio, health, projects, transcripts

api_router = APIRouter()

# Include routers
api_router.include_router(health.router)
api_router.include_router(projects.router)
api_router.include_router(audio.router)
api_router.include_router(transcripts.router)
api_router.include_router(transcripts.exports_router)
