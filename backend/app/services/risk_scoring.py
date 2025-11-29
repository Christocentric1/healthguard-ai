"""Risk scoring and endpoint risk assessment"""
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Dict

from ..models.schemas import RiskLevel, AlertSeverity


class RiskScoringService:
    """Service for calculating endpoint and organisation risk scores"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def calculate_endpoint_risk(self, organisation_id: str, host: str) -> Dict:
        """
        Calculate risk metrics for a specific endpoint.

        Returns a dict with risk_level, risk_score, and various counts.
        """
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)

        # Count alerts in different time windows
        alerts_7d = await self.db.alerts.count_documents({
            "organisation_id": organisation_id,
            "host": host,
            "created_at": {"$gte": seven_days_ago}
        })

        alerts_30d = await self.db.alerts.count_documents({
            "organisation_id": organisation_id,
            "host": host,
            "created_at": {"$gte": thirty_days_ago}
        })

        # Count critical alerts
        critical_alerts = await self.db.alerts.count_documents({
            "organisation_id": organisation_id,
            "host": host,
            "severity": AlertSeverity.CRITICAL.value,
            "status": {"$ne": "resolved"}
        })

        # Count anomaly-triggered alerts
        anomaly_count = await self.db.alerts.count_documents({
            "organisation_id": organisation_id,
            "host": host,
            "triggered_by": "anomaly",
            "created_at": {"$gte": seven_days_ago}
        })

        # Calculate risk score (0-100)
        risk_score = 0.0
        risk_score += min(alerts_7d * 5, 30)  # Up to 30 points for recent alerts
        risk_score += min(critical_alerts * 20, 40)  # Up to 40 points for critical alerts
        risk_score += min(anomaly_count * 10, 30)  # Up to 30 points for anomalies

        risk_score = min(risk_score, 100.0)

        # Determine risk level
        if risk_score >= 75:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 50:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 25:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "alert_count_7d": alerts_7d,
            "alert_count_30d": alerts_30d,
            "anomaly_count": anomaly_count,
            "critical_alerts": critical_alerts,
            "compliance_issues": 0  # Can be enhanced later
        }

    async def update_all_endpoint_risks(self, organisation_id: str):
        """
        Recalculate risk scores for all endpoints in an organisation.
        This can be run periodically as a background task.
        """
        # Get all unique hosts for this organisation
        hosts = await self.db.logs.distinct("host", {"organisation_id": organisation_id})

        for host in hosts:
            risk_data = await self.calculate_endpoint_risk(organisation_id, host)

            # Update endpoint record
            await self.db.endpoints.update_one(
                {"organisation_id": organisation_id, "host": host},
                {
                    "$set": {
                        **risk_data,
                        "last_updated": datetime.utcnow()
                    }
                },
                upsert=True
            )
