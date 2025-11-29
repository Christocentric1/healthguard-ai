# Live API Testing Guide

## Current Status

✅ **Configuration Updated**:
- `.env.local` now points to Railway: `https://cyber-guardian-ai-production-deb8.up.railway.app`
- Mock data disabled: `VITE_USE_MOCK_DATA=false`
- Environment set to production

⚠️ **Issue Detected**: Railway backend returning HTTP 403 errors

## Problem: Railway 403 Errors

All endpoints are returning `403 Access denied`:
```
GET /health         → 403
GET /              → 403
GET /api/auth/*    → 403
GET /api/alerts    → 403
```

## Possible Causes

### 1. Railway Service Not Public
Your Railway service might have authentication enabled or not be publicly accessible.

**Fix**:
1. Go to Railway dashboard: https://railway.app
2. Select your `cyber-guardian-ai-production` service
3. Go to **Settings** → **Networking**
4. Ensure **"Generate Domain"** is enabled
5. Check if there's any **"Service Authentication"** or access control enabled
6. If there's a **"Private Network"** toggle, make sure it's OFF for public access

### 2. Environment Variable Issues
The backend might not be starting correctly.

**Fix**:
1. In Railway dashboard, go to your service
2. Click **Deployments** → View latest deployment logs
3. Look for errors in the startup logs
4. Check that `PORT` environment variable is set correctly

### 3. Incorrect URL
The domain might have changed or be incorrect.

**Fix**:
1. In Railway, go to your service **Settings**
2. Copy the exact **Public Domain** URL
3. Update `.env.local` with the correct URL
4. Restart your frontend dev server

## Testing Steps

### Step 1: Verify Railway Deployment

```bash
# Check Railway service status
railway status  # If you have Railway CLI

# Or check in browser:
# 1. Go to https://railway.app
# 2. Open your project
# 3. Check deployment status
```

### Step 2: Check Backend Logs

In Railway dashboard:
1. Go to your backend service
2. Click **Deployments**
3. Select latest deployment
4. View **Deployment Logs**

Look for:
- ✅ "Started server process"
- ✅ "Application startup complete"
- ✅ "Uvicorn running on http://0.0.0.0:8000"
- ❌ Any error messages

### Step 3: Test from Railway Dashboard

Railway provides a way to test your service:
1. In Railway dashboard, click **Connect**
2. You should see a URL to test your service
3. Try accessing: `https://your-service.railway.app/health`

### Step 4: Test Authentication Flow

Once the backend is accessible, test the full flow:

```bash
# 1. Test health check
curl https://cyber-guardian-ai-production-deb8.up.railway.app/health

# 2. Register a user
curl -X POST https://cyber-guardian-ai-production-deb8.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User",
    "organisation_id": "org_001",
    "role": "analyst"
  }'

# 3. Login
curl -X POST https://cyber-guardian-ai-production-deb8.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'

# 4. Use the access_token from login response to test protected endpoints
curl -H "Authorization: Bearer <your-token>" \
  -H "X-Org-Id: org_001" \
  https://cyber-guardian-ai-production-deb8.up.railway.app/api/alerts
```

## Frontend Testing

Once backend is accessible:

### Option 1: Local Development

```bash
# Start frontend dev server
npm run dev

# Visit http://localhost:8080
# Try to sign up / login
# Open browser dev tools (F12) to see API calls
```

### Option 2: Netlify Deployment

1. Update Netlify environment variables:
   ```
   VITE_API_URL=https://cyber-guardian-ai-production-deb8.up.railway.app
   VITE_USE_MOCK_DATA=false
   VITE_ENV=production
   ```

2. Trigger a new deployment

3. Test at your Netlify URL

## Debugging Tips

### Check CORS Configuration

The backend has CORS enabled for all origins:
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Check MongoDB Connection

Verify MongoDB is connected in Railway logs:
```
✅ Connected to MongoDB
```

If not connected, check:
- `MONGODB_URL` environment variable in Railway
- MongoDB Atlas IP whitelist (should allow 0.0.0.0/0 for Railway)

### Test Script

Run the included test script:
```bash
./test-live-endpoints.sh
```

This will test all major endpoints and show their status.

## Expected Responses

When working correctly, you should see:

**Health Check** (`GET /health`):
```json
{
  "status": "healthy",
  "database": "connected",
  "services": {
    "log_ingestion": "operational",
    "anomaly_detection": "operational",
    "alert_management": "operational",
    "risk_assessment": "operational",
    "compliance": "operational"
  }
}
```

**Root** (`GET /`):
```json
{
  "name": "Cyber HealthGuard AI",
  "version": "1.0.0",
  "status": "healthy",
  "message": "Cyber HealthGuard AI API is running"
}
```

## Next Steps

1. **Fix Railway 403 Issue**:
   - Check Railway service settings
   - Ensure public access is enabled
   - Verify deployment is successful

2. **Test Authentication**:
   - Sign up a test user
   - Verify login works
   - Test protected endpoints with token

3. **Verify Data Flow**:
   - Check that alerts are fetched from API
   - Verify compliance data loads
   - Test endpoint monitoring

4. **Monitor Performance**:
   - Check API response times
   - Verify real-time updates
   - Test under load

## Troubleshooting Checklist

- [ ] Railway service is deployed and running
- [ ] Public domain is configured and accessible
- [ ] MongoDB is connected
- [ ] CORS is properly configured
- [ ] Environment variables are set correctly
- [ ] Frontend .env.local has correct API URL
- [ ] Mock data is disabled
- [ ] Browser dev tools show correct API calls
- [ ] Authentication flow works end-to-end
- [ ] Protected endpoints return data with valid token

## Contact

If you continue to see 403 errors:
1. Check Railway service logs for errors
2. Verify the service is publicly accessible
3. Try redeploying the backend service
4. Check Railway service settings for any access restrictions

The backend code is correct and should work once the Railway configuration is fixed.
