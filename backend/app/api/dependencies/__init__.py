"""
API Dependencies

Dependency injection functions for FastAPI routes.
"""

from app.api.dependencies.auth import (
    get_current_user,
    get_current_active_user,
    get_optional_user,
    require_roles,
    require_verified_email,
    require_mfa,
    get_admin_user,
    get_scorer_user,
    get_team_manager_user,
)

__all__ = [
    "get_current_user",
    "get_current_active_user",
    "get_optional_user",
    "require_roles",
    "require_verified_email",
    "require_mfa",
    "get_admin_user",
    "get_scorer_user",
    "get_team_manager_user",
]
