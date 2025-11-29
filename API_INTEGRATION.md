# API Integration Guide

This document explains where and how to integrate your external REST APIs into the Cyber HealthGuard AI application.

## Overview

The application currently uses mock data defined in `src/data/mockData.ts`. To connect your real backend APIs, you'll need to replace the mock data with actual API calls.

## Mock Data Location

All mock data is defined in:
```
src/data/mockData.ts
```

This file contains:
- `mockAlerts` - Array of security alerts
- `mockEndpoints` - Array of monitored endpoints
- `mockComplianceControls` - Array of compliance controls
- `mockComplianceScore` - Overall compliance score (number)

## API Integration Points

### 1. GET /api/alerts

**Purpose**: Fetch all alerts for the organization

**Used in**: `src/pages/Alerts.tsx`

**Current mock usage**:
```typescript
import { mockAlerts } from "@/data/mockData";
```

**Integration steps**:

1. Create a new file `src/services/api.ts`:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function getAlerts() {
  const response = await fetch(`${API_BASE_URL}/api/alerts`, {
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`, // Add your auth logic
      'Content-Type': 'application/json',
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch alerts');
  }
  
  return response.json();
}
```

2. In `src/pages/Alerts.tsx`, replace:
```typescript
import { mockAlerts } from "@/data/mockData";
```

With:
```typescript
import { useQuery } from "@tanstack/react-query";
import { getAlerts } from "@/services/api";

// Inside component:
const { data: alerts = [], isLoading } = useQuery({
  queryKey: ['alerts'],
  queryFn: getAlerts,
});

// Use 'alerts' instead of 'mockAlerts'
```

3. Also update `src/pages/Dashboard.tsx` which also uses alerts.

---

### 2. GET /api/alerts/:id

**Purpose**: Fetch a single alert by ID

**Used in**: `src/pages/AlertDetail.tsx`

**Current mock usage**:
```typescript
const alert = mockAlerts.find(a => a.id === id);
```

**Integration steps**:

1. Add to `src/services/api.ts`:
```typescript
export async function getAlertById(id: string) {
  const response = await fetch(`${API_BASE_URL}/api/alerts/${id}`, {
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
      'Content-Type': 'application/json',
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch alert');
  }
  
  return response.json();
}
```

2. In `src/pages/AlertDetail.tsx`, replace:
```typescript
const alert = mockAlerts.find(a => a.id === id);
```

With:
```typescript
const { data: alert, isLoading } = useQuery({
  queryKey: ['alert', id],
  queryFn: () => getAlertById(id!),
  enabled: !!id,
});
```

---

### 3. GET /api/endpoints

**Purpose**: Fetch all endpoints for the organization

**Used in**: `src/pages/Endpoints.tsx`

**Current mock usage**:
```typescript
import { mockEndpoints } from "@/data/mockData";
```

**Integration steps**:

1. Add to `src/services/api.ts`:
```typescript
export async function getEndpoints() {
  const response = await fetch(`${API_BASE_URL}/api/endpoints`, {
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
      'Content-Type': 'application/json',
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch endpoints');
  }
  
  return response.json();
}
```

2. In `src/pages/Endpoints.tsx`, replace:
```typescript
import { mockEndpoints } from "@/data/mockData";
```

With:
```typescript
const { data: endpoints = [], isLoading } = useQuery({
  queryKey: ['endpoints'],
  queryFn: getEndpoints,
});

// Use 'endpoints' instead of 'mockEndpoints'
```

---

### 4. GET /api/compliance

**Purpose**: Fetch compliance data (score and controls)

**Used in**: `src/pages/Compliance.tsx`

**Current mock usage**:
```typescript
import { mockComplianceControls, mockComplianceScore } from "@/data/mockData";
```

**Integration steps**:

1. Add to `src/services/api.ts`:
```typescript
export async function getCompliance() {
  const response = await fetch(`${API_BASE_URL}/api/compliance`, {
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
      'Content-Type': 'application/json',
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch compliance data');
  }
  
  return response.json(); // Expected format: { score: number, controls: [...] }
}
```

2. In `src/pages/Compliance.tsx`, replace:
```typescript
import { mockComplianceControls, mockComplianceScore } from "@/data/mockData";
```

With:
```typescript
const { data: complianceData, isLoading } = useQuery({
  queryKey: ['compliance'],
  queryFn: getCompliance,
});

const complianceScore = complianceData?.score || 0;
const complianceControls = complianceData?.controls || [];
```

---

### 5. PATCH /api/alerts/:id

**Purpose**: Update alert status

**Used in**: `src/pages/AlertDetail.tsx` (when changing status dropdown)

**Current behavior**: Status change is only stored in local state

**Integration steps**:

1. Add to `src/services/api.ts`:
```typescript
export async function updateAlertStatus(id: string, status: string) {
  const response = await fetch(`${API_BASE_URL}/api/alerts/${id}`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ status }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to update alert');
  }
  
  return response.json();
}
```

2. In `src/pages/AlertDetail.tsx`, add:
```typescript
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateAlertStatus } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

// Inside component:
const queryClient = useQueryClient();
const { toast } = useToast();

const updateStatusMutation = useMutation({
  mutationFn: (newStatus: string) => updateAlertStatus(id!, newStatus),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['alert', id] });
    queryClient.invalidateQueries({ queryKey: ['alerts'] });
    toast({
      title: "Status updated",
      description: "Alert status has been updated successfully.",
    });
  },
  onError: () => {
    toast({
      title: "Error",
      description: "Failed to update alert status.",
      variant: "destructive",
    });
  },
});

// Update the status change handler:
const handleStatusChange = (newStatus: string) => {
  setStatus(newStatus);
  updateStatusMutation.mutate(newStatus);
};

// Update the Select component:
<Select value={status} onValueChange={handleStatusChange}>
```

---

## Authentication & Authorization

### Multi-tenancy Implementation

The current UI shell includes mock organization info. To implement real multi-tenancy:

1. Store the organization ID in your auth context/token
2. Send it with every API request (either in headers or as a query param)
3. Your backend should filter all data by `organisation_id`

Example auth service (`src/services/auth.ts`):

```typescript
interface User {
  id: string;
  email: string;
  role: 'org_admin' | 'analyst' | 'viewer';
  organisation_id: string;
  organisation_name: string;
}

let currentUser: User | null = null;
let authToken: string | null = null;

export async function login(email: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  
  if (!response.ok) {
    throw new Error('Login failed');
  }
  
  const data = await response.json();
  authToken = data.token;
  currentUser = data.user;
  
  localStorage.setItem('auth_token', authToken);
  localStorage.setItem('user', JSON.stringify(currentUser));
  
  return data;
}

export function getAuthToken(): string | null {
  if (!authToken) {
    authToken = localStorage.getItem('auth_token');
  }
  return authToken;
}

export function getCurrentUser(): User | null {
  if (!currentUser) {
    const stored = localStorage.getItem('user');
    currentUser = stored ? JSON.parse(stored) : null;
  }
  return currentUser;
}

export function logout() {
  authToken = null;
  currentUser = null;
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user');
}
```

### Protecting Routes

Create a protected route wrapper (`src/components/ProtectedRoute.tsx`):

```typescript
import { Navigate } from "react-router-dom";
import { getCurrentUser } from "@/services/auth";

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string[];
}

export function ProtectedRoute({ children, requiredRole }: ProtectedRouteProps) {
  const user = getCurrentUser();
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  if (requiredRole && !requiredRole.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return <>{children}</>;
}
```

Then wrap routes in `App.tsx`:

```typescript
<Route path="/dashboard" element={
  <ProtectedRoute>
    <Dashboard />
  </ProtectedRoute>
} />
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
VITE_API_BASE_URL=https://your-api-domain.com
```

For local development:
```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Expected API Response Formats

### Alert Object
```typescript
{
  id: string;
  timestamp: string; // ISO 8601 format
  organisation_id: string;
  host: string;
  user: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  description: string;
  ai_risk_score: number; // 0-100
  recommended_action: string;
  status: 'new' | 'investigating' | 'resolved' | 'false_positive';
  source: string;
}
```

### Endpoint Object
```typescript
{
  id: string;
  hostname: string;
  ip: string;
  os: string;
  last_seen: string; // ISO 8601 format
  risk_level: 'critical' | 'high' | 'medium' | 'low';
  status: 'online' | 'offline' | 'warning';
}
```

### Compliance Object
```typescript
{
  score: number; // 0-100
  controls: Array<{
    id: string;
    control_id: string;
    name: string;
    description: string;
    status: 'passed' | 'failed' | 'warning';
    remediation: string;
  }>;
}
```

---

## Testing

To test the integration:

1. Keep mock data while developing
2. Create a feature flag in your app to switch between mock and real data
3. Test each endpoint individually
4. Verify multi-tenancy isolation (users only see their org's data)

---

## Dashboard Summary Stats

The dashboard shows aggregated stats. If your API doesn't provide these aggregations, calculate them client-side:

```typescript
const todayAlerts = alerts.filter(a => 
  new Date(a.timestamp).toDateString() === new Date().toDateString()
).length;

const criticalAlerts = alerts.filter(a => 
  a.severity === 'critical' && a.status !== 'resolved'
).length;
```

Or better, create a dedicated endpoint:
```
GET /api/dashboard/stats
```

That returns:
```typescript
{
  total_alerts_today: number;
  critical_alerts: number;
  risk_score: number;
  compliance_score: number;
}
```

---

## Next Steps

1. Implement authentication endpoints in your backend
2. Ensure all endpoints filter by `organisation_id`
3. Test multi-tenancy isolation thoroughly
4. Implement the integration points above one by one
5. Add error handling and loading states
6. Consider adding real-time updates (WebSockets or polling)

For any questions, refer to the TypeScript interfaces in `src/data/mockData.ts` for the exact data structure expected by the UI.
