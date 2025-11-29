#!/bin/bash

# Test script for Cyber HealthGuard AI API

API_URL="http://localhost:8000"
ORG_ID="org_001"

echo "🧪 Testing Cyber HealthGuard AI API"
echo "====================================="
echo ""

# Check API health
echo "1️⃣  Testing health endpoint..."
curl -s "$API_URL/health" | python3 -m json.tool
echo ""
echo ""

# Send a test log event
echo "2️⃣  Sending test log event..."
curl -s -X POST "$API_URL/ingest/logs" \
  -H "X-Org-Id: $ORG_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "organisation_id": "org_001",
    "host": "WKS-TEST-001",
    "user": "test.user",
    "event_type": "login",
    "source": "ActiveDirectory",
    "details": {
      "success": false,
      "ip_address": "192.168.1.100",
      "failure_reason": "Invalid credentials"
    }
  }' | python3 -m json.tool
echo ""
echo ""

# Get alerts
echo "3️⃣  Getting alerts..."
curl -s "$API_URL/alerts" \
  -H "X-Org-Id: $ORG_ID" | python3 -m json.tool
echo ""
echo ""

# Get endpoints
echo "4️⃣  Getting endpoints..."
curl -s "$API_URL/endpoints" \
  -H "X-Org-Id: $ORG_ID" | python3 -m json.tool
echo ""
echo ""

# Get compliance
echo "5️⃣  Getting compliance..."
curl -s "$API_URL/compliance" \
  -H "X-Org-Id: $ORG_ID" | python3 -m json.tool
echo ""
echo ""

echo "✅ Testing complete!"
echo ""
echo "📖 View interactive API docs at: $API_URL/docs"
