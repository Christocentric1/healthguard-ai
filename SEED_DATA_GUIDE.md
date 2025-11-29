# Database Seeding Guide

Your backend is running but has no data. This guide shows you how to populate it with realistic healthcare cybersecurity data.

## Quick Start

### Option 1: Run the Automated Script (Easiest)

```bash
./seed-production-data.sh
```

This will automatically:
1. Set up Python environment
2. Install dependencies
3. Seed the database with realistic data
4. Show you a summary

### Option 2: Manual Seeding

```bash
cd backend
source venv/bin/activate  # or: venv\Scripts\activate on Windows
python3 scripts/seed_database.py
```

## What Gets Seeded

The script creates realistic data for **organization `org_001`**:

### 📝 50 Log Events
- Various event types (login, file access, network, process execution)
- Mixed severities (critical, high, medium, low)
- From different sources (EDR, SIEM, Firewall, IDS, DLP)
- Spread across last 48 hours

### 🚨 5 Alerts
1. **Critical** - Ransomware activity on DESKTOP-MED-01
2. **High** - Multiple failed login attempts on SERVER-EMR-01
3. **Medium** - Unauthorized USB device on LAPTOP-ADMIN-03
4. **High** - Suspicious PowerShell execution on WS-RADIOLOGY-07
5. **Critical** - Data exfiltration from SERVER-BACKUP-02

### 💻 5 Endpoints
- DESKTOP-MED-01 (Windows 11, Critical risk)
- SERVER-EMR-01 (Windows Server 2022, High risk)
- LAPTOP-ADMIN-03 (Windows 11, Medium risk)
- WS-RADIOLOGY-07 (Windows 10, High risk)
- SERVER-BACKUP-02 (Ubuntu, High risk, Offline)

### 📋 12 Compliance Controls
- 3 HIPAA controls
- 3 GDPR controls
- 2 Cyber Essentials controls
- 2 CIS Controls
- 2 ISO 27001 controls

## Verify Seeding Worked

### Test with cURL

```bash
# Get alerts (replace <TOKEN> with your access token)
curl -H "Authorization: Bearer <TOKEN>" \
  -H "X-Org-Id: org_001" \
  https://cyber-guardian-ai-production-deb8.up.railway.app/api/alerts

# Get endpoints
curl -H "Authorization: Bearer <TOKEN>" \
  -H "X-Org-Id: org_001" \
  https://cyber-guardian-ai-production-deb8.up.railway.app/api/endpoints

# Get compliance controls
curl -H "Authorization: Bearer <TOKEN>" \
  -H "X-Org-Id: org_001" \
  https://cyber-guardian-ai-production-deb8.up.railway.app/api/compliance
```

### Test in Frontend

1. Start frontend: `npm run dev`
2. Register/Login with org_001
3. Go to Dashboard - should see 5 alerts
4. Go to Alerts page - should see all 5 alerts
5. Go to Endpoints page - should see 5 endpoints
6. Go to Compliance - should see controls for all frameworks

## Test User Setup

After seeding, create a test user:

```bash
curl -X POST https://cyber-guardian-ai-production-deb8.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@clinic.nhs",
    "password": "SecurePass123!",
    "full_name": "Admin User",
    "organisation_id": "org_001",
    "role": "admin"
  }'
```

Then login:
```bash
curl -X POST https://cyber-guardian-ai-production-deb8.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@clinic.nhs",
    "password": "SecurePass123!"
  }'
```

Save the `access_token` from the response to use in API calls.

## Troubleshooting

### "ModuleNotFoundError: No module named 'motor'"

Install dependencies:
```bash
cd backend
pip install motor pymongo python-dotenv
```

### "Connection refused" or "Authentication failed"

Check your MongoDB connection:
1. In Railway dashboard, check `MONGODB_URL` environment variable
2. Ensure MongoDB Atlas has Railway IPs whitelisted (0.0.0.0/0)
3. Verify database name matches `MONGODB_DB_NAME` in settings

### "Database already has data"

The script clears existing data for `org_001` before seeding. If you want to keep existing data, modify the script to skip the deletion step.

### Script runs but frontend still shows mock data

The frontend components need to be updated to fetch from API. See below.

## Updating Frontend to Use Live Data

The frontend is still importing from `mockData.ts`. You need to update each component:

### Example: Dashboard.tsx

**Current (Mock Data)**:
```typescript
import { mockAlerts, mockEndpoints } from "@/data/mockData";

const alerts = mockAlerts;
const endpoints = mockEndpoints;
```

**Updated (Live API)**:
```typescript
import { useQuery } from '@tanstack/react-query';
import { API_ENDPOINTS } from '@/lib/api';

const { data: alerts = [] } = useQuery({
  queryKey: ['alerts'],
  queryFn: async () => {
    const response = await fetch(API_ENDPOINTS.alerts, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'X-Org-Id': localStorage.getItem('org_id') || 'org_001'
      }
    });
    return response.json();
  }
});
```

## Re-seeding Data

To reset and re-seed:

```bash
# Option 1: Run the script again (it automatically clears org_001 data)
./seed-production-data.sh

# Option 2: Clear all data manually in MongoDB Atlas, then seed
```

## Adding Custom Data

Edit `backend/scripts/seed_database.py` to:
- Add more alerts
- Change endpoint configurations
- Modify compliance control statuses
- Adjust organization IDs

Then re-run the seeding script.

## Production Notes

- The script only seeds `org_001` by default
- Real production deployment should seed via CI/CD pipeline
- Consider using Faker library for more realistic fake data
- Add more organizations by modifying the script

## Next Steps

1. ✅ Run seeding script
2. ✅ Verify data in MongoDB Atlas
3. ✅ Create test user
4. ✅ Login to frontend
5. ⏭️ Update frontend components to fetch from API instead of mock data

Once seeded, your dashboard will have realistic data to work with!
