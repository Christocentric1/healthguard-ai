# 🚀 Deployment Guide - Cyber HealthGuard AI

This guide will help you deploy the Cyber HealthGuard AI platform.

---

## Quick Start (Mock Data - No Backend Required)

The app is **ready to deploy immediately** with mock data. No backend needed!

### Deploy Frontend to Netlify (5 minutes)

1. **Build the frontend:**
   ```bash
   ./deploy.sh
   # Select option 1: Deploy Frontend to Netlify (with mock data)
   ```

2. **Deploy to Netlify:**
   - Go to https://app.netlify.com
   - Click "Add new site" → "Deploy manually"
   - Drag and drop the `dist` folder
   - Done! Your site is live with full DSPT and MITRE ATT&CK features

**What you get:**
- ✅ Full compliance dashboard (HIPAA, GDPR, CIS, ISO 27001, DSPT)
- ✅ MITRE ATT&CK threat intelligence
- ✅ Security alerts and endpoints monitoring
- ✅ All UI features working with realistic mock data
- ✅ No backend configuration needed

---

## Full Stack Deployment (With Live Backend)

### Step 1: Deploy Backend to Railway

1. **Prepare backend:**
   ```bash
   ./deploy-backend.sh
   # Select option 1: Prepare for Railway Deployment
   ```

2. **Deploy to Railway:**
   - Go to https://railway.app
   - New Project → Deploy from GitHub
   - Select this repository
   - **Settings:**
     - Root Directory: `backend`
     - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Add MongoDB:**
   - Click "+ New" → Database → MongoDB
   - Copy the connection URL

4. **Set Environment Variables:**
   ```bash
   ./deploy-backend.sh
   # Select option 3: Generate Railway Environment Variables
   ```

   Copy the variables to Railway → Variables tab

   **Important:**
   - Update `MONGODB_URL` with your Railway MongoDB URL
   - Generate new `SECRET_KEY`: `python -c 'import secrets; print(secrets.token_urlsafe(32))'`

5. **Get your Railway URL:**
   - Settings → Domains → Generate Domain
   - Copy URL (e.g., `https://your-app.up.railway.app`)

### Step 2: Deploy Frontend with Live API

1. **Build frontend with live API:**
   ```bash
   ./deploy.sh
   # Select option 2: Deploy Frontend to Netlify (with live API)
   # Enter your Railway URL when prompted
   ```

2. **Deploy to Netlify:**
   - Drag and drop `dist` folder to Netlify

   OR set environment variables in Netlify:
   - Site settings → Environment variables
   - Add:
     ```
     VITE_API_URL=https://your-railway-app.up.railway.app
     VITE_USE_MOCK_DATA=false
     VITE_ENV=production
     ```

3. **Update CORS in Railway:**
   - Railway → Backend → Variables
   - Update `CORS_ORIGINS` with your Netlify URL
   - Example: `https://your-site.netlify.app`

---

## Local Development

### Frontend Only (Mock Data)
```bash
npm install
npm run dev
```
Open http://localhost:5173

### With Local Backend
1. **Start backend:**
   ```bash
   cd backend
   docker-compose up -d
   ```

2. **Start frontend:**
   ```bash
   npm run dev
   ```

3. **Create `.env.local`:**
   ```env
   VITE_API_URL=http://localhost:8000
   VITE_USE_MOCK_DATA=false
   VITE_ENV=development
   ```

---

## Deployment Scripts

### `./deploy.sh`
Frontend deployment helper with options:
1. Build with mock data (default)
2. Build with live API
3. Configure API URL
4. Test local build
5. Show current configuration

### `./deploy-backend.sh`
Backend deployment helper with options:
1. Prepare for Railway
2. Test locally with Docker
3. Generate environment variables
4. Check configuration

---

## Environment Variables

### Frontend (.env.local or Netlify)
| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |
| `VITE_USE_MOCK_DATA` | Use mock data (true/false) | `true` |
| `VITE_ENV` | Environment | `development` |

### Backend (Railway Variables)
| Variable | Description | Required |
|----------|-------------|----------|
| `MONGODB_URL` | MongoDB connection string | Yes |
| `MONGODB_DB_NAME` | Database name | Yes |
| `SECRET_KEY` | JWT secret key | Yes |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | Yes |
| `ENVIRONMENT` | production/development | No |
| `DEBUG` | Enable debug mode | No |

---

## Features Available

### With Mock Data (No Backend)
- ✅ Full UI with realistic data
- ✅ DSPT compliance monitoring (7 domains)
- ✅ MITRE ATT&CK detections (3 threats)
- ✅ Compliance dashboard (6 frameworks)
- ✅ Alerts and endpoints
- ✅ All navigation and features
- ❌ No real-time updates
- ❌ No data persistence

### With Live Backend
- ✅ Everything above PLUS:
- ✅ Real-time threat detection
- ✅ Live log ingestion
- ✅ ML-powered anomaly detection
- ✅ Automated DSPT assessments
- ✅ Data persistence
- ✅ Multi-tenant support
- ✅ User authentication

---

## Testing Your Deployment

### Frontend
1. Visit your Netlify URL
2. Login page should load
3. Navigate to:
   - `/dashboard` - Main dashboard
   - `/compliance` - Click DSPT tab
   - `/mitre-attack` - Threat intelligence
4. Check browser console for API configuration

### Backend (if deployed)
1. Visit: `https://your-railway-url.up.railway.app/health`
2. Should return: `{"status": "healthy"}`
3. API docs: `https://your-railway-url.up.railway.app/docs`

---

## Troubleshooting

### "Failed to fetch" errors
- Check `VITE_USE_MOCK_DATA=true` in environment
- Or verify backend URL is correct
- Check CORS settings in backend

### Build fails
```bash
# Clear cache and rebuild
rm -rf dist node_modules
npm install
npm run build
```

### Backend not responding
- Check Railway logs
- Verify MongoDB connection
- Check environment variables
- Ensure Root Directory = `backend`

---

## Cost Estimate

### Free Tier (Recommended for Demo)
- **Netlify:** 100GB bandwidth/month (FREE)
- **Railway:** $5 credit/month (FREE tier)
- **Total:** FREE for development and small deployments

### Production Scale
- **Netlify Pro:** $19/month (1TB bandwidth)
- **Railway:** Pay-as-you-go ($0.000463/GB-hour)
- **Total:** ~$25-50/month for typical healthcare organization

---

## Next Steps

1. ✅ Deploy frontend with mock data (immediate demo)
2. 📊 Show stakeholders DSPT and MITRE features
3. 🔧 Deploy backend when ready for live data
4. 🔄 Switch frontend to live API
5. 🚀 Go to production!

---

## Support & Documentation

- **Design Docs:** See `DSPT_FRAMEWORK_DESIGN.md` and `MITRE_ATTACK_DESIGN.md`
- **Implementation Status:** See `IMPLEMENTATION_STATUS.md`
- **API Docs:** See `API_INTEGRATION.md`
- **Backup Tag:** `v1.0-dspt-mitre-ui`

---

**Current Status:** ✅ Frontend complete with DSPT + MITRE ATT&CK UI
**Ready to Deploy:** YES (with mock data)
**Backend Required:** NO (optional for live data)
