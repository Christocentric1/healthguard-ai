"""Log ingestion API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import uuid

from ..database import get_database
from ..models.schemas import LogEvent, LogEventResponse
from ..services.anomaly_detection import AnomalyDetector
from ..services.rule_engine import RuleEngine
from ..services.risk_scoring import RiskScoringService
from ..utils.auth import get_organisation_id

router = APIRouter(prefix="/api/ingest", tags=["Log Ingestion"])


@router.post("/logs", response_model=LogEventResponse, status_code=status.HTTP_201_CREATED)
async def ingest_log(
    log_event: LogEvent,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Ingest a log event and perform anomaly detection and rule-based threat detection.

    The event is analyzed through:
    1. Rule-based detection (failed logins, suspicious processes, etc.)
    2. ML-based anomaly detection
    3. Automatic alert creation if threats are detected

    Returns:
        LogEventResponse with log_id and alert information if generated
    """
    try:
        # Generate log ID
        log_id = f"log_{uuid.uuid4().hex[:16]}"

        # Prepare log document
        log_dict = log_event.model_dump()
        log_dict["log_id"] = log_id
        log_dict["ingested_at"] = datetime.utcnow()

        # Insert log into database
        await db.logs.insert_one(log_dict)

        # Initialize detection services
        rule_engine = RuleEngine(db)
        anomaly_detector = AnomalyDetector(db)

        # 1. Rule-based detection
        rule_alerts = await rule_engine.evaluate_all_rules(log_event)

        # 2. Anomaly detection
        is_anomaly, anomaly_score = await anomaly_detector.predict_anomaly(log_event)

        alert_created = False
        alert_id = None

        # Create alerts from rules
        for alert in rule_alerts:
            alert_dict = alert.model_dump()
            alert_dict["related_log_ids"] = [log_id]
            await db.alerts.insert_one(alert_dict)
            alert_created = True
            alert_id = alert.alert_id

        # Create alert for anomaly if detected
        if is_anomaly and not rule_alerts:  # Only if no rule-based alert was created
            from ..models.schemas import Alert, AlertSeverity, AlertStatus

            # Determine severity based on anomaly score
            if anomaly_score > 0.9:
                severity = AlertSeverity.CRITICAL
            elif anomaly_score > 0.8:
                severity = AlertSeverity.HIGH
            elif anomaly_score > 0.7:
                severity = AlertSeverity.MEDIUM
            else:
                severity = AlertSeverity.LOW

            anomaly_alert = Alert(
                alert_id=f"alert_{uuid.uuid4().hex[:16]}",
                organisation_id=log_event.organisation_id,
                title=f"Anomalous Behavior Detected - {log_event.host}",
                description=f"ML model detected anomalous {log_event.event_type} event on {log_event.host} by {log_event.user} (score: {anomaly_score:.2f})",
                severity=severity,
                status=AlertStatus.OPEN,
                host=log_event.host,
                user=log_event.user,
                event_type=log_event.event_type,
                anomaly_score=anomaly_score,
                triggered_by="anomaly",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                related_log_ids=[log_id]
            )

            await db.alerts.insert_one(anomaly_alert.model_dump())
            alert_created = True
            alert_id = anomaly_alert.alert_id

        # Update endpoint last_seen
        await db.endpoints.update_one(
            {"organisation_id": log_event.organisation_id, "host": log_event.host},
            {
                "$set": {
                    "last_seen": log_event.timestamp,
                    "ip_address": log_event.details.get("ip_address"),
                    "os_type": log_event.details.get("os_type")
                }
            },
            upsert=True
        )

        # Trigger background risk recalculation (simplified - in production use Celery/background tasks)
        # For now, we'll calculate it on-demand in the endpoints API

        return LogEventResponse(
            success=True,
            message="Log event ingested successfully",
            log_id=log_id,
            alert_created=alert_created,
            alert_id=alert_id,
            anomaly_score=anomaly_score if is_anomaly or anomaly_score > 0.5 else None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest log: {str(e)}"
        )
