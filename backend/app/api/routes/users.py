"""
User Management API Routes

Admin endpoints for managing users.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies.auth import get_admin_user
from app.models.auth import User, UserStatus
from app.schemas.auth import (
    UserProfile, UserList, UpdateUserStatus,
    AssignRoleRequest, RemoveRoleRequest
)
from app.services import UserService, RoleService, AuditService

router = APIRouter(prefix="/users", tags=["User Management"])


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.get("", response_model=UserList)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records"),
    search: Optional[str] = Query(None, description="Search by email or name"),
    role: Optional[str] = Query(None, description="Filter by role code"),
    status: Optional[UserStatus] = Query(None, description="Filter by status"),
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all users with pagination and filters (Admin only)
    
    Query Parameters:
    - **skip**: Pagination offset (default: 0)
    - **limit**: Page size (default: 50, max: 100)
    - **search**: Search term for email or name
    - **role**: Filter by role code (ADMIN, SCORER, etc.)
    - **status**: Filter by status (active, locked, pending)
    
    Returns paginated list of users with roles and status.
    """
    user_service = UserService(db)
    
    return await user_service.list_users(
        skip=skip,
        limit=limit,
        search=search,
        role=role,
        status=status
    )


@router.get("/{user_id}", response_model=UserProfile)
async def get_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID (Admin only)
    
    Returns full user profile including roles and status.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
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
        created_at=user.created_at
    )


@router.patch("/{user_id}/status", response_model=UserProfile)
async def update_user_status(
    user_id: int,
    status_update: UpdateUserStatus,
    request: Request,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user account status (Admin only)
    
    - **status**: New status (active, locked, pending)
    - **reason**: Reason for status change (for audit log)
    
    Use cases:
    - Lock account: Set to 'locked' (e.g., security breach)
    - Unlock account: Set to 'active'
    - Suspend verification: Set to 'pending'
    """
    user_service = UserService(db)
    
    try:
        user = await user_service.update_user_status(
            user_id,
            status_update,
            admin.id,
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
            created_at=user.created_at
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{user_id}/roles", response_model=UserProfile)
async def assign_role_to_user(
    user_id: int,
    role_request: AssignRoleRequest,
    request: Request,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Assign role to user (Admin only)
    
    - **role_code**: Role to assign (ADMIN, SCORER, UMPIRE, TEAM_MANAGER, PLAYER, VIEWER)
    
    Users can have multiple roles.
    Audit log records who assigned the role.
    """
    role_service = RoleService(db)
    user_service = UserService(db)
    
    try:
        await role_service.assign_role(
            user_id,
            role_request.role_code,
            admin.id,
            ip_address=get_client_ip(request)
        )
        
        # Return updated user profile
        user = await user_service.get_user_by_id(user_id)
        
        return UserProfile(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
            roles=user.get_roles(),
            is_email_verified=user.is_email_verified,
            mfa_enabled=user.mfa_enabled,
            status=user.status,
            created_at=user.created_at
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}/roles/{role_code}", response_model=UserProfile)
async def remove_role_from_user(
    user_id: int,
    role_code: str,
    request: Request,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove role from user (Admin only)
    
    - **role_code**: Role to remove
    
    Cannot remove user's last role.
    Audit log records who removed the role.
    """
    role_service = RoleService(db)
    user_service = UserService(db)
    
    try:
        await role_service.remove_role(
            user_id,
            role_code,
            admin.id,
            ip_address=get_client_ip(request)
        )
        
        # Return updated user profile
        user = await user_service.get_user_by_id(user_id)
        
        return UserProfile(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
            roles=user.get_roles(),
            is_email_verified=user.is_email_verified,
            mfa_enabled=user.mfa_enabled,
            status=user.status,
            created_at=user.created_at
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user account (Admin only)
    
    Permanently deletes user and all associated data.
    Cannot be undone. Use with caution.
    
    Consider using status update to 'locked' instead for soft delete.
    """
    user_service = UserService(db)
    
    # Prevent self-deletion
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    try:
        await user_service.delete_user(
            user_id,
            admin.id,
            ip_address=get_client_ip(request)
        )
        
        return {"message": "User deleted successfully"}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
