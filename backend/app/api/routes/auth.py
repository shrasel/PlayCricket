"""
Authentication API Routes

Endpoints for user authentication, registration, MFA, and session management.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Header
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies.auth import (
    get_current_user, get_current_active_user, get_optional_user
)
from app.models.auth import User
from app.schemas.auth import (
    UserRegister, UserLogin, TokenResponse, UserProfile,
    RefreshTokenRequest, EmailVerificationRequest, ResendVerificationEmail,
    ForgotPasswordRequest, ResetPasswordRequest,
    MFASetupResponse, MFAEnableRequest, MFADisableRequest, MFAVerifyRequest,
    RefreshTokenInfo, DeviceList, RevokeDeviceRequest,
    ChangePassword, UpdateProfile, PasswordStrengthRequest, PasswordStrengthResponse
)
from app.services import (
    AuthService, UserService, AuthenticationError,
    RegistrationError, LoginError, MFAError
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Extract user agent from request"""
    return request.headers.get("User-Agent", "unknown")


# ============================================================================
# Public Endpoints (No Authentication Required)
# ============================================================================

@router.post("/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def register(
    registration: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account
    
    - **email**: Valid email address (will be lowercased)
    - **password**: Strong password (8-128 chars, validated for strength)
    - **name**: User's full name
    - **phone**: Optional phone number
    - **requested_role**: Optional role code (default: VIEWER)
    
    Returns user profile and sends verification email.
    Password is hashed with Argon2id before storage.
    """
    auth_service = AuthService(db)
    
    try:
        user, verification_token = await auth_service.register_user(
            registration,
            ip_address=get_client_ip(request)
        )
        
        # TODO: Send verification email with token
        # For now, log the token (in production, send via email service)
        print(f"Verification token for {user.email}: {verification_token}")
        print(f"Verification URL: http://localhost:4200/verify-email?token={verification_token}")
        
        return UserProfile(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
            roles=user.get_roles(),
            is_email_verified=user.is_email_verified,
            mfa_enabled=user.mfa_enabled,
            status=user.status,
            last_login_at=user.last_login_at,
            created_at=user.created_at
        )
    
    except RegistrationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and get access token
    
    - **email**: User's email address
    - **password**: User's password
    - **otp_code**: Optional MFA code (required if MFA is enabled)
    - **remember_device**: Optional flag to extend refresh token expiry
    
    Returns access token (15 min) and refresh token (30 days).
    Refresh token is set in httpOnly cookie for security.
    """
    auth_service = AuthService(db)
    
    try:
        user, access_token, refresh_token = await auth_service.authenticate_user(
            login_data,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        # Set refresh token in httpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,  # HTTPS only in production
            samesite="lax",
            max_age=30 * 24 * 60 * 60  # 30 days
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=60 * 60,  # 1 hour in seconds
            user=UserProfile(
                id=user.id,
                email=user.email,
                name=user.name,
                phone=user.phone,
                roles=user.get_roles(),
                is_email_verified=user.is_email_verified,
                mfa_enabled=user.mfa_enabled,
                status=user.status,
                last_login_at=user.last_login_at,
                created_at=user.created_at
            )
        )
    
    except LoginError as e:
        if e.error_code == "MFA_REQUIRED":
            raise HTTPException(
                status_code=status.HTTP_428_PRECONDITION_REQUIRED,
                detail=e.message
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except MFAError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response,
    request: Request,
    refresh_token: Optional[str] = Header(None, alias="X-Refresh-Token"),
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token rotation
    
    Accepts refresh token from:
    1. X-Refresh-Token header (for API clients)
    2. refresh_token cookie (for web browsers)
    
    Returns new access token and new refresh token.
    Implements automatic token rotation and reuse detection.
    """
    # Try to get refresh token from cookie if not in header
    if not refresh_token:
        refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not provided"
        )
    
    auth_service = AuthService(db)
    
    try:
        new_access_token, new_refresh_token = await auth_service.refresh_access_token(
            refresh_token,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        # Update refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=30 * 24 * 60 * 60
        )
        
        # Get user info for response
        user_service = UserService(db)
        from app.core.security.jwt import verify_access_token
        token_data = verify_access_token(new_access_token)
        user = await user_service.get_user_by_id(int(token_data.sub))
        
        return TokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=60 * 60,  # 1 hour in seconds
            user=UserProfile(
                id=user.id,
                email=user.email,
                name=user.name,
                phone=user.phone,
                roles=user.get_roles(),
                is_email_verified=user.is_email_verified,
                mfa_enabled=user.mfa_enabled,
                status=user.status,
                last_login_at=user.last_login_at,
                created_at=user.created_at
            )
        )
    
    except AuthenticationError as e:
        if e.error_code == "TOKEN_REUSE_DETECTED":
            # Clear cookie on security alert
            response.delete_cookie("refresh_token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=e.message
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )


@router.get("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify user email address
    
    - **token**: Email verification token from registration email
    
    Activates user account and marks email as verified.
    """
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.verify_email(token)
        
        return {
            "message": "Email verified successfully",
            "email": user.email,
            "status": user.status.value
        }
    
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


@router.post("/resend-verification")
async def resend_verification_email(
    email_request: ResendVerificationEmail,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Resend email verification token
    
    - **email**: User's email address
    
    Generates new verification token and sends email.
    Always returns success to prevent email enumeration.
    """
    auth_service = AuthService(db)
    user_service = UserService(db)
    
    # Get user
    user = await user_service.get_user_by_email(email_request.email)
    
    if user and not user.is_email_verified:
        # Generate new token (reuse registration logic)
        from app.core.security.password import generate_secure_token, hash_token
        from app.models.auth import EmailVerificationToken
        from datetime import datetime, timedelta
        
        verification_token = generate_secure_token(32)
        token_hash = hash_token(verification_token)
        
        # Invalidate old tokens
        from sqlalchemy import select, update
        await db.execute(
            update(EmailVerificationToken)
            .where(EmailVerificationToken.user_id == user.id)
            .where(EmailVerificationToken.used_at.is_(None))
            .values(used_at=datetime.utcnow())
        )
        
        # Create new token
        email_token = EmailVerificationToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        db.add(email_token)
        await db.commit()
        
        # TODO: Send verification email
        print(f"New verification token for {user.email}: {verification_token}")
    
    # Always return success
    return {"message": "If the email exists and is not verified, a new verification link has been sent."}


@router.post("/forgot-password")
async def forgot_password(
    forgot_request: ForgotPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset token
    
    - **email**: User's email address
    
    Generates password reset token and sends email.
    Always returns success to prevent email enumeration.
    """
    auth_service = AuthService(db)
    
    reset_token = await auth_service.request_password_reset(
        forgot_request.email,
        ip_address=get_client_ip(request)
    )
    
    if reset_token:
        # TODO: Send password reset email
        print(f"Password reset token for {forgot_request.email}: {reset_token}")
        print(f"Reset URL: http://localhost:4200/reset-password?token={reset_token}")
    
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent."}


@router.post("/reset-password")
async def reset_password(
    reset_request: ResetPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password using reset token
    
    - **token**: Password reset token from email
    - **new_password**: New password (validated for strength)
    
    Updates password and invalidates all refresh tokens (logout all devices).
    """
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.reset_password(
            reset_request.token,
            reset_request.new_password,
            ip_address=get_client_ip(request)
        )
        
        return {
            "message": "Password reset successfully",
            "email": user.email
        }
    
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


@router.post("/check-password-strength", response_model=PasswordStrengthResponse)
async def check_password_strength(
    password_check: PasswordStrengthRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Check password strength without creating account
    
    - **password**: Password to check
    
    Returns strength score (0-4) and feedback for improvement.
    Useful for real-time password validation in UI.
    """
    user_service = UserService(db)
    return await user_service.check_password_strength(password_check.password)


# ============================================================================
# Protected Endpoints (Authentication Required)
# ============================================================================

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile
    
    Returns authenticated user's profile information.
    Requires valid access token.
    """
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        phone=current_user.phone,
        roles=current_user.get_roles(),
        is_email_verified=current_user.is_email_verified,
        mfa_enabled=current_user.mfa_enabled,
        status=current_user.status,
        last_login_at=current_user.last_login_at,
        created_at=current_user.created_at
    )


@router.put("/me", response_model=UserProfile)
async def update_current_user_profile(
    profile_update: UpdateProfile,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user profile
    
    - **name**: Updated full name
    - **phone**: Updated phone number
    
    Returns updated user profile.
    """
    user_service = UserService(db)
    
    try:
        user = await user_service.update_profile(
            current_user.id,
            profile_update,
            ip_address=get_client_ip(request)
        )
        
        return UserProfile(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
            roles=user.get_roles(),
            is_email_verified=user.is_email_verified,
            mfa_enabled=user.mfa_enabled,
            status=user.status,
            last_login_at=user.last_login_at,
            created_at=user.created_at
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/change-password")
async def change_password(
    password_change: ChangePassword,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password
    
    - **current_password**: Current password for verification
    - **new_password**: New password (validated for strength)
    
    Requires current password confirmation.
    Increments password version (invalidates old tokens).
    """
    user_service = UserService(db)
    
    try:
        await user_service.change_password(
            current_user.id,
            password_change,
            ip_address=get_client_ip(request)
        )
        
        return {"message": "Password changed successfully"}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/logout")
async def logout(
    response: Response,
    request: Request,
    current_user: User = Depends(get_current_user),
    refresh_token: Optional[str] = Header(None, alias="X-Refresh-Token"),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout current session
    
    Revokes refresh token and clears cookie.
    Access token remains valid until expiry (15 minutes).
    """
    # Try to get refresh token from cookie if not in header
    if not refresh_token:
        refresh_token = request.cookies.get("refresh_token")
    
    auth_service = AuthService(db)
    
    await auth_service.logout(
        current_user.id,
        refresh_token,
        ip_address=get_client_ip(request)
    )
    
    # Clear refresh token cookie
    response.delete_cookie("refresh_token")
    
    return {"message": "Logged out successfully"}


# ============================================================================
# MFA Endpoints
# ============================================================================

@router.get("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate MFA setup data
    
    Returns:
    - **secret**: TOTP secret (Base32)
    - **qr_code**: QR code image (Base64 PNG)
    - **backup_codes**: 10 backup codes (XXXX-XXXX format)
    - **uri**: otpauth:// URI for manual entry
    
    Scan QR code with authenticator app (Google Authenticator, Authy, etc.)
    Save backup codes in a secure location.
    Call /mfa/enable with verification code to activate.
    """
    auth_service = AuthService(db)
    return await auth_service.setup_mfa(current_user.id)


@router.post("/mfa/enable")
async def enable_mfa(
    mfa_enable: MFAEnableRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Enable MFA for account
    
    - **secret**: TOTP secret from setup
    - **verification_code**: 6-digit code from authenticator app
    - **backup_codes**: Backup codes from setup
    
    Verifies authenticator app is configured correctly.
    Future logins will require OTP code.
    """
    auth_service = AuthService(db)
    
    try:
        await auth_service.enable_mfa(
            current_user.id,
            mfa_enable.secret,
            mfa_enable.verification_code,
            mfa_enable.backup_codes,
            ip_address=get_client_ip(request)
        )
        
        return {"message": "MFA enabled successfully"}
    
    except MFAError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


@router.post("/mfa/disable")
async def disable_mfa(
    mfa_disable: MFADisableRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Disable MFA for account
    
    - **password**: Current password for verification
    
    Requires password confirmation for security.
    Future logins will not require OTP code.
    """
    auth_service = AuthService(db)
    
    try:
        await auth_service.disable_mfa(
            current_user.id,
            mfa_disable.password,
            ip_address=get_client_ip(request)
        )
        
        return {"message": "MFA disabled successfully"}
    
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


# ============================================================================
# Session Management Endpoints
# ============================================================================

@router.get("/devices", response_model=DeviceList)
async def get_active_devices(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of active sessions (devices)
    
    Returns all active refresh tokens with:
    - Device name (browser/platform)
    - IP address
    - Last used timestamp
    - Expiration date
    
    Use this to review and manage logged-in devices.
    """
    auth_service = AuthService(db)
    sessions = await auth_service.get_active_sessions(current_user.id)
    
    devices = [
        RefreshTokenInfo(
            id=session.id,
            device_name=session.device_name,
            ip_address=session.ip_address,
            user_agent=session.user_agent,
            created_at=session.created_at,
            last_used_at=session.created_at,  # TODO: Track last use
            expires_at=session.expires_at
        )
        for session in sessions
    ]
    
    return DeviceList(devices=devices, total=len(devices))


@router.delete("/devices/{device_id}")
async def revoke_device(
    device_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke specific session (logout device)
    
    - **device_id**: Refresh token ID from /devices list
    
    Immediately revokes the refresh token.
    That device will need to login again.
    """
    auth_service = AuthService(db)
    
    await auth_service.revoke_session(
        current_user.id,
        device_id,
        ip_address=get_client_ip(request)
    )
    
    return {"message": "Device logged out successfully"}


@router.post("/devices/revoke-all")
async def revoke_all_devices(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout all devices except current
    
    Revokes all refresh tokens for this user.
    Useful if account is compromised.
    Current session remains active until token expires (15 min).
    """
    auth_service = AuthService(db)
    
    count = await auth_service.revoke_all_sessions(
        current_user.id,
        ip_address=get_client_ip(request)
    )
    
    # Clear current refresh token cookie too
    response.delete_cookie("refresh_token")
    
    return {
        "message": f"Logged out {count} device(s) successfully",
        "count": count
    }
