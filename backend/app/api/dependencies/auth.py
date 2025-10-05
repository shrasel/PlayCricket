"""
Authentication Dependencies

FastAPI dependencies for authentication and authorization.
"""

from typing import Optional, List, Callable
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security.jwt import verify_access_token, TokenData
from app.models.auth import User, UserStatus
from app.services.user_service import UserService

# Security scheme for Swagger UI
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Dependency for protected routes. Validates JWT and returns user.
    
    Raises:
        HTTPException 401: If token is invalid or user not found
    
    Example:
        @router.get("/profile")
        async def get_profile(current_user: User = Depends(get_current_user)):
            return current_user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token
        token = credentials.credentials
        
        # Verify JWT token
        token_data: Optional[TokenData] = verify_access_token(token)
        if token_data is None:
            raise credentials_exception
        
        # Get user from database
        user_service = UserService(db)
        user = await user_service.get_user_by_id(int(token_data.sub))
        
        if user is None:
            raise credentials_exception
        
        # Check password version (invalidate tokens if password changed)
        if token_data.ver != user.password_version:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalidated due to password change. Please login again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current authenticated user and verify account is active
    
    Dependency for protected routes requiring active account.
    
    Raises:
        HTTPException 403: If account is not active
    
    Example:
        @router.get("/dashboard")
        async def dashboard(user: User = Depends(get_current_active_user)):
            return {"message": f"Welcome {user.name}"}
    """
    if current_user.status != UserStatus.ACTIVE:
        if current_user.status == UserStatus.LOCKED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is locked. Please contact support."
            )
        elif current_user.status == UserStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email address to activate your account."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is not active."
            )
    
    return current_user


async def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None
    
    Dependency for routes that work with or without authentication.
    
    Example:
        @router.get("/matches")
        async def list_matches(user: Optional[User] = Depends(get_optional_user)):
            # Show public matches, or user's matches if authenticated
            if user:
                return {"matches": user.matches}
            return {"matches": public_matches}
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.replace("Bearer ", "")
        token_data = verify_access_token(token)
        
        if token_data is None:
            return None
        
        user_service = UserService(db)
        user = await user_service.get_user_by_id(int(token_data.sub))
        
        return user
        
    except Exception:
        return None


def require_roles(*allowed_roles: str) -> Callable:
    """
    Create dependency that requires user to have one of the specified roles
    
    Args:
        *allowed_roles: Role codes that are allowed (e.g., "ADMIN", "SCORER")
    
    Returns:
        Dependency function
    
    Raises:
        HTTPException 403: If user doesn't have required role
    
    Example:
        # Require ADMIN role
        @router.delete("/users/{user_id}")
        async def delete_user(
            user_id: int,
            current_user: User = Depends(require_roles("ADMIN"))
        ):
            # Only admins can access this
            pass
        
        # Require ADMIN or SCORER role
        @router.post("/matches/{match_id}/score")
        async def update_score(
            match_id: int,
            current_user: User = Depends(require_roles("ADMIN", "SCORER"))
        ):
            # Admins and scorers can access this
            pass
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        # Get user's role codes
        user_roles = current_user.get_roles()
        
        # Check if user has any of the allowed roles
        if not any(role in allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        
        return current_user
    
    return role_checker


def require_verified_email(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Require user to have verified email address
    
    Dependency for routes that require email verification.
    
    Raises:
        HTTPException 403: If email is not verified
    
    Example:
        @router.post("/sensitive-action")
        async def sensitive_action(
            user: User = Depends(require_verified_email)
        ):
            # Only users with verified emails can access this
            pass
    """
    if not current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required to access this resource."
        )
    
    return current_user


def require_mfa(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Require user to have MFA enabled
    
    Dependency for highly sensitive routes requiring MFA.
    
    Raises:
        HTTPException 403: If MFA is not enabled
    
    Example:
        @router.post("/admin/critical-action")
        async def critical_action(
            user: User = Depends(require_mfa)
        ):
            # Only users with MFA can access this
            pass
    """
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Multi-factor authentication required to access this resource."
        )
    
    return current_user


# Convenience dependencies combining multiple checks

async def get_admin_user(
    current_user: User = Depends(require_roles("ADMIN"))
) -> User:
    """Shortcut for requiring ADMIN role"""
    return current_user


async def get_scorer_user(
    current_user: User = Depends(require_roles("ADMIN", "SCORER", "UMPIRE"))
) -> User:
    """Shortcut for users who can score matches (admins, scorers, umpires)"""
    return current_user


async def get_team_manager_user(
    current_user: User = Depends(require_roles("ADMIN", "TEAM_MANAGER"))
) -> User:
    """Shortcut for users who can manage teams"""
    return current_user
