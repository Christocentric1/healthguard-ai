/**
 * Mock data for DSPT (Data Security and Protection Toolkit) compliance
 * UK NHS framework for data security
 */

export interface DSPTControl {
  control_id: string;
  control_name: string;
  status: 'pass' | 'fail' | 'partial';
  evidence: string;
  last_assessed: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
}

export interface DSPTGap {
  gap_description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  affected_systems: string[];
  remediation: string;
  estimated_effort: string;
}

export interface DSPTDomain {
  domain_id: string;
  domain_name: string;
  score: number;
  status: 'compliant' | 'partial' | 'non_compliant';
  controls: DSPTControl[];
  gaps: DSPTGap[];
  ai_recommendations: string[];
  endpoint_data_sources: string[];
}

export const mockDSPTDomains: DSPTDomain[] = [
  {
    domain_id: 'personal_confidential_data',
    domain_name: 'Personal Confidential Data',
    score: 85,
    status: 'compliant',
    controls: [
      {
        control_id: 'PCD-001',
        control_name: 'Staff training on PCD handling',
        status: 'pass',
        evidence: '95% of staff completed annual training',
        last_assessed: '2025-11-20T10:00:00Z',
        risk_level: 'low'
      },
      {
        control_id: 'PCD-002',
        control_name: 'Data handling policy acceptance',
        status: 'pass',
        evidence: 'All staff have signed policy agreements',
        last_assessed: '2025-11-20T10:00:00Z',
        risk_level: 'low'
      }
    ],
    gaps: [],
    ai_recommendations: [
      'Implement automated training reminders for staff due for refresher courses',
      'Deploy data classification labels on all file shares containing patient data'
    ],
    endpoint_data_sources: ['file_access_logs', 'dlp_events', 'user_training_records']
  },
  {
    domain_id: 'staff_responsibilities',
    domain_name: 'Staff Responsibilities',
    score: 72,
    status: 'partial',
    controls: [
      {
        control_id: 'SR-001',
        control_name: 'Acceptable Use Policy acceptance',
        status: 'pass',
        evidence: '100% of staff signed AUP',
        last_assessed: '2025-11-20T10:00:00Z',
        risk_level: 'low'
      },
      {
        control_id: 'SR-002',
        control_name: 'Automatic screen lock compliance',
        status: 'partial',
        evidence: '78% of workstations have 5-min timeout configured',
        last_assessed: '2025-11-20T10:00:00Z',
        risk_level: 'medium'
      }
    ],
    gaps: [
      {
        gap_description: '22% of workstations missing automatic screen lock timeout',
        severity: 'medium',
        affected_systems: ['WKS-045', 'WKS-067', 'WKS-089', 'WKS-112'],
        remediation: 'Deploy GPO to enforce 5-minute screen lock timeout on all workstations',
        estimated_effort: '2 hours'
      }
    ],
    ai_recommendations: [
      'Deploy Group Policy Object to enforce screen lock after 5 minutes inactivity',
      'Enable USB device whitelisting to prevent unauthorized data transfer'
    ],
    endpoint_data_sources: ['screen_lock_logs', 'usb_device_logs', 'policy_acceptance_records']
  },
  {
    domain_id: 'managing_data_access',
    domain_name: 'Managing Data Access',
    score: 65,
    status: 'partial',
    controls: [
      {
        control_id: 'MDA-001',
        control_name: 'Multi-factor authentication',
        status: 'partial',
        evidence: '68% of accounts have MFA enabled',
        last_assessed: '2025-11-20T10:00:00Z',
        risk_level: 'high'
      },
      {
        control_id: 'MDA-002',
        control_name: 'Access reviews completed',
        status: 'fail',
        evidence: 'Last review completed 8 months ago (overdue)',
        last_assessed: '2025-11-20T10:00:00Z',
        risk_level: 'high'
      },
      {
        control_id: 'MDA-003',
        control_name: 'Dormant account management',
        status: 'partial',
        evidence: '12 dormant accounts detected (>90 days inactive)',
        last_assessed: '2025-11-20T10:00:00Z',
        risk_level: 'medium'
      }
    ],
    gaps: [
      {
        gap_description: '32% of accounts accessing patient data do not have MFA enabled',
        severity: 'high',
        affected_systems: ['Active Directory', 'Patient Management System'],
        remediation: 'Mandate MFA for all accounts with access to patient confidential data',
        estimated_effort: '1 week'
      },
      {
        gap_description: 'Access reviews overdue by 2 quarters',
        severity: 'high',
        affected_systems: ['All systems'],
        remediation: 'Conduct immediate access review and establish quarterly review process',
        estimated_effort: '3 days'
      }
    ],
    ai_recommendations: [
      'URGENT: Enable MFA for all 32% of accounts accessing patient data within 7 days',
      'Initiate immediate access review for all privileged accounts',
      'Implement automated dormant account suspension after 90 days inactivity',
      'Deploy privileged access management (PAM) solution for admin accounts'
    ],
    endpoint_data_sources: ['active_directory_logs', 'mfa_enrollment_status', 'access_review_records']
  },
  {
    domain_id: 'it_protection',
    domain_name: 'IT Protection',
    score: 88,
    status: 'compliant',
    controls: [
      {
        control_id: 'ITP-001',
        control_name: 'Antivirus coverage and currency',
        status: 'pass',
        evidence: '97% of endpoints have current AV definitions',
        last_assessed: '2025-11-20T10:00:00Z',
        risk_level: 'low'
      },
      {
        control_id: 'ITP-002',
        control_name: 'Email security controls',
        status: 'pass',
        evidence: '99.2% of phishing emails blocked',
        last_assessed: '2025-11-20T10:00:00Z',
        risk_level: 'low'
      },
      {
        control_id: 'ITP-003',
        control_name: 'Firewall configuration',
        status: 'pass',
        evidence: 'Firewall rules reviewed and approved within last 6 months',
        last_assessed: '2025-11-20T10:00:00Z',
        risk_level: 'low'
      }
    ],
    gaps: [],
    ai_recommendations: [
      'Consider deploying next-generation antivirus with behavioral detection',
      'Implement email link sandboxing for additional phishing protection'
    ],
    endpoint_data_sources: ['av_status_logs', 'email_gateway_logs', 'firewall_logs']
  },
  {
    domain_id: 'unsupported_systems',
    domain_name: 'Unsupported Systems',
    score: 45,
    status: 'non_compliant',
    controls: [
      {
        control_id: 'US-001',
        control_name: 'Unsupported OS identification',
        status: 'fail',
        evidence: '8 Windows Server 2008 systems still in production',
        last_assessed: '2025-11-20T10:00:00Z',
        risk_level: 'critical'
      },
      {
        control_id: 'US-002',
        control_name: 'Compensating controls for EOL systems',
        status: 'partial',
        evidence: 'Network segmentation implemented, but no virtual patching',
        last_assessed: '2025-11-20T10:00:00Z',
        risk_level: 'high'
      }
    ],
    gaps: [
      {
        gap_description: '8 end-of-life Windows Server 2008 systems without security patches',
        severity: 'critical',
        affected_systems: ['SRV-008', 'SRV-012', 'SRV-019', 'SRV-025', 'SRV-031', 'SRV-044', 'SRV-056', 'SRV-067'],
        remediation: 'URGENT: Migrate to supported OS or implement comprehensive compensating controls',
        estimated_effort: '3 months'
      }
    ],
    ai_recommendations: [
      'CRITICAL: Create migration roadmap for all Windows Server 2008 systems within 90 days',
      'Implement network micro-segmentation to isolate EOL systems from patient data',
      'Deploy virtual patching with IPS/IDS for unpatched vulnerabilities',
      'Establish executive steering committee for legacy system modernization'
    ],
    endpoint_data_sources: ['software_inventory', 'os_version_scans', 'vendor_support_status']
  },
  {
    domain_id: 'network_security',
    domain_name: 'Network Security',
    score: 78,
    status: 'partial',
    controls: [
      {
        control_id: 'NS-001',
        control_name: 'Network segmentation',
        status: 'pass',
        evidence: 'DMZ and internal zones properly segmented with ACLs',
        last_assessed: '2025-11-20T10:00:00Z',
        risk_level: 'low'
      },
      {
        control_id: 'NS-002',
        control_name: 'VPN with MFA',
        status: 'partial',
        evidence: '85% of VPN users have MFA enabled',
        last_assessed: '2025-11-20T10:00:00Z',
        risk_level: 'medium'
      },
      {
        control_id: 'NS-003',
        control_name: 'Wireless security',
        status: 'pass',
        evidence: 'All access points using WPA3 with certificate authentication',
        last_assessed: '2025-11-20T10:00:00Z',
        risk_level: 'low'
      }
    ],
    gaps: [
      {
        gap_description: '15% of VPN users not using MFA',
        severity: 'medium',
        affected_systems: ['VPN Gateway'],
        remediation: 'Mandate MFA for all VPN access',
        estimated_effort: '1 week'
      }
    ],
    ai_recommendations: [
      'Require MFA for all VPN and remote access connections',
      'Implement zero-trust network architecture principles',
      'Deploy network access control (NAC) for device authentication'
    ],
    endpoint_data_sources: ['network_topology', 'vpn_logs', 'wireless_ap_configs']
  }
];

export const mockDSPTScore = {
  overall_score: 72,
  status: 'partial' as const,
  compliant_domains: 2,
  partial_domains: 4,
  non_compliant_domains: 1,
  high_risk_gaps: 3,
  critical_gaps: 1
};

export const mockDSPTEvidenceRequirements = [
  {
    domain_id: 'managing_data_access',
    control_id: 'MDA-001',
    evidence_type: 'MFA enrollment report',
    description: 'List of all accounts with MFA status',
    collection_method: 'Export from identity management system',
    frequency: 'Monthly'
  },
  {
    domain_id: 'managing_data_access',
    control_id: 'MDA-002',
    evidence_type: 'Access review completion certificate',
    description: 'Signed attestation of completed access reviews',
    collection_method: 'Manager sign-off in ticketing system',
    frequency: 'Quarterly'
  },
  {
    domain_id: 'unsupported_systems',
    control_id: 'US-001',
    evidence_type: 'Software inventory report',
    description: 'Complete list of OS versions with support status',
    collection_method: 'Automated scan from asset management tool',
    frequency: 'Weekly'
  }
];

export const mockDSPTEndpointGaps = [
  {
    host: 'WKS-045',
    domain: 'Staff Responsibilities',
    gap_description: 'Screen lock timeout not configured',
    severity: 'medium' as const,
    remediation: 'Apply Group Policy for 5-minute timeout',
    status: 'pending'
  },
  {
    host: 'SRV-008',
    domain: 'Unsupported Systems',
    gap_description: 'Windows Server 2008 (end-of-life)',
    severity: 'critical' as const,
    remediation: 'Migrate to Windows Server 2022',
    status: 'in_progress'
  },
  {
    host: 'WKS-067',
    domain: 'Staff Responsibilities',
    gap_description: 'USB port not restricted',
    severity: 'medium' as const,
    remediation: 'Deploy USB whitelisting policy',
    status: 'pending'
  }
];
