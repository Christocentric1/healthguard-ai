"""Pydantic schemas for request/response models"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


# ============================================================================
# Log Events
# ============================================================================

class LogEvent(BaseModel):
    """Log event ingestion schema"""
    organisation_id: str = Field(..., description="Organisation identifier")
    host: str = Field(..., description="Hostname or endpoint identifier")
    user: str = Field(..., description="Username")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str = Field(..., description="Event type (e.g., login, process, network)")
    source: str = Field(..., description="Log source (e.g., EDR, SIEM, Syslog)")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional event details")

    class Config:
        json_schema_extra = {
            "example": {
                "organisation_id": "org_001",
                "host": "WKS-001",
                "user": "john.doe",
                "timestamp": "2025-11-19T10:30:00Z",
                "event_type": "login",
                "source": "ActiveDirectory",
                "details": {
                    "success": False,
                    "ip_address": "192.168.1.100",
                    "failure_reason": "Invalid credentials"
                }
            }
        }


class LogEventResponse(BaseModel):
    """Log event response schema"""
    success: bool
    message: str
    log_id: Optional[str] = None
    alert_created: bool = False
    alert_id: Optional[str] = None
    anomaly_score: Optional[float] = None


# ============================================================================
# Alerts
# ============================================================================

class AlertStatus(str, Enum):
    """Alert status enumeration"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Alert(BaseModel):
    """Alert schema"""
    alert_id: str
    organisation_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.OPEN
    host: Optional[str] = None
    user: Optional[str] = None
    event_type: Optional[str] = None
    anomaly_score: Optional[float] = None
    triggered_by: str = Field(..., description="rule or anomaly")
    rule_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    comments: List[str] = Field(default_factory=list)
    related_log_ids: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "alert_id": "alert_abc123",
                "organisation_id": "org_001",
                "title": "Multiple Failed Login Attempts",
                "description": "User john.doe had 7 failed login attempts from WKS-001",
                "severity": "high",
                "status": "open",
                "host": "WKS-001",
                "user": "john.doe",
                "event_type": "login",
                "triggered_by": "rule",
                "rule_name": "failed_login_threshold",
                "created_at": "2025-11-19T10:30:00Z",
                "updated_at": "2025-11-19T10:30:00Z"
            }
        }


class AlertUpdate(BaseModel):
    """Alert update schema"""
    status: Optional[AlertStatus] = None
    comment: Optional[str] = None


class AlertListResponse(BaseModel):
    """Paginated alert list response"""
    alerts: List[Alert]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Endpoints
# ============================================================================

class RiskLevel(str, Enum):
    """Endpoint risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Endpoint(BaseModel):
    """Endpoint schema with risk metrics"""
    organisation_id: str
    host: str
    ip_address: Optional[str] = None
    os_type: Optional[str] = None
    last_seen: datetime
    risk_level: RiskLevel = RiskLevel.LOW
    risk_score: float = Field(default=0.0, ge=0.0, le=100.0)
    alert_count_7d: int = 0
    alert_count_30d: int = 0
    anomaly_count: int = 0
    critical_alerts: int = 0
    compliance_issues: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "organisation_id": "org_001",
                "host": "WKS-001",
                "ip_address": "192.168.1.100",
                "os_type": "Windows 10",
                "last_seen": "2025-11-19T10:30:00Z",
                "risk_level": "medium",
                "risk_score": 65.5,
                "alert_count_7d": 3,
                "alert_count_30d": 12,
                "anomaly_count": 2,
                "critical_alerts": 1,
                "compliance_issues": 2
            }
        }


class EndpointListResponse(BaseModel):
    """Endpoint list response"""
    endpoints: List[Endpoint]
    total: int


# ============================================================================
# Compliance
# ============================================================================

class ControlStatus(str, Enum):
    """Compliance control status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    NOT_APPLICABLE = "not_applicable"


class ComplianceControl(BaseModel):
    """Compliance control schema"""
    id: str
    name: str
    status: ControlStatus
    notes: Optional[str] = None
    last_assessed: Optional[datetime] = None


class ComplianceResponse(BaseModel):
    """Compliance response schema"""
    organisation_id: str
    score: float = Field(..., ge=0.0, le=100.0, description="Compliance score 0-100")
    controls: List[ComplianceControl]
    total_controls: int
    compliant_controls: int
    non_compliant_controls: int
    last_updated: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "organisation_id": "org_001",
                "score": 78.5,
                "controls": [
                    {
                        "id": "HIPAA-164.312(a)(1)",
                        "name": "Access Control",
                        "status": "compliant",
                        "notes": "All endpoints have proper authentication"
                    },
                    {
                        "id": "HIPAA-164.312(b)",
                        "name": "Audit Controls",
                        "status": "partial",
                        "notes": "Some endpoints missing audit logging"
                    }
                ],
                "total_controls": 10,
                "compliant_controls": 7,
                "non_compliant_controls": 3,
                "last_updated": "2025-11-19T10:30:00Z"
            }
        }

# ============================================================================
# User Authentication
# ============================================================================

class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"
    ANALYST = "analyst"


class UserRegister(BaseModel):
    """User registration schema"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    full_name: str = Field(..., description="User's full name")
    organisation_id: str = Field(..., description="Organisation identifier")
    role: UserRole = Field(default=UserRole.USER, description="User role")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format"""
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Invalid email format')
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@hospital.com",
                "password": "SecurePass123!",
                "full_name": "John Doe",
                "organisation_id": "org_001",
                "role": "user"
            }
        }


class UserLogin(BaseModel):
    """User login schema"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@hospital.com",
                "password": "SecurePass123!"
            }
        }


class UserResponse(BaseModel):
    """User response schema (without password)"""
    user_id: str = Field(..., description="User identifier")
    email: str = Field(..., description="User email address")
    full_name: str = Field(..., description="User's full name")
    organisation_id: str = Field(..., description="Organisation identifier")
    role: str = Field(..., description="User role")
    created_at: datetime = Field(..., description="Account creation timestamp")
    is_active: bool = Field(default=True, description="Account active status")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_12345",
                "email": "john.doe@hospital.com",
                "full_name": "John Doe",
                "organisation_id": "org_001",
                "role": "user",
                "created_at": "2025-11-19T10:30:00Z",
                "is_active": True
            }
        }


class TokenResponse(BaseModel):
    """JWT token response schema"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="User information")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "user_id": "user_12345",
                    "email": "john.doe@hospital.com",
                    "full_name": "John Doe",
                    "organisation_id": "org_001",
                    "role": "user",
                    "created_at": "2025-11-19T10:30:00Z",
                    "is_active": True
                }
            }
        }


# ============================================================================
# DSPT (Data Security and Protection Toolkit) Compliance
# ============================================================================

class DSPTDomainStatus(str, Enum):
    """DSPT domain compliance status"""
    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"


class DSPTControlStatus(str, Enum):
    """DSPT control status"""
    PASS = "pass"
    FAIL = "fail"
    PARTIAL = "partial"


class DSPTControl(BaseModel):
    """DSPT control schema"""
    control_id: str = Field(..., description="Unique control identifier")
    control_name: str = Field(..., description="Control name")
    status: DSPTControlStatus = Field(..., description="Control status")
    evidence: Optional[str] = Field(None, description="Evidence for compliance")
    last_assessed: datetime = Field(..., description="Last assessment date")
    risk_level: RiskLevel = Field(default=RiskLevel.LOW, description="Risk level if non-compliant")


class DSPTGap(BaseModel):
    """DSPT compliance gap schema"""
    gap_description: str = Field(..., description="Description of the compliance gap")
    severity: RiskLevel = Field(..., description="Gap severity")
    affected_systems: List[str] = Field(default_factory=list, description="Affected systems/endpoints")
    remediation: str = Field(..., description="Remediation action required")
    estimated_effort: str = Field(..., description="Estimated effort to remediate")


class DSPTDomain(BaseModel):
    """DSPT domain schema"""
    domain_id: str = Field(..., description="Domain identifier")
    domain_name: str = Field(..., description="Domain name")
    score: float = Field(..., ge=0.0, le=100.0, description="Domain score (0-100)")
    status: DSPTDomainStatus = Field(..., description="Domain compliance status")
    controls: List[DSPTControl] = Field(default_factory=list, description="Controls in this domain")
    gaps: List[DSPTGap] = Field(default_factory=list, description="Identified compliance gaps")
    ai_recommendations: List[str] = Field(default_factory=list, description="AI-generated recommendations")
    endpoint_data_sources: List[str] = Field(default_factory=list, description="Required endpoint data sources")


class DSPTSummary(BaseModel):
    """DSPT assessment summary"""
    compliant_domains: int = Field(..., description="Number of compliant domains")
    partial_domains: int = Field(..., description="Number of partially compliant domains")
    non_compliant_domains: int = Field(..., description="Number of non-compliant domains")
    high_risk_gaps: int = Field(..., description="Number of high-risk gaps")
    critical_gaps: int = Field(..., description="Number of critical gaps")


class DSPTAssessment(BaseModel):
    """Complete DSPT assessment schema"""
    organisation_id: str = Field(..., description="Organisation identifier")
    assessment_date: datetime = Field(..., description="Assessment date")
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall DSPT score")
    status: DSPTDomainStatus = Field(..., description="Overall compliance status")
    domains: List[DSPTDomain] = Field(..., description="Domain assessments")
    summary: DSPTSummary = Field(..., description="Assessment summary")
    next_assessment_due: datetime = Field(..., description="Next assessment due date")
    assessor: str = Field(..., description="Assessor name/system")

    class Config:
        json_schema_extra = {
            "example": {
                "organisation_id": "org_001",
                "assessment_date": "2025-11-24T00:00:00Z",
                "overall_score": 72.5,
                "status": "partial",
                "domains": [
                    {
                        "domain_id": "personal_confidential_data",
                        "domain_name": "Personal Confidential Data",
                        "score": 85.0,
                        "status": "compliant",
                        "controls": [],
                        "gaps": [],
                        "ai_recommendations": [],
                        "endpoint_data_sources": ["file_access_logs", "dlp_events"]
                    }
                ],
                "summary": {
                    "compliant_domains": 7,
                    "partial_domains": 3,
                    "non_compliant_domains": 2,
                    "high_risk_gaps": 3,
                    "critical_gaps": 1
                },
                "next_assessment_due": "2026-11-24T00:00:00Z",
                "assessor": "AI Assessment Engine"
            }
        }


class DSPTEvidenceRequirement(BaseModel):
    """DSPT evidence requirement schema"""
    domain_id: str = Field(..., description="Domain requiring evidence")
    control_id: str = Field(..., description="Control requiring evidence")
    evidence_type: str = Field(..., description="Type of evidence needed")
    description: str = Field(..., description="Evidence description")
    collection_method: str = Field(..., description="How to collect this evidence")
    frequency: str = Field(..., description="Collection frequency")


class DSPTEndpointGap(BaseModel):
    """DSPT endpoint-specific gap schema"""
    host: str = Field(..., description="Affected endpoint")
    domain: str = Field(..., description="DSPT domain")
    gap_description: str = Field(..., description="Gap description")
    severity: RiskLevel = Field(..., description="Gap severity")
    remediation: str = Field(..., description="Remediation action")
    status: str = Field(..., description="Remediation status")


# ============================================================================
# MITRE ATT&CK Framework
# ============================================================================

class MITRETactic(str, Enum):
    """MITRE ATT&CK tactics"""
    INITIAL_ACCESS = "initial_access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DEFENSE_EVASION = "defense_evasion"
    CREDENTIAL_ACCESS = "credential_access"
    DISCOVERY = "discovery"
    LATERAL_MOVEMENT = "lateral_movement"
    COLLECTION = "collection"
    EXFILTRATION = "exfiltration"
    IMPACT = "impact"


class MITRETechniqueSeverity(str, Enum):
    """MITRE technique severity"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MITREIndicator(BaseModel):
    """MITRE ATT&CK indicator schema"""
    indicator_type: str = Field(..., description="Indicator type (process, file, network, registry)")
    indicator_value: str = Field(..., description="Indicator value")
    timestamp: datetime = Field(..., description="When indicator was observed")


class MITREEvidenceLog(BaseModel):
    """Evidence log for MITRE detection"""
    log_id: str = Field(..., description="Log event ID")
    log_source: str = Field(..., description="Log source system")
    relevant_fields: Dict[str, Any] = Field(..., description="Relevant log fields")


class MITREMitigation(BaseModel):
    """MITRE technique mitigation"""
    mitigation_id: str = Field(..., description="Mitigation identifier")
    description: str = Field(..., description="Mitigation description")
    automated: bool = Field(..., description="Can be automated")
    effectiveness: float = Field(..., ge=0.0, le=100.0, description="Mitigation effectiveness (0-100)")


class MITRETechniqueDetailed(BaseModel):
    """Detailed MITRE ATT&CK technique schema"""
    technique_id: str = Field(..., description="MITRE technique ID (e.g., T1003)")
    technique_name: str = Field(..., description="Technique name")
    tactic: MITRETactic = Field(..., description="Associated tactic")
    sub_technique: Optional[str] = Field(None, description="Sub-technique ID if applicable")
    confidence_score: float = Field(..., ge=0.0, le=100.0, description="Detection confidence (0-100)")
    severity: MITRETechniqueSeverity = Field(..., description="Technique severity")
    indicators: List[MITREIndicator] = Field(default_factory=list, description="Observed indicators")
    evidence_logs: List[MITREEvidenceLog] = Field(default_factory=list, description="Supporting evidence")
    ai_explanation: str = Field(..., description="AI-generated explanation")
    recommended_mitigations: List[str] = Field(default_factory=list, description="Recommended mitigations")


class MITREThreatAssessment(BaseModel):
    """MITRE threat assessment schema"""
    likelihood_score: float = Field(..., ge=0.0, le=100.0, description="Threat likelihood (0-100)")
    risk_level: RiskLevel = Field(..., description="Overall risk level")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Assessment confidence (0-1)")
    attack_chain_detected: bool = Field(..., description="Whether an attack chain was detected")
    temporal_correlation: bool = Field(..., description="Whether techniques are temporally correlated")


class MITRETimelineEvent(BaseModel):
    """MITRE attack timeline event"""
    timestamp: datetime = Field(..., description="Event timestamp")
    technique: str = Field(..., description="Technique ID")
    action: str = Field(..., description="Action description")


class MITREAISummary(BaseModel):
    """MITRE AI-generated summary"""
    executive_summary: str = Field(..., description="Executive summary of the threat")
    detailed_analysis: str = Field(..., description="Detailed analysis")
    attacker_profile: str = Field(..., description="Inferred attacker profile")
    timeline: List[MITRETimelineEvent] = Field(default_factory=list, description="Attack timeline")


class MITREIOC(BaseModel):
    """MITRE Indicators of Compromise"""
    ip_addresses: List[str] = Field(default_factory=list, description="Malicious IP addresses")
    domains: List[str] = Field(default_factory=list, description="Malicious domains")
    file_hashes: List[str] = Field(default_factory=list, description="Malicious file hashes")
    file_paths: List[str] = Field(default_factory=list, description="Malicious file paths")
    registry_keys: List[str] = Field(default_factory=list, description="Malicious registry keys")
    processes: List[str] = Field(default_factory=list, description="Malicious processes")


class MITREResponseRecommendation(BaseModel):
    """MITRE response recommendation schema"""
    priority: int = Field(..., ge=1, le=10, description="Priority (1=highest)")
    action: str = Field(..., description="Recommended action")
    automated: bool = Field(..., description="Can be automated")
    automation_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in automation")
    status: str = Field(default="pending", description="Action status (pending, in_progress, completed)")


class MITREDetectionStatus(str, Enum):
    """MITRE detection status"""
    ACTIVE = "active"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"


class MITREDetection(BaseModel):
    """Complete MITRE ATT&CK detection schema"""
    detection_id: str = Field(..., description="Unique detection ID")
    organisation_id: str = Field(..., description="Organisation identifier")
    timestamp: datetime = Field(..., description="Detection timestamp")
    host: str = Field(..., description="Affected host")
    user: str = Field(..., description="Affected user")
    techniques_detected: List[MITRETechniqueDetailed] = Field(..., description="Detected techniques")
    threat_assessment: MITREThreatAssessment = Field(..., description="Threat assessment")
    ai_summary: MITREAISummary = Field(..., description="AI-generated summary")
    iocs: MITREIOC = Field(..., description="Indicators of Compromise")
    response_recommendations: List[MITREResponseRecommendation] = Field(..., description="Response recommendations")
    status: MITREDetectionStatus = Field(default=MITREDetectionStatus.ACTIVE, description="Detection status")

    class Config:
        json_schema_extra = {
            "example": {
                "detection_id": "det_12345",
                "organisation_id": "org_001",
                "timestamp": "2025-11-24T14:30:00Z",
                "host": "WKS-001",
                "user": "john.doe",
                "techniques_detected": [
                    {
                        "technique_id": "T1003",
                        "technique_name": "OS Credential Dumping",
                        "tactic": "credential_access",
                        "sub_technique": "T1003.001",
                        "confidence_score": 95.0,
                        "severity": "critical",
                        "indicators": [],
                        "evidence_logs": [],
                        "ai_explanation": "Credential dumping detected",
                        "recommended_mitigations": ["Isolate system", "Reset passwords"]
                    }
                ],
                "threat_assessment": {
                    "likelihood_score": 90.0,
                    "risk_level": "critical",
                    "confidence": 0.95,
                    "attack_chain_detected": True,
                    "temporal_correlation": True
                },
                "ai_summary": {
                    "executive_summary": "Critical threat detected",
                    "detailed_analysis": "Attacker attempting credential theft",
                    "attacker_profile": "Advanced persistent threat",
                    "timeline": []
                },
                "iocs": {
                    "ip_addresses": [],
                    "domains": [],
                    "file_hashes": [],
                    "file_paths": [],
                    "registry_keys": [],
                    "processes": ["mimikatz.exe"]
                },
                "response_recommendations": [],
                "status": "active"
            }
        }


class MITRETechniqueMapping(BaseModel):
    """MITRE ATT&CK technique mapping (for reference)"""
    technique_id: str = Field(..., description="Technique ID")
    technique_name: str = Field(..., description="Technique name")
    tactic: MITRETactic = Field(..., description="Primary tactic")
    sub_techniques: List[Dict[str, str]] = Field(default_factory=list, description="Sub-techniques")
    description: str = Field(..., description="Technique description")
    data_sources: List[str] = Field(default_factory=list, description="Required data sources")
    platforms: List[str] = Field(default_factory=list, description="Applicable platforms")
    severity: MITRETechniqueSeverity = Field(..., description="Base severity")
    likelihood_base_score: float = Field(..., ge=0.0, le=100.0, description="Base likelihood score")
    ai_explanation: str = Field(..., description="Why this technique matters")
    mitigations: List[MITREMitigation] = Field(default_factory=list, description="Mitigation strategies")


class MITREHeatmapCell(BaseModel):
    """MITRE ATT&CK heatmap cell data"""
    technique_id: str = Field(..., description="Technique ID")
    technique_name: str = Field(..., description="Technique name")
    tactic: MITRETactic = Field(..., description="Tactic")
    detection_count: int = Field(..., description="Number of detections")
    severity: MITRETechniqueSeverity = Field(..., description="Highest severity detected")
    last_detected: Optional[datetime] = Field(None, description="Last detection timestamp")


class MITREHeatmapResponse(BaseModel):
    """MITRE ATT&CK heatmap response"""
    organisation_id: str = Field(..., description="Organisation identifier")
    time_range: str = Field(..., description="Time range for heatmap (e.g., '7d', '30d')")
    cells: List[MITREHeatmapCell] = Field(..., description="Heatmap cells")
    total_detections: int = Field(..., description="Total number of detections")
    unique_techniques: int = Field(..., description="Number of unique techniques detected")
    generated_at: datetime = Field(..., description="Heatmap generation timestamp")


# ============================================================================
# Telemetry (Endpoint Agent Data)
# ============================================================================

class SecurityEvent(BaseModel):
    """Security event from endpoint"""
    event_id: int
    time_created: str
    level: str
    message: str
    source: str
    user: str


class ProcessInfo(BaseModel):
    """Process information from endpoint"""
    name: str
    pid: int
    cpu: float
    memory_mb: float
    threads: int
    start_time: str
    path: str


class SystemInfo(BaseModel):
    """System information from endpoint"""
    hostname: str
    organisation_id: str
    os_name: str
    os_version: str
    os_architecture: str
    manufacturer: str
    model: str
    bios_version: str
    cpu_name: str
    cpu_cores: int
    total_memory_gb: float
    domain: str
    uptime_hours: float
    last_boot: str
    agent_version: str
    collected_at: str


class TelemetryMetrics(BaseModel):
    """Telemetry collection metrics"""
    total_events: int
    total_processes: int
    collection_duration_ms: int


class TelemetryPayload(BaseModel):
    """Complete telemetry payload from endpoint agent"""
    agent_id: str = Field(..., description="Agent identifier")
    hostname: str = Field(..., description="Endpoint hostname")
    organisation_id: str = Field(..., description="Organisation identifier")
    collected_at: str = Field(..., description="Collection timestamp")
    system_info: SystemInfo = Field(..., description="System information")
    security_events: List[SecurityEvent] = Field(default_factory=list, description="Security events")
    process_info: List[ProcessInfo] = Field(default_factory=list, description="Process information")
    metrics: TelemetryMetrics = Field(..., description="Collection metrics")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "WORKSTATION-01-20251124",
                "hostname": "WORKSTATION-01",
                "organisation_id": "org_healthcare_001",
                "collected_at": "2025-11-24 22:00:00",
                "system_info": {
                    "hostname": "WORKSTATION-01",
                    "organisation_id": "org_healthcare_001",
                    "os_name": "Microsoft Windows 10 Pro",
                    "os_version": "10.0.19045",
                    "os_architecture": "64-bit",
                    "manufacturer": "Dell Inc.",
                    "model": "OptiPlex 7090",
                    "bios_version": "1.2.3",
                    "cpu_name": "Intel Core i7-10700",
                    "cpu_cores": 8,
                    "total_memory_gb": 16.0,
                    "domain": "hospital.local",
                    "uptime_hours": 72.5,
                    "last_boot": "2025-11-21 10:00:00",
                    "agent_version": "2.0",
                    "collected_at": "2025-11-24 22:00:00"
                },
                "security_events": [],
                "process_info": [],
                "metrics": {
                    "total_events": 0,
                    "total_processes": 20,
                    "collection_duration_ms": 0
                }
            }
        }


class TelemetryResponse(BaseModel):
    """Response for telemetry ingestion"""
    success: bool = Field(..., description="Ingestion success status")
    message: str = Field(..., description="Response message")
    telemetry_id: Optional[str] = Field(None, description="Generated telemetry ID")
    endpoint_updated: bool = Field(False, description="Endpoint record updated")
    alerts_created: int = Field(0, description="Number of alerts created")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Telemetry data ingested successfully",
                "telemetry_id": "tel_abc123",
                "endpoint_updated": True,
                "alerts_created": 0
            }
        }
