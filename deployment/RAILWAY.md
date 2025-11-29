# Cyber HealthGuard AI - Railway Deployment Guide

Complete guide for deploying to Railway.app (free tier).

## 🚂 Why Railway?

- ✅ **Free tier** ($5 credit/month)
- ✅ **Automatic SSL** certificates
- ✅ **GitHub integration** (auto-deploy on push)
- ✅ **MongoDB included** (easy setup)
- ✅ **Custom domains** supported
- ✅ **Zero configuration** needed

---

## 📋 Step-by-Step Deployment

### **Step 1: Create Railway Account**

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Sign up with **GitHub** (recommended)
4. Authorize Railway to access your repositories

⏱️ **Time:** 2 minutes

---

### **Step 2: Deploy from GitHub**

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Search for: `cyber-guardian-ai`
4. Click your repository to select it
5. Railway will automatically:
   - ✅ Detect the Dockerfile
   - ✅ Build your application
   - ✅ Deploy it
   - ✅ Give you a public URL

**Wait 2-3 minutes for build to complete**

⏱️ **Time:** 3 minutes

---

### **Step 3: Add MongoDB Database**

1. In your Railway project, click **"New"**
2. Select **"Database"**
3. Choose **"Add MongoDB"**
4. Railway automatically:
   - ✅ Creates MongoDB instance
   - ✅ Generates connection string
   - ✅ Adds it to environment variables

⏱️ **Time:** 1 minute

---

### **Step 4: Configure Environment Variables**

1. Click on your **backend service** (not MongoDB)
2. Go to **"Variables"** tab
3. Add these variables:

```bash
MONGODB_URL=${{MongoDB.MONGO_URL}}
MONGODB_DB_NAME=cyber_healthguard
DEBUG=false
ANOMALY_THRESHOLD=0.7
FAILED_LOGIN_THRESHOLD=5
MIN_SAMPLES_FOR_TRAINING=100
```

**Note:** `${{MongoDB.MONGO_URL}}` is automatically populated by Railway

4. Click **"Deploy"** to restart with new variables

⏱️ **Time:** 2 minutes

---

### **Step 5: Get Your API URL**

1. In your backend service, go to **"Settings"**
2. Scroll to **"Domains"**
3. You'll see a URL like: `https://your-app.railway.app`
4. Click **"Generate Domain"** if not already there

**Test it:**
```bash
curl https://your-app.railway.app/health
```

You should see:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

⏱️ **Time:** 1 minute

---

### **Step 6: Add Custom Domain (cyberwavesecurity.org)**

#### **A. In Railway:**

1. In backend service → **"Settings"** → **"Domains"**
2. Click **"Custom Domain"**
3. Enter: `api.cyberwavesecurity.org`
4. Railway shows you a **CNAME record** (copy it)

#### **B. In Cloudflare (or IONOS DNS):**

**Option 1: Using Cloudflare (Recommended)**

1. Add `cyberwavesecurity.org` to Cloudflare (free)
2. In Cloudflare DNS:
   - Type: `CNAME`
   - Name: `api`
   - Target: `your-app.railway.app` (from Railway)
   - Proxy: **Disabled** ⚠️ (Orange cloud OFF)
3. Update IONOS nameservers to Cloudflare's

**Option 2: Direct IONOS DNS**

1. Go to IONOS domain management
2. Add DNS record:
   - Type: `CNAME`
   - Hostname: `api`
   - Points to: `your-app.railway.app`
3. Save

**Wait 5-60 minutes for DNS propagation**

#### **C. Test Custom Domain:**

```bash
curl https://api.cyberwavesecurity.org/health
```

⏱️ **Time:** 10 minutes (+ DNS propagation)

---

### **Step 7: Test Your Deployment**

```bash
# Health check
curl https://api.cyberwavesecurity.org/health

# API documentation
open https://api.cyberwavesecurity.org/docs

# Test alert endpoint
curl -H "X-Org-Id: org_001" https://api.cyberwavesecurity.org/alerts
```

⏱️ **Time:** 2 minutes

---

### **Step 8: Generate Test Data**

Run locally to populate your Railway database:

```bash
# Update the seed script to use Railway URL
cd backend/scripts

# Edit seed_data.py - change API_URL to:
API_URL = "https://api.cyberwavesecurity.org"

# Run it
python seed_data.py
```

This creates 200 test logs and alerts in your Railway database.

⏱️ **Time:** 3 minutes

---

## 🎯 **Your Live URLs**

After deployment:

| Service | URL |
|---------|-----|
| **API Docs** | https://api.cyberwavesecurity.org/docs |
| **API Base** | https://api.cyberwavesecurity.org |
| **Health Check** | https://api.cyberwavesecurity.org/health |
| **Alerts** | https://api.cyberwavesecurity.org/alerts |
| **Endpoints** | https://api.cyberwavesecurity.org/endpoints |
| **Compliance** | https://api.cyberwavesecurity.org/compliance |

---

## 🔄 **Auto-Deploy on Git Push**

Railway automatically redeploys when you push to your GitHub repo:

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push

# Railway automatically:
# ✅ Detects the push
# ✅ Builds new image
# ✅ Deploys with zero downtime
```

---

## 💰 **Free Tier Limits**

Railway free tier includes:
- ✅ **$5 credit/month**
- ✅ **500 hours** of usage
- ✅ **Unlimited** deployments
- ✅ **1GB RAM** per service
- ✅ **1GB disk** per service

**Your app uses:**
- ~100 MB RAM
- ~200 MB disk
- Costs: **~$3-4/month** (stays in free tier)

---

## 📊 **Monitoring**

In Railway dashboard:

1. **Metrics tab:**
   - CPU usage
   - RAM usage
   - Network traffic

2. **Logs tab:**
   - Application logs
   - Error messages
   - Request logs

3. **Deployments tab:**
   - Build history
   - Deploy status
   - Rollback options

---

## 🔧 **Useful Commands**

### View Logs
```bash
# In Railway dashboard → "Logs" tab
# Or use Railway CLI:
railway logs
```

### Restart Service
```bash
# In Railway dashboard → "Settings" → "Restart"
# Or:
railway restart
```

### Rollback Deployment
```bash
# In Railway dashboard → "Deployments" → Select old deployment → "Redeploy"
```

---

## 🆘 **Troubleshooting**

### Build fails
- Check **"Build Logs"** in Railway
- Ensure `Dockerfile` is in repo root
- Verify `railway.json` exists

### Database connection fails
```bash
# Check environment variables
# Ensure MONGODB_URL=${{MongoDB.MONGO_URL}}
```

### Domain not working
```bash
# Check DNS propagation
nslookup api.cyberwavesecurity.org

# Wait up to 24 hours for DNS
# Ensure CNAME record points to Railway domain
```

### Out of memory
```bash
# Upgrade to paid plan ($5/month)
# Or optimize your application
```

---

## 🚀 **Connect Frontend**

In your frontend code:

```javascript
// API configuration
const API_BASE_URL = 'https://api.cyberwavesecurity.org';
const ORG_ID = 'org_001';

// Make requests
fetch(`${API_BASE_URL}/alerts`, {
  headers: {
    'X-Org-Id': ORG_ID,
    'Content-Type': 'application/json'
  }
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 📦 **Frontend Deployment Options**

Deploy frontend to:

1. **Railway** (same project)
   - Add frontend service
   - Serve on `cyberwavesecurity.org`

2. **Vercel** (recommended for frontend)
   - Free tier
   - Auto-deploy from GitHub
   - Excellent performance

3. **IONOS Webspace**
   - Upload build files via SFTP
   - Use your existing hosting

---

## 🔒 **Security Best Practices**

✅ **Enabled by default:**
- HTTPS/SSL (automatic)
- Environment variables (encrypted)
- Isolated services

✅ **To add:**
- Rate limiting (already in code)
- API authentication (upgrade from X-Org-Id header)
- Monitoring & alerts

---

## 📝 **Next Steps**

1. ✅ Backend deployed on Railway
2. ✅ Custom domain connected
3. ✅ Database populated with test data
4. ⏭️ Deploy frontend (Vercel or IONOS)
5. ⏭️ Connect frontend to `https://api.cyberwavesecurity.org`
6. ⏭️ Add user authentication
7. ⏭️ Set up monitoring

---

## 💡 **Pro Tips**

- **Use Cloudflare** for domain DNS (free DDoS protection)
- **Enable Railway's "Restart on Failure"** (automatic)
- **Monitor your $5 credit** in Railway dashboard
- **Set up alerts** for when credit runs low
- **Use Railway CLI** for faster deployments

---

**Total deployment time: ~25 minutes** (+ DNS propagation)

**Need help?** Check Railway docs at https://docs.railway.app
