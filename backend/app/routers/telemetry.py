"""Telemetry endpoint for agent data ingestion"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from datetime import datetime
import secrets

from ..models.schemas import TelemetryPayload, TelemetryResponse
from ..database import get_database

router = APIRouter(prefix="/api/telemetry", tags=["Telemetry"])


@router.post("/ingest", response_model=TelemetryResponse)
async def ingest_telemetry(
    payload: TelemetryPayload,
    x_organisation_id: Optional[str] = Header(None, alias="X-Organisation-ID"),
    x_agent_version: Optional[str] = Header(None, alias="X-Agent-Version")
):
    """
    Ingest telemetry data from endpoint agents

    This endpoint receives system information, security events, and process data
    from Windows endpoint agents running the CyberGuard PowerShell script.

    The data is stored in MongoDB and used for:
    - Endpoint health monitoring
    - Security event analysis
    - Process behavior analysis
    - Anomaly detection
    - Compliance reporting
    """
    db = await get_database()

    # Validate organisation ID
    org_id = x_organisation_id or payload.organisation_id
    if not org_id:
        raise HTTPException(
            status_code=400,
            detail="Organisation ID must be provided in header or payload"
        )

    # Ensure payload uses the correct org ID
    payload.organisation_id = org_id
    payload.system_info.organisation_id = org_id

    try:
        # Generate telemetry ID
        telemetry_id = f"tel_{secrets.token_hex(12)}"
        timestamp = datetime.utcnow()

        # Prepare telemetry document
        telemetry_doc = {
            "telemetry_id": telemetry_id,
            "agent_id": payload.agent_id,
            "hostname": payload.hostname,
            "organisation_id": org_id,
            "collected_at": payload.collected_at,
            "ingested_at": timestamp,
            "agent_version": x_agent_version or payload.system_info.agent_version,
            "system_info": payload.system_info.model_dump(),
            "security_events": [event.model_dump() for event in payload.security_events],
            "process_info": [proc.model_dump() for proc in payload.process_info],
            "metrics": payload.metrics.model_dump()
        }

        # Store telemetry data
        await db.telemetry.insert_one(telemetry_doc)

        # Update or create endpoint record
        endpoint_doc = {
            "hostname": payload.hostname,
            "organisation_id": org_id,
            "last_seen": timestamp,
            "agent_version": x_agent_version or payload.system_info.agent_version,
            "os_name": payload.system_info.os_name,
            "os_version": payload.system_info.os_version,
            "os_architecture": payload.system_info.os_architecture,
            "cpu_cores": payload.system_info.cpu_cores,
            "total_memory_gb": payload.system_info.total_memory_gb,
            "domain": payload.system_info.domain,
            "manufacturer": payload.system_info.manufacturer,
            "model": payload.system_info.model,
            "status": "online",
            "health_score": 100,  # Calculate based on metrics
            "risk_score": 0,  # Calculate based on security events
            "updated_at": timestamp
        }

        result = await db.endpoints.update_one(
            {"hostname": payload.hostname, "organisation_id": org_id},
            {"$set": endpoint_doc, "$setOnInsert": {"created_at": timestamp}},
            upsert=True
        )

        endpoint_updated = result.modified_count > 0 or result.upserted_id is not None

        # Process security events and create alerts if needed
        alerts_created = 0

        # Check for suspicious security events
        failed_logon_events = [
            event for event in payload.security_events
            if event.event_id == 4625  # Failed logon
        ]

        if len(failed_logon_events) >= 5:
            # Create alert for multiple failed logons
            alert_id = f"alert_{secrets.token_hex(8)}"
            alert_doc = {
                "alert_id": alert_id,
                "organisation_id": org_id,
                "title": "Multiple Failed Logon Attempts Detected",
                "description": f"Endpoint {payload.hostname} had {len(failed_logon_events)} failed logon attempts",
                "severity": "high",
                "status": "open",
                "host": payload.hostname,
                "event_type": "authentication",
                "triggered_by": "rule",
                "rule_name": "Multiple Failed Logons",
                "created_at": timestamp,
                "updated_at": timestamp,
                "related_telemetry_ids": [telemetry_id],
                "comments": []
            }
            await db.alerts.insert_one(alert_doc)
            alerts_created += 1

        # Check for suspicious processes
        high_cpu_processes = [
            proc for proc in payload.process_info
            if proc.cpu > 80  # High CPU usage
        ]

        if len(high_cpu_processes) >= 3:
            # Create alert for high CPU usage
            alert_id = f"alert_{secrets.token_hex(8)}"
            alert_doc = {
                "alert_id": alert_id,
                "organisation_id": org_id,
                "title": "High CPU Usage Detected",
                "description": f"Endpoint {payload.hostname} has {len(high_cpu_processes)} processes with high CPU usage",
                "severity": "medium",
                "status": "open",
                "host": payload.hostname,
                "event_type": "performance",
                "triggered_by": "rule",
                "rule_name": "High CPU Usage",
                "created_at": timestamp,
                "updated_at": timestamp,
                "related_telemetry_ids": [telemetry_id],
                "comments": []
            }
            await db.alerts.insert_one(alert_doc)
            alerts_created += 1

        return TelemetryResponse(
            success=True,
            message="Telemetry data ingested successfully",
            telemetry_id=telemetry_id,
            endpoint_updated=endpoint_updated,
            alerts_created=alerts_created
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest telemetry: {str(e)}"
        )


@router.get("/health")
async def telemetry_health():
    """Health check for telemetry endpoint"""
    return {
        "status": "operational",
        "endpoint": "/telemetry/ingest",
        "version": "2.0",
        "accepts": "TelemetryPayload"
    }
