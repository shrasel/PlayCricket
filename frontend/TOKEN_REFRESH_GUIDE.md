# Token Management & Auto-Refresh Implementation Guide

## How the System Works

### Token Lifecycle
1. **Login** → Receive:
   - `access_token`: Valid for **1 hour** (3600 seconds)
   - `refresh_token`: Valid for **30 days** (stored in httpOnly cookie)

2. **API Calls** → Use `access_token` in Authorization header:
   ```
   Authorization: Bearer <access_token>
   ```

3. **Token Expires** (after 1 hour) → Call `/api/auth/refresh` to get new token

4. **Refresh Token** → Automatically rotates (old one invalidated, new one issued)

## Implementation Strategy

### Option 1: Automatic Refresh with HTTP Interceptor (Recommended)

This automatically refreshes the token when it's about to expire or has expired.

#### 1. Create Token Service (`src/app/core/services/token.service.ts`)

```typescript
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface TokenData {
  access_token: string;
  token_type: string;
  expires_in: number; // seconds
  expires_at?: number; // timestamp when token expires
}

@Injectable({
  providedIn: 'root'
})
export class TokenService {
  private readonly TOKEN_KEY = 'access_token';
  private readonly EXPIRES_AT_KEY = 'token_expires_at';
  private tokenSubject = new BehaviorSubject<string | null>(this.getToken());

  constructor() {}

  setToken(tokenData: TokenData): void {
    const expiresAt = Date.now() + (tokenData.expires_in * 1000);
    localStorage.setItem(this.TOKEN_KEY, tokenData.access_token);
    localStorage.setItem(this.EXPIRES_AT_KEY, expiresAt.toString());
    this.tokenSubject.next(tokenData.access_token);
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  getTokenObservable(): Observable<string | null> {
    return this.tokenSubject.asObservable();
  }

  clearToken(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.EXPIRES_AT_KEY);
    this.tokenSubject.next(null);
  }

  isTokenExpired(): boolean {
    const expiresAt = localStorage.getItem(this.EXPIRES_AT_KEY);
    if (!expiresAt) return true;
    
    // Consider token expired 5 minutes before actual expiry
    const bufferTime = 5 * 60 * 1000; // 5 minutes
    return Date.now() > (parseInt(expiresAt) - bufferTime);
  }

  getTokenExpiryTime(): number | null {
    const expiresAt = localStorage.getItem(this.EXPIRES_AT_KEY);
    return expiresAt ? parseInt(expiresAt) : null;
  }

  getTimeUntilExpiry(): number {
    const expiresAt = this.getTokenExpiryTime();
    if (!expiresAt) return 0;
    return Math.max(0, expiresAt - Date.now());
  }
}
```

#### 2. Update Auth Service (`src/app/core/services/auth.service.ts`)

Add refresh token method:

```typescript
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { TokenService, TokenData } from './token.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private refreshInProgress = false;

  constructor(
    private http: HttpClient,
    private tokenService: TokenService
  ) {}

  login(email: string, password: string): Observable<any> {
    return this.http.post<any>(`${environment.apiUrl}/auth/login`, {
      email,
      password
    }, {
      withCredentials: true // Important: send cookies
    }).pipe(
      tap(response => {
        this.tokenService.setToken({
          access_token: response.access_token,
          token_type: response.token_type,
          expires_in: response.expires_in
        });
      })
    );
  }

  refreshToken(): Observable<any> {
    if (this.refreshInProgress) {
      // Already refreshing, return null or throw
      return throwError(() => new Error('Refresh already in progress'));
    }

    this.refreshInProgress = true;
    
    return this.http.post<any>(`${environment.apiUrl}/auth/refresh`, {}, {
      withCredentials: true // Important: send refresh_token cookie
    }).pipe(
      tap(response => {
        this.tokenService.setToken({
          access_token: response.access_token,
          token_type: response.token_type,
          expires_in: response.expires_in
        });
        this.refreshInProgress = false;
      }),
      catchError(error => {
        this.refreshInProgress = false;
        // Refresh failed - logout user
        this.logout();
        return throwError(() => error);
      })
    );
  }

  logout(): void {
    this.tokenService.clearToken();
    // Clear refresh token cookie by calling backend logout endpoint
    this.http.post(`${environment.apiUrl}/auth/logout`, {}, {
      withCredentials: true
    }).subscribe();
  }
}
```

#### 3. Create HTTP Interceptor (`src/app/core/interceptors/auth.interceptor.ts`)

```typescript
import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, filter, take, switchMap } from 'rxjs/operators';
import { TokenService } from '../services/token.service';
import { AuthService } from '../services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private isRefreshing = false;
  private refreshTokenSubject: BehaviorSubject<any> = new BehaviorSubject<any>(null);

  constructor(
    private tokenService: TokenService,
    private authService: AuthService
  ) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    // Add token to request if available
    const token = this.tokenService.getToken();
    
    if (token && !this.isLoginOrRefreshUrl(request.url)) {
      request = this.addToken(request, token);
    }

    return next.handle(request).pipe(
      catchError(error => {
        if (error instanceof HttpErrorResponse && error.status === 401) {
          return this.handle401Error(request, next);
        }
        return throwError(() => error);
      })
    );
  }

  private addToken(request: HttpRequest<any>, token: string): HttpRequest<any> {
    return request.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      },
      withCredentials: true // Important for cookies
    });
  }

  private handle401Error(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (!this.isRefreshing) {
      this.isRefreshing = true;
      this.refreshTokenSubject.next(null);

      return this.authService.refreshToken().pipe(
        switchMap((response: any) => {
          this.isRefreshing = false;
          this.refreshTokenSubject.next(response.access_token);
          return next.handle(this.addToken(request, response.access_token));
        }),
        catchError((err) => {
          this.isRefreshing = false;
          this.authService.logout();
          return throwError(() => err);
        })
      );
    } else {
      // Wait for refresh to complete
      return this.refreshTokenSubject.pipe(
        filter(token => token != null),
        take(1),
        switchMap(token => {
          return next.handle(this.addToken(request, token));
        })
      );
    }
  }

  private isLoginOrRefreshUrl(url: string): boolean {
    return url.includes('/auth/login') || 
           url.includes('/auth/refresh') ||
           url.includes('/auth/register');
  }
}
```

#### 4. Register Interceptor in `app.config.ts`

```typescript
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { AuthInterceptor } from './core/interceptors/auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withInterceptors([authInterceptor])
    ),
    // ... other providers
  ]
};
```

### Option 2: Proactive Refresh (Before Expiry)

Add a timer-based refresh in your auth service:

```typescript
import { interval } from 'rxjs';

export class AuthService {
  private refreshTimer: any;

  startTokenRefreshTimer(): void {
    // Check every minute
    this.refreshTimer = interval(60000).subscribe(() => {
      if (this.tokenService.isTokenExpired()) {
        this.refreshToken().subscribe();
      }
    });
  }

  stopTokenRefreshTimer(): void {
    if (this.refreshTimer) {
      this.refreshTimer.unsubscribe();
    }
  }

  login(email: string, password: string): Observable<any> {
    return this.http.post(/*...*/).pipe(
      tap(response => {
        this.tokenService.setToken(response);
        this.startTokenRefreshTimer(); // Start auto-refresh
      })
    );
  }

  logout(): void {
    this.stopTokenRefreshTimer(); // Stop auto-refresh
    this.tokenService.clearToken();
  }
}
```

## Best Practices

### 1. **Never call refresh on every API request**
- Only refresh when token is expired or about to expire
- Use interceptor to handle 401 responses automatically

### 2. **Token Storage**
- ✅ Store `access_token` in localStorage or sessionStorage
- ✅ Store `refresh_token` in httpOnly cookie (automatic, secure)
- ❌ Never store refresh_token in localStorage (XSS vulnerability)

### 3. **Security Considerations**
- Always use `withCredentials: true` for refresh endpoint
- Clear tokens on logout
- Handle refresh failures gracefully (logout user)
- Implement token reuse detection (already done in backend)

### 4. **User Experience**
- Show loading state during token refresh
- Don't interrupt user with login prompts during auto-refresh
- Only redirect to login if refresh fails

## Testing the Implementation

### 1. Test Login
```typescript
this.authService.login('email@example.com', 'password').subscribe({
  next: (response) => {
    console.log('Logged in!', response);
    console.log('Token expires in:', response.expires_in, 'seconds');
  }
});
```

### 2. Test Auto-Refresh
Wait 1 hour (or modify expiry time for testing) and make an API call. The interceptor should automatically refresh the token.

### 3. Test Manual Refresh
```typescript
this.authService.refreshToken().subscribe({
  next: (response) => {
    console.log('Token refreshed!', response);
  }
});
```

## Current Token Configuration

- **Access Token**: 1 hour (3600 seconds)
- **Refresh Token**: 30 days
- **Token Rotation**: Enabled (old refresh token invalidated when new one issued)
- **Reuse Detection**: Enabled (all tokens revoked if reuse detected)

## Summary

With this implementation:
1. ✅ User logs in once
2. ✅ Access token is used for 1 hour
3. ✅ After 1 hour, token auto-refreshes seamlessly
4. ✅ User stays logged in for 30 days without re-entering credentials
5. ✅ Security is maintained with httpOnly cookies and token rotation
