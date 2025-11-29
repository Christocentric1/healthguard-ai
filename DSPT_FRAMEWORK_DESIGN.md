# DSPT Compliance Framework Design
## Data Security and Protection Toolkit (UK NHS)

This document outlines the design for DSPT compliance monitoring in Cyber HealthGuard AI.

---

## Overview

The Data Security and Protection Toolkit (DSPT) is an online self-assessment tool that enables organisations to measure their performance against the National Data Guardian's 10 data security standards.

**Implementation Strategy:**
- 10 core domains mapped to technical controls
- Automated assessment using endpoint telemetry
- Evidence collection through log analysis
- Continuous monitoring and scoring
- AI-powered gap analysis and recommendations

---

## DSPT Domains

### 1. Personal Confidential Data (PCD)
**Description:** Ensures staff understand their responsibilities for handling personal confidential data, including training and awareness.

**Key Controls:**
- Staff training completion tracking
- Data handling policy acknowledgment
- PCD access logging and monitoring
- Regular refresher training compliance

**Endpoint/Org Data Required:**
- User training completion records
- File access logs for PCD storage locations
- User authentication logs
- Data handling policy acceptance timestamps

**Scoring Method (0-100):**
```python
score = (
    (trained_users / total_users) * 40 +
    (users_with_policy_acceptance / total_users) * 30 +
    (compliant_access_patterns / total_access_events) * 30
)
```

**Risk Explanation:**
"Without proper staff training on PCD handling, your organisation faces increased risk of data breaches, regulatory non-compliance, and potential harm to patient confidentiality. Untrained staff may inadvertently expose sensitive health information."

**AI Recommendations:**
- Implement mandatory annual training with 95% completion target
- Deploy automated email reminders for training due dates
- Enable data classification labels on all PCD files
- Implement role-based access controls for PCD systems
- Monitor and audit all PCD access with automated alerts

---

### 2. Staff Responsibilities
**Description:** Staff understand their responsibilities for data security through clear policies, acceptable use agreements, and consequences for non-compliance.

**Key Controls:**
- Acceptable Use Policy (AUP) acceptance tracking
- Security awareness training completion
- Incident reporting acknowledgment
- Clear desk/clear screen policy compliance

**Endpoint/Org Data Required:**
- AUP acceptance logs
- Security training completion records
- Workstation lock screen compliance (idle timeout settings)
- USB/removable media usage logs

**Scoring Method (0-100):**
```python
score = (
    (staff_with_aup / total_staff) * 35 +
    (staff_training_current / total_staff) * 35 +
    (workstations_with_timeout / total_workstations) * 30
)
```

**Risk Explanation:**
"Staff who don't understand their security responsibilities can become the weakest link in your security posture. This increases risk of insider threats, social engineering attacks, and accidental data breaches."

**AI Recommendations:**
- Require annual AUP re-acceptance with version tracking
- Implement automated screen lock after 5 minutes of inactivity
- Deploy USB device whitelisting on all endpoints
- Run quarterly phishing simulation campaigns
- Create security champions program for each department

---

### 3. Training
**Description:** All staff complete appropriate training to ensure they understand their data security responsibilities.

**Key Controls:**
- Initial security induction completion
- Annual refresher training compliance
- Role-specific training (e.g., developers, clinicians)
- Training effectiveness assessment

**Endpoint/Org Data Required:**
- Learning Management System (LMS) completion records
- Training module timestamps and scores
- Role assignments per user
- Post-training assessment results

**Scoring Method (0-100):**
```python
base_score = (completed_training / required_training) * 100
recency_penalty = max(0, (days_since_training - 365) / 365) * 20
score = max(0, base_score - recency_penalty)
```

**Risk Explanation:**
"Incomplete or outdated security training leaves staff vulnerable to social engineering, phishing, and other attack vectors. Regular training is essential to maintain security awareness and compliance with NHS standards."

**AI Recommendations:**
- Implement automated training reminders 30 days before expiration
- Create bite-sized monthly security awareness newsletters
- Deploy interactive phishing simulations with immediate feedback
- Track and report training completion to senior management
- Provide additional training for repeat security policy violators

---

### 4. Managing Data Access
**Description:** Access to personal confidential data is controlled and monitored through access controls, user accounts, and auditing.

**Key Controls:**
- Least privilege access model implementation
- Regular access reviews and recertification
- Privileged account monitoring
- Offboarding process automation

**Endpoint/Org Data Required:**
- Active Directory/IAM user accounts and permissions
- Privileged account usage logs
- Access review completion records
- Dormant account detection (90+ days inactive)
- User provisioning/deprovisioning audit trails

**Scoring Method (0-100):**
```python
access_control_score = (
    (accounts_with_mfa / total_accounts) * 25 +
    (accounts_reviewed_12m / total_accounts) * 25 +
    (no_dormant_accounts / total_accounts) * 25 +
    (privileged_accounts_monitored / total_privileged) * 25
)
```

**Risk Explanation:**
"Poor access management can lead to unauthorized data access, privilege escalation, and insider threats. Dormant accounts and excessive permissions are common attack vectors for both external and internal threats."

**AI Recommendations:**
- Implement mandatory MFA for all accounts accessing PCD
- Automate quarterly access reviews with manager approval workflows
- Deploy automated dormant account suspension after 90 days
- Implement privileged access management (PAM) solution
- Enable session recording for all privileged account activities

---

### 5. Process Reviews
**Description:** Regular reviews of processes and systems to ensure continued compliance and identify improvement opportunities.

**Key Controls:**
- Quarterly process review completion
- Annual DSPT self-assessment
- Management review of security incidents
- Continuous improvement action tracking

**Endpoint/Org Data Required:**
- Process review meeting minutes and attendance
- DSPT assessment submission history
- Security incident review records
- Action item tracking database

**Scoring Method (0-100):**
```python
score = (
    (quarterly_reviews_completed / 4) * 30 +
    (dspt_assessment_current ? 40 : 0) +
    (incidents_reviewed / total_incidents) * 30
)
```

**Risk Explanation:**
"Without regular process reviews, security controls can become outdated, misaligned with business needs, or ineffective. This creates compliance gaps and increases vulnerability to evolving threats."

**AI Recommendations:**
- Schedule automatic quarterly review meetings with calendar blocks
- Create process review templates with key questions
- Implement action tracking dashboard with due dates
- Assign process owners with clear responsibilities
- Conduct annual third-party DSPT assessment for validation

---

### 6. Responding to Incidents
**Description:** Organisation has clear incident response procedures, staff know how to report incidents, and all incidents are managed appropriately.

**Key Controls:**
- Incident response plan documented and tested
- Incident reporting mechanisms accessible to all staff
- Mean time to detect (MTTD) and respond (MTTR) tracking
- Post-incident reviews and lessons learned

**Endpoint/Org Data Required:**
- Security incident tickets and timestamps
- Incident response playbook execution logs
- Staff incident reporting metrics
- Tabletop exercise records

**Scoring Method (0-100):**
```python
response_time_score = min(100, (24 / avg_response_hours) * 100)
detection_score = (incidents_detected / total_attacks) * 100
score = (
    (incident_plan_tested ? 30 : 0) +
    (response_time_score * 0.4) +
    (detection_score * 0.3)
)
```

**Risk Explanation:**
"Slow or ineffective incident response can turn minor security events into major breaches. Without clear procedures and tested plans, staff may fail to escalate critical incidents, leading to regulatory fines and reputational damage."

**AI Recommendations:**
- Conduct bi-annual tabletop exercises simulating data breaches
- Implement automated incident detection with SIEM integration
- Create incident response runbooks with step-by-step procedures
- Establish 24/7 security operations coverage
- Deploy automated containment for critical threat types
- Maintain incident response retainer with external forensics firm

---

### 7. Continuity Planning
**Description:** Organisation has business continuity and disaster recovery plans that include data security and are regularly tested.

**Key Controls:**
- Business continuity plan (BCP) documented
- Regular backup verification and testing
- Recovery time objective (RTO) and recovery point objective (RPO) defined
- Annual DR testing and validation

**Endpoint/Org Data Required:**
- Backup success/failure logs
- Backup frequency and retention policies
- DR test execution records and results
- System criticality classifications

**Scoring Method (0-100):**
```python
backup_health = (successful_backups / total_backups) * 100
test_currency = max(0, 100 - ((days_since_dr_test - 365) / 365 * 50))
score = (
    (backup_health * 0.5) +
    (test_currency * 0.3) +
    (bcp_documented ? 20 : 0)
)
```

**Risk Explanation:**
"Without tested continuity plans and reliable backups, a ransomware attack or system failure could result in permanent data loss, extended downtime, and inability to provide patient care. The NHS has seen numerous Trusts crippled by inadequate DR planning."

**AI Recommendations:**
- Implement immutable backups with 3-2-1 strategy
- Test restore procedures monthly on non-critical systems
- Store offline backup copies in geographically separate location
- Document and test failover procedures for critical systems
- Implement automated backup monitoring with alerting
- Maintain system inventory with RTO/RPO for each service

---

### 8. Unsupported Systems
**Description:** Organisation identifies and manages risks associated with unsupported or end-of-life systems.

**Key Controls:**
- Asset inventory of all systems with lifecycle tracking
- Unsupported system risk register
- Compensating controls for EOL systems
- Migration planning and timelines

**Endpoint/Org Data Required:**
- Software inventory with version information
- Operating system versions and patch levels
- Vendor support status database
- Network segmentation for unsupported systems

**Scoring Method (0-100):**
```python
unsupported_count = count(systems where support_end_date < today)
total_risk = sum(unsupported_system.risk_score)
compensating_controls = count(unsupported with mitigations)

base_penalty = min(50, unsupported_count * 5)
mitigation_credit = (compensating_controls / unsupported_count) * 30 if unsupported_count > 0 else 30

score = max(0, 100 - base_penalty + mitigation_credit)
```

**Risk Explanation:**
"Unsupported systems no longer receive security patches, making them prime targets for attackers. The WannaCry ransomware attack that crippled NHS Trusts in 2017 exploited vulnerabilities in unsupported Windows XP systems."

**AI Recommendations:**
- Create migration roadmap for all Windows 7/Server 2008 systems
- Implement network micro-segmentation for unavoidable EOL systems
- Deploy virtual patching with IPS/IDS for unpatched vulnerabilities
- Conduct quarterly vulnerability scans focusing on EOL systems
- Establish executive-level steering committee for legacy system modernization
- Budget and plan for lifecycle replacement before support expires

---

### 9. IT Protection
**Description:** Technical security controls protect systems and data from cyber threats.

**Key Controls:**
- Antivirus/anti-malware on all endpoints (definition currency)
- Firewall configuration and rule reviews
- Intrusion detection/prevention systems (IDS/IPS)
- Email security (anti-phishing, anti-spam, DMARC/SPF/DKIM)
- Web filtering and content inspection

**Endpoint/Org Data Required:**
- Endpoint protection agent status and version
- Malware detection and quarantine logs
- Firewall rule audit logs
- Email security metrics (blocked threats, phishing attempts)
- Web proxy logs and blocked categories

**Scoring Method (0-100):**
```python
av_coverage = (endpoints_with_current_av / total_endpoints) * 100
detection_rate = (threats_blocked / threats_detected) * 100
email_protection = (phishing_blocked / phishing_attempted) * 100

score = (
    (av_coverage * 0.35) +
    (detection_rate * 0.35) +
    (email_protection * 0.30)
)
```

**Risk Explanation:**
"Without layered technical controls, your organisation is vulnerable to malware, ransomware, phishing, and network intrusions. These threats can result in data breaches, system downtime, and ransomware demands."

**AI Recommendations:**
- Deploy next-generation antivirus with behavioural detection
- Implement email link sandboxing for all external URLs
- Enable DMARC policy enforcement to prevent email spoofing
- Deploy web application firewall (WAF) for internet-facing services
- Implement DNS filtering to block malicious domains
- Enable automatic malware quarantine and alert escalation

---

### 10. Accountable Suppliers
**Description:** Organisation ensures that suppliers handling data meet appropriate security standards through contracts and monitoring.

**Key Controls:**
- Supplier security assessment questionnaires
- Data processing agreements (DPAs) in place
- Regular supplier security audits
- Supplier incident notification requirements

**Endpoint/Org Data Required:**
- Supplier contract database with security clauses
- Supplier risk assessment records
- Supplier audit reports and findings
- Supplier access logs to organisation systems

**Scoring Method (0-100):**
```python
suppliers_with_dpa = count(suppliers with signed DPA)
suppliers_assessed = count(suppliers with security assessment < 12 months)
high_risk_suppliers_audited = count(high_risk suppliers with audit < 24 months)

score = (
    (suppliers_with_dpa / total_suppliers) * 40 +
    (suppliers_assessed / total_suppliers) * 35 +
    (high_risk_suppliers_audited / high_risk_suppliers) * 25
)
```

**Risk Explanation:**
"Third-party suppliers represent a significant supply chain risk. Many major breaches occur through suppliers with inadequate security. NHS organisations must ensure suppliers meet DSPT standards or equivalent."

**AI Recommendations:**
- Require suppliers to complete DSPT or equivalent certification
- Include right-to-audit clauses in all supplier contracts
- Implement supplier risk tiering (low/medium/high/critical)
- Conduct annual security reviews for high-risk suppliers
- Require suppliers to notify within 24 hours of security incidents
- Maintain supplier register with security posture dashboard

---

### 11. Secure Configuration
**Description:** Systems are securely configured according to industry best practices (CIS benchmarks, vendor hardening guides).

**Key Controls:**
- CIS benchmark compliance for OS and applications
- Secure baseline configurations documented
- Configuration drift detection and remediation
- Vulnerability management program

**Endpoint/Org Data Required:**
- Configuration compliance scan results
- CIS benchmark scores per system
- Vulnerability scan reports
- Patch deployment success rates
- Security baseline documentation

**Scoring Method (0-100):**
```python
cis_compliance = avg(system.cis_score for all systems)
patching_rate = (systems_patched_30d / total_systems) * 100
vuln_remediation = (critical_vulns_remediated / critical_vulns_found) * 100

score = (
    (cis_compliance * 0.35) +
    (patching_rate * 0.35) +
    (vuln_remediation * 0.30)
)
```

**Risk Explanation:**
"Misconfigured systems with default passwords, unnecessary services, and weak encryption are easily exploited by attackers. Secure configuration is a foundational security control that prevents many common attack vectors."

**AI Recommendations:**
- Implement automated configuration compliance scanning weekly
- Deploy infrastructure-as-code for consistent server builds
- Disable all unnecessary services and protocols
- Change all default passwords on devices and applications
- Enable audit logging on all critical systems
- Implement vulnerability scanning with automatic prioritization
- Establish SLA for critical vulnerability patching (7 days)

---

### 12. Network Security
**Description:** Network architecture is designed for security with segmentation, monitoring, and access controls.

**Key Controls:**
- Network segmentation (DMZ, internal zones, PCD zones)
- VPN for remote access with MFA
- Wireless network security (WPA3, certificate-based auth)
- Network access control (NAC)

**Endpoint/Org Data Required:**
- Network topology and VLAN configuration
- VPN connection logs and MFA status
- Wireless access point configurations
- NAC enforcement logs
- Network traffic analysis and anomaly detection

**Scoring Method (0-100):**
```python
segmentation_score = (vlans_properly_segmented / total_vlans) * 100
vpn_security = (vpn_users_with_mfa / total_vpn_users) * 100
wireless_security = (wpa3_access_points / total_access_points) * 100

score = (
    (segmentation_score * 0.40) +
    (vpn_security * 0.35) +
    (wireless_security * 0.25)
)
```

**Risk Explanation:**
"Flat network architectures allow attackers to move laterally once they gain initial access. Without segmentation, a single compromised workstation can provide access to critical servers and patient data."

**AI Recommendations:**
- Implement zero-trust network architecture principles
- Segment PCD systems into separate VLAN with strict ACLs
- Require MFA for all VPN and remote access
- Deploy network access control (NAC) for device authentication
- Implement 802.1X port-based authentication on wired networks
- Enable wireless intrusion detection system (WIDS)
- Monitor east-west traffic between network segments

---

## Endpoint Telemetry Mapping

### Data Collection Requirements

| DSPT Domain | Endpoint Data Source | Collection Method | Frequency |
|-------------|---------------------|-------------------|-----------|
| Personal Confidential Data | File access logs, DLP events | Agent-based monitoring | Real-time |
| Staff Responsibilities | Workstation lock events, USB usage | Windows Event Logs | Real-time |
| Training | LMS API, training completion records | API integration | Daily sync |
| Managing Data Access | Active Directory, IAM logs | LDAP queries, log forwarding | Hourly |
| Process Reviews | Ticketing system, document management | API integration | Daily sync |
| Responding to Incidents | SIEM, incident tickets | API integration | Real-time |
| Continuity Planning | Backup software logs, DR test records | Agent monitoring, API | Daily |
| Unsupported Systems | Software inventory, OS version | Agent-based scanning | Weekly |
| IT Protection | AV status, firewall logs, email gateway | Agent + log forwarding | Real-time |
| Accountable Suppliers | Contract management system | API integration | Weekly |
| Secure Configuration | CIS compliance scans, vulnerability scans | Agent-based scanning | Weekly |
| Network Security | Network flow logs, VPN logs, NAC logs | Log forwarding | Real-time |

---

## JSON Schema

```json
{
  "dspt_assessment": {
    "organisation_id": "string",
    "assessment_date": "ISO8601 datetime",
    "overall_score": "number (0-100)",
    "status": "compliant|partial|non_compliant",
    "domains": [
      {
        "domain_id": "string",
        "domain_name": "string",
        "score": "number (0-100)",
        "status": "compliant|partial|non_compliant",
        "controls": [
          {
            "control_id": "string",
            "control_name": "string",
            "status": "pass|fail|partial",
            "evidence": "string",
            "last_assessed": "ISO8601 datetime",
            "risk_level": "low|medium|high|critical"
          }
        ],
        "gaps": [
          {
            "gap_description": "string",
            "severity": "low|medium|high|critical",
            "affected_systems": ["string"],
            "remediation": "string",
            "estimated_effort": "string"
          }
        ],
        "ai_recommendations": ["string"],
        "endpoint_data_sources": ["string"]
      }
    ],
    "summary": {
      "compliant_domains": "number",
      "partial_domains": "number",
      "non_compliant_domains": "number",
      "high_risk_gaps": "number",
      "critical_gaps": "number"
    },
    "next_assessment_due": "ISO8601 datetime",
    "assessor": "string"
  }
}
```

---

## Scoring Calculation Method

### Overall DSPT Score
```python
def calculate_overall_dspt_score(domains):
    """
    Calculate overall DSPT score from domain scores
    Uses weighted average with critical domains weighted higher
    """
    weights = {
        'personal_confidential_data': 1.2,
        'managing_data_access': 1.2,
        'it_protection': 1.1,
        'network_security': 1.1,
        'responding_to_incidents': 1.0,
        'continuity_planning': 1.0,
        'staff_responsibilities': 0.9,
        'training': 0.9,
        'process_reviews': 0.8,
        'unsupported_systems': 1.0,
        'accountable_suppliers': 0.9,
        'secure_configuration': 1.0
    }

    weighted_sum = sum(
        domain['score'] * weights.get(domain['domain_id'], 1.0)
        for domain in domains
    )

    total_weight = sum(weights.values())

    return weighted_sum / total_weight
```

### Status Determination
```python
def determine_compliance_status(score):
    """Determine compliance status from score"""
    if score >= 80:
        return 'compliant'
    elif score >= 50:
        return 'partial'
    else:
        return 'non_compliant'
```

---

## AI-Powered Gap Analysis

The system will use AI to analyze compliance gaps and provide contextual recommendations:

1. **Pattern Recognition**: Identify common failure patterns across endpoints
2. **Risk Correlation**: Link compliance gaps to actual security incidents
3. **Prioritization**: Rank remediation actions by risk and effort
4. **Automation Suggestions**: Recommend technical controls that can be automated
5. **Benchmark Comparison**: Compare against industry peers (anonymized)

---

## Integration with Existing System

### Database Collections
- `dspt_assessments` - Historical assessment records
- `dspt_evidence` - Supporting evidence and artifacts
- `dspt_gaps` - Identified compliance gaps
- `dspt_remediation_actions` - Action tracking

### API Endpoints
- `GET /api/compliance/dspt` - Get current DSPT assessment
- `GET /api/compliance/dspt/domains/{domain_id}` - Get domain details
- `GET /api/compliance/dspt/gaps` - Get all compliance gaps
- `POST /api/compliance/dspt/assess` - Trigger new assessment
- `GET /api/compliance/dspt/evidence` - Get evidence requirements
- `GET /api/compliance/dspt/recommendations` - Get AI recommendations

### UI Integration
- New "DSPT Compliance" page in navigation
- Dashboard widget showing overall DSPT score
- Alert integration for critical compliance gaps
- Evidence upload functionality
- Remediation action tracking

---

This framework provides comprehensive DSPT compliance monitoring integrated with endpoint telemetry and AI-powered recommendations.
