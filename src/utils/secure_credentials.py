#!/usr/bin/env python3
"""
Secure credential manager for PersonalAgent
Handles encryption/decryption of sensitive data like API keys
"""

import os
import json
import base64
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecureCredentialManager:
    """Manages encrypted storage of sensitive credentials"""
    
    def __init__(self, config_dir: Path = None):
        """Initialize credential manager with secure storage location"""
        self.config_dir = config_dir or Path("config")
        self.credentials_file = self.config_dir / "secure_credentials.enc"
        self.salt_file = self.config_dir / "credential_salt.dat"
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize encryption key if needed
        self._init_encryption()
    
    def _init_encryption(self):
        """Initialize encryption system with user-specific key"""
        # Use machine-specific salt for encryption
        if not self.salt_file.exists():
            salt = os.urandom(32)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
        else:
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
        
        # Create key from machine characteristics + environment
        machine_id = self._get_machine_identifier()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
        self.cipher = Fernet(key)
    
    def _get_machine_identifier(self) -> str:
        """Generate a machine-specific identifier for encryption"""
        # Combine multiple machine characteristics
        import platform
        import uuid
        
        machine_data = [
            platform.machine(),
            platform.processor(),
            str(uuid.getnode()),  # MAC address
            os.path.expanduser("~"),  # Home directory path
        ]
        
        # Create hash from combined data
        combined = "|".join(machine_data)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def store_credential(self, key: str, value: str):
        """Securely store an encrypted credential"""
        credentials = self._load_credentials()
        credentials[key] = value
        self._save_credentials(credentials)
    
    def get_credential(self, key: str) -> Optional[str]:
        """Retrieve and decrypt a stored credential"""
        credentials = self._load_credentials()
        return credentials.get(key)
    
    def _load_credentials(self) -> Dict[str, str]:
        """Load and decrypt stored credentials"""
        if not self.credentials_file.exists():
            return {}
        
        try:
            with open(self.credentials_file, 'rb') as f:
                encrypted_data = f.read()
            
            if not encrypted_data:
                return {}
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        
        except Exception as e:
            print(f"Warning: Could not decrypt credentials file: {e}")
            return {}
    
    def _save_credentials(self, credentials: Dict[str, str]):
        """Encrypt and save credentials to storage"""
        try:
            data = json.dumps(credentials).encode()
            encrypted_data = self.cipher.encrypt(data)
            
            with open(self.credentials_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Set restrictive permissions (owner read/write only)
            os.chmod(self.credentials_file, 0o600)
            
        except Exception as e:
            print(f"Error: Could not save encrypted credentials: {e}")
            raise
    
    def migrate_env_vars(self):
        """Migrate API keys from environment variables to encrypted storage"""
        env_keys = [
            'OPENAI_API_KEY',
            'GEMINI_API_KEY',
            'ANTHROPIC_API_KEY',
            'OPENROUTER_API_KEY'
        ]
        
        migrated = []
        for key in env_keys:
            value = os.getenv(key)
            if value and not self.get_credential(key):
                self.store_credential(key, value)
                migrated.append(key)
        
        if migrated:
            print(f"✅ Migrated {len(migrated)} API keys to encrypted storage")
            print("   Keys migrated:", ", ".join(migrated))
            print("   You can now remove these from your environment variables")
        
        return migrated
    
    def list_stored_keys(self) -> list:
        """List all stored credential keys (not values)"""
        credentials = self._load_credentials()
        return list(credentials.keys())
    
    def delete_credential(self, key: str) -> bool:
        """Delete a stored credential"""
        credentials = self._load_credentials()
        if key in credentials:
            del credentials[key]
            self._save_credentials(credentials)
            return True
        return False
    
    def export_backup(self, backup_path: Path, password: str):
        """Export encrypted backup of credentials"""
        credentials = self._load_credentials()
        
        # Create password-based encryption for backup
        salt = os.urandom(32)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        backup_cipher = Fernet(key)
        
        # Prepare backup data
        backup_data = {
            'credentials': credentials,
            'version': '1.0.0',
            'exported_at': __import__('datetime').datetime.now().isoformat()
        }
        
        # Encrypt and save
        data = json.dumps(backup_data).encode()
        encrypted_backup = backup_cipher.encrypt(data)
        
        backup_content = {
            'salt': base64.b64encode(salt).decode(),
            'data': base64.b64encode(encrypted_backup).decode()
        }
        
        with open(backup_path, 'w') as f:
            json.dump(backup_content, f, indent=2)
        
        print(f"✅ Encrypted backup created: {backup_path}")
    
    def import_backup(self, backup_path: Path, password: str):
        """Import encrypted backup of credentials"""
        with open(backup_path, 'r') as f:
            backup_content = json.load(f)
        
        # Decrypt backup
        salt = base64.b64decode(backup_content['salt'])
        encrypted_data = base64.b64decode(backup_content['data'])
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        backup_cipher = Fernet(key)
        
        try:
            decrypted_data = backup_cipher.decrypt(encrypted_data)
            backup_data = json.loads(decrypted_data.decode())
            
            # Import credentials
            imported_count = 0
            for key, value in backup_data['credentials'].items():
                self.store_credential(key, value)
                imported_count += 1
            
            print(f"✅ Imported {imported_count} credentials from backup")
            
        except Exception as e:
            print(f"❌ Failed to import backup: {e}")
            raise


def main():
    """Command-line interface for credential management"""
    import sys
    import getpass
    
    manager = SecureCredentialManager()
    
    if len(sys.argv) < 2:
        print("PersonalAgent Secure Credential Manager")
        print("\nUsage:")
        print("  python secure_credentials.py migrate       # Migrate env vars to encrypted storage")
        print("  python secure_credentials.py store <key>   # Store a new credential")
        print("  python secure_credentials.py get <key>     # Retrieve a credential")
        print("  python secure_credentials.py list          # List stored keys")
        print("  python secure_credentials.py delete <key>  # Delete a credential")
        print("  python secure_credentials.py backup        # Create encrypted backup")
        print("  python secure_credentials.py restore       # Restore from backup")
        return
    
    command = sys.argv[1]
    
    if command == "migrate":
        manager.migrate_env_vars()
    
    elif command == "store":
        if len(sys.argv) < 3:
            print("Usage: store <key>")
            return
        
        key = sys.argv[2]
        value = getpass.getpass(f"Enter value for {key}: ")
        manager.store_credential(key, value)
        print(f"✅ Stored credential: {key}")
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage: get <key>")
            return
        
        key = sys.argv[2]
        value = manager.get_credential(key)
        if value:
            print(f"{key}: {value}")
        else:
            print(f"❌ Credential not found: {key}")
    
    elif command == "list":
        keys = manager.list_stored_keys()
        if keys:
            print("Stored credentials:")
            for key in keys:
                print(f"  - {key}")
        else:
            print("No credentials stored")
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage: delete <key>")
            return
        
        key = sys.argv[2]
        if manager.delete_credential(key):
            print(f"✅ Deleted credential: {key}")
        else:
            print(f"❌ Credential not found: {key}")
    
    elif command == "backup":
        backup_path = Path(input("Backup file path: "))
        password = getpass.getpass("Backup password: ")
        manager.export_backup(backup_path, password)
    
    elif command == "restore":
        backup_path = Path(input("Backup file path: "))
        password = getpass.getpass("Backup password: ")
        manager.import_backup(backup_path, password)
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
