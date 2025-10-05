"""
Authentication Service

Handles user registration, login, MFA, password reset, and session management.
Implements OWASP ASVS and NIST SP 800-63B security best practices.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
import secrets
import hashlib

from app.models.auth import (
    User, Role, UserRole, RefreshToken, AuditLog,
    EmailVerificationToken, PasswordResetToken, UserStatus
)
from app.schemas.auth import (
    UserRegister, UserLogin, TokenResponse, UserProfile,
    MFASetupResponse, PasswordStrengthResponse
)
from app.core.security.password import (
    hash_password, verify_password, needs_rehash,
    validate_password_strength, generate_secure_token,
    hash_token, generate_backup_codes, hash_backup_codes,
    verify_backup_code
)
from app.core.security.jwt import create_token_pair, verify_refresh_token
from app.core.security.mfa import (
    setup_mfa, verify_mfa_code, validate_totp_code_format
)


class AuthenticationError(Exception):
    """Base exception for authentication errors"""
    def __init__(self, message: str, error_code: str = "AUTH_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class RegistrationError(AuthenticationError):
    """Raised during registration failures"""
    pass


class LoginError(AuthenticationError):
    """Raised during login failures"""
    pass


class MFAError(AuthenticationError):
    """Raised during MFA operations"""
    pass


class AuthService:
    """Authentication service for user registration, login, and session management"""
    
    # Security configuration
    MAX_FAILED_LOGIN_ATTEMPTS = 5
    ACCOUNT_LOCKOUT_DURATION_MINUTES = 30
    EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS = 24
    PASSWORD_RESET_TOKEN_EXPIRY_HOURS = 1
    REFRESH_TOKEN_REUSE_DETECTION_WINDOW_MINUTES = 5
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register_user(
        self,
        registration: UserRegister,
        ip_address: Optional[str] = None
    ) -> Tuple[User, str]:
        """
        Register a new user account
        
        Args:
            registration: User registration data
            ip_address: Client IP address for audit logging
            
        Returns:
            Tuple of (User, verification_token)
            
        Raises:
            RegistrationError: If registration fails
        """
        # Check if email already exists
        existing_user = await self.db.execute(
            select(User).where(User.email == registration.email.lower())
        )
        if existing_user.scalar_one_or_none():
            raise RegistrationError(
                "Email already registered",
                error_code="EMAIL_EXISTS"
            )
        
        # Validate password strength
        strength = validate_password_strength(registration.password)
        if not strength["valid"]:
            raise RegistrationError(
                f"Password too weak: {', '.join(strength['errors'])}",
                error_code="WEAK_PASSWORD"
            )
        
        # Hash password with Argon2id
        password_hash = hash_password(registration.password)
        
        # Create user
        user = User(
            email=registration.email.lower(),
            password_hash=password_hash,
            password_algo="argon2id",
            password_version=1,
            name=registration.name,
            phone=registration.phone,
            status=UserStatus.PENDING,
            is_email_verified=False
        )
        
        self.db.add(user)
        await self.db.flush()  # Get user.id
        
        # Assign requested role (default: VIEWER)
        role_code = registration.requested_role or "VIEWER"
        role = await self.db.execute(
            select(Role).where(Role.code == role_code)
        )
        role = role.scalar_one_or_none()
        
        if not role:
            # Fallback to VIEWER if requested role doesn't exist
            role = await self.db.execute(
                select(Role).where(Role.code == "VIEWER")
            )
            role = role.scalar_one()
        
        user_role = UserRole(
            user_id=user.id,
            role_id=role.id,
            assigned_by=None  # Self-registration
        )
        self.db.add(user_role)
        
        # Generate email verification token
        verification_token = generate_secure_token(32)
        token_hash = hash_token(verification_token)
        
        email_token = EmailVerificationToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(
                hours=self.EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS
            )
        )
        self.db.add(email_token)
        
        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action="USER_REGISTERED",
            resource="user",
            resource_id=str(user.id),
            details={"email": user.email, "role": role_code},
            ip_address=ip_address,
            status="success"
        )
        self.db.add(audit)
        
        await self.db.commit()
        
        # Reload user with relationships
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(UserRole.role))
            .where(User.id == user.id)
        )
        user = result.scalar_one()
        
        return user, verification_token
    
    async def verify_email(self, token: str) -> User:
        """
        Verify user email address
        
        Args:
            token: Email verification token
            
        Returns:
            Verified user
            
        Raises:
            AuthenticationError: If token is invalid or expired
        """
        token_hash = hash_token(token)
        
        result = await self.db.execute(
            select(EmailVerificationToken)
            .where(EmailVerificationToken.token_hash == token_hash)
            .where(EmailVerificationToken.used_at.is_(None))
        )
        email_token = result.scalar_one_or_none()
        
        if not email_token or not email_token.is_valid:
            raise AuthenticationError(
                "Invalid or expired verification token",
                error_code="INVALID_TOKEN"
            )
        
        # Get user
        user = await self.db.get(User, email_token.user_id)
        if not user:
            raise AuthenticationError(
                "User not found",
                error_code="USER_NOT_FOUND"
            )
        
        # Mark token as used
        email_token.used_at = datetime.utcnow()
        
        # Update user
        user.is_email_verified = True
        user.status = UserStatus.ACTIVE
        
        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action="EMAIL_VERIFIED",
            resource="user",
            resource_id=str(user.id),
            status="success"
        )
        self.db.add(audit)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def authenticate_user(
        self,
        login: UserLogin,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[User, str, str]:
        """
        Authenticate user and create session
        
        Args:
            login: Login credentials
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Tuple of (User, access_token, refresh_token)
            
        Raises:
            LoginError: If authentication fails
        """
        # Get user
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(UserRole.role))
            .where(User.email == login.email.lower())
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Log failed login attempt (even for non-existent users)
            audit = AuditLog(
                action="LOGIN_FAILED",
                resource="auth",
                details={"email": login.email, "reason": "user_not_found"},
                ip_address=ip_address,
                user_agent=user_agent,
                status="failure"
            )
            self.db.add(audit)
            await self.db.commit()
            
            raise LoginError(
                "Invalid email or password",
                error_code="INVALID_CREDENTIALS"
            )
        
        # Check account status
        if user.status == UserStatus.LOCKED:
            # Check if lockout duration has passed
            if user.locked_until and user.locked_until > datetime.utcnow():
                remaining = (user.locked_until - datetime.utcnow()).seconds // 60
                raise LoginError(
                    f"Account locked. Try again in {remaining} minutes.",
                    error_code="ACCOUNT_LOCKED"
                )
            else:
                # Unlock account
                user.status = UserStatus.ACTIVE
                user.failed_login_attempts = 0
                user.locked_until = None
        
        if user.status == UserStatus.PENDING:
            raise LoginError(
                "Please verify your email address",
                error_code="EMAIL_NOT_VERIFIED"
            )
        
        # Verify password
        if not verify_password(login.password, user.password_hash):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            
            # Lock account if max attempts exceeded
            if user.failed_login_attempts >= self.MAX_FAILED_LOGIN_ATTEMPTS:
                user.status = UserStatus.LOCKED
                user.locked_until = datetime.utcnow() + timedelta(
                    minutes=self.ACCOUNT_LOCKOUT_DURATION_MINUTES
                )
            
            # Audit log
            audit = AuditLog(
                user_id=user.id,
                action="LOGIN_FAILED",
                resource="auth",
                details={
                    "email": user.email,
                    "reason": "invalid_password",
                    "attempts": user.failed_login_attempts
                },
                ip_address=ip_address,
                user_agent=user_agent,
                status="failure"
            )
            self.db.add(audit)
            await self.db.commit()
            
            raise LoginError(
                "Invalid email or password",
                error_code="INVALID_CREDENTIALS"
            )
        
        # Check if MFA is enabled
        if user.mfa_enabled:
            if not login.otp_code:
                raise LoginError(
                    "MFA code required",
                    error_code="MFA_REQUIRED"
                )
            
            # Verify MFA code
            verification = verify_mfa_code(
                user.mfa_secret,
                login.otp_code,
                user.backup_codes or []
            )
            
            if not verification.valid:
                # Audit log
                audit = AuditLog(
                    user_id=user.id,
                    action="MFA_FAILED",
                    resource="auth",
                    details={"email": user.email},
                    ip_address=ip_address,
                    user_agent=user_agent,
                    status="failure"
                )
                self.db.add(audit)
                await self.db.commit()
                
                raise MFAError(
                    "Invalid MFA code",
                    error_code="INVALID_MFA_CODE"
                )
            
            # If backup code was used, remove it
            if verification.backup_code_used:
                remaining_codes = [
                    code for code in (user.backup_codes or [])
                    if code != verification.backup_code_used
                ]
                user.backup_codes = remaining_codes
        
        # Check if password needs rehashing (parameters upgraded)
        if needs_rehash(user.password_hash):
            user.password_hash = hash_password(login.password)
            user.password_version += 1
        
        # Reset failed login attempts
        user.failed_login_attempts = 0
        user.last_login_at = datetime.utcnow()
        user.last_login_ip = ip_address
        
        # Get user roles
        roles = [ur.role.code for ur in user.roles]
        
        # Create token pair
        access_token, refresh_token, refresh_jti, refresh_exp = create_token_pair(
            user_id=user.id,
            email=user.email,
            roles=roles,
            password_version=user.password_version
        )
        
        # Store refresh token
        token_hash = hash_token(refresh_token)
        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            jti=refresh_jti,
            user_agent=user_agent,
            ip_address=ip_address,
            device_name=self._extract_device_name(user_agent),
            expires_at=refresh_exp
        )
        self.db.add(refresh_token_record)
        
        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action="LOGIN_SUCCESS",
            resource="auth",
            details={
                "email": user.email,
                "mfa_used": user.mfa_enabled,
                "device": self._extract_device_name(user_agent)
            },
            ip_address=ip_address,
            user_agent=user_agent,
            status="success"
        )
        self.db.add(audit)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user, access_token, refresh_token
    
    async def refresh_access_token(
        self,
        refresh_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Refresh access token using refresh token rotation
        
        Args:
            refresh_token: Current refresh token
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Tuple of (new_access_token, new_refresh_token)
            
        Raises:
            AuthenticationError: If refresh fails or token reuse detected
        """
        # Verify refresh token JWT
        payload = verify_refresh_token(refresh_token)
        if not payload:
            raise AuthenticationError(
                "Invalid refresh token",
                error_code="INVALID_REFRESH_TOKEN"
            )
        
        user_id = int(payload.get("sub"))  # Convert to integer
        jti = payload.get("jti")
        token_hash = hash_token(refresh_token)
        
        # Get refresh token from database
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .where(RefreshToken.user_id == user_id)
        )
        token_record = result.scalar_one_or_none()
        
        if not token_record or not token_record.is_valid:
            # Check if this token was already used (token reuse detection)
            result = await self.db.execute(
                select(RefreshToken)
                .where(RefreshToken.jti == jti)
                .where(RefreshToken.user_id == user_id)
                .where(RefreshToken.replaced_by.isnot(None))
            )
            reused_token = result.scalar_one_or_none()
            
            if reused_token:
                # TOKEN REUSE DETECTED - Revoke entire token family
                await self._revoke_token_family(reused_token.id, user_id)
                
                # Audit log
                audit = AuditLog(
                    user_id=user_id,
                    action="TOKEN_REUSE_DETECTED",
                    resource="auth",
                    details={
                        "jti": jti,
                        "original_token_id": reused_token.id
                    },
                    ip_address=ip_address,
                    user_agent=user_agent,
                    status="security_alert"
                )
                self.db.add(audit)
                await self.db.commit()
                
                raise AuthenticationError(
                    "Token reuse detected. All sessions revoked for security.",
                    error_code="TOKEN_REUSE_DETECTED"
                )
            
            raise AuthenticationError(
                "Invalid or expired refresh token",
                error_code="INVALID_REFRESH_TOKEN"
            )
        
        # Get user
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(UserRole.role))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user or user.status != UserStatus.ACTIVE:
            raise AuthenticationError(
                "User account not active",
                error_code="ACCOUNT_NOT_ACTIVE"
            )
        
        # Check password version (invalidate tokens if password changed)
        token_pwd_version = payload.get("ver", 0)
        if token_pwd_version != user.password_version:
            raise AuthenticationError(
                "Token invalidated due to password change",
                error_code="PASSWORD_CHANGED"
            )
        
        # Get user roles
        roles = [ur.role.code for ur in user.roles]
        
        # Create new token pair
        new_access_token, new_refresh_token, new_jti, new_exp = create_token_pair(
            user_id=user.id,
            email=user.email,
            roles=roles,
            password_version=user.password_version
        )
        
        # Store new refresh token
        new_token_hash = hash_token(new_refresh_token)
        new_token_record = RefreshToken(
            user_id=user.id,
            token_hash=new_token_hash,
            jti=new_jti,
            user_agent=user_agent,
            ip_address=ip_address,
            device_name=self._extract_device_name(user_agent),
            expires_at=new_exp
        )
        self.db.add(new_token_record)
        
        # Mark old token as replaced (rotation)
        token_record.replaced_by = new_token_record.id
        token_record.revoked_at = datetime.utcnow()
        
        await self.db.commit()
        
        return new_access_token, new_refresh_token
    
    async def logout(
        self,
        user_id: int,
        refresh_token: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """
        Logout user and revoke refresh token
        
        Args:
            user_id: User ID
            refresh_token: Refresh token to revoke (if provided)
            ip_address: Client IP address
        """
        if refresh_token:
            token_hash = hash_token(refresh_token)
            
            result = await self.db.execute(
                select(RefreshToken)
                .where(RefreshToken.token_hash == token_hash)
                .where(RefreshToken.user_id == user_id)
            )
            token_record = result.scalar_one_or_none()
            
            if token_record:
                token_record.revoked_at = datetime.utcnow()
        
        # Audit log
        audit = AuditLog(
            user_id=user_id,
            action="LOGOUT",
            resource="auth",
            ip_address=ip_address,
            status="success"
        )
        self.db.add(audit)
        
        await self.db.commit()
    
    async def request_password_reset(
        self,
        email: str,
        ip_address: Optional[str] = None
    ) -> Optional[str]:
        """
        Request password reset token
        
        Args:
            email: User email address
            ip_address: Client IP address
            
        Returns:
            Password reset token (or None if user doesn't exist - don't reveal)
        """
        # Get user
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        user = result.scalar_one_or_none()
        
        # Always return success to prevent email enumeration
        if not user:
            # Audit log
            audit = AuditLog(
                action="PASSWORD_RESET_REQUESTED",
                resource="auth",
                details={"email": email, "result": "user_not_found"},
                ip_address=ip_address,
                status="info"
            )
            self.db.add(audit)
            await self.db.commit()
            return None
        
        # Generate reset token
        reset_token = generate_secure_token(32)
        token_hash = hash_token(reset_token)
        
        # Invalidate existing reset tokens
        await self.db.execute(
            select(PasswordResetToken)
            .where(PasswordResetToken.user_id == user.id)
            .where(PasswordResetToken.used_at.is_(None))
        )
        # Mark them as used
        result = await self.db.execute(
            select(PasswordResetToken)
            .where(PasswordResetToken.user_id == user.id)
            .where(PasswordResetToken.used_at.is_(None))
        )
        old_tokens = result.scalars().all()
        for old_token in old_tokens:
            old_token.used_at = datetime.utcnow()
        
        # Create new reset token
        password_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(
                hours=self.PASSWORD_RESET_TOKEN_EXPIRY_HOURS
            )
        )
        self.db.add(password_token)
        
        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action="PASSWORD_RESET_REQUESTED",
            resource="auth",
            details={"email": user.email},
            ip_address=ip_address,
            status="success"
        )
        self.db.add(audit)
        
        await self.db.commit()
        
        return reset_token
    
    async def reset_password(
        self,
        token: str,
        new_password: str,
        ip_address: Optional[str] = None
    ) -> User:
        """
        Reset user password using reset token
        
        Args:
            token: Password reset token
            new_password: New password
            ip_address: Client IP address
            
        Returns:
            User with updated password
            
        Raises:
            AuthenticationError: If token is invalid or password is weak
        """
        # Validate password strength
        strength = validate_password_strength(new_password)
        if not strength["valid"]:
            raise AuthenticationError(
                f"Password too weak: {', '.join(strength['errors'])}",
                error_code="WEAK_PASSWORD"
            )
        
        token_hash = hash_token(token)
        
        result = await self.db.execute(
            select(PasswordResetToken)
            .where(PasswordResetToken.token_hash == token_hash)
            .where(PasswordResetToken.used_at.is_(None))
        )
        reset_token = result.scalar_one_or_none()
        
        if not reset_token or not reset_token.is_valid:
            raise AuthenticationError(
                "Invalid or expired reset token",
                error_code="INVALID_TOKEN"
            )
        
        # Get user
        user = await self.db.get(User, reset_token.user_id)
        if not user:
            raise AuthenticationError(
                "User not found",
                error_code="USER_NOT_FOUND"
            )
        
        # Update password
        user.password_hash = hash_password(new_password)
        user.password_version += 1
        
        # Mark token as used
        reset_token.used_at = datetime.utcnow()
        
        # Revoke all refresh tokens (force re-login)
        await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user.id)
            .where(RefreshToken.revoked_at.is_(None))
        )
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user.id)
            .where(RefreshToken.revoked_at.is_(None))
        )
        active_tokens = result.scalars().all()
        for token_record in active_tokens:
            token_record.revoked_at = datetime.utcnow()
        
        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action="PASSWORD_RESET",
            resource="auth",
            details={"email": user.email},
            ip_address=ip_address,
            status="success"
        )
        self.db.add(audit)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def setup_mfa(self, user_id: int) -> MFASetupResponse:
        """
        Generate MFA setup data (secret, QR code, backup codes)
        
        Args:
            user_id: User ID
            
        Returns:
            MFA setup response with secret, QR code, and backup codes
        """
        user = await self.db.get(User, user_id)
        if not user:
            raise AuthenticationError(
                "User not found",
                error_code="USER_NOT_FOUND"
            )
        
        # Generate TOTP secret and QR code
        mfa_data = setup_mfa(user.email)
        
        # Generate backup codes
        backup_codes = generate_backup_codes(10)
        
        return MFASetupResponse(
            secret=mfa_data.secret,
            qr_code=mfa_data.qr_code,
            backup_codes=backup_codes,
            uri=mfa_data.uri
        )
    
    async def enable_mfa(
        self,
        user_id: int,
        secret: str,
        verification_code: str,
        backup_codes: list[str],
        ip_address: Optional[str] = None
    ) -> User:
        """
        Enable MFA for user after verifying setup
        
        Args:
            user_id: User ID
            secret: TOTP secret
            verification_code: Code to verify setup
            backup_codes: Backup codes to store
            ip_address: Client IP address
            
        Returns:
            Updated user
            
        Raises:
            MFAError: If verification code is invalid
        """
        user = await self.db.get(User, user_id)
        if not user:
            raise AuthenticationError(
                "User not found",
                error_code="USER_NOT_FOUND"
            )
        
        # Verify the code works
        verification = verify_mfa_code(secret, verification_code, [])
        if not verification.valid:
            raise MFAError(
                "Invalid verification code",
                error_code="INVALID_MFA_CODE"
            )
        
        # Store secret and backup codes (hashed)
        user.mfa_secret = secret
        user.mfa_enabled = True
        user.backup_codes = hash_backup_codes(backup_codes)
        
        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action="MFA_ENABLED",
            resource="user",
            resource_id=str(user.id),
            ip_address=ip_address,
            status="success"
        )
        self.db.add(audit)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def disable_mfa(
        self,
        user_id: int,
        password: str,
        ip_address: Optional[str] = None
    ) -> User:
        """
        Disable MFA for user (requires password confirmation)
        
        Args:
            user_id: User ID
            password: Current password for verification
            ip_address: Client IP address
            
        Returns:
            Updated user
            
        Raises:
            AuthenticationError: If password is incorrect
        """
        user = await self.db.get(User, user_id)
        if not user:
            raise AuthenticationError(
                "User not found",
                error_code="USER_NOT_FOUND"
            )
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise AuthenticationError(
                "Invalid password",
                error_code="INVALID_PASSWORD"
            )
        
        # Clear MFA data
        user.mfa_enabled = False
        user.mfa_secret = None
        user.backup_codes = None
        
        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action="MFA_DISABLED",
            resource="user",
            resource_id=str(user.id),
            ip_address=ip_address,
            status="success"
        )
        self.db.add(audit)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_active_sessions(self, user_id: int) -> list[RefreshToken]:
        """Get all active refresh tokens (sessions) for a user"""
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(RefreshToken.revoked_at.is_(None))
            .where(RefreshToken.expires_at > datetime.utcnow())
            .order_by(RefreshToken.created_at.desc())
        )
        return result.scalars().all()
    
    async def revoke_session(
        self,
        user_id: int,
        token_id: int,
        ip_address: Optional[str] = None
    ) -> None:
        """Revoke a specific refresh token (logout device)"""
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.id == token_id)
            .where(RefreshToken.user_id == user_id)
        )
        token = result.scalar_one_or_none()
        
        if token:
            token.revoked_at = datetime.utcnow()
            
            # Audit log
            audit = AuditLog(
                user_id=user_id,
                action="SESSION_REVOKED",
                resource="auth",
                details={"token_id": token_id},
                ip_address=ip_address,
                status="success"
            )
            self.db.add(audit)
            
            await self.db.commit()
    
    async def revoke_all_sessions(
        self,
        user_id: int,
        ip_address: Optional[str] = None
    ) -> int:
        """Revoke all refresh tokens for a user (logout all devices)"""
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(RefreshToken.revoked_at.is_(None))
        )
        tokens = result.scalars().all()
        
        count = 0
        for token in tokens:
            token.revoked_at = datetime.utcnow()
            count += 1
        
        # Audit log
        audit = AuditLog(
            user_id=user_id,
            action="ALL_SESSIONS_REVOKED",
            resource="auth",
            details={"count": count},
            ip_address=ip_address,
            status="success"
        )
        self.db.add(audit)
        
        await self.db.commit()
        
        return count
    
    # Helper methods
    
    async def _revoke_token_family(self, token_id: int, user_id: int) -> None:
        """
        Revoke entire token family (token reuse detection)
        Follows the replaced_by chain and revokes all tokens
        """
        # Get all tokens in the family
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(
                or_(
                    RefreshToken.id == token_id,
                    RefreshToken.replaced_by == token_id
                )
            )
        )
        tokens = result.scalars().all()
        
        # Follow the chain forward and backward
        all_token_ids = {token_id}
        for token in tokens:
            all_token_ids.add(token.id)
            if token.replaced_by:
                all_token_ids.add(token.replaced_by)
        
        # Revoke all tokens in the family
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.id.in_(all_token_ids))
            .where(RefreshToken.revoked_at.is_(None))
        )
        family_tokens = result.scalars().all()
        
        for token in family_tokens:
            token.revoked_at = datetime.utcnow()
    
    def _extract_device_name(self, user_agent: Optional[str]) -> Optional[str]:
        """Extract simple device name from user agent"""
        if not user_agent:
            return None
        
        ua = user_agent.lower()
        
        # Mobile devices
        if "iphone" in ua:
            return "iPhone"
        elif "ipad" in ua:
            return "iPad"
        elif "android" in ua and "mobile" in ua:
            return "Android Phone"
        elif "android" in ua:
            return "Android Tablet"
        
        # Browsers
        if "chrome" in ua:
            return "Chrome Browser"
        elif "safari" in ua:
            return "Safari Browser"
        elif "firefox" in ua:
            return "Firefox Browser"
        elif "edge" in ua:
            return "Edge Browser"
        
        return "Unknown Device"
