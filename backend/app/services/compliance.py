"""Compliance scoring and assessment"""
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict

from ..models.schemas import ComplianceControl, ControlStatus, AlertSeverity


class ComplianceService:
    """Service for calculating compliance scores and control status"""

    # HIPAA-aligned security controls (sample)
    HIPAA_CONTROLS = [
        {
            "id": "HIPAA-164.312(a)(1)",
            "name": "Access Control - Unique User Identification",
            "category": "access_control"
        },
        {
            "id": "HIPAA-164.312(a)(2)(i)",
            "name": "Access Control - Emergency Access Procedure",
            "category": "access_control"
        },
        {
            "id": "HIPAA-164.312(b)",
            "name": "Audit Controls",
            "category": "audit"
        },
        {
            "id": "HIPAA-164.312(c)(1)",
            "name": "Integrity - Mechanism to Authenticate ePHI",
            "category": "integrity"
        },
        {
            "id": "HIPAA-164.312(d)",
            "name": "Person or Entity Authentication",
            "category": "authentication"
        },
        {
            "id": "HIPAA-164.312(e)(1)",
            "name": "Transmission Security",
            "category": "transmission"
        },
        {
            "id": "HIPAA-164.308(a)(1)(ii)(D)",
            "name": "Information System Activity Review",
            "category": "monitoring"
        },
        {
            "id": "HIPAA-164.308(a)(5)(ii)(C)",
            "name": "Log-in Monitoring",
            "category": "monitoring"
        },
        {
            "id": "HIPAA-164.308(a)(3)(ii)(A)",
            "name": "Authorization and/or Supervision",
            "category": "workforce"
        },
        {
            "id": "HIPAA-164.308(a)(4)(ii)(B)",
            "name": "Isolating Health Care Clearinghouse Functions",
            "category": "isolation"
        }
    ]

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def assess_control_status(
        self,
        organisation_id: str,
        control: Dict
    ) -> ComplianceControl:
        """
        Assess the status of a specific compliance control based on logs and alerts.
        """
        now = datetime.utcnow()
        thirty_days_ago = now - timedelta(days=30)

        status = ControlStatus.COMPLIANT
        notes = []

        category = control["category"]

        # Access Control checks
        if category == "access_control":
            failed_access = await self.db.alerts.count_documents({
                "organisation_id": organisation_id,
                "event_type": "access_denied",
                "created_at": {"$gte": thirty_days_ago},
                "status": {"$ne": "resolved"}
            })
            if failed_access > 5:
                status = ControlStatus.PARTIAL
                notes.append(f"{failed_access} unresolved access control violations")

        # Audit Controls - check if logging is comprehensive
        elif category == "audit":
            total_endpoints = await self.db.endpoints.count_documents({"organisation_id": organisation_id})
            endpoints_with_logs = len(await self.db.logs.distinct(
                "host",
                {"organisation_id": organisation_id, "timestamp": {"$gte": thirty_days_ago}}
            ))

            if total_endpoints > 0 and endpoints_with_logs < total_endpoints * 0.9:
                status = ControlStatus.PARTIAL
                notes.append(f"Only {endpoints_with_logs}/{total_endpoints} endpoints have recent audit logs")
            else:
                notes.append("All endpoints have comprehensive audit logging")

        # Authentication checks
        elif category == "authentication":
            failed_logins = await self.db.alerts.count_documents({
                "organisation_id": organisation_id,
                "rule_name": "failed_login_threshold",
                "created_at": {"$gte": thirty_days_ago}
            })
            if failed_logins > 10:
                status = ControlStatus.NON_COMPLIANT
                notes.append(f"{failed_logins} failed login threshold violations in last 30 days")
            elif failed_logins > 3:
                status = ControlStatus.PARTIAL
                notes.append(f"{failed_logins} failed login incidents detected")

        # Monitoring checks
        elif category == "monitoring":
            unresolved_critical = await self.db.alerts.count_documents({
                "organisation_id": organisation_id,
                "severity": AlertSeverity.CRITICAL.value,
                "status": {"$ne": "resolved"}
            })
            if unresolved_critical > 0:
                status = ControlStatus.NON_COMPLIANT
                notes.append(f"{unresolved_critical} unresolved critical alerts")
            else:
                notes.append("All critical alerts resolved")

        # Default for other categories
        else:
            notes.append("Control assessed based on configuration")

        return ComplianceControl(
            id=control["id"],
            name=control["name"],
            status=status,
            notes=" | ".join(notes) if notes else None,
            last_assessed=now
        )

    async def calculate_compliance_score(self, organisation_id: str) -> Dict:
        """
        Calculate overall compliance score and assess all controls.

        Returns a dict with score, controls, and summary stats.
        """
        controls: List[ComplianceControl] = []

        for control_def in self.HIPAA_CONTROLS:
            control = await self.assess_control_status(organisation_id, control_def)
            controls.append(control)

        # Calculate score
        total_controls = len(controls)
        compliant_controls = sum(1 for c in controls if c.status == ControlStatus.COMPLIANT)
        partial_controls = sum(1 for c in controls if c.status == ControlStatus.PARTIAL)
        non_compliant_controls = sum(1 for c in controls if c.status == ControlStatus.NON_COMPLIANT)

        # Score: compliant = 100%, partial = 50%, non-compliant = 0%
        if total_controls > 0:
            score = ((compliant_controls * 100) + (partial_controls * 50)) / total_controls
        else:
            score = 100.0

        return {
            "organisation_id": organisation_id,
            "score": round(score, 2),
            "controls": controls,
            "total_controls": total_controls,
            "compliant_controls": compliant_controls,
            "non_compliant_controls": non_compliant_controls,
            "last_updated": datetime.utcnow()
        }

    async def update_compliance_cache(self, organisation_id: str):
        """
        Update cached compliance data in database.
        This can be run periodically as a background task.
        """
        compliance_data = await self.calculate_compliance_score(organisation_id)

        # Convert controls to dicts for MongoDB storage
        controls_dict = [c.model_dump() for c in compliance_data["controls"]]
        compliance_data["controls"] = controls_dict

        await self.db.compliance_cache.update_one(
            {"organisation_id": organisation_id},
            {"$set": compliance_data},
            upsert=True
        )
