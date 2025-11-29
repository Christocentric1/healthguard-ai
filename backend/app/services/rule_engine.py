"""Rule-based threat detection engine"""
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Tuple
import uuid

from ..models.schemas import LogEvent, Alert, AlertSeverity, AlertStatus
from ..config import get_settings

settings = get_settings()


class RuleEngine:
    """Rule-based detection engine for known attack patterns"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def check_failed_login_threshold(self, log_event: LogEvent) -> Optional[Alert]:
        """
        Check if user has exceeded failed login threshold.
        """
        if log_event.event_type != "login":
            return None

        if not log_event.details.get("success") is False:
            return None

        # Count recent failed logins for this user
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        failed_count = await self.db.logs.count_documents({
            "organisation_id": log_event.organisation_id,
            "user": log_event.user,
            "event_type": "login",
            "details.success": False,
            "timestamp": {"$gte": one_hour_ago}
        })

        if failed_count >= settings.failed_login_threshold:
            return Alert(
                alert_id=f"alert_{uuid.uuid4().hex[:16]}",
                organisation_id=log_event.organisation_id,
                title=f"Multiple Failed Login Attempts - {log_event.user}",
                description=f"User {log_event.user} has {failed_count} failed login attempts from {log_event.host} in the last hour",
                severity=AlertSeverity.HIGH,
                status=AlertStatus.OPEN,
                host=log_event.host,
                user=log_event.user,
                event_type=log_event.event_type,
                triggered_by="rule",
                rule_name="failed_login_threshold",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

        return None

    async def check_suspicious_process(self, log_event: LogEvent) -> Optional[Alert]:
        """
        Check for suspicious process names or commands.
        """
        if log_event.event_type not in ["process", "command", "execution"]:
            return None

        details_str = str(log_event.details).lower()
        process_name = log_event.details.get("process_name", "").lower()
        command = log_event.details.get("command", "").lower()

        # Check against known suspicious patterns
        for suspicious in settings.suspicious_processes:
            if suspicious.lower() in details_str or \
               suspicious.lower() in process_name or \
               suspicious.lower() in command:
                return Alert(
                    alert_id=f"alert_{uuid.uuid4().hex[:16]}",
                    organisation_id=log_event.organisation_id,
                    title=f"Suspicious Process Detected - {suspicious}",
                    description=f"Suspicious process/command '{suspicious}' detected on {log_event.host} by user {log_event.user}",
                    severity=AlertSeverity.CRITICAL,
                    status=AlertStatus.OPEN,
                    host=log_event.host,
                    user=log_event.user,
                    event_type=log_event.event_type,
                    triggered_by="rule",
                    rule_name="suspicious_process",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

        return None

    async def check_off_hours_access(self, log_event: LogEvent) -> Optional[Alert]:
        """
        Check for access during off-hours (weekends or late night).
        """
        timestamp = log_event.timestamp
        hour = timestamp.hour
        is_weekend = timestamp.weekday() >= 5  # Saturday or Sunday

        # Off-hours: weekends or 10 PM - 6 AM
        if is_weekend or hour >= 22 or hour < 6:
            # Only alert for certain event types
            if log_event.event_type in ["login", "access", "file_access", "database_access"]:
                return Alert(
                    alert_id=f"alert_{uuid.uuid4().hex[:16]}",
                    organisation_id=log_event.organisation_id,
                    title=f"Off-Hours Access - {log_event.user}",
                    description=f"User {log_event.user} accessed {log_event.host} during off-hours ({timestamp.strftime('%Y-%m-%d %H:%M')})",
                    severity=AlertSeverity.MEDIUM,
                    status=AlertStatus.OPEN,
                    host=log_event.host,
                    user=log_event.user,
                    event_type=log_event.event_type,
                    triggered_by="rule",
                    rule_name="off_hours_access",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

        return None

    async def check_multiple_host_access(self, log_event: LogEvent) -> Optional[Alert]:
        """
        Check if user is accessing from multiple hosts in short time.
        """
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        unique_hosts = await self.db.logs.distinct(
            "host",
            {
                "organisation_id": log_event.organisation_id,
                "user": log_event.user,
                "timestamp": {"$gte": one_hour_ago}
            }
        )

        if len(unique_hosts) >= 5:
            return Alert(
                alert_id=f"alert_{uuid.uuid4().hex[:16]}",
                organisation_id=log_event.organisation_id,
                title=f"Multiple Host Access - {log_event.user}",
                description=f"User {log_event.user} accessed {len(unique_hosts)} different hosts in the last hour",
                severity=AlertSeverity.MEDIUM,
                status=AlertStatus.OPEN,
                host=log_event.host,
                user=log_event.user,
                event_type=log_event.event_type,
                triggered_by="rule",
                rule_name="multiple_host_access",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

        return None

    async def evaluate_all_rules(self, log_event: LogEvent) -> List[Alert]:
        """
        Evaluate all detection rules against a log event.

        Returns:
            List of alerts generated by rules
        """
        alerts = []

        # Run all rule checks
        rules = [
            self.check_failed_login_threshold(log_event),
            self.check_suspicious_process(log_event),
            self.check_off_hours_access(log_event),
            self.check_multiple_host_access(log_event)
        ]

        # Gather results
        for rule_result in await asyncio.gather(*rules):
            if rule_result:
                alerts.append(rule_result)

        return alerts


import asyncio  # Import at module level for gather
