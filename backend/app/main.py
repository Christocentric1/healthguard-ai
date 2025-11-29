"""Main FastAPI application for Cyber HealthGuard AI"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import get_settings
from .database import connect_to_mongo, close_mongo_connection
from .routers import logs, alerts, endpoints, compliance, auth, telemetry

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Cyber HealthGuard AI - Backend API

    A multi-tenant healthcare cybersecurity platform with AI-powered threat detection.

    ### Features
    - 🔍 **Log Ingestion**: Ingest logs from endpoints, SIEM, and other sources
    - 🤖 **AI/ML Anomaly Detection**: Machine learning-based anomaly detection using Isolation Forest
    - 🚨 **Alert Management**: Create, view, and manage security alerts
    - 📊 **Risk Assessment**: Endpoint risk scoring and aggregation
    - ✅ **Compliance Monitoring**: HIPAA compliance scoring and control assessment
    - 🏢 **Multi-Tenancy**: Secure organisation-based data isolation

    ### Authentication
    All requests must include the `X-Org-Id` header with your organisation ID.

    Example: `X-Org-Id: org_001`
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
# Read allowed origins from environment variables with fallback defaults
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_env:
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
else:
    # Default allowed origins
    allowed_origins = [
        "https://healthguards-ai.netlify.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ]

# Read origin regex from environment variable
allow_origin_regex_env = os.getenv("ALLOW_ORIGIN_REGEX", "")
if allow_origin_regex_env:
    allow_origin_regex = allow_origin_regex_env
else:
    # Default: Allow all Netlify deploy previews
    allow_origin_regex = r"https://.*\.netlify\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(logs.router)
app.include_router(alerts.router)
app.include_router(endpoints.router)
app.include_router(compliance.router)
app.include_router(telemetry.router)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
        "message": "Cyber HealthGuard AI API is running"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "services": {
            "log_ingestion": "operational",
            "anomaly_detection": "operational",
            "alert_management": "operational",
            "risk_assessment": "operational",
            "compliance": "operational"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
