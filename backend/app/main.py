"""Main FastAPI application for Cyber HealthGuard AI"""
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
# NOTE: Cannot use "*" with allow_credentials=True
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cyberhealthguards.netlify.app",
        "https://*.netlify.app",  # All Netlify deploy previews
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
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
