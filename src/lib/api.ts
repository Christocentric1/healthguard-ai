/**
 * API Configuration for Cyber Guardian
 *
 * This module provides centralized API configuration and utilities
 * for making requests to the backend.
 */

// Get API URL from environment variables and remove trailing slash
const rawApiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const API_BASE_URL = rawApiUrl.replace(/\/+$/, ''); // Remove trailing slashes

// Check if we should use mock data
export const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === 'true';

// Environment
export const ENV = import.meta.env.VITE_ENV || 'development';

/**
 * API endpoints configuration
 */
export const API_ENDPOINTS = {
  // Health check
  health: `${API_BASE_URL}/health`,

  // Alerts
  alerts: `${API_BASE_URL}/api/alerts`,
  alertById: (id: string) => `${API_BASE_URL}/api/alerts/${id}`,

  // Endpoints monitoring
  endpoints: `${API_BASE_URL}/api/endpoints`,
  endpointById: (id: string) => `${API_BASE_URL}/api/endpoints/${id}`,

  // Compliance
  compliance: `${API_BASE_URL}/api/compliance`,
  complianceReports: `${API_BASE_URL}/api/compliance/reports`,

  // DSPT Compliance
  dspt: `${API_BASE_URL}/api/compliance/dspt`,
  dsptDomains: `${API_BASE_URL}/api/compliance/dspt/domains`,
  dsptGaps: `${API_BASE_URL}/api/compliance/dspt/gaps`,
  dsptEvidence: `${API_BASE_URL}/api/compliance/dspt/evidence`,
  dsptEndpointGaps: `${API_BASE_URL}/api/compliance/dspt/endpoint-gaps`,

  // MITRE ATT&CK
  mitreDetections: `${API_BASE_URL}/api/mitre/detections`,
  mitreHeatmap: `${API_BASE_URL}/api/mitre/heatmap`,
  mitreTechniques: `${API_BASE_URL}/api/mitre/techniques`,
  mitreActiveThreats: `${API_BASE_URL}/api/mitre/active-threats`,

  // Settings
  settings: `${API_BASE_URL}/api/settings`,

  // Dashboard metrics
  dashboardMetrics: `${API_BASE_URL}/api/dashboard/metrics`,

  // Authentication
  register: `${API_BASE_URL}/api/auth/register`,
  login: `${API_BASE_URL}/api/auth/login`,
  logout: `${API_BASE_URL}/api/auth/logout`,
  me: `${API_BASE_URL}/api/auth/me`,
};

/**
 * Fetch wrapper with error handling and automatic JWT token inclusion
 */
export async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  try {
    // Get JWT token and org ID from localStorage
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user');
    let orgId = 'org_001'; // Default org

    // Parse user object to get organisation_id
    if (user) {
      try {
        const userData = JSON.parse(user);
        orgId = userData.organisation_id || orgId;
      } catch (e) {
        console.warn('Failed to parse user data:', e);
      }
    }

    // Build headers
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'X-Org-Id': orgId, // Required for multi-tenancy
      ...options?.headers,
    };

    // Add Authorization header if token exists
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(endpoint, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: response.statusText,
      }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

/**
 * Check if the backend API is healthy
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(API_ENDPOINTS.health, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    return response.ok;
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
}

/**
 * Log API configuration on app startup
 */
export function logApiConfig() {
  console.log('🔧 API Configuration:');
  console.log(`  - Environment: ${ENV}`);
  console.log(`  - API Base URL: ${API_BASE_URL}`);
  console.log(`  - Use Mock Data: ${USE_MOCK_DATA}`);
}

/**
 * Transform API alert response to frontend Alert format
 */
interface ApiAlert {
  alert_id: string;
  organisation_id: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  host: string;
  user: string;
  event_type: string;
  anomaly_score: number | null;
  triggered_by: string;
  rule_name?: string;
  created_at: string;
  updated_at: string;
  comments: unknown[];
  related_log_ids: string[];
}

interface ApiAlertsResponse {
  alerts: ApiAlert[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export function transformAlert(apiAlert: ApiAlert) {
  return {
    id: apiAlert.alert_id,
    timestamp: apiAlert.created_at,
    organisation_id: apiAlert.organisation_id,
    host: apiAlert.host,
    user: apiAlert.user,
    severity: apiAlert.severity as 'critical' | 'high' | 'medium' | 'low',
    category: apiAlert.title,
    description: apiAlert.description,
    ai_risk_score: apiAlert.anomaly_score ? Math.round(apiAlert.anomaly_score * 100) : 50,
    recommended_action: `Review ${apiAlert.event_type} event triggered by ${apiAlert.triggered_by}`,
    status: apiAlert.status === 'open' ? 'new' : apiAlert.status as 'new' | 'investigating' | 'resolved' | 'false_positive',
    source: apiAlert.triggered_by === 'rule' ? `Rule: ${apiAlert.rule_name || 'Unknown'}` : 'AI Detection',
  };
}

export function transformAlertsResponse(response: ApiAlertsResponse) {
  return {
    alerts: response.alerts.map(transformAlert),
    total: response.total,
    page: response.page,
    page_size: response.page_size,
    total_pages: response.total_pages,
  };
}

/**
 * Transform API endpoint response to frontend Endpoint format
 */
interface ApiEndpoint {
  organisation_id: string;
  host: string;
  ip_address: string | null;
  os_type: string | null;
  last_seen: string;
  risk_level: string;
  risk_score: number;
  alert_count_7d: number;
  alert_count_30d: number;
  anomaly_count: number;
  critical_alerts: number;
  compliance_issues: number;
}

interface ApiEndpointsResponse {
  endpoints: ApiEndpoint[];
  total: number;
}

export function transformEndpoint(apiEndpoint: ApiEndpoint, index: number) {
  return {
    id: `EP-${String(index + 1).padStart(3, '0')}`,
    hostname: apiEndpoint.host,
    ip: apiEndpoint.ip_address || 'Unknown',
    os: apiEndpoint.os_type || 'Unknown',
    last_seen: apiEndpoint.last_seen,
    status: 'online' as const,
    risk_level: apiEndpoint.risk_level as 'critical' | 'high' | 'medium' | 'low',
    agent_version: '1.0.0',
    compliance_score: Math.max(0, 100 - (apiEndpoint.compliance_issues * 10)),
    alert_count: apiEndpoint.alert_count_7d,
    risk_score: apiEndpoint.risk_score,
  };
}

export function transformEndpointsResponse(response: ApiEndpointsResponse) {
  return {
    endpoints: response.endpoints.map((ep, i) => transformEndpoint(ep, i)),
    total: response.total,
  };
}

/**
 * Fetch alerts with automatic transformation
 */
export async function fetchAlerts() {
  const response = await apiFetch<ApiAlertsResponse>(API_ENDPOINTS.alerts);
  return transformAlertsResponse(response);
}

/**
 * Fetch endpoints with automatic transformation
 */
export async function fetchEndpoints() {
  const response = await apiFetch<ApiEndpointsResponse>(API_ENDPOINTS.endpoints);
  return transformEndpointsResponse(response);
}
