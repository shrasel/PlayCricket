"""
Role Management and Audit Log API Routes

Admin endpoints for role management and audit log viewing.
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies.auth import get_admin_user
from app.models.auth import User
from app.schemas.auth import RoleInfo, AuditLogList
from app.services import RoleService, AuditService

router = APIRouter(prefix="/roles", tags=["Role Management"])


@router.get("", response_model=list[RoleInfo])
async def list_roles(
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all available roles (Admin only)
    
    Returns all role definitions with codes, names, and descriptions.
    
    Available roles:
    - **ADMIN**: Full system access
    - **SCORER**: Can score matches
    - **UMPIRE**: Can officiate and score matches
    - **TEAM_MANAGER**: Can manage teams and players
    - **PLAYER**: Can view own statistics
    - **VIEWER**: Read-only access
    """
    role_service = RoleService(db)
    roles = await role_service.get_all_roles()
    
    return [
        RoleInfo(
            id=role.id,
            code=role.code,
            name=role.name,
            description=role.description
        )
        for role in roles
    ]


@router.get("/{role_code}", response_model=RoleInfo)
async def get_role(
    role_code: str,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get role details by code (Admin only)
    
    Returns role information including permissions description.
    """
    role_service = RoleService(db)
    role = await role_service.get_role_by_code(role_code)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_code}' not found"
        )
    
    return RoleInfo(
        id=role.id,
        code=role.code,
        name=role.name,
        description=role.description
    )


# ============================================================================
# Audit Log Routes
# ============================================================================

audit_router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@audit_router.get("", response_model=AuditLogList)
async def get_audit_logs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    resource: Optional[str] = Query(None, description="Filter by resource type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    ip_address: Optional[str] = Query(None, description="Filter by IP address"),
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get audit logs with filters (Admin only)
    
    Query Parameters:
    - **skip**: Pagination offset (default: 0)
    - **limit**: Page size (default: 50, max: 100)
    - **user_id**: Filter by user ID
    - **action**: Filter by action (LOGIN_SUCCESS, USER_CREATED, etc.)
    - **resource**: Filter by resource type (auth, user, match, etc.)
    - **status**: Filter by status (success, failure, security_alert)
    - **start_date**: Filter events after this date (ISO 8601)
    - **end_date**: Filter events before this date (ISO 8601)
    - **ip_address**: Filter by IP address
    
    Returns paginated audit log entries with user details.
    
    Common actions:
    - LOGIN_SUCCESS, LOGIN_FAILED
    - USER_REGISTERED, EMAIL_VERIFIED
    - PASSWORD_CHANGED, PASSWORD_RESET
    - MFA_ENABLED, MFA_DISABLED, MFA_FAILED
    - TOKEN_REUSE_DETECTED
    - ROLE_ASSIGNED, ROLE_REMOVED
    - USER_STATUS_UPDATED, USER_DELETED
    """
    audit_service = AuditService(db)
    
    return await audit_service.get_audit_logs(
        skip=skip,
        limit=limit,
        user_id=user_id,
        action=action,
        resource=resource,
        status=status,
        start_date=start_date,
        end_date=end_date,
        ip_address=ip_address
    )


@audit_router.get("/user/{user_id}", response_model=AuditLogList)
async def get_user_activity(
    user_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get activity history for specific user (Admin only)
    
    - **user_id**: User ID to get activity for
    - **days**: Number of days to look back (default: 30, max: 365)
    
    Returns recent activity for the user.
    Useful for investigating user behavior or security incidents.
    """
    audit_service = AuditService(db)
    
    return await audit_service.get_user_activity(
        user_id=user_id,
        days=days,
        skip=skip,
        limit=limit
    )


@audit_router.get("/security/events", response_model=AuditLogList)
async def get_security_events(
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent security-related events (Admin only)
    
    - **days**: Number of days to look back (default: 7, max: 30)
    
    Returns recent security events including:
    - Failed login attempts
    - MFA failures
    - Token reuse detection
    - Password resets
    - Account status changes
    - Role modifications
    
    Use this to monitor for suspicious activity and security incidents.
    """
    audit_service = AuditService(db)
    
    return await audit_service.get_security_events(
        skip=skip,
        limit=limit,
        days=days
    )
