# Netlify Deployment Guide - Cyber HealthGuard Frontend

This guide will help you deploy the Cyber HealthGuard frontend to Netlify while keeping the backend API running on Railway or your homelab.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Frontend (Netlify)                                     │
│  - React + TypeScript                                   │
│  - Vite build                                           │
│  - Static hosting                                       │
│  - CDN + SSL                                            │
│                                                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ HTTPS API Requests
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Backend API (Railway or Homelab)                       │
│  - FastAPI + Python                                     │
│  - MongoDB Database                                     │
│  - Health monitoring                                    │
│  - Alert management                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **Netlify Account**: Sign up at [netlify.com](https://netlify.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Backend API**: Your backend should already be deployed and accessible via HTTPS
   - Railway: `https://your-app.railway.app`
   - Homelab: `https://api.cyberwavesecurity.org`

## Deployment Steps

### Step 1: Connect GitHub to Netlify

1. Log in to [Netlify](https://app.netlify.com)
2. Click **"Add new site"** → **"Import an existing project"**
3. Select **"GitHub"** and authorize Netlify
4. Choose your `cyber-guardian-ai` repository
5. Select the branch you want to deploy (e.g., `main` or your current branch)

### Step 2: Configure Build Settings

Netlify should auto-detect these settings from `netlify.toml`, but verify:

| Setting | Value |
|---------|-------|
| **Base directory** | (leave empty or `.`) |
| **Build command** | `npm run build` |
| **Publish directory** | `dist` |
| **Node version** | 20 |

### Step 3: Set Environment Variables

In Netlify dashboard:

1. Go to **Site settings** → **Environment variables**
2. Add the following variables:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `VITE_API_URL` | `https://your-backend-url` | Your backend API URL (Railway or homelab) |
| `VITE_ENV` | `production` | Environment name |
| `VITE_USE_MOCK_DATA` | `false` | Set to false to use real API |

**Example values:**

For Railway:
```env
VITE_API_URL=https://cyber-healthguard.railway.app
VITE_ENV=production
VITE_USE_MOCK_DATA=false
```

For Homelab:
```env
VITE_API_URL=https://api.cyberwavesecurity.org
VITE_ENV=production
VITE_USE_MOCK_DATA=false
```

### Step 4: Deploy

1. Click **"Deploy site"**
2. Netlify will:
   - Install dependencies (`npm install`)
   - Build your React app (`npm run build`)
   - Deploy to CDN
   - Assign a random subdomain (e.g., `random-name-123456.netlify.app`)

### Step 5: Custom Domain (Optional)

To use a custom domain like `app.cyberwavesecurity.org`:

1. Go to **Domain settings** → **Add custom domain**
2. Enter your domain name
3. Add DNS records as instructed by Netlify:
   ```
   Type: CNAME
   Name: app (or your subdomain)
   Value: your-site-name.netlify.app
   ```
4. Netlify automatically provisions SSL certificate (via Let's Encrypt)

## Configuration Files

### netlify.toml

The `netlify.toml` file at the root of the project configures:

- **Build settings**: Node version, build command, publish directory
- **Redirects**: SPA routing support (all routes → `index.html`)
- **Security headers**: XSS protection, frame options, content security
- **Caching**: Static assets cached for 1 year

### Environment Variables in Code

Access environment variables in your React code:

```typescript
import { API_BASE_URL, USE_MOCK_DATA } from '@/lib/api';

console.log(API_BASE_URL); // https://your-backend-url
console.log(USE_MOCK_DATA); // false
```

## CORS Configuration

Your backend API must allow requests from your Netlify domain.

### For FastAPI (backend/app/main.py)

Add your Netlify URL to allowed origins:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # Local development
        "https://your-site.netlify.app",  # Netlify
        "https://app.cyberwavesecurity.org",  # Custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Verifying Deployment

### 1. Check Build Logs

In Netlify dashboard → **Deploys** → Click latest deploy → View logs

Look for:
```
✓ build success
✓ Deploy succeeded
```

### 2. Test the Frontend

Visit your Netlify URL and verify:

- [ ] Site loads correctly
- [ ] Dark/light theme toggle works
- [ ] Navigation works (Dashboard, Alerts, Endpoints, etc.)
- [ ] API connection status (check browser console)

### 3. Check API Connection

Open browser console (F12) and look for:

```
🔧 API Configuration:
  - Environment: production
  - API Base URL: https://your-backend-url
  - Use Mock Data: false
```

Test API health:
```javascript
fetch('https://your-backend-url/health')
  .then(r => r.json())
  .then(console.log)
```

Should return:
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "log_ingestion": "operational",
    ...
  }
}
```

## Continuous Deployment

Netlify automatically deploys when you push to your connected branch:

```bash
git add .
git commit -m "Update frontend"
git push origin main  # Or your configured branch
```

Netlify will:
1. Detect the push
2. Trigger a new build
3. Deploy automatically
4. Keep previous versions for rollback

## Branch Previews

Netlify creates preview deployments for pull requests:

1. Create a branch: `git checkout -b feature/new-dashboard`
2. Push changes: `git push origin feature/new-dashboard`
3. Open PR on GitHub
4. Netlify creates preview URL: `deploy-preview-123--your-site.netlify.app`

## Environment-Specific Builds

### Production (main branch)
```env
VITE_API_URL=https://api.cyberwavesecurity.org
VITE_ENV=production
VITE_USE_MOCK_DATA=false
```

### Staging (staging branch)
```env
VITE_API_URL=https://staging-api.railway.app
VITE_ENV=staging
VITE_USE_MOCK_DATA=false
```

### Development (local)
```env
VITE_API_URL=http://localhost:8000
VITE_ENV=development
VITE_USE_MOCK_DATA=true
```

## Troubleshooting

### Issue: 404 on page refresh

**Cause**: SPA routing not configured

**Fix**: Already handled by `netlify.toml` redirects. Verify the file exists.

### Issue: API requests fail with CORS error

**Cause**: Backend doesn't allow Netlify domain

**Fix**: Add Netlify URL to CORS allowed origins in backend

### Issue: Environment variables not working

**Cause**: Variables must be prefixed with `VITE_`

**Fix**: Ensure all environment variables start with `VITE_` (e.g., `VITE_API_URL`)

### Issue: Build fails

**Cause**: Missing dependencies or incompatible Node version

**Fix**:
- Check build logs in Netlify dashboard
- Verify Node version in `netlify.toml` matches your local version
- Ensure `package.json` includes all dependencies

### Issue: Slow initial load

**Cause**: Unoptimized build or large bundle

**Fix**:
- Enable code splitting (Vite does this by default)
- Check bundle size: `npm run build` shows chunk sizes
- Optimize images and assets

## Performance Optimization

### Netlify Features Already Enabled

- ✅ **CDN**: Global content delivery
- ✅ **Brotli Compression**: Smaller file sizes
- ✅ **HTTP/2**: Faster loading
- ✅ **Asset Optimization**: Automatic image optimization (Pro plan)
- ✅ **Edge Caching**: Static assets cached at edge

### Additional Optimizations

1. **Enable Netlify Image CDN** (Pro plan):
   ```html
   <img src="/.netlify/images?url=/image.jpg&w=800" />
   ```

2. **Prerender Routes** (for SEO):
   Add to `netlify.toml`:
   ```toml
   [[plugins]]
     package = "@netlify/plugin-nextjs"
   ```

3. **Analytics** (optional):
   Enable Netlify Analytics for real-time traffic data

## Monitoring

### Netlify Analytics

Track:
- Page views
- Top pages
- Bandwidth usage
- Deploy frequency

### Backend Health Check

Monitor backend health from frontend:

```typescript
import { checkApiHealth } from '@/lib/api';

// On app startup
checkApiHealth().then(healthy => {
  if (!healthy) {
    console.error('Backend API is unhealthy');
  }
});
```

## Cost

| Plan | Price | Features |
|------|-------|----------|
| **Starter** | **Free** | 100GB bandwidth/month, 300 build minutes/month |
| Pro | $19/month | 1TB bandwidth, 1000 build minutes |
| Business | Custom | Unlimited builds, SLA, SSO |

**Recommended**: Start with **Free tier** (sufficient for most use cases)

## Next Steps

1. ✅ Deploy frontend to Netlify
2. ✅ Configure environment variables
3. ✅ Update backend CORS settings
4. ✅ Test API integration
5. ⬜ Set up custom domain
6. ⬜ Configure branch previews
7. ⬜ Enable monitoring/analytics

## Support

- **Netlify Docs**: https://docs.netlify.com
- **Netlify Support**: https://answers.netlify.com
- **Project Issues**: [GitHub Issues](https://github.com/yourusername/cyber-guardian-ai/issues)

---

**Happy deploying! 🚀**

Your Cyber HealthGuard platform is now globally distributed and lightning-fast on Netlify's CDN.
