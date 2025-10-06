# Session Restore After Page Refresh - Test Guide

## Problem Fixed
After successful login, refreshing the page was logging users out because the `AuthService` wasn't being initialized on app startup.

## Solution Implemented
Updated `app.component.ts` to inject `AuthService` in the constructor. This ensures:
1. AuthService is initialized when the app starts
2. The `restoreSession()` method is called automatically
3. If a valid refresh token exists in the httpOnly cookie, a new access token is obtained
4. User remains logged in after page refresh

## How It Works

### Token Storage Strategy
- **Access Token**: Stored in-memory (not localStorage for security)
- **Refresh Token**: Stored in httpOnly cookie (cannot be accessed by JavaScript, prevents XSS attacks)
- **Expiry**: Access token = 1 hour, Refresh token = 30 days

### Session Restore Flow
1. User logs in → receives access token (in memory) + refresh token (httpOnly cookie)
2. User closes browser tab or refreshes page → access token is lost from memory
3. On app initialization → `AppComponent` constructor runs
4. `AuthService` constructor calls `restoreSession()`
5. `restoreSession()` calls `/api/auth/refresh` endpoint with cookie
6. Backend validates refresh token cookie
7. Backend returns new access token + rotated refresh token
8. User is automatically logged back in without re-entering credentials

### Code Changes

**File: `frontend/src/app/app.component.ts`**

```typescript
import { AuthService } from '@core/services/auth.service';

export class AppComponent {
  constructor(private authService: AuthService) {
    // Initialize AuthService to trigger restoreSession() in constructor
  }
}
```

**File: `frontend/src/app/core/services/auth.service.ts`** (already implemented)

```typescript
constructor(private http: HttpClient, private router: Router) {
  this.restoreSession(); // Called automatically
}

private restoreSession(): void {
  this.http.post<TokenResponse>(`${this.API_URL}/refresh`, {}, {
    withCredentials: true // Sends httpOnly cookie
  }).subscribe({
    next: (response) => {
      this.handleAuthResponse(response); // Restores user session
    },
    error: () => {
      this.clearAuthData(); // No valid session
    }
  });
}
```

## Testing Steps

### Test 1: Login and Refresh Page
1. Open browser at `http://localhost:4200`
2. Navigate to login page
3. Login with credentials:
   - Email: `shahjahan.rasell@gmail.com`
   - Password: `Asdfg!123`
4. Verify you're redirected to dashboard/home
5. **Refresh the page (F5 or Cmd+R)**
6. ✅ **Expected**: You should remain logged in
7. ❌ **Previous behavior**: You were logged out

### Test 2: Close and Reopen Browser Tab
1. Login successfully
2. Close the browser tab completely
3. Open new tab and navigate to `http://localhost:4200`
4. ✅ **Expected**: You should be automatically logged in
5. Note: This works because the refresh token cookie persists across browser sessions

### Test 3: Clear Cookies
1. Login successfully
2. Open browser DevTools → Application/Storage → Cookies
3. Delete all cookies for `localhost:8000`
4. Refresh the page
5. ✅ **Expected**: You should be logged out (no refresh token available)
6. This is correct behavior - user needs to login again

### Test 4: Token Expiry After 30 Days
1. Login successfully
2. Wait 30 days (or manually expire the refresh token in database)
3. Refresh the page
4. ✅ **Expected**: You should be logged out and redirected to login
5. This is correct security behavior

## Security Benefits

### Why This Approach is Secure

1. **In-Memory Access Token**
   - Not stored in localStorage
   - Prevents XSS attacks from stealing token
   - Lost on page refresh (by design)

2. **HttpOnly Refresh Token**
   - Cannot be accessed by JavaScript
   - Prevents XSS attacks
   - Automatically sent with requests to same domain
   - 30-day expiry reduces need for frequent logins

3. **Token Rotation**
   - Old refresh token invalidated when new one issued
   - Prevents token reuse attacks
   - Entire token family revoked if reuse detected

4. **Short-Lived Access Token**
   - 1-hour expiry reduces risk window
   - Even if stolen, expires quickly
   - Automatically refreshed before expiry

## Browser DevTools Verification

### Check Cookies (DevTools → Application → Cookies)
After login, you should see:
```
Name: refresh_token
Value: <encrypted_token>
Domain: localhost
Path: /
HttpOnly: ✓ (Yes)
Secure: ✓ (Yes in production)
SameSite: Lax
Expires: <30 days from now>
```

### Check Network Tab (DevTools → Network)
On page refresh, you should see:
```
POST /api/auth/refresh
Status: 200 OK
Request Headers:
  Cookie: refresh_token=...
Response:
  {
    "access_token": "eyJhbGci...",
    "expires_in": 3600,
    "user": {...}
  }
```

### Check Console (DevTools → Console)
No errors should appear. Session should be silently restored.

## Common Issues & Troubleshooting

### Issue: Still getting logged out on refresh
**Solution**:
1. Check browser DevTools → Network tab
2. Look for `/api/auth/refresh` request on page load
3. If 401 Unauthorized:
   - Refresh token expired (>30 days old)
   - Refresh token revoked
   - Cookie not being sent
4. If no request at all:
   - Angular server not reloaded with changes
   - Restart: `cd frontend && npm start`

### Issue: "Cannot read property 'value' of null"
**Solution**:
- AuthService not initialized
- Make sure `app.component.ts` has the fix applied
- Restart Angular dev server

### Issue: CORS errors on /refresh endpoint
**Solution**:
Add to `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,  # Important!
    allow_origins=["http://localhost:4200"],
)
```

### Issue: Cookie not being sent
**Solution**:
Check `withCredentials: true` in all HTTP calls:
```typescript
this.http.post(url, data, {
  withCredentials: true  // Required for cookies
})
```

## Production Deployment Notes

When deploying to production:

1. **Update CORS settings** to match production domain
2. **Enable HTTPS** (required for Secure cookies)
3. **Set SameSite=Strict** for production cookies
4. **Configure cookie domain** to match production domain
5. **Set secure cookie flags** in backend

**Backend changes for production** (`backend/app/core/security/jwt.py`):
```python
response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,
    secure=True,  # Requires HTTPS
    samesite="strict",  # Stricter in production
    domain=".yourdomain.com",  # Your production domain
    max_age=30 * 24 * 60 * 60
)
```

## Summary

✅ **Fix Applied**: AppComponent now injects AuthService on startup
✅ **Session Restore**: Automatic via refresh token cookie
✅ **Security**: In-memory access token + httpOnly refresh token
✅ **User Experience**: Stay logged in for 30 days without re-authentication
✅ **Token Rotation**: Automatic security protection

The session restore now works seamlessly. Users will remain logged in across:
- Page refreshes
- Browser tab closes/reopens
- Browser restarts
- Up to 30 days without re-login
