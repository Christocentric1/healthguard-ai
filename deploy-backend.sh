#!/bin/bash
# Backend deployment script for Cyber HealthGuard AI
# Deploy FastAPI backend to Railway or other platforms

set -e

echo "🚀 Backend Deployment Helper"
echo "=============================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo -e "${RED}❌ Error: backend directory not found${NC}"
    exit 1
fi

echo "📋 Backend Deployment Options:"
echo "1. Prepare for Railway Deployment"
echo "2. Test Backend Locally with Docker"
echo "3. Generate Railway Environment Variables"
echo "4. Check Backend Configuration"
echo ""
read -p "Select option (1-4): " option

case $option in
    1)
        echo -e "${YELLOW}📦 Preparing for Railway deployment...${NC}"
        echo ""
        echo "✅ Checklist:"
        echo ""

        # Check requirements.txt
        if [ -f "backend/requirements.txt" ]; then
            echo -e "${GREEN}✓${NC} requirements.txt found"
        else
            echo -e "${RED}✗${NC} requirements.txt missing"
        fi

        # Check main.py
        if [ -f "backend/app/main.py" ]; then
            echo -e "${GREEN}✓${NC} app/main.py found"
        else
            echo -e "${RED}✗${NC} app/main.py missing"
        fi

        # Check Dockerfile
        if [ -f "backend/Dockerfile" ]; then
            echo -e "${GREEN}✓${NC} Dockerfile found"
        else
            echo -e "${RED}✗${NC} Dockerfile missing"
        fi

        echo ""
        echo "📝 Railway Deployment Steps:"
        echo ""
        echo "1. Go to https://railway.app"
        echo "2. Create new project → Deploy from GitHub repo"
        echo "3. Select this repository"
        echo "4. Settings → Set Root Directory to: backend"
        echo "5. Settings → Set Start Command to:"
        echo "   uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
        echo ""
        echo "6. Add MongoDB database:"
        echo "   - Click '+ New' → Database → MongoDB"
        echo "   - Copy connection URL"
        echo ""
        echo "7. Add Environment Variables (see option 3)"
        echo ""
        echo "8. Deploy!"
        echo ""
        echo "After deployment, copy your Railway URL and use it in the frontend."
        ;;

    2)
        echo -e "${YELLOW}🐳 Testing backend with Docker...${NC}"
        echo ""

        cd backend

        # Check if docker-compose exists
        if [ ! -f "docker-compose.yml" ]; then
            echo -e "${RED}❌ docker-compose.yml not found${NC}"
            exit 1
        fi

        echo "Starting services..."
        docker-compose up -d

        echo ""
        echo -e "${GREEN}✅ Backend started!${NC}"
        echo ""
        echo "Services running:"
        docker-compose ps
        echo ""
        echo "API Documentation: http://localhost:8000/docs"
        echo "Health Check: http://localhost:8000/health"
        echo ""
        echo "To view logs:"
        echo "  docker-compose logs -f"
        echo ""
        echo "To stop:"
        echo "  docker-compose down"
        ;;

    3)
        echo -e "${YELLOW}⚙️  Railway Environment Variables${NC}"
        echo ""
        echo "Copy these to Railway → Variables:"
        echo ""
        cat <<'EOF'
# MongoDB Connection
MONGODB_URL=mongodb://mongo:27017
# (Replace with your Railway MongoDB connection string)

MONGODB_DB_NAME=cyber_healthguard

# App Settings
APP_NAME=Cyber HealthGuard AI
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production

# Authentication (CHANGE THIS!)
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# ML Settings
ANOMALY_THRESHOLD=0.7
MIN_SAMPLES_FOR_TRAINING=100

# Rules
FAILED_LOGIN_THRESHOLD=5

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# CORS (Add your Netlify URL)
CORS_ORIGINS=https://your-frontend.netlify.app,http://localhost:5173
EOF
        echo ""
        echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
        echo "1. Generate a secure SECRET_KEY:"
        echo "   python -c 'import secrets; print(secrets.token_urlsafe(32))'"
        echo ""
        echo "2. Get MongoDB URL from Railway MongoDB service"
        echo ""
        echo "3. Add your Netlify frontend URL to CORS_ORIGINS"
        ;;

    4)
        echo -e "${YELLOW}🔍 Checking backend configuration...${NC}"
        echo ""

        echo "Backend structure:"
        ls -la backend/ 2>/dev/null || echo "Backend directory not found"
        echo ""

        echo "Python files:"
        find backend/app -name "*.py" -type f 2>/dev/null | head -20 || echo "No Python files found"
        echo ""

        echo "Requirements:"
        if [ -f "backend/requirements.txt" ]; then
            echo "Python packages:"
            cat backend/requirements.txt
        else
            echo "requirements.txt not found"
        fi
        echo ""

        echo "Git status:"
        git status -s backend/
        ;;

    *)
        echo -e "${RED}❌ Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✨ Done!${NC}"
