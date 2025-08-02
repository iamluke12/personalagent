#!/usr/bin/env python3
"""
Security Manager for PersonalAgent
=================================

Handles secure credential storage and management for PersonalAgent.
Integrates with the existing secure_credentials.py system.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class SecurityManager:
    """Manages security aspects of PersonalAgent configuration"""
    
    def __init__(self, config_paths):
        """Initialize security manager with configuration paths"""
        self.paths = config_paths
        self.config_dir = self.paths.config_dir
        
        # Import secure credentials manager
        try:
            from src.utils.secure_credentials import SecureCredentialManager
            self.secure_creds = SecureCredentialManager(str(self.config_dir))
        except ImportError:
            self.secure_creds = None
    
    def is_secure_storage_available(self) -> bool:
        """Check if secure credential storage is available"""
        return self.secure_creds is not None
    
    def setup_secure_storage(self) -> bool:
        """Initialize secure credential storage"""
        try:
            if not self.secure_creds:
                from src.utils.secure_credentials import SecureCredentialManager
                self.secure_creds = SecureCredentialManager(str(self.config_dir))
            
            # Test encryption/decryption
            test_key = "test_key"
            test_value = "test_value"
            
            self.secure_creds.store_credential(test_key, test_value)
            retrieved = self.secure_creds.get_credential(test_key)
            
            if retrieved == test_value:
                # Clean up test
                self.secure_creds.delete_credential(test_key)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Secure storage setup failed: {e}")
            return False
    
    def list_stored_credentials(self) -> list:
        """List all stored credential keys (not values)"""
        if not self.secure_creds:
            return []
        
        try:
            return self.secure_creds.list_credentials()
        except Exception:
            return []
    
    def store_credential(self, key: str, value: str) -> bool:
        """Store a credential securely"""
        if not self.secure_creds:
            print("❌ Secure storage not available")
            return False
        
        try:
            self.secure_creds.store_credential(key, value)
            return True
        except Exception as e:
            print(f"❌ Failed to store credential: {e}")
            return False
    
    def get_credential(self, key: str) -> Optional[str]:
        """Retrieve a credential"""
        if not self.secure_creds:
            return None
        
        try:
            return self.secure_creds.get_credential(key)
        except Exception:
            return None
    
    def delete_credential(self, key: str) -> bool:
        """Delete a credential"""
        if not self.secure_creds:
            return False
        
        try:
            self.secure_creds.delete_credential(key)
            return True
        except Exception as e:
            print(f"❌ Failed to delete credential: {e}")
            return False
    
    def migrate_legacy_credentials(self) -> Dict[str, Any]:
        """Migrate credentials from legacy storage"""
        migration_status = {
            'success': False,
            'migrated_count': 0,
            'errors': []
        }
        
        try:
            # Check for legacy credentials.json
            legacy_creds_file = self.config_dir / 'credentials.json'
            
            if legacy_creds_file.exists():
                print("⚠️ Legacy credentials.json found but should have been removed")
                migration_status['errors'].append("Legacy credentials.json still exists")
            
            # Check for existing secure storage
            if self.is_secure_storage_available():
                migration_status['success'] = True
                migration_status['migrated_count'] = len(self.list_stored_credentials())
            
        except Exception as e:
            migration_status['errors'].append(f"Migration check failed: {e}")
        
        return migration_status
    
    def run_security_audit(self) -> Dict[str, Any]:
        """Run security audit on configuration"""
        audit_results = {
            'overall_score': 0,
            'checks_passed': 0,
            'checks_total': 0,
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Import security audit if available
            from src.utils.security_audit import SecurityAuditor
            auditor = SecurityAuditor(str(self.config_dir))
            results = auditor.run_audit()
            
            audit_results.update(results)
            
        except ImportError:
            audit_results['issues'].append("Security audit module not available")
        except Exception as e:
            audit_results['issues'].append(f"Security audit failed: {e}")
        
        return audit_results
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status"""
        status = {
            'secure_storage': {
                'available': self.is_secure_storage_available(),
                'credentials_count': len(self.list_stored_credentials()) if self.is_secure_storage_available() else 0
            },
            'files': {
                'secure_credentials_exists': (self.config_dir / 'secure_credentials.enc').exists(),
                'credential_salt_exists': (self.config_dir / 'credential_salt.dat').exists(),
                'legacy_credentials_exists': (self.config_dir / 'credentials.json').exists()
            },
            'permissions': {}
        }
        
        # Check file permissions
        try:
            secure_creds_file = self.config_dir / 'secure_credentials.enc'
            if secure_creds_file.exists():
                stat_info = secure_creds_file.stat()
                # Check if file is readable only by owner (mode 600)
                status['permissions']['secure_credentials'] = oct(stat_info.st_mode)[-3:]
            
            salt_file = self.config_dir / 'credential_salt.dat'
            if salt_file.exists():
                stat_info = salt_file.stat()
                status['permissions']['credential_salt'] = oct(stat_info.st_mode)[-3:]
                
        except Exception as e:
            status['permissions']['error'] = str(e)
        
        return status
    
    def validate(self) -> Dict[str, Any]:
        """Validate security configuration"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check secure storage
        if not self.is_secure_storage_available():
            validation['warnings'].append("Secure credential storage not available")
        
        # Check for legacy files
        if (self.config_dir / 'credentials.json').exists():
            validation['errors'].append("Legacy credentials.json file still exists")
            validation['valid'] = False
        
        # Check file permissions
        try:
            secure_file = self.config_dir / 'secure_credentials.enc'
            if secure_file.exists():
                stat_info = secure_file.stat()
                mode = oct(stat_info.st_mode)[-3:]
                if mode != '600':
                    validation['warnings'].append(f"Secure credentials file has permissions {mode}, should be 600")
        except Exception:
            pass
        
        return validation
