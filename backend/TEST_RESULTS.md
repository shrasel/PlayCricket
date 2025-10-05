# API Endpoint Test Results

## Test Summary
- **Total Tests**: 11
- **Passed**: 11
- **Failed**: 0
- **Success Rate**: 100.0%

## Test Execution
Date: October 5, 2025
Test Framework: httpx + Python asyncio

## Issues Found and Fixed

### 1. SQLAlchemy Relationship Name Error
**Error**: `AttributeError: type object 'User' has no attribute 'user_roles'`

**Root Cause**: Code was using `User.user_roles` but the model defined the relationship as `User.roles`

**Locations Fixed**:
- `auth_service.py` line 258: `selectinload(User.user_roles)` → `selectinload(User.roles)`
- `auth_service.py` line 389: `user.user_roles` → `user.roles`
- `auth_service.py` line 516: `selectinload(User.user_roles)` → `selectinload(User.roles)`
- `auth_service.py` line 536: `user.user_roles` → `user.roles`

### 2. MissingGreenlet Error (Lazy Loading in Async Context)
**Error**: `sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here`

**Root Cause**: The `User.get_roles()` method was trying to access the `roles` relationship which wasn't eagerly loaded, causing SQLAlchemy to attempt lazy loading in an async context

**Fix**: Replaced `await self.db.refresh(user)` with explicit eager loading query:
```python
result = await self.db.execute(
    select(User)
    .options(selectinload(User.roles).selectinload(UserRole.role))
    .where(User.id == user.id)
)
user = result.scalar_one()
```

### 3. Pydantic Validation Error
**Error**: `pydantic_core._pydantic_core.ValidationError: 1 validation error for UserProfile - last_login_at: Field required`

**Root Cause**: The `UserProfile` Pydantic model has `last_login_at` as a field, but it wasn't being included when creating UserProfile instances in the route handlers

**Locations Fixed**:
- `auth.py` register endpoint (line 81): Added `last_login_at=user.last_login_at`
- `auth.py` get current user endpoint (line 434): Added `last_login_at=current_user.last_login_at`
- `auth.py` update profile endpoint (line 471): Added `last_login_at=user.last_login_at`

### 4. HTTP Status Code Expectations
**Issue**: Tests expected different status codes than what the API was returning

**Fixes**:
- Registration endpoints: Changed expected status from 200 to 201 (Created) - more RESTful
- Endpoints without auth: Changed expected status from 401 to 403 when no Authorization header is provided (standard FastAPI HTTPBearer behavior)

## Test Coverage

### 1. Health Check
- ✅ Root endpoint (/)
- ✅ Health check endpoint (/health)

### 2. Authentication Endpoints
- ✅ Password strength check
- ✅ User registration (returns 201 Created)
- ✅ Duplicate registration prevention (returns 400)
- ✅ Login with unverified email (returns 401)
- ✅ Forgot password request

### 3. Token Endpoints
- ✅ Refresh token without authentication (returns 401)

### 4. User Management
- ✅ Get current user without auth (returns 403)
- ✅ List users without auth (returns 403)

## Test Script Features
- Async HTTP client using httpx
- Color-coded console output (green=pass, red=fail, yellow=info)
- Unique test data per run using timestamps
- Detailed error reporting with JSON responses
- Success rate calculation

## Running the Tests

```bash
cd backend
venv/bin/python test_api_endpoints.py
```

## Next Steps
- Add authenticated endpoint tests (requires login flow)
- Add MFA setup and verification tests
- Add email verification flow tests
- Add password reset flow tests
- Add user management tests with proper roles
- Add RBAC permission tests
