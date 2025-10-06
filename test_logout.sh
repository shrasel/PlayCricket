#!/bin/bash

echo "🧪 Testing Logout Functionality"
echo "================================"
echo ""

# Step 1: Login
echo "📝 Step 1: Logging in..."
LOGIN_RESPONSE=$(curl -s -i -c /tmp/test_cookies_logout.txt -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }')

# Extract access token from login response
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Login failed. Response:"
  echo "$LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Login successful"
echo "   Access Token: ${ACCESS_TOKEN:0:20}..."
echo ""

# Check if cookie was set
if grep -q "refresh_token" /tmp/test_cookies_logout.txt; then
  echo "✅ Refresh token cookie set"
else
  echo "⚠️  No refresh token cookie found"
fi
echo ""

# Step 2: Test logout
echo "📝 Step 2: Testing logout..."
LOGOUT_RESPONSE=$(curl -s -i -b /tmp/test_cookies_logout.txt -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

LOGOUT_STATUS=$(echo "$LOGOUT_RESPONSE" | grep "HTTP/" | awk '{print $2}')

echo "   Response Status: $LOGOUT_STATUS"
echo ""

if [ "$LOGOUT_STATUS" == "200" ]; then
  echo "✅ Logout successful!"
  echo ""
  echo "📄 Response:"
  echo "$LOGOUT_RESPONSE" | grep -A 10 "{"
else
  echo "❌ Logout failed!"
  echo ""
  echo "📄 Full Response:"
  echo "$LOGOUT_RESPONSE"
fi

echo ""
echo "================================"
echo "Test completed!"
