# 🚀 Deployment Guide - Cyber Guardian AI

Railway is currently down, so here are quick alternatives to get your backend deployed.

---

## ⚡ Option 1: Render (FASTEST - 5 minutes)

### Why Render?
- ✅ Free tier: 750 hours/month (1 service 24/7)
- ✅ Auto-deploy from GitHub
- ✅ Very similar to Railway
- ⚠️ Free tier sleeps after 15 min inactivity (30s cold start)

### Deploy Steps:

1. **Sign up**: https://render.com (use GitHub login)

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repo: `Christocentric1/cyber-guardian-ai`
   - Branch: `main` (or your current branch)

3. **Configure**:
   ```
   Name: cyber-guardian-backend
   Region: Oregon (or nearest)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   Plan: Free
   ```

4. **Add Environment Variables** (in Render dashboard):
   ```
   MONGO_URL=mongodb+srv://<your-atlas-connection-string>
   MONGODB_DB_NAME=cyber_healthguard
   SECRET_KEY=<generate-random-key>
   DEBUG=false
   ```

5. **Deploy**: Click "Create Web Service" - deploys automatically!

6. **Get URL**: Your backend will be at `https://cyber-guardian-backend.onrender.com`

7. **Update Frontend**: Update your Netlify frontend API URL to point to Render

---

## 🌍 Option 2: Fly.io (BEST FREE TIER - No Sleep!)

### Why Fly.io?
- ✅ No cold starts on free tier
- ✅ Always-on (doesn't sleep)
- ✅ 3 VMs with 256MB RAM free
- ✅ Global edge deployment

### Deploy Steps:

1. **Install flyctl** (Windows PowerShell):
   ```powershell
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Sign up & Login**:
   ```powershell
   fly auth signup
   # or
   fly auth login
   ```

3. **Deploy** (from backend directory):
   ```powershell
   cd C:\Users\Hertz-Terotech\Documents\cyber-guardian-ai\backend
   fly launch
   ```

4. **Configure when prompted**:
   - App name: cyber-guardian-backend
   - Region: Choose nearest
   - PostgreSQL: No
   - Redis: No
   - Deploy: Yes

5. **Set Environment Variables**:
   ```powershell
   fly secrets set MONGO_URL="mongodb+srv://<your-connection-string>"
   fly secrets set SECRET_KEY="<random-key>"
   fly secrets set MONGODB_DB_NAME="cyber_healthguard"
   ```

6. **Deploy**:
   ```powershell
   fly deploy
   ```

Your app will be at: `https://cyber-guardian-backend.fly.dev`

---

## ☁️ Option 3: Google Cloud Run (Best for Scaling + $300 Free Credits)

### Why Cloud Run?
- ✅ $300 free credits (90 days)
- ✅ Serverless (pay only when running)
- ✅ 2M requests/month free tier
- ✅ Auto-scales

### Deploy Steps:

1. **Install Google Cloud CLI**: https://cloud.google.com/sdk/docs/install

2. **Login & Create Project**:
   ```bash
   gcloud auth login
   gcloud projects create cyber-guardian-ai
   gcloud config set project cyber-guardian-ai
   ```

3. **Enable Cloud Run**:
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

4. **Deploy from backend directory**:
   ```bash
   cd backend
   gcloud run deploy cyber-guardian-backend \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars MONGO_URL="<your-connection>",MONGODB_DB_NAME="cyber_healthguard"
   ```

Your app will be at: `https://cyber-guardian-backend-<hash>.run.app`

---

## 🔧 After Deployment - Update Frontend

Once your backend is deployed, update the Netlify frontend:

1. Go to Netlify dashboard
2. Site settings → Environment variables
3. Update `VITE_API_URL` to your new backend URL:
   - Render: `https://cyber-guardian-backend.onrender.com`
   - Fly.io: `https://cyber-guardian-backend.fly.dev`
   - Cloud Run: `https://cyber-guardian-backend-<hash>.run.app`

4. Trigger new deployment

---

## 📊 Comparison

| Platform | Setup Time | Free Tier | Cold Starts | Always On |
|----------|------------|-----------|-------------|-----------|
| Render | 5 min | 750h/month | Yes (30s) | No |
| Fly.io | 10 min | Always | No | Yes ✅ |
| Cloud Run | 15 min | 2M req/mo | Yes (2s) | No |

**Recommendation**:
- **Quick start**: Render
- **Best free tier**: Fly.io
- **Long-term**: Cloud Run (with $300 credits)

---

## 🆘 Need Help?

If you run into issues:
1. Check logs in the platform dashboard
2. Verify MongoDB connection string
3. Ensure SECRET_KEY is set
4. Check CORS settings match frontend URL

---

## 🎯 My Recommendation: Start with Render

It's the fastest to set up (literally 5 minutes), and most similar to Railway. You can always migrate to Fly.io or Cloud Run later if needed.
