"""
Seed script to populate MongoDB with realistic healthcare cybersecurity data
Run this after backend is deployed to populate the database
"""
import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings
import random

settings = get_settings()

# Test organization
ORG_ID = "org_001"


async def seed_data():
    """Populate MongoDB with seed data"""
    print("🌱 Starting data seeding...")

    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]

    print(f"✅ Connected to MongoDB: {settings.mongodb_db_name}")

    # Clear existing data for org_001
    print("🗑️  Clearing existing data for org_001...")
    await db.log_events.delete_many({"organisation_id": ORG_ID})
    await db.alerts.delete_many({"organisation_id": ORG_ID})
    await db.endpoints.delete_many({"organisation_id": ORG_ID})
    await db.compliance_controls.delete_many({"organisation_id": ORG_ID})

    # Seed Log Events
    print("📝 Seeding log events...")
    log_events = []
    now = datetime.utcnow()

    for i in range(50):
        event_time = now - timedelta(hours=random.randint(0, 48))
        log_events.append({
            "organisation_id": ORG_ID,
            "timestamp": event_time,
            "source": random.choice(["EDR", "SIEM", "Firewall", "IDS", "DLP"]),
            "event_type": random.choice(["login", "file_access", "network_connection", "process_execution", "authentication"]),
            "severity": random.choice(["critical", "high", "medium", "low"]),
            "host": random.choice(["DESKTOP-MED-01", "SERVER-EMR-01", "LAPTOP-ADMIN-03", "WS-RADIOLOGY-07", "SERVER-BACKUP-02"]),
            "user": random.choice(["dr.smith@clinic.nhs", "nurse.jones@clinic.nhs", "admin@clinic.nhs", "system"]),
            "description": f"Security event {i+1}",
            "raw_log": f"Raw log data for event {i+1}",
        })

    if log_events:
        await db.log_events.insert_many(log_events)
        print(f"   ✓ Created {len(log_events)} log events")

    # Seed Alerts
    print("🚨 Seeding alerts...")
    alerts = [
        {
            "organisation_id": ORG_ID,
            "timestamp": now - timedelta(hours=1),
            "host": "DESKTOP-MED-01",
            "user": "dr.smith@clinic.nhs",
            "severity": "critical",
            "category": "Malware Detection",
            "description": "Potential ransomware activity detected on endpoint",
            "ai_risk_score": 95,
            "recommended_action": "Isolate endpoint immediately and run full system scan",
            "status": "new",
            "source": "EDR System",
            "mitre_tactics": ["TA0040"],
            "iocs": ["suspicious.exe", "192.168.1.50"]
        },
        {
            "organisation_id": ORG_ID,
            "timestamp": now - timedelta(hours=3),
            "host": "SERVER-EMR-01",
            "user": "system",
            "severity": "high",
            "category": "Unauthorized Access",
            "description": "Multiple failed login attempts from external IP",
            "ai_risk_score": 82,
            "recommended_action": "Review firewall rules and enable MFA for all users",
            "status": "investigating",
            "source": "SIEM",
            "mitre_tactics": ["TA0001"],
            "iocs": ["185.220.101.23"]
        },
        {
            "organisation_id": ORG_ID,
            "timestamp": now - timedelta(hours=6),
            "host": "LAPTOP-ADMIN-03",
            "user": "admin@clinic.nhs",
            "severity": "medium",
            "category": "Policy Violation",
            "description": "USB device connected without authorization",
            "ai_risk_score": 58,
            "recommended_action": "Enforce USB device control policy",
            "status": "new",
            "source": "DLP System",
            "mitre_tactics": ["TA0009"],
            "iocs": []
        },
        {
            "organisation_id": ORG_ID,
            "timestamp": now - timedelta(hours=12),
            "host": "WS-RADIOLOGY-07",
            "user": "radiologist@clinic.nhs",
            "severity": "high",
            "category": "Suspicious Command Execution",
            "description": "PowerShell execution with suspicious parameters detected",
            "ai_risk_score": 78,
            "recommended_action": "Review PowerShell execution logs and isolate if necessary",
            "status": "new",
            "source": "EDR System",
            "mitre_tactics": ["TA0002"],
            "iocs": ["powershell.exe -enc"]
        },
        {
            "organisation_id": ORG_ID,
            "timestamp": now - timedelta(hours=24),
            "host": "SERVER-BACKUP-02",
            "user": "backup_service",
            "severity": "critical",
            "category": "Data Exfiltration",
            "description": "Large data transfer to external IP detected",
            "ai_risk_score": 92,
            "recommended_action": "Block IP at firewall and investigate data transfer",
            "status": "investigating",
            "source": "DLP System",
            "mitre_tactics": ["TA0010"],
            "iocs": ["45.142.212.61", "10GB transfer"]
        }
    ]

    if alerts:
        result = await db.alerts.insert_many(alerts)
        print(f"   ✓ Created {len(alerts)} alerts")

    # Seed Endpoints
    print("💻 Seeding endpoints...")
    endpoints = [
        {
            "organisation_id": ORG_ID,
            "hostname": "DESKTOP-MED-01",
            "ip_address": "192.168.1.101",
            "mac_address": "00:1B:44:11:3A:B7",
            "os": "Windows 11 Pro",
            "os_version": "22H2",
            "last_seen": now - timedelta(minutes=5),
            "risk_level": "critical",
            "status": "online",
            "agent_version": "7.2.1",
            "vulnerabilities": 12,
            "missing_patches": 8,
            "antivirus_status": "outdated",
            "firewall_status": "enabled",
            "encryption_status": "disabled"
        },
        {
            "organisation_id": ORG_ID,
            "hostname": "SERVER-EMR-01",
            "ip_address": "192.168.1.10",
            "mac_address": "00:1B:44:11:3A:B8",
            "os": "Windows Server 2022",
            "os_version": "21H2",
            "last_seen": now - timedelta(minutes=2),
            "risk_level": "high",
            "status": "online",
            "agent_version": "7.2.1",
            "vulnerabilities": 5,
            "missing_patches": 3,
            "antivirus_status": "active",
            "firewall_status": "enabled",
            "encryption_status": "enabled"
        },
        {
            "organisation_id": ORG_ID,
            "hostname": "LAPTOP-ADMIN-03",
            "ip_address": "192.168.1.105",
            "mac_address": "00:1B:44:11:3A:B9",
            "os": "Windows 11 Pro",
            "os_version": "22H2",
            "last_seen": now - timedelta(minutes=10),
            "risk_level": "medium",
            "status": "online",
            "agent_version": "7.2.0",
            "vulnerabilities": 3,
            "missing_patches": 2,
            "antivirus_status": "active",
            "firewall_status": "enabled",
            "encryption_status": "enabled"
        },
        {
            "organisation_id": ORG_ID,
            "hostname": "WS-RADIOLOGY-07",
            "ip_address": "192.168.1.207",
            "mac_address": "00:1B:44:11:3A:C0",
            "os": "Windows 10 Pro",
            "os_version": "21H2",
            "last_seen": now - timedelta(hours=2),
            "risk_level": "high",
            "status": "warning",
            "agent_version": "7.1.5",
            "vulnerabilities": 8,
            "missing_patches": 12,
            "antivirus_status": "active",
            "firewall_status": "enabled",
            "encryption_status": "disabled"
        },
        {
            "organisation_id": ORG_ID,
            "hostname": "SERVER-BACKUP-02",
            "ip_address": "192.168.1.12",
            "mac_address": "00:1B:44:11:3A:C1",
            "os": "Ubuntu Server 22.04",
            "os_version": "22.04.1",
            "last_seen": now - timedelta(hours=24),
            "risk_level": "high",
            "status": "offline",
            "agent_version": "7.2.1",
            "vulnerabilities": 6,
            "missing_patches": 15,
            "antivirus_status": "inactive",
            "firewall_status": "enabled",
            "encryption_status": "disabled"
        }
    ]

    if endpoints:
        await db.endpoints.insert_many(endpoints)
        print(f"   ✓ Created {len(endpoints)} endpoints")

    # Seed Compliance Controls
    print("📋 Seeding compliance controls...")
    frameworks = ["hipaa", "gdpr", "cyber_essentials", "cis", "iso27001"]

    compliance_controls = [
        # HIPAA
        {"organisation_id": ORG_ID, "control_id": "HIPAA-164.308", "framework": "hipaa", "name": "Access Control", "description": "Implement technical policies and procedures for electronic information systems", "status": "passed", "last_assessed": now},
        {"organisation_id": ORG_ID, "control_id": "HIPAA-164.312", "framework": "hipaa", "name": "Encryption and Decryption", "description": "Implement a mechanism to encrypt and decrypt ePHI", "status": "failed", "last_assessed": now, "remediation": "Enable BitLocker encryption on all endpoints containing ePHI"},
        {"organisation_id": ORG_ID, "control_id": "HIPAA-164.308(a)(5)", "framework": "hipaa", "name": "Security Awareness Training", "description": "Implement a security awareness and training program", "status": "warning", "last_assessed": now, "remediation": "3 staff members have not completed annual training"},

        # GDPR
        {"organisation_id": ORG_ID, "control_id": "GDPR-Art.32", "framework": "gdpr", "name": "Security of Processing", "description": "Implement appropriate technical and organizational measures", "status": "passed", "last_assessed": now},
        {"organisation_id": ORG_ID, "control_id": "GDPR-Art.33", "framework": "gdpr", "name": "Breach Notification", "description": "Notify supervisory authority of breach within 72 hours", "status": "passed", "last_assessed": now},
        {"organisation_id": ORG_ID, "control_id": "GDPR-Art.30", "framework": "gdpr", "name": "Records of Processing", "description": "Maintain records of all processing activities", "status": "failed", "last_assessed": now, "remediation": "Create comprehensive data processing inventory"},

        # Cyber Essentials
        {"organisation_id": ORG_ID, "control_id": "CE-FW", "framework": "cyber_essentials", "name": "Boundary Firewalls", "description": "Configure firewalls to restrict unauthorized access", "status": "passed", "last_assessed": now},
        {"organisation_id": ORG_ID, "control_id": "CE-PM", "framework": "cyber_essentials", "name": "Patch Management", "description": "Keep software and firmware up to date", "status": "failed", "last_assessed": now, "remediation": "Deploy pending security patches to 25 endpoints"},

        # CIS Controls
        {"organisation_id": ORG_ID, "control_id": "CIS-1", "framework": "cis", "name": "Inventory of Authorized Assets", "description": "Actively manage all hardware devices", "status": "passed", "last_assessed": now},
        {"organisation_id": ORG_ID, "control_id": "CIS-4", "framework": "cis", "name": "Secure Configuration", "description": "Establish and maintain secure configurations", "status": "failed", "last_assessed": now, "remediation": "Apply CIS benchmarks to all servers"},

        # ISO 27001
        {"organisation_id": ORG_ID, "control_id": "ISO-A.9.1.1", "framework": "iso27001", "name": "Access Control Policy", "description": "Establish and review access control policy", "status": "passed", "last_assessed": now},
        {"organisation_id": ORG_ID, "control_id": "ISO-A.12.4.1", "framework": "iso27001", "name": "Event Logging", "description": "Event logs recording user activities shall be produced", "status": "failed", "last_assessed": now, "remediation": "Enable comprehensive logging on 8 network devices"},
    ]

    if compliance_controls:
        await db.compliance_controls.insert_many(compliance_controls)
        print(f"   ✓ Created {len(compliance_controls)} compliance controls")

    print("\n✅ Data seeding completed successfully!")
    print(f"\n📊 Summary:")
    print(f"   - Log Events: {len(log_events)}")
    print(f"   - Alerts: {len(alerts)}")
    print(f"   - Endpoints: {len(endpoints)}")
    print(f"   - Compliance Controls: {len(compliance_controls)}")
    print(f"\n🔑 Test User Credentials:")
    print(f"   Organization ID: {ORG_ID}")
    print(f"   Create a user via: POST /api/auth/register")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed_data())
