"""
Encryption Service - Client-side encryption utilities
Provides server-side support for zero-knowledge encryption
"""

import secrets
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
from config import config


class EncryptionService:
    """Handle encryption keys and secure vault creation"""

    def __init__(self):
        self.secret_key = config.SECRET_KEY

    def generate_encryption_key(self, patient_id: int, passphrase: str) -> Dict:
        """
        Generate encryption key derived from patient passphrase
        
        In production client-side implementation:
        1. Use PBKDF2 with high iteration count
        2. Combine with device fingerprint
        3. Never send passphrase to server
        
        Server just provides salt and parameters
        """
        salt = secrets.token_bytes(32)
        
        return {
            "salt": salt.hex(),
            "iterations": 100000,
            "key_length": 32,
            "algorithm": "PBKDF2-SHA256",
            "info": "Use these parameters to derive your encryption key client-side"
        }

    def create_secure_vault(
        self, 
        patient_id: int, 
        event_ids: list, 
        recipient_email: str,
        expiry_hours: int = 48
    ) -> Dict:
        """
        Create secure sharing vault with 2FA
        
        Returns vault token and 2FA code
        """
        # Generate unique vault token
        vault_token = secrets.token_urlsafe(32)
        
        # Generate 6-digit 2FA code
        two_fa_code = f"{secrets.randbelow(1000000):06d}"
        
        # Create expiration timestamp
        expires_at = datetime.now() + timedelta(hours=expiry_hours)
        
        # Create JWT token with vault metadata
        vault_payload = {
            "vault_token": vault_token,
            "patient_id": patient_id,
            "event_ids": event_ids,
            "recipient_email": recipient_email,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat()
        }
        
        jwt_token = jwt.encode(vault_payload, self.secret_key, algorithm="HS256")
        
        return {
            "vault_token": vault_token,
            "vault_url": f"/vault/{vault_token}",
            "two_fa_code": two_fa_code,
            "two_fa_method": "email",
            "expires_at": expires_at.isoformat(),
            "expiry_hours": expiry_hours,
            "jwt_token": jwt_token
        }

    def verify_vault_access(self, vault_token: str, two_fa_code: str, stored_2fa: str) -> bool:
        """Verify 2FA code for vault access"""
        return two_fa_code == stored_2fa

    def generate_2fa_code(self) -> str:
        """Generate new 6-digit 2FA code"""
        return f"{secrets.randbelow(1000000):06d}"

    def hash_sensitive_data(self, data: str) -> str:
        """One-way hash for sensitive data storage"""
        return hashlib.sha256(data.encode()).hexdigest()

    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # Check expiration
            expires_at = datetime.fromisoformat(payload.get("expires_at"))
            if datetime.now() > expires_at:
                return None
                
            return payload
        except jwt.InvalidTokenError:
            return None

    def encrypt_field_metadata(self, field_name: str) -> Dict:
        """
        Provide metadata for client-side field encryption
        
        Returns information needed for AES-256-GCM encryption
        """
        # Generate IV (Initialization Vector) for this field
        iv = secrets.token_bytes(12).hex()
        
        return {
            "field": field_name,
            "algorithm": "AES-256-GCM",
            "iv": iv,
            "tag_length": 16,
            "encoding": "base64"
        }

    def create_access_log_entry(self, vault_token: str, ip_address: str, user_agent: str) -> Dict:
        """Create access log entry for vault access tracking"""
        return {
            "timestamp": datetime.now().isoformat(),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "vault_token": vault_token,
            "action": "vault_access"
        }


# Singleton instance
encryption_service = EncryptionService()
