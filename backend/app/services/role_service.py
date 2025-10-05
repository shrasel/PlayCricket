"""
Role Management Service

Handles role assignment, removal, and role-based access control.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.auth import User, Role, UserRole, AuditLog


class RoleService:
    """Role management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_roles(self) -> List[Role]:
        """Get all available roles"""
        result = await self.db.execute(select(Role).order_by(Role.id))
        return result.scalars().all()
    
    async def get_role_by_code(self, code: str) -> Optional[Role]:
        """Get role by code"""
        result = await self.db.execute(
            select(Role).where(Role.code == code)
        )
        return result.scalar_one_or_none()
    
    async def assign_role(
        self,
        user_id: int,
        role_code: str,
        assigned_by_id: int,
        ip_address: Optional[str] = None
    ) -> UserRole:
        """
        Assign role to user
        
        Args:
            user_id: User ID to assign role to
            role_code: Role code to assign
            assigned_by_id: ID of admin assigning the role
            ip_address: Client IP address
            
        Returns:
            Created UserRole
            
        Raises:
            ValueError: If user or role not found, or role already assigned
        """
        # Get user
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.user_roles))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        
        # Get role
        role = await self.get_role_by_code(role_code)
        if not role:
            raise ValueError(f"Role '{role_code}' not found")
        
        # Check if user already has this role
        existing = await self.db.execute(
            select(UserRole)
            .where(UserRole.user_id == user_id)
            .where(UserRole.role_id == role.id)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"User already has role '{role_code}'")
        
        # Create user role
        user_role = UserRole(
            user_id=user_id,
            role_id=role.id,
            assigned_by=assigned_by_id
        )
        self.db.add(user_role)
        
        # Audit log
        audit = AuditLog(
            user_id=assigned_by_id,
            action="ROLE_ASSIGNED",
            resource="user_role",
            resource_id=str(user_id),
            details={
                "target_user": user.email,
                "role": role_code
            },
            ip_address=ip_address,
            status="success"
        )
        self.db.add(audit)
        
        await self.db.commit()
        await self.db.refresh(user_role)
        
        return user_role
    
    async def remove_role(
        self,
        user_id: int,
        role_code: str,
        removed_by_id: int,
        ip_address: Optional[str] = None
    ) -> None:
        """
        Remove role from user
        
        Args:
            user_id: User ID to remove role from
            role_code: Role code to remove
            removed_by_id: ID of admin removing the role
            ip_address: Client IP address
            
        Raises:
            ValueError: If user or role not found, or role not assigned
        """
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        
        # Get role
        role = await self.get_role_by_code(role_code)
        if not role:
            raise ValueError(f"Role '{role_code}' not found")
        
        # Get user role
        result = await self.db.execute(
            select(UserRole)
            .where(UserRole.user_id == user_id)
            .where(UserRole.role_id == role.id)
        )
        user_role = result.scalar_one_or_none()
        
        if not user_role:
            raise ValueError(f"User does not have role '{role_code}'")
        
        # Check if this is the user's last role
        result = await self.db.execute(
            select(UserRole).where(UserRole.user_id == user_id)
        )
        user_roles = result.scalars().all()
        
        if len(user_roles) == 1:
            raise ValueError("Cannot remove user's last role. Assign another role first.")
        
        # Audit log before deletion
        audit = AuditLog(
            user_id=removed_by_id,
            action="ROLE_REMOVED",
            resource="user_role",
            resource_id=str(user_id),
            details={
                "target_user": user.email,
                "role": role_code
            },
            ip_address=ip_address,
            status="success"
        )
        self.db.add(audit)
        
        # Delete user role
        await self.db.delete(user_role)
        await self.db.commit()
    
    async def get_user_roles(self, user_id: int) -> List[Role]:
        """Get all roles for a user"""
        result = await self.db.execute(
            select(Role)
            .join(UserRole)
            .where(UserRole.user_id == user_id)
            .order_by(Role.id)
        )
        return result.scalars().all()
    
    async def has_role(self, user_id: int, role_code: str) -> bool:
        """Check if user has a specific role"""
        result = await self.db.execute(
            select(UserRole)
            .join(Role)
            .where(UserRole.user_id == user_id)
            .where(Role.code == role_code)
        )
        return result.scalar_one_or_none() is not None
    
    async def has_any_role(self, user_id: int, role_codes: List[str]) -> bool:
        """Check if user has any of the specified roles"""
        result = await self.db.execute(
            select(UserRole)
            .join(Role)
            .where(UserRole.user_id == user_id)
            .where(Role.code.in_(role_codes))
        )
        return result.scalar_one_or_none() is not None
