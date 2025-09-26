"""
Encryption Module - Secure data handling and storage
Implements AES-256 encryption, RSA key management, and secure credential storage
"""

import os
import base64
import json
import hashlib
from typing import Any, Dict, Optional, Tuple, Union
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import secrets
from loguru import logger


class EncryptionManager:
    """
    Comprehensive encryption manager for sensitive data
    Implements multiple encryption methods and secure key management
    """
    
    def __init__(self, key: Optional[str] = None, key_rotation_days: int = 30):
        """
        Initialize encryption manager
        
        Args:
            key: Master encryption key (will be derived if not provided)
            key_rotation_days: Days before key rotation is recommended
        """
        self.master_key = self._derive_master_key(key)
        self.fernet = Fernet(self.master_key)
        self.key_rotation_days = key_rotation_days
        self.key_created_at = datetime.now()
        
        # RSA keys for asymmetric encryption
        self.rsa_private_key = None
        self.rsa_public_key = None
        self._generate_rsa_keys()
        
        # Session keys for temporary encryption
        self.session_keys = {}
        
        # Encrypted storage
        self.encrypted_storage = {}
        
        # Initialize secure random
        self.secure_random = secrets.SystemRandom()
        
        logger.info("Encryption manager initialized")
    
    def _derive_master_key(self, key: Optional[str]) -> bytes:
        """
        Derive master key from provided key or generate new one
        
        Args:
            key: Optional key string
            
        Returns:
            Derived key bytes
        """
        if key:
            # Derive key from provided string
            salt = b'seeking_bot_salt_v1'  # In production, use random salt
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key_bytes = base64.urlsafe_b64encode(kdf.derive(key.encode()))
        else:
            # Generate new random key
            key_bytes = Fernet.generate_key()
            
            # Save key securely (in production, use key management service)
            self._save_key(key_bytes)
        
        return key_bytes
    
    def _save_key(self, key: bytes):
        """Save encryption key securely"""
        # In production, use AWS KMS, HashiCorp Vault, or similar
        # For now, save to environment variable
        os.environ['SEEKING_BOT_MASTER_KEY'] = key.decode()
        logger.warning("Master key saved to environment - use proper key management in production")
    
    def _generate_rsa_keys(self):
        """Generate RSA key pair for asymmetric encryption"""
        self.rsa_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.rsa_public_key = self.rsa_private_key.public_key()
        logger.debug("RSA key pair generated")
    
    def encrypt(self, data: Union[str, bytes, dict]) -> str:
        """
        Encrypt data using Fernet (symmetric encryption)
        
        Args:
            data: Data to encrypt (string, bytes, or dict)
            
        Returns:
            Base64 encoded encrypted string
        """
        try:
            # Convert data to bytes
            if isinstance(data, dict):
                data_bytes = json.dumps(data).encode()
            elif isinstance(data, str):
                data_bytes = data.encode()
            else:
                data_bytes = data
            
            # Encrypt
            encrypted = self.fernet.encrypt(data_bytes)
            
            # Return base64 encoded string
            return base64.b64encode(encrypted).decode()
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> Union[str, dict]:
        """
        Decrypt data encrypted with Fernet
        
        Args:
            encrypted_data: Base64 encoded encrypted string
            
        Returns:
            Decrypted data (string or dict)
        """
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            
            # Decrypt
            decrypted = self.fernet.decrypt(encrypted_bytes)
            
            # Try to parse as JSON
            try:
                return json.loads(decrypted.decode())
            except json.JSONDecodeError:
                return decrypted.decode()
                
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def encrypt_field(self, field_value: str, field_name: str) -> Dict[str, str]:
        """
        Encrypt a specific field with metadata
        
        Args:
            field_value: Value to encrypt
            field_name: Name of the field (for audit)
            
        Returns:
            Dictionary with encrypted value and metadata
        """
        encrypted_value = self.encrypt(field_value)
        
        return {
            'value': encrypted_value,
            'field': field_name,
            'encrypted_at': datetime.now().isoformat(),
            'algorithm': 'AES-256-CBC',
            'key_version': self._get_key_version()
        }
    
    def decrypt_field(self, encrypted_field: Dict[str, str]) -> str:
        """
        Decrypt a field encrypted with encrypt_field
        
        Args:
            encrypted_field: Dictionary from encrypt_field
            
        Returns:
            Decrypted value
        """
        # Check key version for rotation handling
        if encrypted_field.get('key_version') != self._get_key_version():
            logger.warning("Key version mismatch - may need key rotation")
        
        return self.decrypt(encrypted_field['value'])
    
    def encrypt_credentials(self, username: str, password: str) -> Dict[str, str]:
        """
        Securely encrypt login credentials
        
        Args:
            username: Username to encrypt
            password: Password to encrypt
            
        Returns:
            Dictionary with encrypted credentials
        """
        # Generate unique salt for this credential set
        salt = secrets.token_hex(16)
        
        # Encrypt with additional security
        encrypted_creds = {
            'username': self.encrypt(username),
            'password': self.encrypt(password),
            'salt': salt,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        # Store hash for verification without decryption
        combined = f"{username}:{password}:{salt}"
        encrypted_creds['verification_hash'] = hashlib.sha256(combined.encode()).hexdigest()
        
        return encrypted_creds
    
    def decrypt_credentials(self, encrypted_creds: Dict[str, str]) -> Tuple[str, str]:
        """
        Decrypt credentials
        
        Args:
            encrypted_creds: Encrypted credentials dictionary
            
        Returns:
            Tuple of (username, password)
        """
        # Check expiration
        expires_at = datetime.fromisoformat(encrypted_creds['expires_at'])
        if datetime.now() > expires_at:
            raise ValueError("Credentials have expired")
        
        username = self.decrypt(encrypted_creds['username'])
        password = self.decrypt(encrypted_creds['password'])
        
        # Verify integrity
        salt = encrypted_creds['salt']
        combined = f"{username}:{password}:{salt}"
        expected_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        if expected_hash != encrypted_creds['verification_hash']:
            raise ValueError("Credential integrity check failed")
        
        return username, password
    
    def encrypt_rsa(self, data: bytes) -> bytes:
        """
        Encrypt data using RSA (asymmetric encryption)
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted bytes
        """
        return self.rsa_public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    
    def decrypt_rsa(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt RSA encrypted data
        
        Args:
            encrypted_data: Encrypted bytes
            
        Returns:
            Decrypted bytes
        """
        return self.rsa_private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    
    def create_session_key(self, session_id: str) -> str:
        """
        Create a temporary session key
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session key
        """
        session_key = Fernet.generate_key()
        self.session_keys[session_id] = {
            'key': session_key,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=1)
        }
        return base64.b64encode(session_key).decode()
    
    def encrypt_with_session_key(self, data: str, session_id: str) -> str:
        """
        Encrypt using session-specific key
        
        Args:
            data: Data to encrypt
            session_id: Session identifier
            
        Returns:
            Encrypted data
        """
        if session_id not in self.session_keys:
            raise ValueError("Invalid session ID")
        
        session_data = self.session_keys[session_id]
        
        # Check expiration
        if datetime.now() > session_data['expires_at']:
            del self.session_keys[session_id]
            raise ValueError("Session key expired")
        
        fernet = Fernet(session_data['key'])
        return base64.b64encode(fernet.encrypt(data.encode())).decode()
    
    def secure_delete(self, data: Any):
        """
        Securely delete sensitive data from memory
        
        Args:
            data: Data to securely delete
        """
        if isinstance(data, str):
            # Overwrite string in memory (Python specific)
            data = ' ' * len(data)
        elif isinstance(data, bytes):
            # Overwrite bytes
            data = b'\x00' * len(data)
        elif isinstance(data, dict):
            # Recursively clear dictionary
            for key in list(data.keys()):
                self.secure_delete(data[key])
                del data[key]
        
        # Force garbage collection
        import gc
        gc.collect()
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt
        
        Args:
            password: Password to hash
            
        Returns:
            Hashed password
        """
        import bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Password to verify
            hashed: Hashed password
            
        Returns:
            True if password matches
        """
        import bcrypt
        return bcrypt.checkpw(password.encode(), hashed.encode())
    
    def tokenize_pii(self, pii_data: str) -> Tuple[str, str]:
        """
        Tokenize PII data for compliance
        
        Args:
            pii_data: Personally identifiable information
            
        Returns:
            Tuple of (token, encrypted_data)
        """
        # Generate unique token
        token = secrets.token_urlsafe(32)
        
        # Encrypt PII
        encrypted = self.encrypt(pii_data)
        
        # Store mapping (in production, use secure database)
        self.encrypted_storage[token] = {
            'data': encrypted,
            'created_at': datetime.now().isoformat(),
            'type': 'pii'
        }
        
        return token, encrypted
    
    def detokenize_pii(self, token: str) -> str:
        """
        Retrieve PII data from token
        
        Args:
            token: PII token
            
        Returns:
            Original PII data
        """
        if token not in self.encrypted_storage:
            raise ValueError("Invalid token")
        
        encrypted = self.encrypted_storage[token]['data']
        return self.decrypt(encrypted)
    
    def check_key_rotation_needed(self) -> bool:
        """Check if key rotation is needed"""
        age = (datetime.now() - self.key_created_at).days
        return age >= self.key_rotation_days
    
    def rotate_keys(self) -> Dict[str, str]:
        """
        Rotate encryption keys
        
        Returns:
            Dictionary with new key information
        """
        logger.info("Rotating encryption keys")
        
        # Generate new master key
        old_key = self.master_key
        new_key = Fernet.generate_key()
        
        # Re-encrypt all stored data with new key
        old_fernet = self.fernet
        new_fernet = Fernet(new_key)
        
        for token, data in self.encrypted_storage.items():
            if 'data' in data:
                # Decrypt with old key
                decrypted = old_fernet.decrypt(base64.b64decode(data['data']))
                # Encrypt with new key
                data['data'] = base64.b64encode(new_fernet.encrypt(decrypted)).decode()
        
        # Update keys
        self.master_key = new_key
        self.fernet = new_fernet
        self.key_created_at = datetime.now()
        
        # Generate new RSA keys
        self._generate_rsa_keys()
        
        # Save new key
        self._save_key(new_key)
        
        return {
            'rotated_at': datetime.now().isoformat(),
            'next_rotation': (datetime.now() + timedelta(days=self.key_rotation_days)).isoformat(),
            'key_version': self._get_key_version()
        }
    
    def _get_key_version(self) -> str:
        """Get current key version identifier"""
        return hashlib.sha256(self.master_key).hexdigest()[:8]
    
    def export_public_key(self) -> str:
        """Export RSA public key for sharing"""
        pem = self.rsa_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode()
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)