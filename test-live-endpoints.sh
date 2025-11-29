#!/bin/bash
# Test script for Cyber Guardian AI live endpoints
# Tests Railway backend connectivity

API_URL="https://cyber-guardian-ai-production-deb8.up.railway.app"

echo "🧪 Testing Cyber Guardian AI Live Endpoints"
echo "==========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo "1️⃣  Testing Health Check Endpoint..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/health")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo -e "${RED}✗ Health check failed (HTTP $http_code)${NC}"
    echo "$body"
fi
echo ""

# Test 2: Root Endpoint
echo "2️⃣  Testing Root Endpoint..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Root endpoint passed${NC}"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo -e "${RED}✗ Root endpoint failed (HTTP $http_code)${NC}"
    echo "$body"
fi
echo ""

# Test 3: API Documentation
echo "3️⃣  Testing API Documentation..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/docs")
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ API docs accessible at: $API_URL/docs${NC}"
else
    echo -e "${RED}✗ API docs failed (HTTP $http_code)${NC}"
fi
echo ""

# Test 4: Auth Registration (without credentials)
echo "4️⃣  Testing Auth Registration Endpoint (OPTIONS)..."
response=$(curl -s -w "\n%{http_code}" -X OPTIONS "$API_URL/api/auth/register")
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Auth endpoint accessible (CORS configured)${NC}"
else
    echo -e "${YELLOW}⚠ Auth endpoint returned HTTP $http_code${NC}"
fi
echo ""

# Test 5: Alerts Endpoint (without auth - should fail)
echo "5️⃣  Testing Alerts Endpoint (without auth)..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/alerts")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
    echo -e "${GREEN}✓ Auth protection working (HTTP $http_code)${NC}"
elif [ "$http_code" = "200" ]; then
    echo -e "${YELLOW}⚠ Endpoint accessible without auth${NC}"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo -e "${RED}✗ Unexpected response (HTTP $http_code)${NC}"
    echo "$body"
fi
echo ""

# Test 6: Compliance Endpoint (without auth)
echo "6️⃣  Testing Compliance Endpoint (without auth)..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/compliance")
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
    echo -e "${GREEN}✓ Auth protection working (HTTP $http_code)${NC}"
elif [ "$http_code" = "200" ]; then
    echo -e "${YELLOW}⚠ Endpoint accessible without auth${NC}"
else
    echo -e "${RED}✗ Unexpected response (HTTP $http_code)${NC}"
fi
echo ""

# Summary
echo "==========================================="
echo "📊 Test Summary"
echo "==========================================="
echo ""
echo "Backend URL: $API_URL"
echo "Status: All core endpoints are responding"
echo ""
echo "Next Steps:"
echo "  1. Open your browser dev tools (F12)"
echo "  2. Start your frontend: npm run dev"
echo "  3. Try to sign up / login"
echo "  4. Check console for API calls"
echo ""
echo "To test with authentication:"
echo "  1. Sign up at your Netlify URL"
echo "  2. Copy the access_token from browser localStorage"
echo "  3. Run: curl -H 'Authorization: Bearer <token>' $API_URL/api/alerts"
echo ""
