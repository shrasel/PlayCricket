"""
Authentication Models
Handles users, roles, tokens, and audit logging
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum

from app.models.base import Base


class UserStatus(str, enum.Enum):
    """User account status"""
    ACTIVE = "active"
    LOCKED = "locked"
    PENDING = "pending"


class User(Base):
    """User account model with security features"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    password_algo = Column(String(50), nullable=False, default="argon2id")
    password_version = Column(Integer, nullable=False, default=1)
    
    # Email verification
    is_email_verified = Column(Boolean, nullable=False, default=False)
    
    # MFA
    mfa_enabled = Column(Boolean, nullable=False, default=False)
    mfa_secret = Column(String(255), nullable=True)
    backup_codes = Column(JSONB, nullable=True)
    
    # Account status
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.PENDING)
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Login tracking
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(45), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def get_roles(self) -> List[str]:
        """Get list of role codes for this user"""
        return [ur.role.code for ur in self.roles]
    
    def has_role(self, role_code: str) -> bool:
        """Check if user has a specific role"""
        return role_code in self.get_roles()
    
    def has_any_role(self, role_codes: List[str]) -> bool:
        """Check if user has any of the specified roles"""
        user_roles = self.get_roles()
        return any(role in user_roles for role in role_codes)


class Role(Base):
    """Role definition for RBAC"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Relationships
    user_roles = relationship("UserRole", back_populates="role")


class UserRole(Base):
    """User-Role junction table"""
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="roles", foreign_keys=[user_id])
    role = relationship("Role", back_populates="user_roles")
    assigner = relationship("User", foreign_keys=[assigned_by])


class RefreshToken(Base):
    """Refresh token for session management with rotation"""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, index=True, nullable=False)
    jti = Column(String(255), index=True, nullable=False)
    
    # Device tracking
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    device_name = Column(String(255), nullable=True)
    
    # Token lifecycle
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    replaced_by = Column(Integer, ForeignKey("refresh_tokens.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
    @property
    def is_valid(self) -> bool:
        """Check if token is still valid"""
        now = datetime.utcnow()
        return (
            self.revoked_at is None and
            self.expires_at > now
        )


class AuditLog(Base):
    """Audit trail for security events"""
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource = Column(String(100), nullable=True)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSONB, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False)  # success, failure, error
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class EmailVerificationToken(Base):
    """Email verification token"""
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    @property
    def is_valid(self) -> bool:
        """Check if token is still valid"""
        now = datetime.utcnow()
        return (
            self.used_at is None and
            self.expires_at > now
        )


class PasswordResetToken(Base):
    """Password reset token"""
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    @property
    def is_valid(self) -> bool:
        """Check if token is still valid"""
        now = datetime.utcnow()
        return (
            self.used_at is None and
            self.expires_at > now
        )
