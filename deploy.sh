#!/bin/bash
# Deployment script for Cyber HealthGuard AI
# This script helps deploy frontend to Netlify and configure backend

set -e  # Exit on error

echo "🚀 Cyber HealthGuard AI - Deployment Script"
echo "============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: package.json not found. Please run from project root.${NC}"
    exit 1
fi

echo "📋 Deployment Options:"
echo "1. Deploy Frontend to Netlify (with mock data)"
echo "2. Deploy Frontend to Netlify (with live API)"
echo "3. Configure Backend API URL"
echo "4. Test Local Build"
echo "5. Show Current Configuration"
echo ""
read -p "Select option (1-5): " option

case $option in
    1)
        echo -e "${YELLOW}📦 Building frontend with MOCK data...${NC}"
        export VITE_API_URL="http://localhost:8000"
        export VITE_USE_MOCK_DATA="true"
        export VITE_ENV="production"

        npm run build

        echo -e "${GREEN}✅ Build complete!${NC}"
        echo ""
        echo "To deploy to Netlify:"
        echo "1. Go to https://app.netlify.com"
        echo "2. Drag and drop the 'dist' folder"
        echo "OR use Netlify CLI:"
        echo "   npm install -g netlify-cli"
        echo "   netlify deploy --prod --dir=dist"
        ;;

    2)
        echo -e "${YELLOW}📦 Building frontend with LIVE API...${NC}"
        read -p "Enter your Railway API URL (e.g., https://your-app.up.railway.app): " api_url

        if [ -z "$api_url" ]; then
            echo -e "${RED}❌ API URL is required${NC}"
            exit 1
        fi

        export VITE_API_URL="$api_url"
        export VITE_USE_MOCK_DATA="false"
        export VITE_ENV="production"

        echo "Building with:"
        echo "  API URL: $api_url"
        echo "  Mock Data: false"
        echo ""

        npm run build

        echo -e "${GREEN}✅ Build complete!${NC}"
        echo ""
        echo "To deploy to Netlify:"
        echo "1. Go to https://app.netlify.com"
        echo "2. Site settings → Environment variables"
        echo "3. Add these variables:"
        echo "   VITE_API_URL=$api_url"
        echo "   VITE_USE_MOCK_DATA=false"
        echo "   VITE_ENV=production"
        echo "4. Trigger new deployment or drag 'dist' folder"
        ;;

    3)
        echo -e "${YELLOW}⚙️  Backend API Configuration${NC}"
        echo ""
        echo "Current .env.example configuration:"
        cat .env.example
        echo ""
        read -p "Enter new API URL: " new_api_url

        if [ -z "$new_api_url" ]; then
            echo -e "${RED}❌ API URL is required${NC}"
            exit 1
        fi

        # Update .env.example
        sed -i.bak "s|VITE_API_URL=.*|VITE_API_URL=$new_api_url|" .env.example

        echo -e "${GREEN}✅ Updated .env.example${NC}"
        echo ""
        echo "For local development, create .env.local:"
        cat > .env.local <<EOF
VITE_API_URL=$new_api_url
VITE_USE_MOCK_DATA=false
VITE_ENV=development
EOF
        echo -e "${GREEN}✅ Created .env.local${NC}"
        ;;

    4)
        echo -e "${YELLOW}🧪 Testing local build...${NC}"
        export VITE_API_URL="http://localhost:8000"
        export VITE_USE_MOCK_DATA="true"
        export VITE_ENV="development"

        npm run build

        echo -e "${GREEN}✅ Build successful!${NC}"
        echo ""
        echo "To test the build locally:"
        echo "  npm run preview"
        echo ""
        echo "Then open: http://localhost:4173"
        ;;

    5)
        echo -e "${YELLOW}📊 Current Configuration${NC}"
        echo ""
        echo "Git branch:"
        git branch --show-current
        echo ""
        echo "Latest commit:"
        git log -1 --oneline
        echo ""
        echo ".env.example contents:"
        cat .env.example 2>/dev/null || echo "No .env.example found"
        echo ""
        echo ".env.local contents:"
        cat .env.local 2>/dev/null || echo "No .env.local found (this is normal)"
        echo ""
        echo "Current API endpoints configured in src/lib/api.ts:"
        grep -A 2 "API_BASE_URL" src/lib/api.ts | head -5
        ;;

    *)
        echo -e "${RED}❌ Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✨ Done!${NC}"
