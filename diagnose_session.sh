#!/bin/bash

# Session Restore Diagnostic Script
# This script helps diagnose why session restoration isn't working

echo "🔍 PlayCricket Session Restore Diagnostics"
echo "==========================================="
echo ""

# Check if backend is running
echo "1️⃣ Checking Backend Server..."
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "   ✅ Backend is running on port 8000"
else
    echo "   ❌ Backend is NOT running on port 8000"
    echo "   Run: cd backend && PYTHONPATH=\$PWD venv/bin/python3.13 -m uvicorn app.main:app --reload --port 8000"
    exit 1
fi
echo ""

# Check if frontend is running
echo "2️⃣ Checking Frontend Server..."
if curl -s http://localhost:4200 > /dev/null 2>&1; then
    echo "   ✅ Frontend is running on port 4200"
else
    echo "   ❌ Frontend is NOT running on port 4200"
    echo "   Run: cd frontend && npm start"
    exit 1
fi
echo ""

# Test login endpoint
echo "3️⃣ Testing Login Endpoint..."
LOGIN_RESPONSE=$(curl -s -c /tmp/session_test_cookies.txt -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "shahjahan.rasell@gmail.com", "password": "Asdfg!123"}')

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "   ✅ Login successful"
    echo "   📧 User: $(echo "$LOGIN_RESPONSE" | grep -o '"email":"[^"]*' | cut -d'"' -f4)"
else
    echo "   ❌ Login failed"
    echo "   Response: $LOGIN_RESPONSE"
    exit 1
fi
echo ""

# Check if refresh token cookie was set
echo "4️⃣ Checking Refresh Token Cookie..."
if [ -f /tmp/session_test_cookies.txt ]; then
    if grep -q "refresh_token" /tmp/session_test_cookies.txt; then
        echo "   ✅ Refresh token cookie found"
        
        # Check if cookie has Secure flag
        COOKIE_LINE=$(grep "refresh_token" /tmp/session_test_cookies.txt)
        echo "   📝 Cookie details:"
        echo "      $COOKIE_LINE"
        
        # Check for Secure flag in actual HTTP response
        SECURE_CHECK=$(curl -s -i -X POST http://localhost:8000/api/auth/login \
          -H "Content-Type: application/json" \
          -d '{"email": "shahjahan.rasell@gmail.com", "password": "Asdfg!123"}' 2>&1 | grep -i "set-cookie")
        
        if echo "$SECURE_CHECK" | grep -i "Secure"; then
            echo "   ⚠️  WARNING: Cookie has Secure flag (won't work over HTTP)"
            echo "   Set secure=not settings.DEBUG in backend/app/api/routes/auth.py"
        else
            echo "   ✅ Cookie does NOT have Secure flag (works over HTTP)"
        fi
    else
        echo "   ❌ Refresh token cookie NOT found"
        exit 1
    fi
else
    echo "   ❌ Cookie file not created"
    exit 1
fi
echo ""

# Test refresh endpoint
echo "5️⃣ Testing Refresh Endpoint..."
REFRESH_RESPONSE=$(curl -s -b /tmp/session_test_cookies.txt -X POST http://localhost:8000/api/auth/refresh)

if echo "$REFRESH_RESPONSE" | grep -q "access_token"; then
    echo "   ✅ Refresh endpoint works"
    echo "   🔑 New access token received"
else
    echo "   ❌ Refresh endpoint failed"
    echo "   Response: $REFRESH_RESPONSE"
    
    # Try with verbose output
    echo ""
    echo "   🔍 Verbose refresh test:"
    curl -v -b /tmp/session_test_cookies.txt -X POST http://localhost:8000/api/auth/refresh 2>&1 | grep -E "(Cookie|HTTP|set-cookie)"
    exit 1
fi
echo ""

# Test CORS configuration
echo "6️⃣ Testing CORS Configuration..."
CORS_TEST=$(curl -s -i -X OPTIONS http://localhost:8000/api/auth/refresh \
  -H "Origin: http://localhost:4200" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" 2>&1)

if echo "$CORS_TEST" | grep -q "Access-Control-Allow-Origin"; then
    echo "   ✅ CORS is configured"
    
    if echo "$CORS_TEST" | grep -q "Access-Control-Allow-Credentials: true"; then
        echo "   ✅ CORS allows credentials (cookies)"
    else
        echo "   ⚠️  WARNING: CORS might not allow credentials"
        echo "   Check app.add_middleware(CORSMiddleware, allow_credentials=True)"
    fi
else
    echo "   ⚠️  CORS headers not found"
fi
echo ""

# Browser testing instructions
echo "7️⃣ Browser Testing Instructions"
echo "================================"
echo ""
echo "   1. Open browser DevTools (F12)"
echo "   2. Go to Console tab"
echo "   3. Navigate to: http://localhost:4200"
echo "   4. Look for console messages:"
echo "      - '🔄 Attempting to restore session from refresh token...'"
echo "      - '✅ Session restored successfully!' OR"
echo "      - 'ℹ️ No valid session to restore'"
echo ""
echo "   5. Login with:"
echo "      Email: shahjahan.rasell@gmail.com"
echo "      Password: Asdfg!123"
echo ""
echo "   6. After login, check Application tab → Cookies → http://localhost:8000"
echo "      - Should see 'refresh_token' cookie"
echo "      - HttpOnly: ✓"
echo "      - Secure: (should be empty for HTTP)"
echo ""
echo "   7. Refresh the page (F5)"
echo "      - Should see console message: '🔄 Attempting to restore session...'"
echo "      - Check Network tab for POST request to /api/auth/refresh"
echo "      - Status should be 200 OK"
echo ""
echo "   8. If you see 401 on refresh:"
echo "      - Cookie not being sent (check Secure flag)"
echo "      - CORS issue (check console for CORS errors)"
echo "      - Backend issue (check backend logs)"
echo ""
echo "==========================================="
echo "✅ Diagnostics Complete!"
echo ""
echo "Next Steps:"
echo "1. If all tests pass, try browser testing above"
echo "2. Check browser console for error messages"
echo "3. Check browser Network tab for /api/auth/refresh request"
echo "4. If still failing, run: tail -f /tmp/backend_server.log"
echo ""

# Cleanup
rm -f /tmp/session_test_cookies.txt
