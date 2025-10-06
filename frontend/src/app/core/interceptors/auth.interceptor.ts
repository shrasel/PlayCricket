/**
 * Authentication Interceptor
 * 
 * Automatically attaches JWT access token to outgoing HTTP requests.
 * Handles 401 Unauthorized responses by attempting token refresh.
 * 
 * Features:
 * - Adds Authorization header with Bearer token
 * - Automatic token refresh on 401 errors
 * - Prevents infinite refresh loops
 * - Logout on refresh failure
 */

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
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private isRefreshing = false;
  private refreshTokenSubject = new BehaviorSubject<string | null>(null);

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    console.log('🌐 HTTP Request:', request.method, request.url);
    
    // Add auth token to request if available
    const modifiedRequest = this.addToken(request);
    
    console.log('  - Has Authorization header:', modifiedRequest.headers.has('Authorization'));
    
    return next.handle(modifiedRequest).pipe(
      catchError(error => {
        if (error instanceof HttpErrorResponse) {
          console.error('❌ HTTP Error:', error.status, error.statusText, 'for', request.url);
          
          if (error.status === 401) {
            // Handle 401 Unauthorized errors
            return this.handle401Error(modifiedRequest, next);
          }
        }
        
        return throwError(() => error);
      })
    );
  }

  /**
   * Add Authorization header with access token
   */
  private addToken(request: HttpRequest<unknown>): HttpRequest<unknown> {
    const token = this.authService.token;
    
    console.log('🔒 Auth Interceptor - URL:', request.url);
    console.log('🔑 Auth Interceptor - Token available:', !!token);
    
    if (token) {
      console.log('✅ Adding Authorization header to request');
      console.log('   Token (first 30 chars):', token.substring(0, 30) + '...');
      
      const cloned = request.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        },
        withCredentials: true // Include cookies for refresh token
      });
      
      console.log('   Authorization header set:', cloned.headers.get('Authorization')?.substring(0, 40) + '...');
      return cloned;
    }
    
    console.log('⚠️ No token available, sending request without Authorization header');
    return request.clone({
      withCredentials: true
    });
  }

  /**
   * Handle 401 Unauthorized by attempting token refresh
   */
  private handle401Error(
    request: HttpRequest<unknown>,
    next: HttpHandler
  ): Observable<HttpEvent<unknown>> {
    // Don't try to refresh if already refreshing or if it's the refresh endpoint
    if (request.url.includes('/auth/refresh') || request.url.includes('/auth/login')) {
      return throwError(() => new Error('Authentication failed'));
    }
    
    if (!this.isRefreshing) {
      this.isRefreshing = true;
      this.refreshTokenSubject.next(null);
      
      return this.authService.refreshToken().pipe(
        switchMap((response) => {
          this.isRefreshing = false;
          this.refreshTokenSubject.next(response.access_token);
          
          // Retry the failed request with new token
          return next.handle(this.addToken(request));
        }),
        catchError((error) => {
          this.isRefreshing = false;
          
          // Refresh failed, logout user
          this.authService.logout().subscribe();
          this.router.navigate(['/login']);
          
          return throwError(() => error);
        })
      );
    } else {
      // Wait for refresh to complete
      return this.refreshTokenSubject.pipe(
        filter(token => token !== null),
        take(1),
        switchMap(() => {
          // Retry the failed request with new token
          return next.handle(this.addToken(request));
        })
      );
    }
  }
}

