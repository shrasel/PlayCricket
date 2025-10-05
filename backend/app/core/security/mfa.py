"""
Multi-Factor Authentication (MFA) Utilities
Implements TOTP (Time-based One-Time Password) per RFC 6238
"""
import pyotp
import qrcode
import io
import base64
from typing import Optional, List, Tuple
from pydantic import BaseModel


class MFASetupData(BaseModel):
    """MFA setup data for user"""
    secret: str
    qr_code: str  # Base64 encoded PNG
    backup_codes: List[str]
    uri: str  # otpauth:// URI


def generate_totp_secret() -> str:
    """
    Generate random TOTP secret
    
    Returns:
        Base32 encoded secret (32 characters)
    """
    return pyotp.random_base32()


def generate_totp_uri(secret: str, email: str, issuer: str = "PlayCricket") -> str:
    """
    Generate otpauth:// URI for QR code
    
    Args:
        secret: TOTP secret
        email: User email
        issuer: Service name
        
    Returns:
        otpauth:// URI string
        
    Example:
        otpauth://totp/PlayCricket:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=PlayCricket
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(
        name=email,
        issuer_name=issuer
    )


def generate_qr_code(uri: str) -> str:
    """
    Generate QR code image from otpauth:// URI
    
    Args:
        uri: otpauth:// URI
        
    Returns:
        Base64 encoded PNG image
    """
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def verify_totp_code(secret: str, code: str, window: int = 1) -> bool:
    """
    Verify TOTP code
    
    Args:
        secret: User's TOTP secret
        code: 6-digit code to verify
        window: Number of time windows to check (default 1 = ±30 seconds)
        
    Returns:
        True if code is valid, False otherwise
    """
    try:
        totp = pyotp.TOTP(secret)
        # Verify with time window to account for clock drift
        return totp.verify(code, valid_window=window)
    except Exception:
        return False


def get_current_totp_code(secret: str) -> str:
    """
    Get current TOTP code (for testing only)
    
    Args:
        secret: TOTP secret
        
    Returns:
        Current 6-digit code
    """
    totp = pyotp.TOTP(secret)
    return totp.now()


def setup_mfa(email: str) -> Tuple[str, str, str]:
    """
    Complete MFA setup for user
    
    Args:
        email: User email
        
    Returns:
        Tuple of (secret, qr_code_base64, otpauth_uri)
    """
    # Generate secret
    secret = generate_totp_secret()
    
    # Generate URI
    uri = generate_totp_uri(secret, email)
    
    # Generate QR code
    qr_code = generate_qr_code(uri)
    
    return secret, qr_code, uri


def validate_totp_code_format(code: str) -> bool:
    """
    Validate TOTP code format
    
    Args:
        code: Code to validate
        
    Returns:
        True if format is valid (6 digits)
    """
    return code.isdigit() and len(code) == 6


class MFAVerificationResult(BaseModel):
    """Result of MFA verification"""
    valid: bool
    method: Optional[str] = None  # 'totp' or 'backup_code'
    backup_code_used: Optional[str] = None  # If backup code was used


def verify_mfa_code(
    secret: str,
    code: str,
    backup_codes: Optional[List[str]] = None
) -> MFAVerificationResult:
    """
    Verify MFA code (TOTP or backup code)
    
    Args:
        secret: TOTP secret
        code: Code to verify (6 digits for TOTP, 8 chars for backup)
        backup_codes: List of hashed backup codes
        
    Returns:
        MFAVerificationResult
    """
    # Try TOTP first
    if validate_totp_code_format(code):
        if verify_totp_code(secret, code):
            return MFAVerificationResult(valid=True, method='totp')
    
    # Try backup codes if provided
    if backup_codes:
        from app.core.security.password import verify_backup_code
        if verify_backup_code(code, backup_codes):
            return MFAVerificationResult(
                valid=True,
                method='backup_code',
                backup_code_used=code
            )
    
    return MFAVerificationResult(valid=False)


def get_totp_time_remaining() -> int:
    """
    Get seconds remaining in current TOTP time window
    
    Returns:
        Seconds until next code (0-30)
    """
    import time
    return 30 - int(time.time()) % 30


# Test vectors for verification
TEST_VECTORS = {
    'secret': 'JBSWY3DPEHPK3PXP',  # Base32 encoded "Hello!"
    'email': 'test@playcricket.com',
    'expected_uri': 'otpauth://totp/PlayCricket:test@playcricket.com?secret=JBSWY3DPEHPK3PXP&issuer=PlayCricket',
    # Note: Actual TOTP codes change every 30 seconds based on current time
}
