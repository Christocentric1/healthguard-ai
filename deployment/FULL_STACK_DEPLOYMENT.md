# Complete Deployment Guide: Railway + Netlify

**Deploy Cyber HealthGuard AI with Railway backend and Netlify frontend**

This guide walks you through deploying the complete stack:
- **Backend**: FastAPI + MongoDB on Railway
- **Frontend**: React app on Netlify

**Total Time**: ~20-30 minutes
**Cost**: Free tier for both platforms

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Part 1: Deploy Backend to Railway](#part-1-deploy-backend-to-railway)
3. [Part 2: Deploy Frontend to Netlify](#part-2-deploy-frontend-to-netlify)
4. [Part 3: Connect Frontend to Backend](#part-3-connect-frontend-to-backend)
5. [Part 4: Testing](#part-4-testing)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- ✅ [GitHub Account](https://github.com) (free)
- ✅ [Railway Account](https://railway.app) (free tier: $5 credit/month)
- ✅ [Netlify Account](https://netlify.com) (free tier: 100GB bandwidth/month)

### Required Tools
- ✅ Git installed locally
- ✅ Code pushed to GitHub repository

### Check Your Repository
```bash
# Verify you're on the correct branch
git status

# Push latest changes
git push origin your-branch-name
```

---

## Part 1: Deploy Backend to Railway

### Step 1.1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"**
3. Sign up with GitHub (recommended for easy integration)
4. Verify your account via email

### Step 1.2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. If first time:
   - Click **"Configure GitHub App"**
   - Select your `cyber-guardian-ai` repository
   - Click **"Install & Authorize"**
4. Select **`cyber-guardian-ai`** from the list
5. Railway will detect the repository

### Step 1.3: Add MongoDB Database

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"** → **"Add MongoDB"**
3. Railway automatically creates a MongoDB instance
4. Wait for deployment to complete (~30 seconds)
5. MongoDB connection string is automatically generated

### Step 1.4: Configure Backend Service

1. Click on your **backend service** (the one connected to GitHub repo)
2. Go to **"Settings"** tab

#### Set Root Directory
- Find **"Root Directory"**
- Set to: `backend`
- Click **"Update"**

#### Set Start Command
- Find **"Start Command"**
- Set to: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Click **"Update"**

### Step 1.5: Configure Environment Variables

1. Go to **"Variables"** tab
2. Click **"+ New Variable"**
3. Add the following variables:

#### MongoDB Connection

Click on your **MongoDB service** → **"Connect"** → Copy the connection string

| Variable Name | Value | Notes |
|--------------|--------|-------|
| `MONGODB_URL` | `mongodb://mongo:PASSWORD@monorail.proxy.rlwy.net:PORT` | Copy from MongoDB service |
| `MONGODB_DB_NAME` | `cyber_healthguard` | Database name |

#### Application Settings

| Variable Name | Value | Notes |
|--------------|--------|-------|
| `ENVIRONMENT` | `production` | Environment mode |
| `LOG_LEVEL` | `info` | Logging level |

#### Security (Optional but Recommended)

| Variable Name | Value | Notes |
|--------------|--------|-------|
| `SECRET_KEY` | Generate with: `openssl rand -hex 32` | For JWT tokens |
| `CORS_ORIGINS` | `https://*.netlify.app,https://your-custom-domain.com` | We'll update this in Part 3 |

**To get MongoDB URL automatically:**
1. Click **"MongoDB"** service
2. Go to **"Connect"** tab
3. Copy the **"MongoDB Connection URL"**
4. Paste into `MONGODB_URL` variable

### Step 1.6: Deploy Backend

1. Go to **"Deployments"** tab
2. Railway automatically deploys on git push
3. Click latest deployment to view logs
4. Wait for deployment to complete (~2-3 minutes)

**Look for these success messages:**
```
✓ Build completed
✓ Deployment live
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:PORT
```

### Step 1.7: Get Backend URL

1. Go to **"Settings"** tab
2. Find **"Domains"** section
3. Click **"Generate Domain"**
4. Railway creates a URL like: `https://cyber-healthguard-production-XXXX.up.railway.app`
5. **SAVE THIS URL** - you'll need it for Netlify

### Step 1.8: Test Backend

Open your browser and test these endpoints:

**Health Check:**
```
https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "log_ingestion": "operational",
    "anomaly_detection": "operational",
    "alert_management": "operational",
    "risk_assessment": "operational",
    "compliance": "operational"
  },
  "timestamp": "2025-11-20T..."
}
```

**API Documentation:**
```
https://your-app.railway.app/docs
```

Should show FastAPI Swagger UI.

✅ **Backend deployment complete!** Move to Part 2.

---

## Part 2: Deploy Frontend to Netlify

### Step 2.1: Create Netlify Account

1. Go to [netlify.com](https://netlify.com)
2. Click **"Sign up"**
3. Sign up with GitHub (recommended)
4. Authorize Netlify to access your GitHub repositories

### Step 2.2: Import Repository

1. Click **"Add new site"** → **"Import an existing project"**
2. Select **"GitHub"**
3. If first time:
   - Click **"Configure the Netlify app on GitHub"**
   - Select your `cyber-guardian-ai` repository
   - Click **"Install"**
4. Select **`cyber-guardian-ai`** from the list

### Step 2.3: Configure Build Settings

Netlify should auto-detect settings from `netlify.toml`, but verify:

| Setting | Value |
|---------|-------|
| **Branch to deploy** | `main` (or your production branch) |
| **Base directory** | (leave empty) |
| **Build command** | `npm run build` |
| **Publish directory** | `dist` |

Click **"Show advanced"** to verify:
- Node version: `20` (set in netlify.toml)

### Step 2.4: Set Environment Variables

**BEFORE deploying**, add environment variables:

1. Click **"Add environment variables"** (or skip and add after)
2. Add these variables:

| Variable Name | Value | Example |
|--------------|--------|---------|
| `VITE_API_URL` | Your Railway backend URL | `https://cyber-healthguard-production-XXXX.up.railway.app` |
| `VITE_ENV` | `production` | `production` |
| `VITE_USE_MOCK_DATA` | `false` | `false` |

**Important**: Use your Railway URL from Step 1.7 for `VITE_API_URL`

### Step 2.5: Deploy Frontend

1. Click **"Deploy [your-site-name]"**
2. Netlify will:
   - Clone your repository
   - Install dependencies (`npm install`)
   - Build React app (`npm run build`)
   - Deploy to global CDN
3. Wait for deployment (~2-4 minutes)

**Watch the deploy logs for:**
```
✓ Installing dependencies
✓ Building frontend
✓ Build succeeded
✓ Site is live
```

### Step 2.6: Get Frontend URL

1. After deployment completes, Netlify shows your site URL
2. Default format: `https://random-name-123456.netlify.app`
3. **SAVE THIS URL** - you'll need it for CORS

### Step 2.7: Custom Domain (Optional)

To use a custom domain like `app.cyberwavesecurity.org`:

1. Go to **"Domain settings"**
2. Click **"Add custom domain"**
3. Enter your domain: `app.cyberwavesecurity.org`
4. Click **"Verify"**

#### Add DNS Records at Your Domain Provider

Add this CNAME record:
```
Type: CNAME
Name: app
Value: your-site-name.netlify.app
TTL: 3600
```

5. Wait for DNS propagation (~5-60 minutes)
6. Netlify automatically provisions SSL certificate (Let's Encrypt)

✅ **Frontend deployed!** Now connect them together.

---

## Part 3: Connect Frontend to Backend

### Step 3.1: Update Backend CORS Settings

Your backend needs to allow requests from your Netlify domain.

#### Option A: Via Railway Dashboard (Temporary)

1. Go to Railway dashboard
2. Click **Backend service** → **"Variables"**
3. Update `CORS_ORIGINS` variable:
   ```
   https://your-site.netlify.app,https://app.cyberwavesecurity.org
   ```
4. Save (Railway auto-redeploys)

#### Option B: Update Code (Permanent - Recommended)

1. Edit `backend/app/main.py`:

```python
# Find the CORS middleware section
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # Local development
        "https://your-site.netlify.app",  # Your Netlify URL
        "https://app.cyberwavesecurity.org",  # Your custom domain (if any)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. Commit and push:
```bash
git add backend/app/main.py
git commit -m "Update CORS origins for Netlify deployment"
git push origin your-branch-name
```

3. Railway automatically redeploys (~2 minutes)

### Step 3.2: Update Frontend Environment Variables (If Changed)

If you got a custom domain or changed URLs:

1. Go to Netlify dashboard
2. **Site settings** → **Environment variables**
3. Update `VITE_API_URL` if Railway URL changed
4. Click **"Save"**
5. Go to **"Deploys"** → **"Trigger deploy"** → **"Deploy site"**

### Step 3.3: Verify Connection

1. Open your Netlify site: `https://your-site.netlify.app`
2. Open browser console (F12)
3. Look for API configuration logs:
   ```
   🔧 API Configuration:
     - Environment: production
     - API Base URL: https://your-app.railway.app
     - Use Mock Data: false
   ```

4. Check for API health:
   ```javascript
   // Run in browser console
   fetch('https://your-app.railway.app/health')
     .then(r => r.json())
     .then(console.log)
   ```

✅ **Full stack connected!** Time to test.

---

## Part 4: Testing

### 4.1 Frontend Testing

Visit your Netlify URL and verify:

- [ ] **Site loads** without errors
- [ ] **Dark/light theme toggle** works
- [ ] **Navigation** works (Dashboard, Alerts, Endpoints, Compliance, Settings)
- [ ] **No CORS errors** in console (F12)
- [ ] **API connection** established (check console logs)

### 4.2 Backend Testing

Test these API endpoints:

#### Health Check
```bash
curl https://your-app.railway.app/health
```

Expected: `{"status": "healthy", ...}`

#### API Documentation
Open: `https://your-app.railway.app/docs`

Should show interactive API docs (Swagger UI)

#### Database Connection
```bash
curl https://your-app.railway.app/api/alerts
```

Expected: JSON array of alerts (may be empty)

### 4.3 Full Stack Testing

1. **Login** (if authentication is enabled)
2. **Navigate to Dashboard** - check if metrics load
3. **View Alerts** - check if data displays
4. **Check Endpoints** - verify monitoring data
5. **Test Compliance** - ensure reports are accessible
6. **Update Settings** - verify changes are saved

### 4.4 Browser Console Check

Open Developer Tools (F12) and verify:

✅ **No errors** in Console tab
✅ **API requests** returning 200 OK status
✅ **No CORS errors**
✅ **Network tab** shows successful API calls

---

## Part 5: Continuous Deployment

### Automatic Deployments

Both platforms auto-deploy on git push:

```bash
# Make changes to your code
git add .
git commit -m "Add new feature"
git push origin main
```

**What happens:**
1. **Railway** detects push → rebuilds backend → redeploys (~2 min)
2. **Netlify** detects push → rebuilds frontend → redeploys (~3 min)

### Branch Previews (Netlify)

1. Create feature branch:
   ```bash
   git checkout -b feature/new-dashboard
   ```

2. Make changes and push:
   ```bash
   git push origin feature/new-dashboard
   ```

3. Create Pull Request on GitHub

4. Netlify automatically creates preview:
   `https://deploy-preview-123--your-site.netlify.app`

### Monitoring Deployments

#### Railway
- Dashboard → **Deployments** tab
- View logs in real-time
- Rollback to previous deployment if needed

#### Netlify
- Dashboard → **Deploys** tab
- View build logs
- Rollback with one click (Deploys → click deploy → "Publish deploy")

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         USERS                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    NETLIFY CDN                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Frontend (React + TypeScript)                        │   │
│  │  - Dashboard, Alerts, Compliance UI                   │   │
│  │  - Dark mode, responsive design                       │   │
│  │  - Static assets cached globally                      │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTPS API Requests
                     │ (CORS enabled)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   RAILWAY PLATFORM                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Backend API (FastAPI + Python)                       │   │
│  │  - REST API endpoints                                 │   │
│  │  - JWT authentication                                 │   │
│  │  - Business logic                                     │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                         │
│                     │ MongoDB Protocol                        │
│                     ▼                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  MongoDB Database                                     │   │
│  │  - Alerts collection                                  │   │
│  │  - Logs collection                                    │   │
│  │  - Compliance data                                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Frontend Issues

#### Issue: "Failed to fetch" or network errors

**Cause**: Backend URL incorrect or CORS not configured

**Fix**:
1. Check `VITE_API_URL` in Netlify environment variables
2. Verify Railway backend URL is correct
3. Check CORS settings in `backend/app/main.py`
4. Redeploy Netlify after changing env vars

#### Issue: 404 on page refresh

**Cause**: SPA routing not configured (shouldn't happen with netlify.toml)

**Fix**:
1. Verify `netlify.toml` exists in repository root
2. Check redirect rules are present:
   ```toml
   [[redirects]]
     from = "/*"
     to = "/index.html"
     status = 200
   ```
3. Redeploy Netlify

#### Issue: Environment variables not working

**Cause**: Variables not prefixed with `VITE_` or not set in Netlify

**Fix**:
1. Ensure all variables start with `VITE_`
2. Set in Netlify dashboard: **Site settings** → **Environment variables**
3. Trigger redeploy: **Deploys** → **Trigger deploy**

#### Issue: Build fails on Netlify

**Cause**: Missing dependencies or wrong Node version

**Fix**:
1. Check build logs in Netlify dashboard
2. Verify `netlify.toml` has correct Node version (20)
3. Ensure all dependencies in `package.json`
4. Test build locally:
   ```bash
   npm install
   npm run build
   ```

### Backend Issues

#### Issue: Railway deployment fails

**Cause**: Wrong directory or missing requirements

**Fix**:
1. Verify **Root Directory** is set to `backend`
2. Check `backend/requirements.txt` exists
3. View deployment logs for specific errors
4. Verify Python version (3.11 recommended)

#### Issue: Database connection failed

**Cause**: MongoDB URL incorrect or MongoDB service down

**Fix**:
1. Check MongoDB service status in Railway
2. Verify `MONGODB_URL` variable is correct
3. Click MongoDB service → **Connect** → copy fresh URL
4. Update `MONGODB_URL` and redeploy

#### Issue: CORS errors in browser

**Cause**: Netlify URL not in allowed origins

**Fix**:
1. Update `backend/app/main.py` CORS settings
2. Add your Netlify URL to `allow_origins` list
3. Commit and push changes
4. Wait for Railway to redeploy

#### Issue: Health endpoint returns 500 error

**Cause**: Database connection issue or service error

**Fix**:
1. Check Railway logs: Click service → **Deployments** → **View logs**
2. Look for error messages
3. Verify MongoDB is running
4. Check environment variables are set correctly

### CORS Troubleshooting

If you see this error in browser console:
```
Access to fetch at 'https://your-app.railway.app/api/alerts' from origin
'https://your-site.netlify.app' has been blocked by CORS policy
```

**Quick Fix**:
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporary - allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then restrict to specific domains in production:
```python
allow_origins=[
    "https://your-site.netlify.app",
    "https://app.cyberwavesecurity.org",
]
```

### Performance Issues

#### Frontend loading slowly

**Fix**:
- Enable Netlify asset optimization (automatic)
- Check bundle size: `npm run build` shows chunk sizes
- Optimize images and assets
- Use lazy loading for routes

#### Backend API slow

**Fix**:
- Check Railway logs for slow queries
- Optimize MongoDB queries
- Add database indexes
- Upgrade Railway plan for more resources

---

## Deployment Checklist

Use this checklist to ensure everything is configured:

### Pre-Deployment
- [ ] Code pushed to GitHub
- [ ] All tests passing locally
- [ ] Environment variables documented

### Railway (Backend)
- [ ] Railway account created
- [ ] MongoDB service added
- [ ] Root directory set to `backend`
- [ ] Start command configured
- [ ] `MONGODB_URL` set
- [ ] `MONGODB_DB_NAME` set
- [ ] Backend deployed successfully
- [ ] Health endpoint returns 200 OK
- [ ] API docs accessible at `/docs`
- [ ] Custom domain configured (optional)

### Netlify (Frontend)
- [ ] Netlify account created
- [ ] Repository connected
- [ ] Build settings verified
- [ ] `VITE_API_URL` set (Railway URL)
- [ ] `VITE_ENV` set to `production`
- [ ] `VITE_USE_MOCK_DATA` set to `false`
- [ ] Frontend deployed successfully
- [ ] Site loads without errors
- [ ] Custom domain configured (optional)

### Integration
- [ ] CORS configured with Netlify URL
- [ ] API connection verified (no CORS errors)
- [ ] Full stack tested (frontend ↔ backend)
- [ ] Authentication working (if enabled)
- [ ] Data displays correctly

### Post-Deployment
- [ ] Monitor Railway logs for errors
- [ ] Monitor Netlify analytics
- [ ] Set up uptime monitoring (optional)
- [ ] Configure alerts (optional)
- [ ] Document custom domains
- [ ] Share URLs with team

---

## Cost Breakdown

### Free Tier Limits

| Service | Free Tier | Overage Cost |
|---------|-----------|--------------|
| **Railway** | $5 credit/month | $0.000463/GB-hour RAM, $0.000231/vCPU-hour |
| **Netlify** | 100GB bandwidth, 300 build min/month | $0.20/GB bandwidth |
| **Total** | **FREE** (within limits) | Pay-as-you-go |

### Estimated Monthly Usage

For a small to medium traffic site:
- **Railway**: ~$2-5/month (within free credit)
- **Netlify**: FREE (unless >100GB traffic)

**Total: FREE to $5/month**

---

## Next Steps

### After Successful Deployment

1. **Set up monitoring**:
   - Enable Netlify Analytics
   - Use Railway's built-in metrics
   - Consider: UptimeRobot, Sentry, or LogRocket

2. **Configure CI/CD**:
   - Already automatic with git push!
   - Add GitHub Actions for testing (optional)

3. **Security hardening**:
   - Enable rate limiting in backend
   - Add JWT authentication
   - Set up secrets rotation
   - Configure Content Security Policy

4. **Performance optimization**:
   - Enable Netlify's image optimization (Pro plan)
   - Add Redis caching to Railway (optional)
   - Optimize database queries

5. **Backup strategy**:
   - Railway: MongoDB backups (Pro plan) or use MongoDB Atlas
   - Export important data regularly

6. **Custom domains** (if not done):
   - Set up `app.yourdomain.com` (frontend)
   - Set up `api.yourdomain.com` (backend)

---

## Support & Resources

### Documentation
- **Netlify Docs**: https://docs.netlify.com
- **Railway Docs**: https://docs.railway.app
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev

### Community Support
- **Netlify Community**: https://answers.netlify.com
- **Railway Discord**: https://discord.gg/railway
- **Project Issues**: GitHub Issues

### Getting Help

If you encounter issues:
1. Check the **Troubleshooting** section above
2. Review deployment logs (Railway & Netlify dashboards)
3. Search community forums
4. Open a GitHub issue with:
   - Error messages
   - Deployment logs
   - Steps to reproduce

---

## Success! 🎉

Your Cyber HealthGuard platform is now live:

- **Frontend**: `https://your-site.netlify.app` (globally distributed)
- **Backend**: `https://your-app.railway.app` (scalable API)
- **Database**: MongoDB on Railway (persistent storage)

**Architecture Benefits**:
- ⚡ Lightning-fast frontend (Netlify CDN)
- 🔒 Automatic HTTPS on both platforms
- 🚀 Auto-deploys on git push
- 💰 Free tier for both services
- 📈 Scales automatically with traffic
- 🌍 Global distribution

**Your healthcare security monitoring platform is ready to protect patient data!**

---

**Questions?** Refer to individual guides:
- [Frontend: deployment/NETLIFY.md](NETLIFY.md)
- [Backend: deployment/RAILWAY.md](RAILWAY.md)
- [Homelab: deployment/README.md](README.md)
