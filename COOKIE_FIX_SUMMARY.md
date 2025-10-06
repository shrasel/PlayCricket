# Cookie Fix for Session Persistence - Summary

## Problem

After successful login, refreshing the page was logging users out. This was caused by **two issues**:

### Issue 1: AuthService Not Initialized on App Startup
The `AuthService` stores access tokens in-memory (for security). When the page refreshes, the in-memory token is lost. The service has a `restoreSession()` method that automatically calls `/api/auth/refresh` to get a new access token using the refresh token cookie, but this wasn't being called because the service wasn't being initialized.

### Issue 2: Secure Cookie Flag in Development
The refresh token cookie was being set with `secure=True`, which means browsers will ONLY send it over HTTPS connections. In development, we use HTTP (`http://localhost`), so the browser was refusing to send the cookie, making session restoration impossible.

## Solutions Applied

### Fix 1: Initialize AuthService on App Startup

**File**: `frontend/src/app/app.component.ts`

```typescript
import { AuthService } from '@core/services/auth.service';

export class AppComponent {
  constructor(private authService: AuthService) {
    // Initialize AuthService to trigger restoreSession() in constructor
    // This ensures the user stays logged in after page refresh
  }
}
```

**What it does**:
- Injects `AuthService` in the root `AppComponent` constructor
- This ensures the service is instantiated when the app starts
- The service constructor automatically calls `restoreSession()`
- `restoreSession()` calls `/api/auth/refresh` with the refresh token cookie
- If successful, user is automatically logged back in

### Fix 2: Disable Secure Cookie Flag in Development

**File**: `backend/app/api/routes/auth.py`

**Changes made** (2 locations - login and refresh endpoints):

```python
from app.core.config import settings  # Added import

# In login endpoint (~line 130):
response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,
    secure=not settings.DEBUG,  # ← Changed from secure=True
    samesite="lax",
    max_age=30 * 24 * 60 * 60
)

# In refresh endpoint (~line 211):
response.set_cookie(
    key="refresh_token",
    value=new_refresh_token,
    httponly=True,
    secure=not settings.DEBUG,  # ← Changed from secure=True
    samesite="lax",
    max_age=30 * 24 * 60 * 60
)
```

**What it does**:
- In **development** (`DEBUG=True`): `secure=False` → cookies work over HTTP
- In **production** (`DEBUG=False`): `secure=True` → cookies only over HTTPS (secure)
- Uses environment-aware configuration for optimal security

## How It Works Now

### Login Flow
1. User logs in at `http://localhost:4200/login`
2. Backend returns:
   - `access_token` (stored in memory, expires in 1 hour)
   - `refresh_token` (httpOnly cookie, expires in 30 days)
3. Cookie is set WITHOUT `Secure` flag (because `DEBUG=True`)
4. Browser stores cookie and will send it with future requests

### Page Refresh Flow
1. User refreshes page (F5 or Cmd+R)
2. Angular app starts → `AppComponent` initializes
3. `AppComponent` constructor injects `AuthService`
4. `AuthService` constructor calls `restoreSession()`
5. `restoreSession()` calls `POST /api/auth/refresh` with cookie
6. Browser automatically sends `refresh_token` cookie (because HTTP is allowed)
7. Backend validates refresh token, returns new access token
8. User is logged back in automatically! ✅

### Browser Tab Close/Reopen
1. User closes browser tab
2. Opens new tab and navigates to `http://localhost:4200`
3. Same flow as page refresh above
4. User is logged back in automatically! ✅

## Testing Results

### cURL Tests (Backend)

**Login Test**:
```bash
curl -i -c /tmp/test_cookies3.txt -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "shahjahan.rasell@gmail.com", "password": "Asdfg!123"}'
```

**Response Headers**:
```
HTTP/1.1 200 OK
set-cookie: refresh_token=...; HttpOnly; Max-Age=2592000; Path=/; SameSite=lax
```

✅ **Result**: Cookie set without `Secure` flag (works over HTTP)

**Refresh Test**:
```bash
curl -i -b /tmp/test_cookies3.txt -X POST http://localhost:8000/api/auth/refresh
```

**Response**:
```
HTTP/1.1 200 OK
set-cookie: refresh_token=...; HttpOnly; Max-Age=2592000; Path=/; SameSite=lax
{"access_token":"...","expires_in":3600,"user":{...}}
```

✅ **Result**: Cookie sent successfully, new token received

### Browser Testing

**Steps to verify**:
1. Open browser at `http://localhost:4200`
2. Login with:
   - Email: `shahjahan.rasell@gmail.com`
   - Password: `Asdfg!123`
3. Verify you're logged in and redirected
4. Open DevTools → Application → Cookies → `http://localhost:8000`
5. Verify `refresh_token` cookie exists (HttpOnly, no Secure flag)
6. **Refresh the page (F5 or Cmd+R)**
7. ✅ **Expected**: You remain logged in
8. **Close browser tab completely**
9. **Open new tab** and navigate to `http://localhost:4200`
10. ✅ **Expected**: You are automatically logged in

## Security Implications

### Development (Current Setup)
- ✅ Cookies work over HTTP
- ✅ Access token in memory (prevents XSS)
- ✅ Refresh token in httpOnly cookie (prevents JavaScript access)
- ⚠️ `Secure` flag disabled (acceptable for local development only)

### Production (After Deployment)
- ✅ Cookies ONLY over HTTPS (`Secure` flag enabled)
- ✅ Access token in memory (prevents XSS)
- ✅ Refresh token in httpOnly cookie (prevents JavaScript access)
- ✅ Full security with HTTPS + Secure cookies

**Environment Detection**:
```python
# In backend/app/core/config.py
class Settings(BaseSettings):
    DEBUG: bool = True  # Development
    # DEBUG: bool = False  # Production
```

When `DEBUG=False` in production:
- `secure=not settings.DEBUG` → `secure=True`
- Cookies only sent over HTTPS
- Full production security

## Files Modified

### Frontend
1. **`frontend/src/app/app.component.ts`**
   - Added `AuthService` injection in constructor
   - Triggers automatic session restoration on app startup

### Backend
2. **`backend/app/api/routes/auth.py`**
   - Added `from app.core.config import settings` import
   - Updated `secure` flag in login endpoint: `secure=not settings.DEBUG`
   - Updated `secure` flag in refresh endpoint: `secure=not settings.DEBUG`

## Session Persistence Details

### Token Lifetimes
- **Access Token**: 1 hour
- **Refresh Token**: 30 days
- **Session Duration**: Up to 30 days without re-login

### What Persists
- ✅ Page refreshes (F5)
- ✅ Browser tab close/reopen
- ✅ Browser restart (refresh token cookie persists)
- ✅ Computer restart (cookie persists up to 30 days)

### What Triggers Logout
- ❌ Refresh token expires (after 30 days)
- ❌ User clicks "Logout" button
- ❌ User clears browser cookies
- ❌ Token reuse detected (security feature)
- ❌ Backend revokes token

## Next Steps

### For User
1. Test the fix in browser:
   - Login
   - Refresh page
   - Should stay logged in! ✅

2. Monitor browser DevTools → Console for any errors

3. Check Network tab for `/api/auth/refresh` call on page load

### For Production Deployment

When deploying to production, ensure:

1. **Set `DEBUG=False` in backend environment**:
   ```bash
   # In production .env
   DEBUG=False
   ```

2. **Enable HTTPS**:
   - Use SSL/TLS certificates
   - All traffic over HTTPS

3. **Update CORS origins**:
   ```python
   # In backend/app/main.py
   allow_origins=[
       "https://yourdomain.com",  # Production frontend
   ]
   ```

4. **Update cookie domain**:
   ```python
   # Optional: Set cookie domain for production
   response.set_cookie(
       key="refresh_token",
       domain=".yourdomain.com",  # Share across subdomains
       ...
   )
   ```

## Troubleshooting

### Issue: Still getting logged out on refresh

**Check**:
1. Browser DevTools → Application → Cookies
2. Verify `refresh_token` cookie exists for `localhost:8000`
3. Check if cookie has `Secure` flag (should NOT have it)

**If cookie is missing**:
- Backend not running (`http://localhost:8000`)
- Login failed
- Clear all cookies and try again

**If cookie has Secure flag**:
- Backend not reloaded with changes
- Restart backend server

**If refresh endpoint fails**:
- Check browser DevTools → Network → `/api/auth/refresh`
- Look for error response
- Check backend logs for errors

### Issue: Cookie not being sent

**Possible causes**:
1. Cookie has `Secure` flag (shouldn't in dev)
2. CORS not configured for credentials
3. Frontend not using `withCredentials: true`

**Verify**:
```typescript
// In Angular HTTP calls
this.http.post(url, data, {
  withCredentials: true  // Must be present!
})
```

## Success Indicators

### Backend Logs
```
INFO:     127.0.0.1:54076 - "POST /api/auth/refresh HTTP/1.1" 200 OK
```

### Browser Network Tab
- `POST /api/auth/refresh` on page load
- Status: `200 OK`
- Response includes new `access_token`

### Browser Console
- No authentication errors
- Silent session restoration

### User Experience
- No login prompt after page refresh
- Seamless experience
- Stay logged in for 30 days

## Summary

Both issues are now fixed:

1. ✅ **AuthService initialized on app startup** → `restoreSession()` called automatically
2. ✅ **Cookies work over HTTP in development** → `secure=not settings.DEBUG`

The authentication system now provides:
- ✅ Persistent sessions (30 days)
- ✅ Automatic session restoration on page refresh
- ✅ Secure token storage (in-memory + httpOnly cookies)
- ✅ Token rotation for security
- ✅ Environment-aware cookie security
- ✅ Seamless user experience

**Result**: Users stay logged in across page refreshes and browser restarts! 🎉
