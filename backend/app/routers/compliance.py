"""Compliance assessment API endpoints"""
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta

from ..database import get_database
from ..models.schemas import ComplianceResponse, ComplianceControl
from ..utils.auth import get_organisation_id
from ..services.compliance import ComplianceService

router = APIRouter(prefix="/api/compliance", tags=["Compliance"])


@router.get("", response_model=ComplianceResponse)
async def get_compliance(
    organisation_id: str = Depends(get_organisation_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get compliance score and control status for the organisation.

    Returns:
    - Overall compliance score (0-100)
    - List of HIPAA security controls with their status
    - Summary statistics (total, compliant, non-compliant counts)

    Compliance data is cached and refreshed periodically.
    """
    compliance_service = ComplianceService(db)

    # Check if we have cached compliance data that's fresh (< 1 hour old)
    cached = await db.compliance_cache.find_one({"organisation_id": organisation_id})

    if cached:
        last_updated = cached.get("last_updated", datetime.min)
        if (datetime.utcnow() - last_updated).total_seconds() < 3600:
            # Use cached data
            controls = [ComplianceControl(**c) for c in cached["controls"]]
            return ComplianceResponse(
                organisation_id=cached["organisation_id"],
                score=cached["score"],
                controls=controls,
                total_controls=cached["total_controls"],
                compliant_controls=cached["compliant_controls"],
                non_compliant_controls=cached["non_compliant_controls"],
                last_updated=cached["last_updated"]
            )

    # Calculate fresh compliance data
    compliance_data = await compliance_service.calculate_compliance_score(organisation_id)

    # Update cache
    await compliance_service.update_compliance_cache(organisation_id)

    return ComplianceResponse(**compliance_data)
