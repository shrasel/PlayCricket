"""
Authentication Schemas
Pydantic models for request/response validation
"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime


# ============================================================================
# Registration & Login
# ============================================================================

class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    requested_role: Optional[str] = Field(None, description="Initial role request (subject to approval)")
    
    @validator('password')
    def validate_password_strength(cls, v):
        from app.core.security.password import validate_password_strength
        result = validate_password_strength(v)
        if not result['valid']:
            raise ValueError(', '.join(result['errors']))
        return v


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str
    otp: Optional[str] = Field(None, description="TOTP code if MFA enabled")
    remember_device: bool = Field(default=False)


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds
    user: 'UserProfile'


class RefreshTokenRequest(BaseModel):
    """Refresh token request (token comes from httpOnly cookie)"""
    pass


# ============================================================================
# User Profile
# ============================================================================

class UserProfile(BaseModel):
    """User profile response"""
    id: int
    email: str
    name: str
    phone: Optional[str]
    roles: List[str]
    is_email_verified: bool
    mfa_enabled: bool
    status: str
    last_login_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UpdateProfile(BaseModel):
    """Update user profile"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)


class ChangePassword(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        from app.core.security.password import validate_password_strength
        result = validate_password_strength(v)
        if not result['valid']:
            raise ValueError(', '.join(result['errors']))
        return v


# ============================================================================
# Email Verification
# ============================================================================

class EmailVerificationRequest(BaseModel):
    """Email verification request"""
    token: str


class ResendVerificationEmail(BaseModel):
    """Resend verification email"""
    email: EmailStr


# ============================================================================
# Password Reset
# ============================================================================

class ForgotPasswordRequest(BaseModel):
    """Forgot password request"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        from app.core.security.password import validate_password_strength
        result = validate_password_strength(v)
        if not result['valid']:
            raise ValueError(', '.join(result['errors']))
        return v


# ============================================================================
# MFA (Multi-Factor Authentication)
# ============================================================================

class MFASetupResponse(BaseModel):
    """MFA setup response"""
    secret: str
    qr_code: str
    backup_codes: List[str]
    uri: str


class MFAEnableRequest(BaseModel):
    """Enable MFA request"""
    code: str = Field(..., pattern=r'^\d{6}$', description="6-digit TOTP code")


class MFADisableRequest(BaseModel):
    """Disable MFA request"""
    password: str
    code: Optional[str] = Field(None, description="6-digit TOTP code or backup code")


class MFAVerifyRequest(BaseModel):
    """Verify MFA code"""
    code: str = Field(..., description="6-digit TOTP code or 8-char backup code")


# ============================================================================
# Session/Device Management
# ============================================================================

class RefreshTokenInfo(BaseModel):
    """Refresh token/session information"""
    id: int
    device_name: Optional[str]
    user_agent: Optional[str]
    ip_address: Optional[str]
    created_at: datetime
    expires_at: datetime
    last_used_at: Optional[datetime]
    is_current: bool
    
    class Config:
        from_attributes = True


class DeviceList(BaseModel):
    """List of user devices/sessions"""
    devices: List[RefreshTokenInfo]
    total: int


class RevokeDeviceRequest(BaseModel):
    """Revoke device/session"""
    device_id: int


# ============================================================================
# Role Management (Admin)
# ============================================================================

class RoleInfo(BaseModel):
    """Role information"""
    id: int
    code: str
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


class AssignRoleRequest(BaseModel):
    """Assign role to user"""
    user_id: int
    role_code: str


class RemoveRoleRequest(BaseModel):
    """Remove role from user"""
    user_id: int
    role_code: str


# ============================================================================
# User Management (Admin)
# ============================================================================

class UserListItem(BaseModel):
    """User list item"""
    id: int
    email: str
    name: str
    roles: List[str]
    status: str
    is_email_verified: bool
    mfa_enabled: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserList(BaseModel):
    """Paginated user list"""
    users: List[UserListItem]
    total: int
    page: int
    page_size: int


class UpdateUserStatus(BaseModel):
    """Update user status"""
    status: str = Field(..., pattern=r'^(active|locked|pending)$')
    reason: Optional[str]


# ============================================================================
# Audit Log
# ============================================================================

class AuditLogEntry(BaseModel):
    """Audit log entry"""
    id: int
    user_id: Optional[int]
    user_email: Optional[str]
    action: str
    resource: Optional[str]
    resource_id: Optional[str]
    details: Optional[dict]
    ip_address: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogList(BaseModel):
    """Paginated audit log"""
    logs: List[AuditLogEntry]
    total: int
    page: int
    page_size: int


# ============================================================================
# Password Strength Check
# ============================================================================

class PasswordStrengthRequest(BaseModel):
    """Password strength check request"""
    password: str


class PasswordStrengthResponse(BaseModel):
    """Password strength check response"""
    valid: bool
    score: int
    strength: str
    errors: List[str]
    warnings: List[str]
    feedback: str


# Update forward references
TokenResponse.model_rebuild()
