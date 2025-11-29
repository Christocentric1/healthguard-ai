"""Alert management API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from datetime import datetime
import math

from ..database import get_database
from ..models.schemas import Alert, AlertUpdate, AlertListResponse, AlertStatus
from ..utils.auth import get_organisation_id
from ..config import get_settings

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])
settings = get_settings()


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    organisation_id: str = Depends(get_organisation_id),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[AlertStatus] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    host: Optional[str] = Query(None, description="Filter by host"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get paginated list of alerts for the authenticated organisation.

    Filters:
    - status: Filter by alert status (open, in_progress, resolved)
    - severity: Filter by severity (low, medium, high, critical)
    - host: Filter by specific host/endpoint
    """
    # Build query filter
    query = {"organisation_id": organisation_id}

    if status_filter:
        query["status"] = status_filter.value

    if severity:
        query["severity"] = severity

    if host:
        query["host"] = host

    # Get total count
    total = await db.alerts.count_documents(query)

    # Calculate pagination
    skip = (page - 1) * page_size
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    # Fetch alerts
    cursor = db.alerts.find(query).sort("created_at", -1).skip(skip).limit(page_size)
    alert_docs = await cursor.to_list(length=page_size)

    # Convert to Alert models
    alerts = [Alert(**doc) for doc in alert_docs]

    return AlertListResponse(
        alerts=alerts,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{alert_id}", response_model=Alert)
async def get_alert(
    alert_id: str,
    organisation_id: str = Depends(get_organisation_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get a single alert by ID.

    Ensures the alert belongs to the authenticated organisation.
    """
    alert_doc = await db.alerts.find_one({
        "alert_id": alert_id,
        "organisation_id": organisation_id
    })

    if not alert_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found"
        )

    return Alert(**alert_doc)


@router.patch("/{alert_id}", response_model=Alert)
async def update_alert(
    alert_id: str,
    update: AlertUpdate,
    organisation_id: str = Depends(get_organisation_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update an alert's status and/or add a comment.

    Only the status and comments can be updated.
    The alert must belong to the authenticated organisation.
    """
    # Find the alert
    alert_doc = await db.alerts.find_one({
        "alert_id": alert_id,
        "organisation_id": organisation_id
    })

    if not alert_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found"
        )

    # Prepare update
    update_data = {"updated_at": datetime.utcnow()}

    if update.status:
        update_data["status"] = update.status.value

    if update.comment:
        # Append comment to comments array
        await db.alerts.update_one(
            {"alert_id": alert_id},
            {"$push": {"comments": f"[{datetime.utcnow().isoformat()}] {update.comment}"}}
        )

    # Apply updates
    await db.alerts.update_one(
        {"alert_id": alert_id},
        {"$set": update_data}
    )

    # Fetch updated alert
    updated_doc = await db.alerts.find_one({"alert_id": alert_id})
    return Alert(**updated_doc)
