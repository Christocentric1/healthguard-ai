"""Main FastAPI application for Cyber HealthGuard AI"""

import os
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from .config import get_settings
from .database import connect_to_mongo, close_mongo_connection
from .routers import logs, alerts, endpoints, compliance, auth, telemetry, agent

settings = get_settings()


def _parse_allowed_origins(raw_origins: str | None, defaults: List[str]) -> List[str]:
    """Parse comma-separated list of origins or fallback to defaults."""
    if not raw_origins:
        return defaults
    parsed = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return parsed or defaults


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events."""
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Cyber HealthGuard AI - Backend API

    A multi-tenant healthcare cybersecurity platform with AI-powered threat detection.

    ### Features
    - Log Ingestion
    - AI/ML Anomaly Detection
    - Alert Management
    - Risk Assessment
    - Compliance Monitoring
    - Multi-Tenancy (X-Org-Id required)
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# -----------------------------
# CORS CONFIGURATION
# -----------------------------

DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://healthguards-ai.netlify.app",         # Production Netlify
]

# Load overrides from Fly.io env (secret)
ALLOWED_ORIGINS = _parse_allowed_origins(
    os.getenv("ALLOWED_ORIGINS"),
    DEFAULT_ALLOWED_ORIGINS,
)

# Allow all Netlify preview URLs
raw_origin_regex = os.getenv("ALLOW_ORIGIN_REGEX")
ALLOW_ORIGIN_REGEX = (
    raw_origin_regex.strip()
    if raw_origin_regex and raw_origin_regex.strip()
    else r"https://.*\.netlify\.app"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=ALLOW_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# -----------------------------
# GLOBAL PRE-FLIGHT HANDLER
# -----------------------------
# Required to stop 400 errors on OPTIONS hitting auth routes

@app.options("/{path:path}")
async def preflight_handler(path: str):
    """Return 200 immediately so CORS middleware can attach headers."""
    return Response(status_code=200)


# -----------------------------
# ROUTERS
# -----------------------------
app.include_router(auth.router)
app.include_router(logs.router)
app.include_router(alerts.router)
app.include_router(endpoints.router)
app.include_router(compliance.router)
app.include_router(telemetry.router)
app.include_router(agent.router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
        "message": "Cyber HealthGuard AI API is running"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
