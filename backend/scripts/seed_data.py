"""Seed script to generate fake log data for testing"""
import requests
import random
from datetime import datetime, timedelta
import time

API_URL = "http://localhost:8000"
ORG_ID = "org_001"

# Sample data
HOSTS = [
    "WKS-001", "WKS-002", "WKS-003", "WKS-004", "WKS-005",
    "SRV-DB-01", "SRV-WEB-01", "SRV-APP-01", "LAPTOP-HR-01", "LAPTOP-IT-01"
]

USERS = [
    "john.doe", "jane.smith", "bob.johnson", "alice.williams", "charlie.brown",
    "diana.martinez", "evan.davis", "fiona.wilson", "george.anderson", "hannah.taylor"
]

EVENT_TYPES = ["login", "logout", "file_access", "process", "network", "database_access", "command"]

SOURCES = ["ActiveDirectory", "EDR", "SIEM", "Syslog", "Database", "Firewall"]

SUSPICIOUS_PROCESSES = [
    "mimikatz.exe", "powershell.exe -enc", "cmd.exe /c whoami", "net user",
    "procdump.exe", "psexec.exe"
]

NORMAL_PROCESSES = [
    "chrome.exe", "outlook.exe", "word.exe", "excel.exe", "teams.exe",
    "python.exe", "java.exe", "notepad.exe"
]


def generate_log_event(is_suspicious=False, is_anomalous=False):
    """Generate a single log event"""
    host = random.choice(HOSTS)
    user = random.choice(USERS)
    event_type = random.choice(EVENT_TYPES)
    source = random.choice(SOURCES)

    # Base timestamp - randomly in the last 7 days
    timestamp = datetime.utcnow() - timedelta(
        days=random.randint(0, 7),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )

    # If anomalous, make it at odd hours
    if is_anomalous:
        timestamp = timestamp.replace(hour=random.choice([2, 3, 4, 23, 1]))

    details = {}

    if event_type == "login":
        # Generate failed logins for suspicious events
        if is_suspicious:
            details["success"] = False
            details["failure_reason"] = random.choice(["Invalid credentials", "Account locked", "Timeout"])
        else:
            details["success"] = random.choice([True, True, True, False])  # 75% success
        details["ip_address"] = f"192.168.1.{random.randint(1, 254)}"
        details["method"] = random.choice(["Password", "MFA", "SSO"])

    elif event_type == "process":
        if is_suspicious:
            details["process_name"] = random.choice(SUSPICIOUS_PROCESSES)
            details["command"] = details["process_name"]
        else:
            details["process_name"] = random.choice(NORMAL_PROCESSES)
        details["pid"] = random.randint(1000, 9999)

    elif event_type == "file_access":
        details["file_path"] = random.choice([
            "/var/log/secure",
            "/etc/passwd",
            "/home/user/documents/patient_records.xlsx",
            "C:\\Users\\Public\\Documents\\report.docx",
            "\\\\file-server\\shared\\data.csv"
        ])
        details["action"] = random.choice(["read", "write", "delete", "modify"])

    elif event_type == "network":
        details["destination_ip"] = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        details["destination_port"] = random.choice([80, 443, 22, 3389, 445, 1433, 3306])
        details["protocol"] = random.choice(["TCP", "UDP"])
        details["bytes_sent"] = random.randint(100, 100000)

    details["os_type"] = "Windows 10" if host.startswith("WKS") or host.startswith("LAPTOP") else "Linux"

    return {
        "organisation_id": ORG_ID,
        "host": host,
        "user": user,
        "timestamp": timestamp.isoformat() + "Z",
        "event_type": event_type,
        "source": source,
        "details": details
    }


def send_log(log_event):
    """Send a log event to the API"""
    headers = {"X-Org-Id": ORG_ID, "Content-Type": "application/json"}
    try:
        response = requests.post(f"{API_URL}/ingest/logs", json=log_event, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error sending log: {e}")
        return None


def main():
    """Generate and send fake log data"""
    print("🚀 Starting data seeding for Cyber HealthGuard AI\n")
    print(f"📡 API URL: {API_URL}")
    print(f"🏢 Organisation ID: {ORG_ID}\n")

    # Check if API is running
    try:
        response = requests.get(f"{API_URL}/health")
        response.raise_for_status()
        print("✅ API is healthy\n")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Please make sure the API is running with: docker-compose up")
        return

    # Generate logs
    total_logs = 200
    suspicious_count = 15
    anomalous_count = 10

    print(f"📝 Generating {total_logs} log events...")
    print(f"   - Normal events: {total_logs - suspicious_count - anomalous_count}")
    print(f"   - Suspicious events: {suspicious_count}")
    print(f"   - Anomalous events: {anomalous_count}\n")

    alerts_created = 0
    logs_with_anomaly = 0

    # Generate suspicious events (should trigger rules)
    print("🔴 Generating suspicious events...")
    for i in range(suspicious_count):
        log_event = generate_log_event(is_suspicious=True)
        result = send_log(log_event)
        if result and result.get("alert_created"):
            alerts_created += 1
            print(f"   ✓ Alert created: {result.get('alert_id')}")
        time.sleep(0.1)

    # Generate anomalous events (odd timing, unusual patterns)
    print("\n🟡 Generating anomalous events...")
    for i in range(anomalous_count):
        log_event = generate_log_event(is_anomalous=True)
        result = send_log(log_event)
        if result and result.get("anomaly_score"):
            logs_with_anomaly += 1
        if result and result.get("alert_created"):
            alerts_created += 1
            print(f"   ✓ Alert created: {result.get('alert_id')}")
        time.sleep(0.1)

    # Generate normal events
    print("\n🟢 Generating normal events...")
    normal_count = total_logs - suspicious_count - anomalous_count
    for i in range(normal_count):
        log_event = generate_log_event()
        result = send_log(log_event)
        if result and result.get("alert_created"):
            alerts_created += 1
        if i % 20 == 0:
            print(f"   ✓ Sent {i}/{normal_count} normal events...")
        time.sleep(0.05)

    # Summary
    print("\n" + "="*60)
    print("📊 SEEDING SUMMARY")
    print("="*60)
    print(f"✅ Total logs generated: {total_logs}")
    print(f"🚨 Total alerts created: {alerts_created}")
    print(f"🤖 Logs with anomaly scores: {logs_with_anomaly}")
    print("\n🔗 Access the API:")
    print(f"   - API Docs: {API_URL}/docs")
    print(f"   - Get Alerts: {API_URL}/alerts (with X-Org-Id: {ORG_ID})")
    print(f"   - Get Endpoints: {API_URL}/endpoints (with X-Org-Id: {ORG_ID})")
    print(f"   - Get Compliance: {API_URL}/compliance (with X-Org-Id: {ORG_ID})")
    print("\n💡 Try these curl commands:")
    print(f'\ncurl -H "X-Org-Id: {ORG_ID}" {API_URL}/alerts')
    print(f'\ncurl -H "X-Org-Id: {ORG_ID}" {API_URL}/endpoints')
    print(f'\ncurl -H "X-Org-Id: {ORG_ID}" {API_URL}/compliance')


if __name__ == "__main__":
    main()
