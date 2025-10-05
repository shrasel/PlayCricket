"""
User Management Service

Handles user profile management, password changes, and admin user operations.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.auth import User, Role, UserRole, AuditLog, UserStatus
from app.schemas.auth import (
    UpdateProfile, ChangePassword, UserListItem, UserList,
    UpdateUserStatus, PasswordStrengthResponse
)
from app.core.security.password import (
    hash_password, verify_password, validate_password_strength
)


class UserService:
    """User management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID with roles"""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(UserRole.role))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email with roles"""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(UserRole.role))
            .where(User.email == email.lower())
        )
        return result.scalar_one_or_none()
    
    async def update_profile(
        self,
        user_id: int,
        update_data: UpdateProfile,
        ip_address: Optional[str] = None
    ) -> User:
        """Update user profile information"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Update fields
        if update_data.name is not None:
            user.name = update_data.name
        if update_data.phone is not None:
            user.phone = update_data.phone
        
        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action="PROFILE_UPDATED",
            resource="user",
            resource_id=str(user.id),
            details={
                "fields_updated": [
                    k for k, v in update_data.model_dump(exclude_unset=True).items()
                ]
            },
            ip_address=ip_address,
            status="success"
        )
        self.db.add(audit)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def change_password(
        self,
        user_id: int,
        password_data: ChangePassword,
        ip_address: Optional[str] = None
    ) -> User:
        """Change user password (requires current password)"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not verify_password(password_data.current_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        
        # Validate new password strength
        strength = validate_password_strength(password_data.new_password)
        if not strength["valid"]:
            raise ValueError(f"Password too weak: {', '.join(strength['errors'])}")
        
        # Check if new password is different from current
        if verify_password(password_data.new_password, user.password_hash):
            raise ValueError("New password must be different from current password")
        
        # Update password
        user.password_hash = hash_password(password_data.new_password)
        user.password_version += 1
        
        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action="PASSWORD_CHANGED",
            resource="user",
            resource_id=str(user.id),
            ip_address=ip_address,
            status="success"
        )
        self.db.add(audit)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def check_password_strength(self, password: str) -> PasswordStrengthResponse:
        """Check password strength without saving"""
        result = validate_password_strength(password)
        return PasswordStrengthResponse(
            valid=result["valid"],
            score=result["score"],
            strength=result["strength"],
            errors=result.get("errors", []),
            warnings=result.get("warnings", []),
            feedback=result.get("feedback", "")
        )
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        role: Optional[str] = None,
        status: Optional[UserStatus] = None
    ) -> UserList:
        """
        List users with pagination and filters (admin only)
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Search term (email or name)
            role: Filter by role code
            status: Filter by user status
            
        Returns:
            Paginated user list
        """
        # Build query
        query = select(User).options(
            selectinload(User.roles).selectinload(UserRole.role)
        )
        
        # Apply filters
        filters = []
        
        if search:
            search_term = f"%{search.lower()}%"
            filters.append(
                or_(
                    User.email.ilike(search_term),
                    User.name.ilike(search_term)
                )
            )
        
        if status:
            filters.append(User.status == status)
        
        if role:
            # Join with user_roles and roles to filter by role code
            query = query.join(User.roles).join(UserRole.role)
            filters.append(Role.code == role)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        count_query = select(func.count()).select_from(User)
        if filters:
            if role:
                count_query = count_query.join(User.roles).join(UserRole.role)
            count_query = count_query.where(and_(*filters))
        
        result = await self.db.execute(count_query)
        total = result.scalar()
        
        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self.db.execute(query)
        users = result.unique().scalars().all()
        
        # Convert to response models
        items = [
            UserListItem(
                id=user.id,
                email=user.email,
                name=user.name,
                roles=[ur.role.code for ur in user.roles],
                status=user.status,
                is_email_verified=user.is_email_verified,
                mfa_enabled=user.mfa_enabled,
                last_login_at=user.last_login_at,
                created_at=user.created_at
            )
            for user in users
        ]
        
        return UserList(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def update_user_status(
        self,
        user_id: int,
        status_update: UpdateUserStatus,
        admin_id: int,
        ip_address: Optional[str] = None
    ) -> User:
        """
        Update user status (admin only)
        
        Args:
            user_id: User ID to update
            status_update: New status
            admin_id: ID of admin performing the action
            ip_address: Client IP address
            
        Returns:
            Updated user
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        old_status = user.status
        user.status = status_update.status
        
        # If unlocking account, reset failed attempts
        if status_update.status == UserStatus.ACTIVE and old_status == UserStatus.LOCKED:
            user.failed_login_attempts = 0
            user.locked_until = None
        
        # Audit log
        audit = AuditLog(
            user_id=admin_id,
            action="USER_STATUS_UPDATED",
            resource="user",
            resource_id=str(user.id),
            details={
                "target_user": user.email,
                "old_status": old_status.value,
                "new_status": status_update.status.value,
                "reason": status_update.reason
            },
            ip_address=ip_address,
            status="success"
        )
        self.db.add(audit)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def delete_user(
        self,
        user_id: int,
        admin_id: int,
        ip_address: Optional[str] = None
    ) -> None:
        """
        Delete user account (admin only)
        
        Args:
            user_id: User ID to delete
            admin_id: ID of admin performing the action
            ip_address: Client IP address
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Audit log before deletion
        audit = AuditLog(
            user_id=admin_id,
            action="USER_DELETED",
            resource="user",
            resource_id=str(user.id),
            details={"deleted_user": user.email},
            ip_address=ip_address,
            status="success"
        )
        self.db.add(audit)
        
        # Delete user (cascade will handle related records)
        await self.db.delete(user)
        await self.db.commit()
