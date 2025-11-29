export interface Alert {
  id: string;
  timestamp: string;
  organisation_id: string;
  host: string;
  user: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  description: string;
  ai_risk_score: number;
  recommended_action: string;
  status: 'new' | 'investigating' | 'resolved' | 'false_positive';
  source: string;
}

export interface Endpoint {
  id: string;
  hostname: string;
  ip: string;
  os: string;
  last_seen: string;
  risk_level: 'critical' | 'high' | 'medium' | 'low';
  status: 'online' | 'offline' | 'warning';
}

export interface ComplianceControl {
  id: string;
  control_id: string;
  name: string;
  description: string;
  status: 'passed' | 'failed' | 'warning';
  remediation: string;
  framework: 'hipaa' | 'gdpr' | 'cyber_essentials' | 'cis' | 'iso27001';
}

export interface AIInsight {
  id: string;
  insight: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  affected_count: number;
  correlation_type: string;
}

export interface EndpointHealth {
  total_endpoints: number;
  online: number;
  offline: number;
  at_risk: number;
  outdated_patches: number;
  high_risk_count: number;
}

export interface EndpointDetail {
  hostname: string;
  risk_level: 'critical' | 'high' | 'medium' | 'low';
  issue: string;
  last_seen: string;
}

export interface FileIntegrityEvent {
  id: string;
  timestamp: string;
  file_path: string;
  action: 'created' | 'modified' | 'deleted' | 'accessed';
  user: string;
  hash_before?: string;
  hash_after?: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'flagged' | 'reviewed' | 'approved';
}

export const mockAlerts: Alert[] = [
  {
    id: 'ALT-001',
    timestamp: new Date().toISOString(),
    organisation_id: 'org-123',
    host: 'DESKTOP-MED-01',
    user: 'dr.smith@clinic.nhs',
    severity: 'critical',
    category: 'Malware Detection',
    description: 'Potential ransomware activity detected on endpoint',
    ai_risk_score: 95,
    recommended_action: 'Isolate endpoint immediately and run full system scan',
    status: 'new',
    source: 'EDR System'
  },
  {
    id: 'ALT-002',
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    organisation_id: 'org-123',
    host: 'SERVER-EMR-01',
    user: 'system',
    severity: 'high',
    category: 'Unauthorized Access',
    description: 'Multiple failed login attempts from external IP',
    ai_risk_score: 82,
    recommended_action: 'Review firewall rules and enable MFA for all users',
    status: 'investigating',
    source: 'SIEM'
  },
  {
    id: 'ALT-003',
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    organisation_id: 'org-123',
    host: 'LAPTOP-ADMIN-03',
    user: 'admin@clinic.nhs',
    severity: 'medium',
    category: 'Policy Violation',
    description: 'USB device connected without authorization',
    ai_risk_score: 58,
    recommended_action: 'Enforce USB device control policy',
    status: 'new',
    source: 'DLP System'
  },
  {
    id: 'ALT-004',
    timestamp: new Date(Date.now() - 10800000).toISOString(),
    organisation_id: 'org-123',
    host: 'WORKSTATION-05',
    user: 'nurse.jones@clinic.nhs',
    severity: 'low',
    category: 'Software Update',
    description: 'Critical security patch available for installed software',
    ai_risk_score: 35,
    recommended_action: 'Schedule maintenance window for updates',
    status: 'resolved',
    source: 'Patch Management'
  }
];

export const mockEndpoints: Endpoint[] = [
  {
    id: 'EP-001',
    hostname: 'DESKTOP-MED-01',
    ip: '192.168.1.101',
    os: 'Windows 11 Pro',
    last_seen: new Date(Date.now() - 300000).toISOString(),
    risk_level: 'critical',
    status: 'online'
  },
  {
    id: 'EP-002',
    hostname: 'SERVER-EMR-01',
    ip: '192.168.1.10',
    os: 'Windows Server 2022',
    last_seen: new Date(Date.now() - 60000).toISOString(),
    risk_level: 'high',
    status: 'warning'
  },
  {
    id: 'EP-003',
    hostname: 'LAPTOP-ADMIN-03',
    ip: '192.168.1.105',
    os: 'Windows 11 Pro',
    last_seen: new Date(Date.now() - 120000).toISOString(),
    risk_level: 'medium',
    status: 'online'
  },
  {
    id: 'EP-004',
    hostname: 'WORKSTATION-05',
    ip: '192.168.1.108',
    os: 'Windows 10 Pro',
    last_seen: new Date(Date.now() - 86400000).toISOString(),
    risk_level: 'low',
    status: 'offline'
  }
];

export const mockComplianceControls: ComplianceControl[] = [
  // HIPAA Controls
  {
    id: 'CC-001',
    control_id: 'HIPAA-164.308',
    name: 'Access Control',
    description: 'Implement technical policies and procedures for electronic information systems',
    status: 'passed',
    remediation: '',
    framework: 'hipaa'
  },
  {
    id: 'CC-002',
    control_id: 'HIPAA-164.312',
    name: 'Encryption and Decryption',
    description: 'Implement a mechanism to encrypt and decrypt electronic protected health information',
    status: 'failed',
    remediation: 'Enable BitLocker encryption on all endpoints containing ePHI',
    framework: 'hipaa'
  },
  {
    id: 'CC-003',
    control_id: 'HIPAA-164.308(a)(5)',
    name: 'Security Awareness Training',
    description: 'Implement a security awareness and training program',
    status: 'warning',
    remediation: '3 staff members have not completed annual training',
    framework: 'hipaa'
  },
  {
    id: 'CC-004',
    control_id: 'HIPAA-164.308(a)(1)',
    name: 'Risk Analysis',
    description: 'Conduct an accurate and thorough assessment of the potential risks',
    status: 'passed',
    remediation: '',
    framework: 'hipaa'
  },
  // GDPR Controls
  {
    id: 'CC-005',
    control_id: 'GDPR-Art.32',
    name: 'Security of Processing',
    description: 'Implement appropriate technical and organizational measures to ensure security',
    status: 'passed',
    remediation: '',
    framework: 'gdpr'
  },
  {
    id: 'CC-006',
    control_id: 'GDPR-Art.33',
    name: 'Breach Notification',
    description: 'Notify supervisory authority of personal data breach within 72 hours',
    status: 'passed',
    remediation: '',
    framework: 'gdpr'
  },
  {
    id: 'CC-007',
    control_id: 'GDPR-Art.25',
    name: 'Data Protection by Design',
    description: 'Implement data protection principles at the time of determination of means',
    status: 'warning',
    remediation: 'Review data minimization practices in customer signup process',
    framework: 'gdpr'
  },
  {
    id: 'CC-008',
    control_id: 'GDPR-Art.30',
    name: 'Records of Processing',
    description: 'Maintain records of all processing activities',
    status: 'failed',
    remediation: 'Create comprehensive data processing inventory and update quarterly',
    framework: 'gdpr'
  },
  {
    id: 'CC-009',
    control_id: 'GDPR-Art.17',
    name: 'Right to Erasure',
    description: 'Enable data subjects to obtain erasure of personal data',
    status: 'passed',
    remediation: '',
    framework: 'gdpr'
  },
  // Cyber Essentials Controls
  {
    id: 'CC-010',
    control_id: 'CE-FW',
    name: 'Boundary Firewalls',
    description: 'Configure firewalls to restrict unauthorized access',
    status: 'passed',
    remediation: '',
    framework: 'cyber_essentials'
  },
  {
    id: 'CC-011',
    control_id: 'CE-SC',
    name: 'Secure Configuration',
    description: 'Apply security configurations to devices and software',
    status: 'warning',
    remediation: '12 workstations require configuration baseline updates',
    framework: 'cyber_essentials'
  },
  {
    id: 'CC-012',
    control_id: 'CE-UAC',
    name: 'User Access Control',
    description: 'Control user privileges and access to data and services',
    status: 'passed',
    remediation: '',
    framework: 'cyber_essentials'
  },
  {
    id: 'CC-013',
    control_id: 'CE-MP',
    name: 'Malware Protection',
    description: 'Protect against malware with up-to-date antivirus',
    status: 'passed',
    remediation: '',
    framework: 'cyber_essentials'
  },
  {
    id: 'CC-014',
    control_id: 'CE-PM',
    name: 'Patch Management',
    description: 'Keep software and firmware up to date',
    status: 'failed',
    remediation: 'Deploy pending security patches to 25 endpoints within 48 hours',
    framework: 'cyber_essentials'
  },
  // CIS Controls
  {
    id: 'CC-015',
    control_id: 'CIS-1',
    name: 'Inventory of Authorized Assets',
    description: 'Actively manage all hardware devices on the network',
    status: 'passed',
    remediation: '',
    framework: 'cis'
  },
  {
    id: 'CC-016',
    control_id: 'CIS-2',
    name: 'Inventory of Authorized Software',
    description: 'Actively manage all software on the network',
    status: 'warning',
    remediation: 'Audit and remove 8 unauthorized applications',
    framework: 'cis'
  },
  {
    id: 'CC-017',
    control_id: 'CIS-3',
    name: 'Data Protection',
    description: 'Develop processes to identify, classify, and handle data',
    status: 'passed',
    remediation: '',
    framework: 'cis'
  },
  {
    id: 'CC-018',
    control_id: 'CIS-4',
    name: 'Secure Configuration',
    description: 'Establish and maintain secure configurations',
    status: 'failed',
    remediation: 'Apply CIS benchmarks to all server configurations',
    framework: 'cis'
  },
  {
    id: 'CC-019',
    control_id: 'CIS-5',
    name: 'Account Management',
    description: 'Use processes and tools to manage credentials and accounts',
    status: 'passed',
    remediation: '',
    framework: 'cis'
  },
  {
    id: 'CC-020',
    control_id: 'CIS-6',
    name: 'Access Control Management',
    description: 'Manage access to assets and data',
    status: 'passed',
    remediation: '',
    framework: 'cis'
  },
  // ISO 27001 Controls
  {
    id: 'CC-021',
    control_id: 'ISO-A.9.1.1',
    name: 'Access Control Policy',
    description: 'Establish, document and review access control policy',
    status: 'passed',
    remediation: '',
    framework: 'iso27001'
  },
  {
    id: 'CC-022',
    control_id: 'ISO-A.9.2.3',
    name: 'Management of Privileged Access',
    description: 'Restrict and control allocation of privileged access rights',
    status: 'warning',
    remediation: 'Review and revoke 5 unused administrative accounts',
    framework: 'iso27001'
  },
  {
    id: 'CC-023',
    control_id: 'ISO-A.12.6.1',
    name: 'Technical Vulnerability Management',
    description: 'Obtain timely information about technical vulnerabilities',
    status: 'passed',
    remediation: '',
    framework: 'iso27001'
  },
  {
    id: 'CC-024',
    control_id: 'ISO-A.18.1.5',
    name: 'Regulation of Cryptographic Controls',
    description: 'Use cryptographic controls in compliance with agreements and legislation',
    status: 'passed',
    remediation: '',
    framework: 'iso27001'
  },
  {
    id: 'CC-025',
    control_id: 'ISO-A.12.4.1',
    name: 'Event Logging',
    description: 'Event logs recording user activities and security events shall be produced',
    status: 'failed',
    remediation: 'Enable comprehensive logging on 8 network devices',
    framework: 'iso27001'
  },
  {
    id: 'CC-026',
    control_id: 'ISO-A.16.1.1',
    name: 'Incident Management Responsibilities',
    description: 'Establish management responsibilities and procedures for incident response',
    status: 'warning',
    remediation: 'Update incident response playbook for ransomware scenarios',
    framework: 'iso27001'
  }
];

export const mockComplianceScore = 78;

export const mockComplianceScores = {
  hipaa: 75,
  gdpr: 80,
  cyber_essentials: 72,
  cis: 83,
  iso27001: 79,
  dspt: 72
};

export const mockFileIntegrityEvents: FileIntegrityEvent[] = [
  {
    id: 'FIM-001',
    timestamp: new Date().toISOString(),
    file_path: '/etc/passwd',
    action: 'modified',
    user: 'root',
    hash_before: 'a1b2c3d4e5f6...',
    hash_after: 'f6e5d4c3b2a1...',
    severity: 'critical',
    status: 'flagged'
  },
  {
    id: 'FIM-002',
    timestamp: new Date(Date.now() - 1800000).toISOString(),
    file_path: '/var/www/html/config.php',
    action: 'modified',
    user: 'www-data',
    hash_before: '1a2b3c4d5e6f...',
    hash_after: '6f5e4d3c2b1a...',
    severity: 'high',
    status: 'flagged'
  },
  {
    id: 'FIM-003',
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    file_path: '/home/admin/.ssh/authorized_keys',
    action: 'modified',
    user: 'admin',
    hash_before: 'abc123def456...',
    hash_after: '456defabc123...',
    severity: 'critical',
    status: 'reviewed'
  },
  {
    id: 'FIM-004',
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    file_path: '/opt/app/settings.json',
    action: 'modified',
    user: 'appuser',
    hash_before: 'xyz789uvw012...',
    hash_after: '012uvwxyz789...',
    severity: 'medium',
    status: 'approved'
  },
  {
    id: 'FIM-005',
    timestamp: new Date(Date.now() - 10800000).toISOString(),
    file_path: '/var/log/auth.log',
    action: 'deleted',
    user: 'unknown',
    hash_before: 'log123hash456...',
    severity: 'critical',
    status: 'flagged'
  },
  {
    id: 'FIM-006',
    timestamp: new Date(Date.now() - 14400000).toISOString(),
    file_path: '/etc/cron.d/backup',
    action: 'created',
    user: 'root',
    hash_after: 'cron789backup...',
    severity: 'medium',
    status: 'approved'
  },
  {
    id: 'FIM-007',
    timestamp: new Date(Date.now() - 18000000).toISOString(),
    file_path: '/etc/sudoers',
    action: 'modified',
    user: 'root',
    hash_before: 'sudo111orig222...',
    hash_after: 'sudo222new111...',
    severity: 'high',
    status: 'reviewed'
  },
  {
    id: 'FIM-008',
    timestamp: new Date(Date.now() - 21600000).toISOString(),
    file_path: '/usr/bin/suspicious-binary',
    action: 'created',
    user: 'unknown',
    hash_after: 'binary999new888...',
    severity: 'critical',
    status: 'flagged'
  }
];

// AI Security Analyst Summary Data
export const mockAIInsights: AIInsight[] = [
  {
    id: 'AI-001',
    insight: '3 alerts correlated to privilege escalation attack chain targeting administrative accounts',
    severity: 'critical',
    affected_count: 3,
    correlation_type: 'privilege_escalation'
  },
  {
    id: 'AI-002',
    insight: 'Suspicious PowerShell command execution detected across 5 endpoints in radiology department',
    severity: 'high',
    affected_count: 5,
    correlation_type: 'lateral_movement'
  },
  {
    id: 'AI-003',
    insight: 'Unusual data exfiltration pattern detected from SERVER-EMR-01 to external IP 185.220.101.23',
    severity: 'critical',
    affected_count: 1,
    correlation_type: 'data_exfiltration'
  },
  {
    id: 'AI-004',
    insight: 'Failed authentication attempts increased 340% from baseline - potential brute force attack',
    severity: 'high',
    affected_count: 12,
    correlation_type: 'brute_force'
  },
  {
    id: 'AI-005',
    insight: 'Unauthorized USB device connected to 2 workstations containing patient data',
    severity: 'medium',
    affected_count: 2,
    correlation_type: 'policy_violation'
  }
];

export const mockAISummary = {
  last_updated: new Date().toISOString(),
  alerts_24h: 47,
  critical_incidents: 3,
  threats_mitigated: 12,
  average_response_time: '8.5 minutes',
  recommended_actions: [
    'Isolate DESKTOP-MED-01 and initiate forensic analysis',
    'Force password reset for all administrative accounts (dr.admin@clinic.nhs, sys.admin@clinic.nhs)',
    'Block external IP 185.220.101.23 at firewall level',
    'Deploy MFA enforcement to radiology department endpoints',
    'Review and update USB device control policies'
  ]
};

// Endpoint Health Data
export const mockEndpointHealth: EndpointHealth = {
  total_endpoints: 156,
  online: 142,
  offline: 14,
  at_risk: 23,
  outdated_patches: 38,
  high_risk_count: 8
};

export const mockHighRiskEndpoints: EndpointDetail[] = [
  {
    hostname: 'DESKTOP-MED-01',
    risk_level: 'critical',
    issue: 'Ransomware indicators detected | Outdated AV definitions',
    last_seen: new Date(Date.now() - 300000).toISOString()
  },
  {
    hostname: 'SERVER-EMR-01',
    risk_level: 'critical',
    issue: 'Unusual outbound traffic | Failed login attempts (45)',
    last_seen: new Date(Date.now() - 120000).toISOString()
  },
  {
    hostname: 'LAPTOP-ADMIN-03',
    risk_level: 'high',
    issue: 'Unauthorized USB device | Missing 12 critical patches',
    last_seen: new Date(Date.now() - 180000).toISOString()
  },
  {
    hostname: 'WS-RADIOLOGY-07',
    risk_level: 'high',
    issue: 'Suspicious PowerShell execution | Weak password policy',
    last_seen: new Date(Date.now() - 600000).toISOString()
  },
  {
    hostname: 'SERVER-BACKUP-02',
    risk_level: 'high',
    issue: 'Encryption disabled | No MFA configured',
    last_seen: new Date(Date.now() - 86400000).toISOString()
  }
];
