# 🔷 Azure Deployment Guide - Cyber Guardian AI

## 🎁 What You Get with Azure Free Tier

- **$100 credit** for 30 days (all services)
- **12 months free** of popular services
- **Always free** tier for 25+ services
- **No credit card required** if you're a student

---

## 🚀 Option 1: Azure Container Apps (Recommended)

Azure Container Apps is the easiest and most modern way to deploy your FastAPI backend.

### Prerequisites

1. **Azure Account**: Sign up at https://azure.microsoft.com/free/
   - Students: Use https://azure.microsoft.com/free/students/ (no credit card!)

2. **Install Azure CLI** (Windows PowerShell as Admin):
   ```powershell
   winget install Microsoft.AzureCLI
   # Or download from: https://aka.ms/installazurecliwindows
   ```

3. **Restart PowerShell** after installation

### Step-by-Step Deployment

#### 1. Login to Azure
```powershell
az login
```
This opens your browser - sign in with your Azure account.

#### 2. Set Your Subscription (if you have multiple)
```powershell
# List subscriptions
az account list --output table

# Set the subscription you want to use
az account set --subscription "Your Subscription Name"
```

#### 3. Create Resource Group
```powershell
# Create a resource group (logical container for your resources)
az group create `
  --name cyber-guardian-rg `
  --location eastus
```

#### 4. Create Container Apps Environment
```powershell
# Install the Container Apps extension
az extension add --name containerapp --upgrade

# Create the environment (shared infrastructure for your apps)
az containerapp env create `
  --name cyber-guardian-env `
  --resource-group cyber-guardian-rg `
  --location eastus
```

#### 5. Deploy Your Backend
```powershell
cd C:\Users\Hertz-Terotech\Documents\cyber-guardian-ai\backend

# Deploy directly from your local Docker context
az containerapp up `
  --name cyber-guardian-backend `
  --resource-group cyber-guardian-rg `
  --location eastus `
  --environment cyber-guardian-env `
  --source . `
  --target-port 8000 `
  --ingress external `
  --env-vars `
    "MONGO_URL=your-mongodb-atlas-connection-string" `
    "MONGODB_DB_NAME=cyber_healthguard" `
    "SECRET_KEY=your-secret-key-change-this" `
    "DEBUG=false" `
    "APP_NAME=Cyber HealthGuard AI" `
    "ALGORITHM=HS256" `
    "ACCESS_TOKEN_EXPIRE_MINUTES=43200"
```

**Important**: Replace `your-mongodb-atlas-connection-string` and `your-secret-key-change-this` with your actual values!

#### 6. Get Your Backend URL
```powershell
az containerapp show `
  --name cyber-guardian-backend `
  --resource-group cyber-guardian-rg `
  --query properties.configuration.ingress.fqdn `
  --output tsv
```

Your backend will be at: `https://<output-from-above-command>`

---

## 🔧 Option 2: Azure App Service (Alternative)

If you prefer traditional PaaS deployment:

### Deploy Steps

#### 1. Create App Service Plan
```powershell
az appservice plan create `
  --name cyber-guardian-plan `
  --resource-group cyber-guardian-rg `
  --sku B1 `
  --is-linux
```

#### 2. Create Web App
```powershell
az webapp create `
  --resource-group cyber-guardian-rg `
  --plan cyber-guardian-plan `
  --name cyber-guardian-backend-<your-unique-name> `
  --runtime "PYTHON:3.11" `
  --startup-file "uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

#### 3. Configure Environment Variables
```powershell
az webapp config appsettings set `
  --resource-group cyber-guardian-rg `
  --name cyber-guardian-backend-<your-unique-name> `
  --settings `
    MONGO_URL="your-mongodb-connection" `
    MONGODB_DB_NAME="cyber_healthguard" `
    SECRET_KEY="your-secret-key" `
    DEBUG="false"
```

#### 4. Deploy Code
```powershell
cd C:\Users\Hertz-Terotech\Documents\cyber-guardian-ai\backend

# Deploy from local Git
az webapp up `
  --resource-group cyber-guardian-rg `
  --name cyber-guardian-backend-<your-unique-name> `
  --runtime "PYTHON:3.11"
```

Your app will be at: `https://cyber-guardian-backend-<your-unique-name>.azurewebsites.net`

---

## 🎓 For Students: Extra Free Resources

If you're a student, verify with GitHub Student Developer Pack:

1. Go to https://education.github.com/pack
2. Verify with your student email (.edu)
3. Get Azure credits + tons of other free tools

---

## 🔐 Setting Up Secrets

### Generate a Secret Key
```powershell
# Generate a secure random key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and use it as your `SECRET_KEY`.

### MongoDB Connection String

Get from MongoDB Atlas:
1. Go to https://cloud.mongodb.com
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Copy the connection string
5. Replace `<password>` with your actual password

Example:
```
mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

---

## 📊 Managing Your Deployment

### View Logs
```powershell
# Container Apps
az containerapp logs show `
  --name cyber-guardian-backend `
  --resource-group cyber-guardian-rg `
  --follow

# App Service
az webapp log tail `
  --name cyber-guardian-backend-<your-name> `
  --resource-group cyber-guardian-rg
```

### Update Environment Variables
```powershell
# Container Apps
az containerapp update `
  --name cyber-guardian-backend `
  --resource-group cyber-guardian-rg `
  --set-env-vars "NEW_VAR=value"

# App Service
az webapp config appsettings set `
  --resource-group cyber-guardian-rg `
  --name cyber-guardian-backend-<your-name> `
  --settings NEW_VAR="value"
```

### Scale Your App
```powershell
# Container Apps - set min/max replicas
az containerapp update `
  --name cyber-guardian-backend `
  --resource-group cyber-guardian-rg `
  --min-replicas 0 `
  --max-replicas 5

# App Service - change plan
az appservice plan update `
  --name cyber-guardian-plan `
  --resource-group cyber-guardian-rg `
  --sku B2
```

---

## 💰 Cost Management

### Free Tier Limits

**Container Apps**:
- First 180,000 vCPU-seconds/month free
- First 360,000 GiB-seconds/month free
- ~$0.04/hour for always-on (with your $100 credit = 2,500 hours)

**App Service**:
- B1 tier: ~$13/month (covered by free credits)
- F1 tier: Free (with limitations)

### Monitor Your Spending
```powershell
# Check your credit balance
az consumption budget list --resource-group cyber-guardian-rg
```

Or check the Azure Portal → Cost Management

---

## 🔄 Update Your Netlify Frontend

After deployment, update your frontend:

1. Go to Netlify dashboard
2. Site settings → Environment variables
3. Update `VITE_API_URL`:
   ```
   https://cyber-guardian-backend.xxx.azurecontainerapps.io
   ```
   Or for App Service:
   ```
   https://cyber-guardian-backend-<your-name>.azurewebsites.net
   ```
4. Trigger new deployment

---

## 🚨 Troubleshooting

### Backend Won't Start
```powershell
# Check logs
az containerapp logs show `
  --name cyber-guardian-backend `
  --resource-group cyber-guardian-rg `
  --follow
```

Common issues:
- ❌ Wrong MongoDB connection string → Check MONGO_URL
- ❌ Missing SECRET_KEY → Generate and set it
- ❌ Port mismatch → Ensure target-port is 8000

### Can't Connect to MongoDB
- Verify MongoDB Atlas allows Azure IPs
- Go to MongoDB Atlas → Network Access → Allow access from anywhere (0.0.0.0/0)

### CORS Errors
- Backend CORS is already configured for Netlify
- Make sure frontend VITE_API_URL is correct

---

## ✅ Quick Start Summary

```powershell
# 1. Install Azure CLI
winget install Microsoft.AzureCLI

# 2. Login
az login

# 3. Create resources
az group create --name cyber-guardian-rg --location eastus
az extension add --name containerapp --upgrade
az containerapp env create --name cyber-guardian-env --resource-group cyber-guardian-rg --location eastus

# 4. Deploy (replace with your MongoDB URL and secret key)
cd backend
az containerapp up `
  --name cyber-guardian-backend `
  --resource-group cyber-guardian-rg `
  --environment cyber-guardian-env `
  --source . `
  --target-port 8000 `
  --ingress external `
  --env-vars "MONGO_URL=your-mongodb-url" "MONGODB_DB_NAME=cyber_healthguard" "SECRET_KEY=your-secret" "DEBUG=false"

# 5. Get URL
az containerapp show --name cyber-guardian-backend --resource-group cyber-guardian-rg --query properties.configuration.ingress.fqdn -o tsv
```

That's it! 🎉

---

## 📞 Need Help?

- Azure Docs: https://docs.microsoft.com/azure/container-apps/
- Azure Support: Built into Azure Portal
- Check logs first: `az containerapp logs show --follow`
