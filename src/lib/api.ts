/**
 * API Configuration for Cyber HealthGuard
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
