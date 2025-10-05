"""
Password Security Utilities
Implements NIST SP 800-63B and OWASP ASVS guidelines
Uses Argon2id for password hashing with secure parameters
"""
import hashlib
import secrets
import re
from typing import Optional, Dict, List
from passlib.context import CryptContext
from passlib.hash import argon2


# Argon2id configuration following OWASP recommendations
# Memory cost: 64 MB, Time cost: 3 iterations, Parallelism: 4 threads
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,  # 3 iterations
    argon2__parallelism=4,  # 4 threads
    argon2__hash_len=32,  # 32 byte hash
    argon2__salt_len=16,  # 16 byte salt
    argon2__type="id"  # Argon2id (hybrid)
)


class PasswordStrength:
    """Password strength scoring"""
    VERY_WEAK = 0
    WEAK = 1
    FAIR = 2
    STRONG = 3
    VERY_STRONG = 4


def hash_password(password: str) -> str:
    """
    Hash password using Argon2id
    
    Args:
        password: Plain text password
        
    Returns:
        Argon2id hash with embedded salt and parameters
        
    Example hash format:
        $argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Argon2id hash to check against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if password hash needs to be upgraded
    
    Args:
        hashed_password: Existing password hash
        
    Returns:
        True if hash uses outdated parameters
    """
    return pwd_context.needs_update(hashed_password)


def validate_password_strength(password: str) -> Dict[str, any]:
    """
    Validate password strength per NIST SP 800-63B guidelines
    
    NIST Requirements:
    - Minimum 8 characters (we enforce this)
    - Maximum 64+ characters (we allow up to 128)
    - No composition rules (no mandatory symbols, etc.)
    - Check against compromised password lists
    - Allow all printable characters including spaces
    
    Args:
        password: Password to validate
        
    Returns:
        Dict with validation results:
        {
            'valid': bool,
            'score': int (0-4),
            'errors': List[str],
            'warnings': List[str],
            'feedback': str
        }
    """
    errors = []
    warnings = []
    score = PasswordStrength.VERY_WEAK
    
    # Length checks (NIST 800-63B §5.1.1.2)
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    elif len(password) > 128:
        errors.append("Password must not exceed 128 characters")
    
    if len(password) >= 8:
        score = PasswordStrength.WEAK
    
    if len(password) >= 12:
        score = PasswordStrength.FAIR
    
    if len(password) >= 16:
        score = PasswordStrength.STRONG
    
    if len(password) >= 20:
        score = PasswordStrength.VERY_STRONG
    
    # Check for common patterns (not NIST required, but recommended)
    if len(password) >= 8:
        # Sequential characters
        if re.search(r'(012|123|234|345|456|567|678|789|abc|bcd|cde)', password.lower()):
            warnings.append("Avoid sequential characters")
            score = max(score - 1, PasswordStrength.WEAK)
        
        # Repeated characters
        if re.search(r'(.)\1{2,}', password):
            warnings.append("Avoid repeated characters")
            score = max(score - 1, PasswordStrength.WEAK)
        
        # Common keyboard patterns
        if re.search(r'(qwert|asdf|zxcv|qaz|wsx)', password.lower()):
            warnings.append("Avoid keyboard patterns")
            score = max(score - 1, PasswordStrength.WEAK)
    
    # Entropy calculation for additional strength assessment
    unique_chars = len(set(password))
    if unique_chars >= len(password) * 0.7:  # Good character diversity
        score = min(score + 1, PasswordStrength.VERY_STRONG)
    
    # Check character variety (bonus, not required by NIST)
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[^a-zA-Z0-9]', password))
    
    variety_count = sum([has_lower, has_upper, has_digit, has_special])
    
    # Provide feedback
    feedback = _get_password_feedback(len(password), score, variety_count)
    
    return {
        'valid': len(errors) == 0,
        'score': score,
        'errors': errors,
        'warnings': warnings,
        'feedback': feedback,
        'strength': _score_to_label(score)
    }


def _score_to_label(score: int) -> str:
    """Convert numeric score to label"""
    labels = {
        PasswordStrength.VERY_WEAK: "Very Weak",
        PasswordStrength.WEAK: "Weak",
        PasswordStrength.FAIR: "Fair",
        PasswordStrength.STRONG: "Strong",
        PasswordStrength.VERY_STRONG: "Very Strong"
    }
    return labels.get(score, "Unknown")


def _get_password_feedback(length: int, score: int, variety: int) -> str:
    """Generate user-friendly feedback"""
    if length < 8:
        return "Password is too short. Use at least 8 characters."
    
    if score == PasswordStrength.VERY_STRONG:
        return "Excellent password strength!"
    
    if score == PasswordStrength.STRONG:
        return "Good password strength. Consider making it longer for extra security."
    
    if score == PasswordStrength.FAIR:
        return "Moderate password strength. Consider using a longer password or passphrase."
    
    if variety < 2:
        return "Consider mixing different character types for better security."
    
    if length < 12:
        return "Consider using a longer password (12+ characters) for better security."
    
    return "Consider using a longer and more varied password."


async def is_compromised_password(password: str) -> bool:
    """
    Check if password appears in breach databases using k-Anonymity
    
    Uses HaveIBeenPwned API with k-anonymity to preserve privacy:
    - Hashes password with SHA-1
    - Sends only first 5 characters of hash
    - Checks if full hash appears in response
    
    Args:
        password: Password to check
        
    Returns:
        True if password found in breaches, False otherwise
        
    Note: This is a stub. In production, implement actual API call
    with proper error handling and caching.
    """
    # TODO: Implement actual HIBP API check
    # For now, check against a small common password list
    
    common_passwords = {
        'password', '12345678', 'qwerty', 'abc123', 'monkey',
        'letmein', 'trustno1', 'dragon', 'baseball', 'iloveyou',
        'master', 'sunshine', 'ashley', 'bailey', 'shadow',
        'superman', 'football', 'michael', 'ninja', 'mustang',
        'password123', 'admin', 'welcome', 'login', 'passw0rd'
    }
    
    return password.lower() in common_passwords


def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token
    
    Args:
        length: Number of bytes (will be hex encoded, so output is 2x length)
        
    Returns:
        Hex-encoded secure random token
    """
    return secrets.token_hex(length)


def hash_token(token: str) -> str:
    """
    Hash token for storage (one-way)
    
    Args:
        token: Token to hash
        
    Returns:
        SHA-256 hash of token
    """
    return hashlib.sha256(token.encode()).hexdigest()


def generate_backup_codes(count: int = 10) -> List[str]:
    """
    Generate backup codes for MFA recovery
    
    Args:
        count: Number of backup codes to generate
        
    Returns:
        List of formatted backup codes (8 characters each)
    """
    codes = []
    for _ in range(count):
        # Generate 8-character codes with format: XXXX-XXXX
        code = secrets.token_hex(2).upper() + '-' + secrets.token_hex(2).upper()
        codes.append(code)
    return codes


def hash_backup_codes(codes: List[str]) -> List[str]:
    """
    Hash backup codes for storage
    
    Args:
        codes: List of plain backup codes
        
    Returns:
        List of hashed codes
    """
    return [hash_token(code.replace('-', '')) for code in codes]


def verify_backup_code(plain_code: str, hashed_codes: List[str]) -> bool:
    """
    Verify backup code against hashed list
    
    Args:
        plain_code: Plain backup code to verify
        hashed_codes: List of hashed backup codes
        
    Returns:
        True if code matches any hash
    """
    code_hash = hash_token(plain_code.replace('-', ''))
    return code_hash in hashed_codes


# Test vectors for verification
TEST_VECTORS = {
    'password': 'TestPassword123!',
    'hash': '$argon2id$v=19$m=65536,t=3,p=4$',  # This will vary due to salt
    'params': {
        'memory_cost': 65536,  # 64 MB
        'time_cost': 3,
        'parallelism': 4,
        'hash_len': 32,
        'salt_len': 16
    }
}
