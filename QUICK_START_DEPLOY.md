# 🚀 Quick Deployment Guide - Railway + Netlify

**Follow these steps to deploy Cyber HealthGuard in 20 minutes**

---

## ✅ Pre-Flight Checklist

Before starting, make sure you have:
- [ ] GitHub account
- [ ] This repository pushed to GitHub
- [ ] Railway account (sign up: https://railway.app)
- [ ] Netlify account (sign up: https://netlify.com)

---

## 📦 PART 1: Deploy Backend to Railway (10 minutes)

### Step 1: Create Railway Project
1. Go to https://railway.app
2. Click **"Login"** → Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose **`cyber-guardian-ai`** repository

### Step 2: Add MongoDB Database
1. In Railway dashboard, click **"+ New"**
2. Select **"Database"** → **"Add MongoDB"**
3. Wait 30 seconds for MongoDB to deploy
4. Click MongoDB service → **"Connect"** tab → Copy connection URL

### Step 3: Configure Backend Service
1. Click your **backend service** (the GitHub repo one)
2. Go to **"Settings"** tab

**Set Root Directory:**
- Find **"Root Directory"**
- Enter: `backend`
- Click **"Update"**

**Set Start Command:**
- Find **"Start Command"**
- Enter: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Click **"Update"**

### Step 4: Add Environment Variables
1. Stay on your backend service
2. Go to **"Variables"** tab
3. Click **"+ New Variable"** and add these:

```
MONGODB_URL = [paste the MongoDB connection URL from Step 2]
MONGODB_DB_NAME = cyber_healthguard
ENVIRONMENT = production
LOG_LEVEL = info
```

**To get MongoDB URL:**
- Click MongoDB service → "Connect" tab → Copy the URL

### Step 5: Deploy Backend
1. Go to **"Deployments"** tab
2. Railway automatically deploys (2-3 minutes)
3. Watch for: `✓ Deployment live`

### Step 6: Get Your Backend URL
1. Go to **"Settings"** tab
2. Scroll to **"Domains"** section
3. Click **"Generate Domain"**
4. **COPY THIS URL** → Example: `https://cyber-healthguard-production-abcd1234.up.railway.app`

### Step 7: Test Backend
Open in browser:
```
https://YOUR-RAILWAY-URL/health
```

Should return:
```json
{"status": "healthy", "services": {...}}
```

✅ **Backend Done!** Save your Railway URL for the next part.

---

## 🎨 PART 2: Deploy Frontend to Netlify (10 minutes)

### Step 8: Create Netlify Site
1. Go to https://app.netlify.com
2. Click **"Sign up"** → Sign in with GitHub
3. Click **"Add new site"** → **"Import an existing project"**
4. Select **"GitHub"**
5. Choose **`cyber-guardian-ai`** repository
6. Select branch: **`claude/log-ingestion-api-011P3kSEzZE5J59zjndie52R`** (or `main` if merged)

### Step 9: Configure Build Settings

Netlify auto-detects from `netlify.toml`. Verify these settings:

```
Branch to deploy: main (or your current branch)
Base directory: (leave empty)
Build command: npm run build
Publish directory: dist
```

Click **"Show advanced"** if needed.

### Step 10: Set Environment Variables

**BEFORE clicking Deploy**, add environment variables:

1. Click **"Add environment variables"** (or scroll down)
2. Add these variables:

| Variable Name | Value |
|--------------|--------|
| `VITE_API_URL` | **YOUR RAILWAY URL from Step 6** |
| `VITE_ENV` | `production` |
| `VITE_USE_MOCK_DATA` | `false` |

**Example:**
```
VITE_API_URL = https://cyber-healthguard-production-abcd1234.up.railway.app
VITE_ENV = production
VITE_USE_MOCK_DATA = false
```

### Step 11: Deploy Frontend
1. Click **"Deploy [site-name]"**
2. Wait 3-4 minutes for build
3. Watch for: `✓ Site is live`

### Step 12: Get Your Frontend URL
After deployment:
- Netlify shows your URL: `https://random-name-123456.netlify.app`
- **COPY THIS URL** for the next step

### Step 13: Test Frontend
1. Open your Netlify URL in browser
2. Site should load
3. Press F12 → Console tab
4. Look for: `🔧 API Configuration`

---

## 🔗 PART 3: Connect Frontend & Backend (5 minutes)

### Step 14: Update CORS in Backend

**Option A: Quick Fix (via Railway Dashboard)**
1. Go to Railway → Backend service → **"Variables"**
2. Click **"+ New Variable"**
3. Add:
   ```
   CORS_ORIGINS = https://YOUR-NETLIFY-URL.netlify.app
   ```
4. Save (Railway auto-redeploys in ~2 minutes)

**Option B: Code Fix (Permanent)**
1. Open `backend/app/main.py` locally
2. Find the `CORSMiddleware` section (around line 20-30)
3. Update `allow_origins`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:8080",  # Local dev
           "https://YOUR-NETLIFY-URL.netlify.app",  # Your Netlify URL
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
4. Save, commit, and push:
   ```bash
   git add backend/app/main.py
   git commit -m "Add Netlify URL to CORS origins"
   git push
   ```
5. Railway auto-deploys in ~2 minutes

---

## ✅ PART 4: Final Testing (5 minutes)

### Step 15: Test Full Stack

1. **Open your Netlify site** in browser

2. **Check browser console** (F12):
   - Look for: `🔧 API Configuration`
   - Should show your Railway URL
   - Should NOT show CORS errors

3. **Test API connection** in console:
   ```javascript
   fetch('https://YOUR-RAILWAY-URL/health')
     .then(r => r.json())
     .then(console.log)
   ```
   Should return: `{status: "healthy", ...}`

4. **Navigate the app:**
   - [ ] Dashboard loads
   - [ ] Alerts page works
   - [ ] Endpoints page works
   - [ ] Compliance page works
   - [ ] Theme toggle works

5. **Check Network tab** (F12 → Network):
   - API requests should return **200 OK**
   - No CORS errors

### Step 16: If You See CORS Errors

If you see: `Access to fetch... has been blocked by CORS policy`

**Quick Fix:**
1. Go to Railway → Backend service → Variables
2. Add: `CORS_ORIGINS = *` (temporary - allows all)
3. Wait 2 minutes for redeploy
4. Refresh Netlify site
5. Later, change to your specific Netlify URL

---

## 🎉 SUCCESS CHECKLIST

Your deployment is complete when:

- [ ] Railway backend shows: `✓ Deployment live`
- [ ] Railway health endpoint returns: `{"status": "healthy"}`
- [ ] Netlify frontend shows: `✓ Site is live`
- [ ] Netlify site loads without errors
- [ ] Browser console shows NO CORS errors
- [ ] Dashboard displays correctly
- [ ] API calls work (check Network tab)

---

## 📝 Save These URLs

Write down your deployment URLs:

```
Backend (Railway): https://_____________________________.up.railway.app
Frontend (Netlify): https://_____________________________.netlify.app
```

---

## 🚨 Common Issues & Quick Fixes

### Issue: "Failed to fetch" on Netlify
**Fix:**
1. Check CORS settings in Railway
2. Add your Netlify URL to `CORS_ORIGINS` variable

### Issue: Railway deployment fails
**Fix:**
1. Check Root Directory is set to `backend`
2. Check Start Command is correct
3. View logs: Railway → Backend → Deployments → View logs

### Issue: Netlify build fails
**Fix:**
1. Check branch has `netlify.toml` file
2. Verify `package.json` exists
3. View logs: Netlify → Deploys → Click deploy → View logs

### Issue: Environment variables not working
**Fix:**
1. Ensure variables start with `VITE_` (frontend only)
2. Re-deploy Netlify: Deploys → Trigger deploy → Deploy site
3. Clear browser cache

---

## 🔄 Future Deployments (Automatic!)

After this initial setup, deployments are automatic:

```bash
# Make changes to your code
git add .
git commit -m "Your changes"
git push
```

**What happens:**
- Railway detects push → rebuilds backend → deploys (~2 min)
- Netlify detects push → rebuilds frontend → deploys (~3 min)

---

## 📚 Need More Details?

See the complete guides:
- **Full details:** [deployment/FULL_STACK_DEPLOYMENT.md](FULL_STACK_DEPLOYMENT.md)
- **Netlify only:** [deployment/NETLIFY.md](NETLIFY.md)
- **Railway only:** [deployment/RAILWAY.md](RAILWAY.md)

---

## 💰 Cost

- **Railway:** $5 free credit/month (enough for this app)
- **Netlify:** 100GB bandwidth/month free
- **Total:** **FREE** for small-medium traffic

---

## 🆘 Need Help?

1. Check Railway logs: Backend service → Deployments → View logs
2. Check Netlify logs: Deploys → Click deploy → View logs
3. Check browser console (F12) for frontend errors
4. Review troubleshooting in [FULL_STACK_DEPLOYMENT.md](FULL_STACK_DEPLOYMENT.md)

---

## 🎯 Next Steps After Deployment

1. [ ] Set up custom domain (optional)
2. [ ] Enable monitoring/analytics
3. [ ] Configure database backups
4. [ ] Set up alerts for downtime
5. [ ] Add SSL certificate (automatic on both platforms)

---

**You're done! Your Cyber HealthGuard platform is now live! 🚀**

Backend API: Railway
Frontend App: Netlify
Database: MongoDB on Railway

All automatically deployed on every git push!
