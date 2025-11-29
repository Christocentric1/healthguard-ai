/**
 * Mock data for MITRE ATT&CK threat detection
 * Enterprise attack techniques and threat intelligence
 */

export interface MITREIndicator {
  indicator_type: 'process' | 'file' | 'network' | 'registry';
  indicator_value: string;
  timestamp: string;
}

export interface MITRETechniqueDetailed {
  technique_id: string;
  technique_name: string;
  tactic: string;
  sub_technique?: string;
  confidence_score: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  indicators: MITREIndicator[];
  ai_explanation: string;
  recommended_mitigations: string[];
}

export interface MITREDetection {
  detection_id: string;
  timestamp: string;
  host: string;
  user: string;
  techniques_detected: MITRETechniqueDetailed[];
  threat_assessment: {
    likelihood_score: number;
    risk_level: 'low' | 'medium' | 'high' | 'critical';
    confidence: number;
    attack_chain_detected: boolean;
    temporal_correlation: boolean;
  };
  ai_summary: {
    executive_summary: string;
    detailed_analysis: string;
    attacker_profile: string;
  };
  iocs: {
    ip_addresses: string[];
    domains: string[];
    file_hashes: string[];
    file_paths: string[];
    registry_keys: string[];
    processes: string[];
  };
  status: 'active' | 'investigating' | 'contained' | 'resolved';
}

export const mockMITREDetections: MITREDetection[] = [
  {
    detection_id: 'det_001',
    timestamp: '2025-11-24T14:30:00Z',
    host: 'WKS-089',
    user: 'john.smith',
    techniques_detected: [
      {
        technique_id: 'T1003',
        technique_name: 'OS Credential Dumping',
        tactic: 'Credential Access',
        sub_technique: 'T1003.001 - LSASS Memory',
        confidence_score: 95,
        severity: 'critical',
        indicators: [
          {
            indicator_type: 'process',
            indicator_value: 'procdump.exe -ma lsass.exe lsass.dmp',
            timestamp: '2025-11-24T14:29:45Z'
          },
          {
            indicator_type: 'file',
            indicator_value: 'C:\\Temp\\lsass.dmp',
            timestamp: '2025-11-24T14:29:48Z'
          }
        ],
        ai_explanation: 'CRITICAL: Credential dumping activity detected using ProcDump to extract LSASS memory. This is a common technique used by attackers to steal credentials for lateral movement and privilege escalation. The LSASS memory dump can contain plaintext passwords, NTLM hashes, and Kerberos tickets.',
        recommended_mitigations: [
          'IMMEDIATE: Isolate workstation WKS-089 from network',
          'Force password reset for user john.smith',
          'Enable Credential Guard on all Windows 10/11 systems',
          'Implement LSASS protection (RunAsPPL)',
          'Hunt for lateral movement indicators across environment'
        ]
      },
      {
        technique_id: 'T1070',
        technique_name: 'Indicator Removal on Host',
        tactic: 'Defense Evasion',
        sub_technique: 'T1070.001 - Clear Windows Event Logs',
        confidence_score: 85,
        severity: 'high',
        indicators: [
          {
            indicator_type: 'process',
            indicator_value: 'wevtutil.exe cl Security',
            timestamp: '2025-11-24T14:31:12Z'
          }
        ],
        ai_explanation: 'Attacker is attempting to cover tracks by clearing Windows Security event logs. This is typically performed after credential theft or malicious activity to evade detection and hinder forensic investigation.',
        recommended_mitigations: [
          'Enable centralized log forwarding to SIEM to prevent local deletion',
          'Implement log immutability with write-once-read-many (WORM) storage',
          'Alert on any log clearing events (Event ID 1102)',
          'Restrict log clearing to authorized administrator accounts only'
        ]
      }
    ],
    threat_assessment: {
      likelihood_score: 92,
      risk_level: 'critical',
      confidence: 0.95,
      attack_chain_detected: true,
      temporal_correlation: true
    },
    ai_summary: {
      executive_summary: 'CRITICAL THREAT: Multi-stage attack detected on WKS-089. Attacker successfully dumped credentials from LSASS memory and attempted to clear event logs. This pattern is consistent with advanced persistent threat (APT) activity or ransomware preparation. Immediate containment required.',
      detailed_analysis: 'At 14:29 UTC, ProcDump was executed to extract LSASS memory containing credentials. Within 2 minutes, the attacker cleared Security event logs to cover tracks. This rapid sequence indicates a skilled adversary with knowledge of Windows internals. The LSASS dump likely contains credentials for lateral movement. Recommend immediate threat hunting across the environment for signs of lateral movement or privilege escalation.',
      attacker_profile: 'Advanced Persistent Threat (APT) or experienced cybercriminal. Demonstrates knowledge of credential theft techniques and anti-forensics. Likely part of a larger intrusion with objectives of ransomware deployment or data exfiltration.'
    },
    iocs: {
      ip_addresses: [],
      domains: [],
      file_hashes: ['a3f8d7e2c1b94f5e8a2d1c3b4e5f6a7b'],
      file_paths: ['C:\\Temp\\lsass.dmp', 'C:\\Users\\john.smith\\AppData\\Local\\Temp\\procdump.exe'],
      registry_keys: [],
      processes: ['procdump.exe', 'wevtutil.exe']
    },
    status: 'active'
  },
  {
    detection_id: 'det_002',
    timestamp: '2025-11-24T10:15:00Z',
    host: 'WKS-045',
    user: 'sarah.johnson',
    techniques_detected: [
      {
        technique_id: 'T1566',
        technique_name: 'Phishing',
        tactic: 'Initial Access',
        sub_technique: 'T1566.001 - Spearphishing Attachment',
        confidence_score: 88,
        severity: 'high',
        indicators: [
          {
            indicator_type: 'file',
            indicator_value: 'Invoice_November.xlsm',
            timestamp: '2025-11-24T10:14:30Z'
          },
          {
            indicator_type: 'process',
            indicator_value: 'excel.exe spawned powershell.exe',
            timestamp: '2025-11-24T10:14:45Z'
          }
        ],
        ai_explanation: 'Phishing attack detected. User opened malicious Excel document that executed macro code, spawning PowerShell. This is a common malware delivery mechanism used to download second-stage payloads, establish persistence, or exfiltrate data.',
        recommended_mitigations: [
          'Immediately isolate endpoint WKS-045 from network',
          'Quarantine email attachment from all mailboxes',
          'Run full antivirus and EDR scan',
          'Block sender domain at email gateway',
          'Implement attachment sandboxing for Office macros',
          'Provide security awareness training to sarah.johnson'
        ]
      }
    ],
    threat_assessment: {
      likelihood_score: 78,
      risk_level: 'high',
      confidence: 0.88,
      attack_chain_detected: false,
      temporal_correlation: false
    },
    ai_summary: {
      executive_summary: 'Phishing attack in progress on WKS-045. User opened malicious Excel document with embedded macro that executed PowerShell. Quick containment prevented progression to next attack stage.',
      detailed_analysis: 'User sarah.johnson received targeted phishing email with Invoice_November.xlsm attachment. Upon opening, VBA macro executed and spawned PowerShell process, likely attempting to download additional malware. EDR detection triggered before payload could execute. Recommend analysis of PowerShell command line and network connections for C2 infrastructure.',
      attacker_profile: 'Commodity cybercriminal using common phishing techniques. Likely automated campaign targeting multiple organizations. Medium sophistication level.'
    },
    iocs: {
      ip_addresses: [],
      domains: ['malicious-invoice-hosting[.]com'],
      file_hashes: ['f7e8d9c2b1a94f5e8a2d1c3b4e5f6a7b'],
      file_paths: ['C:\\Users\\sarah.johnson\\Downloads\\Invoice_November.xlsm'],
      registry_keys: [],
      processes: ['excel.exe', 'powershell.exe']
    },
    status: 'contained'
  },
  {
    detection_id: 'det_003',
    timestamp: '2025-11-23T22:45:00Z',
    host: 'SRV-025',
    user: 'SYSTEM',
    techniques_detected: [
      {
        technique_id: 'T1110',
        technique_name: 'Brute Force',
        tactic: 'Credential Access',
        sub_technique: 'T1110.003 - Password Spraying',
        confidence_score: 92,
        severity: 'high',
        indicators: [
          {
            indicator_type: 'network',
            indicator_value: '45 failed login attempts from 192.168.50.100',
            timestamp: '2025-11-23T22:40:00Z'
          }
        ],
        ai_explanation: 'Password spraying attack detected from internal IP. Attacker is using common passwords across multiple accounts to avoid lockouts. This indicates either a compromised internal system or insider threat. The attack pattern suggests automated tooling.',
        recommended_mitigations: [
          'Block source IP 192.168.50.100 immediately',
          'Enable account lockout policy (5 failed attempts)',
          'Implement MFA for all accounts',
          'Enable rate limiting on authentication endpoints',
          'Investigate source system for compromise',
          'Deploy geolocation-based access controls'
        ]
      }
    ],
    threat_assessment: {
      likelihood_score: 82,
      risk_level: 'high',
      confidence: 0.92,
      attack_chain_detected: false,
      temporal_correlation: false
    },
    ai_summary: {
      executive_summary: 'Password spraying attack detected from internal network. 45 accounts targeted with common passwords. Attack blocked by security controls. Source IP requires investigation for compromise.',
      detailed_analysis: 'Automated password spraying attack originated from 192.168.50.100 targeting domain accounts. Attack used common passwords (Password123!, Winter2025!, etc.) across multiple accounts. No successful logins recorded. Source IP belongs to workstation WKS-112 which may be compromised or accessed by malicious insider.',
      attacker_profile: 'Either compromised endpoint being used as pivot point, or malicious insider with network access. Medium sophistication - using known attack tool.'
    },
    iocs: {
      ip_addresses: ['192.168.50.100'],
      domains: [],
      file_hashes: [],
      file_paths: [],
      registry_keys: [],
      processes: []
    },
    status: 'investigating'
  }
];

export interface MITREHeatmapCell {
  technique_id: string;
  technique_name: string;
  tactic: string;
  detection_count: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  last_detected: string;
}

export const mockMITREHeatmap: MITREHeatmapCell[] = [
  { technique_id: 'T1003', technique_name: 'OS Credential Dumping', tactic: 'Credential Access', detection_count: 1, severity: 'critical', last_detected: '2025-11-24T14:30:00Z' },
  { technique_id: 'T1566', technique_name: 'Phishing', tactic: 'Initial Access', detection_count: 3, severity: 'high', last_detected: '2025-11-24T10:15:00Z' },
  { technique_id: 'T1110', technique_name: 'Brute Force', tactic: 'Credential Access', detection_count: 2, severity: 'high', last_detected: '2025-11-23T22:45:00Z' },
  { technique_id: 'T1070', technique_name: 'Indicator Removal', tactic: 'Defense Evasion', detection_count: 1, severity: 'high', last_detected: '2025-11-24T14:31:00Z' },
  { technique_id: 'T1059', technique_name: 'Command and Scripting Interpreter', tactic: 'Execution', detection_count: 5, severity: 'medium', last_detected: '2025-11-24T10:14:00Z' },
  { technique_id: 'T1082', technique_name: 'System Information Discovery', tactic: 'Discovery', detection_count: 8, severity: 'low', last_detected: '2025-11-23T16:20:00Z' },
  { technique_id: 'T1021', technique_name: 'Remote Services', tactic: 'Lateral Movement', detection_count: 4, severity: 'medium', last_detected: '2025-11-22T11:30:00Z' },
  { technique_id: 'T1078', technique_name: 'Valid Accounts', tactic: 'Initial Access', detection_count: 6, severity: 'medium', last_detected: '2025-11-24T08:00:00Z' }
];

export const mockMITRETechniques = [
  {
    technique_id: 'T1003',
    technique_name: 'OS Credential Dumping',
    tactic: 'Credential Access',
    description: 'Adversaries attempt to dump credentials to obtain account login and credential material.',
    severity: 'critical',
    data_sources: ['Process monitoring', 'PowerShell logs', 'API monitoring'],
    platforms: ['Windows', 'Linux', 'macOS']
  },
  {
    technique_id: 'T1566',
    technique_name: 'Phishing',
    tactic: 'Initial Access',
    description: 'Adversaries send phishing messages to gain access to victim systems.',
    severity: 'high',
    data_sources: ['Email gateway', 'File monitoring', 'Network traffic'],
    platforms: ['Windows', 'Linux', 'macOS', 'Office 365']
  },
  {
    technique_id: 'T1110',
    technique_name: 'Brute Force',
    tactic: 'Credential Access',
    description: 'Adversaries use brute force techniques to gain access to accounts.',
    severity: 'high',
    data_sources: ['Authentication logs', 'Network traffic'],
    platforms: ['Windows', 'Linux', 'macOS', 'Cloud']
  }
];
