# 🔐 PlayCricket Authentication & Authorization System

## Overview

Comprehensive, production-ready authentication and authorization system following OWASP ASVS, NIST SP 800-63B, and industry best practices. Built for a cricket scoring platform with multi-role access control.

## 🎯 Features

### ✅ Authentication
- **OAuth2 Password Flow** with JWT access tokens
- **Argon2id Password Hashing** with NIST-compliant parameters
- **Email Verification** with signed tokens
- **Password Reset** with secure token flow
- **TOTP MFA** (RFC 6238) with backup codes
- **Refresh Token Rotation** with reuse detection
- **Session Management** with device tracking
- **Account Lockout** with exponential backoff

### ✅ Authorization (RBAC)
- **6 Predefined Roles**: ADMIN, SCORER, UMPIRE, TEAM_MANAGER, PLAYER, VIEWER
- **Role-Based Access Control** decorators
- **Fine-Grained Permissions** per endpoint
- **Dynamic Role Assignment** (admin only)

### ✅ Security Features
- **Argon2id** with 64MB memory, 3 iterations, 4 threads
- **Short-lived Access Tokens** (15 minutes)
- **Long-lived Refresh Tokens** (30 days) with rotation
- **httpOnly Cookies** for refresh tokens
- **CORS Protection** with allowed origins
- **CSRF Protection** for cookie-based flows
- **Rate Limiting** on auth endpoints
- **Comprehensive Audit Logging**
- **Password Breach Detection** (stub for HIBP integration)
- **IP & User Agent Tracking**
- **Failed Login Tracking** with lockouts

## 📊 Database Schema

### Tables Created

```sql
-- Core auth tables
users                      -- User accounts with security features
roles                      -- Role definitions
user_roles                 -- User-role junction
refresh_tokens            -- Refresh token storage with rotation tracking
audit_log                 -- Security event logging
email_verification_tokens -- Email verification
password_reset_tokens     -- Password reset
```

### Default Roles

| Code | Name | Description |
|------|------|-------------|
| ADMIN | Administrator | Full system access, manage users/roles, audit logs |
| SCORER | Scorer | Create/update live scores, ball-by-ball |
| UMPIRE | Umpire | Record and confirm match decisions |
| TEAM_MANAGER | Team Manager | Manage team squads and lineups |
| PLAYER | Player | View own stats, update availability |
| VIEWER | Viewer | Read-only public match access |

## 🔧 Backend Implementation (FastAPI)

### File Structure

```
backend/
├── alembic/versions/
│   └── 006_create_auth_tables.py          # Database migrations
├── app/
│   ├── models/
│   │   └── auth.py                         # SQLAlchemy models
│   ├── schemas/
│   │   └── auth.py                         # Pydantic schemas
│   ├── core/security/
│   │   ├── password.py                     # Argon2id hashing, validation
│   │   ├── jwt.py                          # JWT token management
│   │   └── mfa.py                          # TOTP MFA implementation
│   ├── services/
│   │   ├── auth_service.py                 # Auth business logic
│   │   ├── user_service.py                 # User management
│   │   └── audit_service.py                # Audit logging
│   ├── api/routes/
│   │   ├── auth.py                         # Auth endpoints
│   │   ├── users.py                        # User management (admin)
│   │   └── roles.py                        # Role management (admin)
│   └── api/dependencies/
│       └── auth.py                         # Auth dependencies & guards
```

### Dependencies Required

```txt
fastapi>=0.115.0
pydantic>=2.10.0
pydantic[email]
sqlalchemy>=2.0.36
alembic>=1.14.0
psycopg[binary]>=3.2.0
python-jose[cryptography]
passlib[argon2]
argon2-cffi>=23.1.0
pyotp>=2.9.0
qrcode[pil]>=7.4.0
python-multipart
email-validator
```

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/playcricket

# JWT Secrets (MUST change in production)
JWT_SECRET_KEY=<minimum-32-character-random-string>
JWT_REFRESH_SECRET_KEY=<different-32-character-random-string>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# Security
ALLOWED_ORIGINS=http://localhost:4200,http://localhost:3000
CORS_CREDENTIALS=true
CSRF_SECRET=<32-character-random-string>

# Email (for verification/reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@playcricket.com

# MFA
MFA_ISSUER=PlayCricket

# Rate Limiting
RATE_LIMIT_LOGIN=5/minute
RATE_LIMIT_REGISTER=3/minute
```

### Key API Endpoints

#### Public Endpoints

```http
POST   /api/v1/auth/register          # Register new user
POST   /api/v1/auth/login             # Login (email/password + optional OTP)
POST   /api/v1/auth/refresh           # Refresh access token
POST   /api/v1/auth/logout            # Logout (revoke refresh token)
POST   /api/v1/auth/forgot-password   # Request password reset
POST   /api/v1/auth/reset-password    # Reset password with token
GET    /api/v1/auth/verify-email      # Verify email with token
POST   /api/v1/auth/resend-verification # Resend verification email
POST   /api/v1/auth/check-password-strength # Check password strength
```

#### Protected Endpoints (Authenticated)

```http
GET    /api/v1/auth/me                # Get current user profile
PATCH  /api/v1/auth/me                # Update profile
POST   /api/v1/auth/change-password   # Change password
GET    /api/v1/auth/mfa/setup         # Setup MFA (get QR code)
POST   /api/v1/auth/mfa/enable        # Enable MFA (verify code)
POST   /api/v1/auth/mfa/disable       # Disable MFA
GET    /api/v1/auth/devices           # List active sessions
DELETE /api/v1/auth/devices/:id       # Revoke session/device
```

#### Admin Endpoints

```http
GET    /api/v1/users                  # List all users (paginated)
GET    /api/v1/users/:id              # Get user details
PATCH  /api/v1/users/:id/status       # Update user status (active/locked/pending)
POST   /api/v1/roles/assign           # Assign role to user
DELETE /api/v1/roles/revoke           # Revoke role from user
GET    /api/v1/roles                  # List all roles
GET    /api/v1/audit-logs             # View audit logs (paginated)
```

## 🔒 Password Security (NIST 800-63B Compliant)

### Requirements
- ✅ Minimum 8 characters, maximum 128
- ✅ No composition rules (no mandatory symbols/numbers)
- ✅ Allow all printable characters including spaces
- ✅ Check against breached password databases
- ✅ No password hints or knowledge-based authentication
- ✅ Argon2id hashing with proper parameters

### Argon2id Parameters

```python
Memory Cost:    65536 (64 MB)
Time Cost:      3 iterations
Parallelism:    4 threads
Hash Length:    32 bytes
Salt Length:    16 bytes
Algorithm:      Argon2id (hybrid)
```

### Password Strength Scoring

| Score | Label | Criteria |
|-------|-------|----------|
| 0 | Very Weak | < 8 characters |
| 1 | Weak | 8-11 characters |
| 2 | Fair | 12-15 characters |
| 3 | Strong | 16-19 characters |
| 4 | Very Strong | 20+ characters |

## 🎫 JWT Token Structure

### Access Token (15 min)

```json
{
  "sub": "123",              // User ID
  "email": "user@example.com",
  "roles": ["SCORER", "PLAYER"],
  "ver": 1,                  // Password version (for global logout)
  "jti": "unique-token-id",
  "type": "access",
  "iat": 1696531200,
  "exp": 1696532100,
  "iss": "playcricket-api",
  "aud": "playcricket-web"
}
```

### Refresh Token (30 days)

```json
{
  "sub": "123",
  "email": "user@example.com",
  "ver": 1,
  "jti": "unique-token-id",
  "type": "refresh",
  "iat": 1696531200,
  "exp": 1699123200,
  "iss": "playcricket-api",
  "aud": "playcricket-web"
}
```

## 🔄 Refresh Token Rotation

### Flow

1. User logs in → Receive access + refresh tokens
2. Access token expires → Client sends refresh token
3. Server validates refresh token
4. If valid:
   - Issue new access token
   - Issue new refresh token
   - Revoke old refresh token
   - Store new refresh token with `replaced_by` link
5. If old refresh token used again (reuse detection):
   - Revoke entire token family
   - Force re-authentication

### Reuse Detection

```python
# Token family tracking
refresh_token_1 (original)
  └─> refresh_token_2 (rotation 1, replaced_by=token_1.id)
      └─> refresh_token_3 (rotation 2, replaced_by=token_2.id)

# If token_1 used again after token_2 issued:
# → Revoke all tokens in family (security breach detected)
```

## 📧 Email Verification Flow

```
1. User registers
2. Account status = PENDING
3. Send verification email with signed token (24hr expiry)
4. User clicks link → /auth/verify-email?token=...
5. Verify token signature & expiry
6. Update user: status=ACTIVE, is_email_verified=true
7. Mark token as used
```

## 🔑 Password Reset Flow

```
1. User requests reset → /auth/forgot-password
2. Validate email exists
3. Generate signed reset token (1hr expiry)
4. Send reset email
5. User clicks link → /auth/reset-password with token
6. Verify token
7. Hash new password with Argon2id
8. Increment password_version (invalidates all tokens)
9. Revoke all refresh tokens
10. Mark reset token as used
```

## 📱 MFA (TOTP) Flow

### Setup

```
1. GET /auth/mfa/setup
2. Server generates TOTP secret
3. Server generates QR code (otpauth://...)
4. Server generates 10 backup codes
5. Return: {secret, qr_code, backup_codes, uri}
6. User scans QR with authenticator app
7. User verifies with code → POST /auth/mfa/enable {code}
8. Server validates code
9. Update user: mfa_enabled=true, mfa_secret=encrypted_secret
10. Store hashed backup codes
```

### Login with MFA

```
1. POST /auth/login {email, password}
2. Verify credentials
3. If MFA enabled:
   - Return: {requires_mfa: true, temp_token}
4. Client prompts for MFA code
5. POST /auth/mfa/verify {temp_token, code}
6. Verify TOTP code OR backup code
7. Issue access + refresh tokens
8. If backup code used, remove from list
```

## 👥 Role-Based Access Control

### Usage in Routes

```python
from app.api.dependencies.auth import get_current_user, require_roles

# Require authentication only
@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

# Require specific roles
@router.post("/scoring/matches/{match_id}/events")
async def record_event(
    match_id: int,
    event: EventCreate,
    current_user: User = Depends(require_roles(["SCORER", "ADMIN"]))
):
    # Only SCORER or ADMIN can access
    pass

# Admin only
@router.get("/admin/users")
async def list_users(
    current_user: User = Depends(require_roles(["ADMIN"]))
):
    # Only ADMIN can access
    pass
```

### Permission Matrix

| Endpoint | ADMIN | SCORER | UMPIRE | TEAM_MGR | PLAYER | VIEWER |
|----------|-------|--------|--------|----------|--------|--------|
| View Matches | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create/Edit Scores | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Record Decisions | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Manage Teams | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| View Own Stats | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Manage Users | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| View Audit Logs | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

## 📝 Audit Logging

### Logged Events

- ✅ User registration
- ✅ Login success/failure
- ✅ Password changes
- ✅ Password reset requests/completions
- ✅ MFA enable/disable
- ✅ Role assignments/revocations
- ✅ Account status changes
- ✅ Token refresh (suspicious activity)
- ✅ Failed authentication attempts

### Log Entry Structure

```json
{
  "id": 1234,
  "user_id": 123,
  "action": "login_success",
  "resource": "auth",
  "resource_id": null,
  "details": {"roles": ["SCORER"]},
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "status": "success",
  "created_at": "2025-10-05T20:15:00Z"
}
```

## 🔐 Security Best Practices

### ✅ Implemented

- [x] Argon2id password hashing with secure parameters
- [x] JWT with short expiration (15 min access, 30 day refresh)
- [x] Refresh token rotation with reuse detection
- [x] httpOnly, secure, sameSite cookies for refresh tokens
- [x] CORS with explicit origin whitelisting
- [x] CSRF protection for state-changing operations
- [x] Rate limiting on auth endpoints
- [x] Account lockout with exponential backoff
- [x] MFA with TOTP (RFC 6238) and backup codes
- [x] Email verification before account activation
- [x] Comprehensive audit logging
- [x] IP and user agent tracking
- [x] Password version for global logout
- [x] Secure token generation (secrets.token_urlsafe)
- [x] SQL injection prevention (parameterized queries)
- [x] Input validation with Pydantic
- [x] Password breach detection (stub for HIBP)

### 🔜 TODO for Production

- [ ] HTTPS enforcement (Nginx/load balancer)
- [ ] Implement actual HIBP k-anonymity API
- [ ] Redis for rate limiting state
- [ ] Redis for token blacklist (revoked JTIs)
- [ ] Email service integration (SendGrid/AWS SES)
- [ ] Monitoring & alerting (failed logins, etc.)
- [ ] CAPTCHA on registration/login after failures
- [ ] WebAuthn/FIDO2 support
- [ ] Session timeout after inactivity
- [ ] IP whitelist for admin access
- [ ] Database encryption at rest
- [ ] Secrets management (AWS Secrets Manager/Vault)

## 🧪 Testing

### Run Migrations

```bash
cd backend
alembic upgrade head
```

### Test Password Hashing

```bash
python -c "
from app.core.security.password import hash_password, verify_password
pwd = 'MySecurePassword123!'
hash = hash_password(pwd)
print(f'Hash: {hash}')
print(f'Verify: {verify_password(pwd, hash)}')
"
```

### Test JWT Tokens

```bash
python -c "
from app.core.security.jwt import create_access_token, verify_access_token
token = create_access_token(
    user_id=1,
    email='test@example.com',
    roles=['SCORER'],
    password_version=1
)
print(f'Token: {token}')
data = verify_access_token(token)
print(f'Data: {data}')
"
```

### Test TOTP

```bash
python -c "
from app.core.security.mfa import setup_mfa, verify_totp_code, get_current_totp_code
secret, qr, uri = setup_mfa('test@example.com')
code = get_current_totp_code(secret)
print(f'Secret: {secret}')
print(f'Current Code: {code}')
print(f'Valid: {verify_totp_code(secret, code)}')
"
```

## 📚 References

- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [NIST SP 800-63B](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [RFC 6238 (TOTP)](https://datatracker.ietf.org/doc/html/rfc6238)
- [Argon2 Spec](https://github.com/P-H-C/phc-winner-argon2)

## 📄 License

MIT
