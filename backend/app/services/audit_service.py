"""
Audit Service

Handles security audit logging and audit log retrieval.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.auth import AuditLog, User
from app.schemas.auth import AuditLogEntry, AuditLogList


class AuditService:
    """Audit logging service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log_event(
        self,
        action: str,
        resource: str,
        user_id: Optional[int] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success"
    ) -> AuditLog:
        """
        Log an audit event
        
        Args:
            action: Action performed (e.g., LOGIN_SUCCESS, USER_CREATED)
            resource: Resource type (e.g., auth, user, match)
            user_id: ID of user performing the action
            resource_id: ID of affected resource
            details: Additional details (stored as JSON)
            ip_address: Client IP address
            user_agent: Client user agent
            status: Event status (success, failure, security_alert)
            
        Returns:
            Created AuditLog
        """
        audit = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            status=status
        )
        self.db.add(audit)
        await self.db.commit()
        await self.db.refresh(audit)
        
        return audit
    
    async def get_audit_logs(
        self,
        skip: int = 0,
        limit: int = 50,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        ip_address: Optional[str] = None
    ) -> AuditLogList:
        """
        Get audit logs with pagination and filters
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            user_id: Filter by user ID
            action: Filter by action
            resource: Filter by resource type
            status: Filter by status
            start_date: Filter by start date
            end_date: Filter by end date
            ip_address: Filter by IP address
            
        Returns:
            Paginated audit log list
        """
        # Build query
        query = select(AuditLog)
        
        # Apply filters
        filters = []
        
        if user_id:
            filters.append(AuditLog.user_id == user_id)
        
        if action:
            filters.append(AuditLog.action == action)
        
        if resource:
            filters.append(AuditLog.resource == resource)
        
        if status:
            filters.append(AuditLog.status == status)
        
        if start_date:
            filters.append(AuditLog.created_at >= start_date)
        
        if end_date:
            filters.append(AuditLog.created_at <= end_date)
        
        if ip_address:
            filters.append(AuditLog.ip_address == ip_address)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        count_query = select(func.count()).select_from(AuditLog)
        if filters:
            count_query = count_query.where(and_(*filters))
        
        result = await self.db.execute(count_query)
        total = result.scalar()
        
        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(AuditLog.created_at.desc())
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        # Get user emails for logs with user_id
        user_ids = {log.user_id for log in logs if log.user_id}
        users_result = await self.db.execute(
            select(User).where(User.id.in_(user_ids))
        )
        users = {user.id: user.email for user in users_result.scalars().all()}
        
        # Convert to response models
        items = [
            AuditLogEntry(
                id=log.id,
                user_id=log.user_id,
                user_email=users.get(log.user_id) if log.user_id else None,
                action=log.action,
                resource=log.resource,
                resource_id=log.resource_id,
                details=log.details,
                ip_address=log.ip_address,
                user_agent=log.user_agent,
                status=log.status,
                created_at=log.created_at
            )
            for log in logs
        ]
        
        return AuditLogList(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_user_activity(
        self,
        user_id: int,
        days: int = 30,
        skip: int = 0,
        limit: int = 50
    ) -> AuditLogList:
        """
        Get recent activity for a user
        
        Args:
            user_id: User ID
            days: Number of days to look back
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Paginated audit log list
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        return await self.get_audit_logs(
            skip=skip,
            limit=limit,
            user_id=user_id,
            start_date=start_date
        )
    
    async def get_security_events(
        self,
        skip: int = 0,
        limit: int = 50,
        days: int = 7
    ) -> AuditLogList:
        """
        Get recent security-related events
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            days: Number of days to look back
            
        Returns:
            Paginated audit log list
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Security-related actions
        security_actions = [
            "LOGIN_FAILED",
            "MFA_FAILED",
            "TOKEN_REUSE_DETECTED",
            "PASSWORD_RESET_REQUESTED",
            "PASSWORD_RESET",
            "MFA_ENABLED",
            "MFA_DISABLED",
            "ALL_SESSIONS_REVOKED",
            "USER_STATUS_UPDATED",
            "ROLE_ASSIGNED",
            "ROLE_REMOVED"
        ]
        
        # Build query
        query = select(AuditLog).where(
            and_(
                AuditLog.action.in_(security_actions),
                AuditLog.created_at >= start_date
            )
        )
        
        # Get total count
        count_query = select(func.count()).select_from(AuditLog).where(
            and_(
                AuditLog.action.in_(security_actions),
                AuditLog.created_at >= start_date
            )
        )
        
        result = await self.db.execute(count_query)
        total = result.scalar()
        
        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(AuditLog.created_at.desc())
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        # Get user emails
        user_ids = {log.user_id for log in logs if log.user_id}
        users_result = await self.db.execute(
            select(User).where(User.id.in_(user_ids))
        )
        users = {user.id: user.email for user in users_result.scalars().all()}
        
        # Convert to response models
        items = [
            AuditLogEntry(
                id=log.id,
                user_id=log.user_id,
                user_email=users.get(log.user_id) if log.user_id else None,
                action=log.action,
                resource=log.resource,
                resource_id=log.resource_id,
                details=log.details,
                ip_address=log.ip_address,
                user_agent=log.user_agent,
                status=log.status,
                created_at=log.created_at
            )
            for log in logs
        ]
        
        return AuditLogList(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
