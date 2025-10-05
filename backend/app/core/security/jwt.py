"""
JWT Token Utilities
Implements OAuth2 Password flow with JWT access tokens and refresh token rotation
"""
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import secrets


class TokenConfig:
    """JWT Token Configuration"""
    # Access token settings
    ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Short-lived access tokens
    ACCESS_TOKEN_ALGORITHM = "HS256"
    
    # Refresh token settings
    REFRESH_TOKEN_EXPIRE_DAYS = 30  # Long-lived refresh tokens
    REFRESH_TOKEN_ALGORITHM = "HS256"
    
    # Token issuer
    ISSUER = "playcricket-api"
    AUDIENCE = "playcricket-web"
    
    # These should come from environment variables
    # For development, using placeholder. MUST be changed in production
    SECRET_KEY = "CHANGE_THIS_TO_SECURE_SECRET_KEY_IN_PRODUCTION_MIN_32_CHARS"
    REFRESH_SECRET_KEY = "CHANGE_THIS_TO_DIFFERENT_SECURE_SECRET_FOR_REFRESH_TOKENS"


class TokenData(BaseModel):
    """Token payload data"""
    sub: str  # Subject (user ID)
    email: str
    roles: List[str]
    ver: int  # Password version for global logout
    jti: str  # JWT ID for token tracking
    type: str  # 'access' or 'refresh'


class TokenPair(BaseModel):
    """Access and refresh token pair"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Access token expiry in seconds


def create_access_token(
    user_id: int,
    email: str,
    roles: List[str],
    password_version: int,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token
    
    Args:
        user_id: User ID
        email: User email
        roles: List of user roles
        password_version: Password version for global logout
        expires_delta: Custom expiration time
        
    Returns:
        Encoded JWT access token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=TokenConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Generate unique JWT ID
    jti = secrets.token_urlsafe(32)
    
    # Create token payload
    payload = {
        "sub": str(user_id),
        "email": email,
        "roles": roles,
        "ver": password_version,
        "jti": jti,
        "type": "access",
        "iat": datetime.utcnow(),
        "exp": expire,
        "iss": TokenConfig.ISSUER,
        "aud": TokenConfig.AUDIENCE
    }
    
    # Encode token
    encoded_jwt = jwt.encode(
        payload,
        TokenConfig.SECRET_KEY,
        algorithm=TokenConfig.ACCESS_TOKEN_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    user_id: int,
    email: str,
    password_version: int,
    expires_delta: Optional[timedelta] = None
) -> tuple[str, str, datetime]:
    """
    Create refresh token
    
    Args:
        user_id: User ID
        email: User email
        password_version: Password version for global logout
        expires_delta: Custom expiration time
        
    Returns:
        Tuple of (token, jti, expiration)
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=TokenConfig.REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Generate unique JWT ID for tracking
    jti = secrets.token_urlsafe(32)
    
    # Create token payload (minimal for refresh tokens)
    payload = {
        "sub": str(user_id),
        "email": email,
        "ver": password_version,
        "jti": jti,
        "type": "refresh",
        "iat": datetime.utcnow(),
        "exp": expire,
        "iss": TokenConfig.ISSUER,
        "aud": TokenConfig.AUDIENCE
    }
    
    # Encode token
    encoded_jwt = jwt.encode(
        payload,
        TokenConfig.REFRESH_SECRET_KEY,
        algorithm=TokenConfig.REFRESH_TOKEN_ALGORITHM
    )
    
    return encoded_jwt, jti, expire


def verify_access_token(token: str) -> Optional[TokenData]:
    """
    Verify and decode access token
    
    Args:
        token: JWT access token
        
    Returns:
        TokenData if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            TokenConfig.SECRET_KEY,
            algorithms=[TokenConfig.ACCESS_TOKEN_ALGORITHM],
            audience=TokenConfig.AUDIENCE,
            issuer=TokenConfig.ISSUER
        )
        
        # Verify token type
        if payload.get("type") != "access":
            return None
        
        return TokenData(
            sub=payload.get("sub"),
            email=payload.get("email"),
            roles=payload.get("roles", []),
            ver=payload.get("ver", 1),
            jti=payload.get("jti"),
            type=payload.get("type")
        )
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.JWTError:
        # Invalid token
        return None


def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode refresh token
    
    Args:
        token: JWT refresh token
        
    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            TokenConfig.REFRESH_SECRET_KEY,
            algorithms=[TokenConfig.REFRESH_TOKEN_ALGORITHM],
            audience=TokenConfig.AUDIENCE,
            issuer=TokenConfig.ISSUER
        )
        
        # Verify token type
        if payload.get("type") != "refresh":
            return None
        
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.JWTError:
        # Invalid token
        return None


def decode_token_without_verification(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode token without verification (for debugging/logging only)
    
    Args:
        token: JWT token
        
    Returns:
        Decoded payload (unverified)
        
    Warning: DO NOT use for authentication decisions
    """
    try:
        return jwt.decode(token, options={"verify_signature": False})
    except jwt.JWTError:
        return None


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get token expiration time without full verification
    
    Args:
        token: JWT token
        
    Returns:
        Expiration datetime if present, None otherwise
    """
    payload = decode_token_without_verification(token)
    if payload and "exp" in payload:
        return datetime.fromtimestamp(payload["exp"])
    return None


def is_token_expired(token: str) -> bool:
    """
    Check if token is expired
    
    Args:
        token: JWT token
        
    Returns:
        True if expired, False otherwise
    """
    expiration = get_token_expiration(token)
    if expiration:
        return datetime.utcnow() > expiration
    return True


def extract_user_id(token: str) -> Optional[int]:
    """
    Extract user ID from token without full verification
    
    Args:
        token: JWT token
        
    Returns:
        User ID if present, None otherwise
    """
    payload = decode_token_without_verification(token)
    if payload and "sub" in payload:
        try:
            return int(payload["sub"])
        except (ValueError, TypeError):
            return None
    return None


def extract_jti(token: str) -> Optional[str]:
    """
    Extract JWT ID from token
    
    Args:
        token: JWT token
        
    Returns:
        JWT ID if present, None otherwise
    """
    payload = decode_token_without_verification(token)
    if payload and "jti" in payload:
        return payload["jti"]
    return None


def create_token_pair(
    user_id: int,
    email: str,
    roles: List[str],
    password_version: int
) -> tuple[str, str, str, datetime]:
    """
    Create both access and refresh tokens
    
    Args:
        user_id: User ID
        email: User email
        roles: List of user roles
        password_version: Password version for global logout
        
    Returns:
        Tuple of (access_token, refresh_token, refresh_jti, refresh_expiration)
    """
    # Create access token
    access_token = create_access_token(
        user_id=user_id,
        email=email,
        roles=roles,
        password_version=password_version
    )
    
    # Create refresh token
    refresh_token, refresh_jti, refresh_expiration = create_refresh_token(
        user_id=user_id,
        email=email,
        password_version=password_version
    )
    
    return access_token, refresh_token, refresh_jti, refresh_expiration


# Configuration validation
def validate_token_config():
    """
    Validate token configuration
    
    Raises:
        ValueError: If configuration is invalid
    """
    if len(TokenConfig.SECRET_KEY) < 32:
        raise ValueError("SECRET_KEY must be at least 32 characters")
    
    if len(TokenConfig.REFRESH_SECRET_KEY) < 32:
        raise ValueError("REFRESH_SECRET_KEY must be at least 32 characters")
    
    if TokenConfig.SECRET_KEY == TokenConfig.REFRESH_SECRET_KEY:
        raise ValueError("SECRET_KEY and REFRESH_SECRET_KEY must be different")
    
    if "CHANGE_THIS" in TokenConfig.SECRET_KEY:
        # Warning only in development
        import warnings
        warnings.warn("Using default SECRET_KEY. Change in production!")
    
    if TokenConfig.ACCESS_TOKEN_EXPIRE_MINUTES < 5:
        raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be at least 5")
    
    if TokenConfig.ACCESS_TOKEN_EXPIRE_MINUTES > 60:
        import warnings
        warnings.warn("ACCESS_TOKEN_EXPIRE_MINUTES > 60 may be insecure")
