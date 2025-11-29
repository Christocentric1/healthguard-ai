"""Endpoint management and risk assessment API"""
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime

from ..database import get_database
from ..models.schemas import Endpoint, EndpointListResponse, RiskLevel
from ..utils.auth import get_organisation_id
from ..services.risk_scoring import RiskScoringService

router = APIRouter(prefix="/api/endpoints", tags=["Endpoints"])


@router.get("", response_model=EndpointListResponse)
async def list_endpoints(
    organisation_id: str = Depends(get_organisation_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get list of all endpoints for the organisation with aggregated risk metrics.

    Each endpoint includes:
    - Risk level and score
    - Alert counts (7-day and 30-day windows)
    - Anomaly detection counts
    - Critical alert counts
    - Compliance issues
    """
    # Get all unique hosts from logs
    hosts = await db.logs.distinct("host", {"organisation_id": organisation_id})

    risk_service = RiskScoringService(db)
    endpoints = []

    for host in hosts:
        # Try to get existing endpoint record
        endpoint_doc = await db.endpoints.find_one({
            "organisation_id": organisation_id,
            "host": host
        })

        if endpoint_doc:
            # Check if risk data is stale (> 1 hour old)
            last_updated = endpoint_doc.get("last_updated", datetime.min)
            if (datetime.utcnow() - last_updated).total_seconds() > 3600:
                # Recalculate risk
                risk_data = await risk_service.calculate_endpoint_risk(organisation_id, host)
                endpoint_doc.update(risk_data)
                await db.endpoints.update_one(
                    {"organisation_id": organisation_id, "host": host},
                    {"$set": {**risk_data, "last_updated": datetime.utcnow()}}
                )
        else:
            # Calculate risk for new endpoint
            risk_data = await risk_service.calculate_endpoint_risk(organisation_id, host)

            # Get last seen timestamp
            last_log = await db.logs.find_one(
                {"organisation_id": organisation_id, "host": host},
                sort=[("timestamp", -1)]
            )

            endpoint_doc = {
                "organisation_id": organisation_id,
                "host": host,
                "last_seen": last_log["timestamp"] if last_log else datetime.utcnow(),
                **risk_data
            }

            await db.endpoints.insert_one(endpoint_doc)

        # Convert to Endpoint model
        try:
            endpoint = Endpoint(**endpoint_doc)
            endpoints.append(endpoint)
        except Exception:
            # Fallback for missing fields
            endpoint = Endpoint(
                organisation_id=organisation_id,
                host=host,
                last_seen=endpoint_doc.get("last_seen", datetime.utcnow()),
                risk_level=endpoint_doc.get("risk_level", RiskLevel.LOW),
                risk_score=endpoint_doc.get("risk_score", 0.0),
                alert_count_7d=endpoint_doc.get("alert_count_7d", 0),
                alert_count_30d=endpoint_doc.get("alert_count_30d", 0),
                anomaly_count=endpoint_doc.get("anomaly_count", 0),
                critical_alerts=endpoint_doc.get("critical_alerts", 0),
                compliance_issues=endpoint_doc.get("compliance_issues", 0),
                ip_address=endpoint_doc.get("ip_address"),
                os_type=endpoint_doc.get("os_type")
            )
            endpoints.append(endpoint)

    # Sort by risk score descending
    endpoints.sort(key=lambda e: e.risk_score, reverse=True)

    return EndpointListResponse(
        endpoints=endpoints,
        total=len(endpoints)
    )
