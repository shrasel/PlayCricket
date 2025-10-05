/**
 * Authentication Service
 * 
 * Handles user authentication, token management, and session state.
 * Implements secure token storage and automatic refresh token rotation.
 * 
 * Features:
 * - Login/Logout/Registration
 * - JWT token management (in-memory storage)
 * - Automatic token refresh
 * - MFA support (TOTP)
 * - Password reset flows
 * - Session management
 * - Observable state for reactive UI
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, throwError, timer, EMPTY } from 'rxjs';
import { map, catchError, tap, switchMap, shareReplay } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

// ============================================================================
// Interfaces
// ============================================================================

export interface User {
  id: number;
  email: string;
  name: string;
  phone?: string;
  roles: string[];
  is_email_verified: boolean;
  mfa_enabled: boolean;
  status: 'active' | 'locked' | 'pending';
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  otp_code?: string;
  remember_device?: boolean;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  phone?: string;
  requested_role?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface MFASetupResponse {
  secret: string;
  qr_code: string;
  backup_codes: string[];
  uri: string;
}

export interface DeviceInfo {
  id: number;
  device_name?: string;
  user_agent?: string;
  ip_address?: string;
  created_at: string;
  expires_at: string;
  last_used_at?: string;
  is_current: boolean;
}

export interface PasswordStrength {
  score: number;
  strength: string;
  feedback?: string;
  warnings: string[];
  suggestions: string[];
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly API_URL = `${environment.apiUrl}/auth`;
  
  // In-memory token storage (more secure than localStorage)
  private accessToken: string | null = null;
  private tokenExpiryTimeout: any = null;
  
  // Observable state
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();
  
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(false);
  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();
  
  private isLoadingSubject = new BehaviorSubject<boolean>(false);
  public isLoading$ = this.isLoadingSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    // Try to restore session on service initialization
    this.restoreSession();
  }

  // ============================================================================
  // Public API
  // ============================================================================

  /**
   * Get current user (synchronous)
   */
  get currentUser(): User | null {
    return this.currentUserSubject.value;
  }

  /**
   * Get current access token
   */
  get token(): string | null {
    return this.accessToken;
  }

  /**
   * Check if user is authenticated (synchronous)
   */
  get isAuthenticated(): boolean {
    return this.isAuthenticatedSubject.value;
  }

  /**
   * Check if user has specific role
   */
  hasRole(role: string): boolean {
    return this.currentUser?.roles.includes(role) ?? false;
  }

  /**
   * Check if user has any of the specified roles
   */
  hasAnyRole(roles: string[]): boolean {
    return roles.some(role => this.hasRole(role));
  }

  /**
   * Check if user has all of the specified roles
   */
  hasAllRoles(roles: string[]): boolean {
    return roles.every(role => this.hasRole(role));
  }

  // ============================================================================
  // Authentication Methods
  // ============================================================================

  /**
   * User login
   */
  login(credentials: LoginRequest): Observable<User> {
    this.isLoadingSubject.next(true);
    
    return this.http.post<TokenResponse>(`${this.API_URL}/login`, credentials, {
      withCredentials: true // Send cookies for refresh token
    }).pipe(
      tap(response => this.handleAuthResponse(response)),
      map(response => response.user),
      catchError(error => this.handleAuthError(error)),
      tap(() => this.isLoadingSubject.next(false))
    );
  }

  /**
   * User registration
   */
  register(data: RegisterRequest): Observable<User> {
    this.isLoadingSubject.next(true);
    
    return this.http.post<User>(`${this.API_URL}/register`, data).pipe(
      catchError(error => this.handleAuthError(error)),
      tap(() => this.isLoadingSubject.next(false))
    );
  }

  /**
   * Logout current session
   */
  logout(): Observable<void> {
    return this.http.post<void>(`${this.API_URL}/logout`, {}, {
      withCredentials: true
    }).pipe(
      tap(() => this.clearAuthData()),
      catchError(() => {
        // Clear auth data even if logout fails
        this.clearAuthData();
        return EMPTY;
      })
    );
  }

  /**
   * Logout all devices
   */
  logoutAllDevices(): Observable<{ message: string; count: number }> {
    return this.http.post<{ message: string; count: number }>(
      `${this.API_URL}/devices/revoke-all`,
      {},
      { withCredentials: true }
    ).pipe(
      tap(() => this.clearAuthData()),
      catchError(error => this.handleAuthError(error))
    );
  }

  /**
   * Refresh access token using refresh token rotation
   */
  refreshToken(): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.API_URL}/refresh`, {}, {
      withCredentials: true // Send refresh token cookie
    }).pipe(
      tap(response => this.handleAuthResponse(response)),
      catchError(error => {
        // If refresh fails, clear auth and redirect to login
        this.clearAuthData();
        this.router.navigate(['/login']);
        return throwError(() => error);
      })
    );
  }

  // ============================================================================
  // Email Verification
  // ============================================================================

  /**
   * Verify email address with token
   */
  verifyEmail(token: string): Observable<{ message: string; email: string; status: string }> {
    return this.http.get<{ message: string; email: string; status: string }>(
      `${this.API_URL}/verify-email`,
      { params: { token } }
    ).pipe(
      catchError(error => this.handleAuthError(error))
    );
  }

  /**
   * Resend verification email
   */
  resendVerificationEmail(email: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(
      `${this.API_URL}/resend-verification`,
      { email }
    ).pipe(
      catchError(error => this.handleAuthError(error))
    );
  }

  // ============================================================================
  // Password Management
  // ============================================================================

  /**
   * Request password reset
   */
  forgotPassword(email: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(
      `${this.API_URL}/forgot-password`,
      { email }
    ).pipe(
      catchError(error => this.handleAuthError(error))
    );
  }

  /**
   * Reset password with token
   */
  resetPassword(token: string, newPassword: string): Observable<{ message: string; email: string }> {
    return this.http.post<{ message: string; email: string }>(
      `${this.API_URL}/reset-password`,
      { token, new_password: newPassword }
    ).pipe(
      catchError(error => this.handleAuthError(error))
    );
  }

  /**
   * Change password (requires current password)
   */
  changePassword(currentPassword: string, newPassword: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(
      `${this.API_URL}/change-password`,
      { current_password: currentPassword, new_password: newPassword }
    ).pipe(
      catchError(error => this.handleAuthError(error))
    );
  }

  /**
   * Check password strength
   */
  checkPasswordStrength(password: string): Observable<PasswordStrength> {
    return this.http.post<PasswordStrength>(
      `${this.API_URL}/check-password-strength`,
      { password }
    ).pipe(
      catchError(error => this.handleAuthError(error))
    );
  }

  // ============================================================================
  // MFA (Multi-Factor Authentication)
  // ============================================================================

  /**
   * Setup MFA - generate QR code and backup codes
   */
  setupMFA(): Observable<MFASetupResponse> {
    return this.http.get<MFASetupResponse>(`${this.API_URL}/mfa/setup`).pipe(
      catchError(error => this.handleAuthError(error))
    );
  }

  /**
   * Enable MFA after verifying setup
   */
  enableMFA(secret: string, verificationCode: string, backupCodes: string[]): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(
      `${this.API_URL}/mfa/enable`,
      {
        secret,
        verification_code: verificationCode,
        backup_codes: backupCodes
      }
    ).pipe(
      tap(() => {
        // Update current user's mfa_enabled status
        if (this.currentUser) {
          const updatedUser = { ...this.currentUser, mfa_enabled: true };
          this.currentUserSubject.next(updatedUser);
        }
      }),
      catchError(error => this.handleAuthError(error))
    );
  }

  /**
   * Disable MFA (requires password)
   */
  disableMFA(password: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(
      `${this.API_URL}/mfa/disable`,
      { password }
    ).pipe(
      tap(() => {
        // Update current user's mfa_enabled status
        if (this.currentUser) {
          const updatedUser = { ...this.currentUser, mfa_enabled: false };
          this.currentUserSubject.next(updatedUser);
        }
      }),
      catchError(error => this.handleAuthError(error))
    );
  }

  // ============================================================================
  // Profile Management
  // ============================================================================

  /**
   * Get current user profile
   */
  getCurrentProfile(): Observable<User> {
    return this.http.get<User>(`${this.API_URL}/me`).pipe(
      tap(user => this.currentUserSubject.next(user)),
      catchError(error => this.handleAuthError(error))
    );
  }

  /**
   * Update user profile
   */
  updateProfile(data: { name?: string; phone?: string }): Observable<User> {
    return this.http.put<User>(`${this.API_URL}/me`, data).pipe(
      tap(user => this.currentUserSubject.next(user)),
      catchError(error => this.handleAuthError(error))
    );
  }

  // ============================================================================
  // Session/Device Management
  // ============================================================================

  /**
   * Get list of active devices/sessions
   */
  getActiveDevices(): Observable<DeviceInfo[]> {
    return this.http.get<{ devices: DeviceInfo[]; total: number }>(
      `${this.API_URL}/devices`
    ).pipe(
      map(response => response.devices),
      catchError(error => this.handleAuthError(error))
    );
  }

  /**
   * Revoke specific device/session
   */
  revokeDevice(deviceId: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(
      `${this.API_URL}/devices/${deviceId}`
    ).pipe(
      catchError(error => this.handleAuthError(error))
    );
  }

  // ============================================================================
  // Session Management (Internal)
  // ============================================================================

  /**
   * Restore session from refresh token
   */
  private restoreSession(): void {
    // Try to refresh token on app initialization
    // The refresh token is in httpOnly cookie, so we just call the endpoint
    this.http.post<TokenResponse>(`${this.API_URL}/refresh`, {}, {
      withCredentials: true
    }).subscribe({
      next: (response) => {
        this.handleAuthResponse(response);
      },
      error: () => {
        // No valid session, that's okay
        this.clearAuthData();
      }
    });
  }

  /**
   * Handle successful authentication response
   */
  private handleAuthResponse(response: TokenResponse): void {
    // Store access token in memory
    this.accessToken = response.access_token;
    
    // Update user state
    this.currentUserSubject.next(response.user);
    this.isAuthenticatedSubject.next(true);
    
    // Setup automatic token refresh before expiry
    this.scheduleTokenRefresh(response.expires_in);
  }

  /**
   * Schedule automatic token refresh
   * Refreshes 1 minute before expiry
   */
  private scheduleTokenRefresh(expiresIn: number): void {
    // Clear any existing timeout
    if (this.tokenExpiryTimeout) {
      clearTimeout(this.tokenExpiryTimeout);
    }
    
    // Refresh 1 minute (60 seconds) before expiry
    const refreshTime = (expiresIn - 60) * 1000;
    
    if (refreshTime > 0) {
      this.tokenExpiryTimeout = setTimeout(() => {
        this.refreshToken().subscribe({
          error: () => {
            // Refresh failed, logout user
            this.clearAuthData();
            this.router.navigate(['/login']);
          }
        });
      }, refreshTime);
    }
  }

  /**
   * Clear all authentication data
   */
  private clearAuthData(): void {
    // Clear token
    this.accessToken = null;
    
    // Clear timeout
    if (this.tokenExpiryTimeout) {
      clearTimeout(this.tokenExpiryTimeout);
      this.tokenExpiryTimeout = null;
    }
    
    // Update state
    this.currentUserSubject.next(null);
    this.isAuthenticatedSubject.next(false);
  }

  /**
   * Handle authentication errors
   */
  private handleAuthError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = error.error.message;
    } else {
      // Server-side error
      errorMessage = error.error?.detail || error.message;
    }
    
    return throwError(() => new Error(errorMessage));
  }
}
