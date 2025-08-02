#!/usr/bin/env python3
"""
PersonalAgent Configuration Manager
==================================

Core configuration management engine that handles all PersonalAgent configurations
including profiles, contexts, and system settings.
"""

import json
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

@dataclass
class ConfigPaths:
    """Configuration file paths"""
    config_dir: Path
    profiles: Path
    context: Path
    backup_dir: Path
    
    def __post_init__(self):
        """Ensure all directories exist"""
        self.config_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)

class ConfigManager:
    """Main configuration management engine"""
    
    def __init__(self, config_dir: str = None):
        """Initialize configuration manager"""
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'config')
        
        self.config_dir = Path(config_dir).resolve()
        self.paths = ConfigPaths(
            config_dir=self.config_dir,
            profiles=self.config_dir / 'calendar_profiles.json',
            context=self.config_dir / 'personal_context.json',
            backup_dir=self.config_dir / 'backup'
        )
        
        # Initialize managers
        from .profile_manager import ProfileManager
        from .context_manager import ContextManager
        from .backup_manager import BackupManager
        
        self.profiles = ProfileManager(self.paths)
        self.context = ContextManager(self.paths)
        self.backup = BackupManager(self.paths)
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate entire configuration and return status"""
        status = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'profiles': None,
            'context': None
        }
        
        try:
            # Validate profiles
            profile_status = self.profiles.validate()
            status['profiles'] = profile_status
            if not profile_status['valid']:
                status['valid'] = False
                status['errors'].extend(profile_status['errors'])
            
            # Validate context
            context_status = self.context.validate()
            status['context'] = context_status
            if not context_status['valid']:
                status['valid'] = False
                status['errors'].extend(context_status['errors'])
                
        except Exception as e:
            status['valid'] = False
            status['errors'].append(f"Configuration validation failed: {str(e)}")
        
        return status
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive configuration status"""
        try:
            profiles_data = self.profiles.load_profiles()
            context_data = self.context.load_context()
            
            return {
                'config_dir': str(self.config_dir),
                'profiles': {
                    'count': len(profiles_data.get('profiles', {})),
                    'current': profiles_data.get('current_profile'),
                    'available': list(profiles_data.get('profiles', {}).keys())
                },
                'context': {
                    'location_set': bool(context_data.get('location')),
                    'preferences_set': bool(context_data.get('preferences')),
                    'resources_set': bool(context_data.get('resources'))
                },
                'files': {
                    'profiles_exists': self.paths.profiles.exists(),
                    'context_exists': self.paths.context.exists(),
                    'backup_dir_exists': self.paths.backup_dir.exists()
                }
            }
        except Exception as e:
            return {
                'error': f"Failed to get status: {str(e)}",
                'config_dir': str(self.config_dir)
            }
    
    def create_backup(self, label: str = None) -> bool:
        """Create a backup of current configuration"""
        try:
            return self.backup.create_backup(label)
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restore configuration from backup"""
        try:
            return self.backup.restore_backup(backup_name)
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to safe defaults"""
        try:
            # Create backup first
            self.create_backup("before_reset")
            
            # Reset profiles to minimal setup
            default_profiles = {
                "profiles": {
                    "personal": {
                        "name": "Personal Profile",
                        "description": "Default personal calendar",
                        "priority": 1,
                        "calendars": [],
                        "conflict_resolution": {
                            "blocks_others": False,
                            "can_be_moved": True,
                            "auto_suggest_alternatives": True
                        },
                        "display_settings": {
                            "show_as_busy": True,
                            "filter_keywords": ["personal"]
                        }
                    }
                },
                "current_profile": "personal",
                "settings": {
                    "auto_switch_on_keyword": True,
                    "override_mode": False,
                    "conflict_notification": True,
                    "smart_suggestions": True,
                    "terminal_prompt_integration": False
                }
            }
            
            # Reset context to minimal setup
            default_context = {
                "location": {
                    "home": {"address": "", "has_kitchen": True, "has_car": False},
                    "work": {"remote": True, "office_location": ""}
                },
                "preferences": {
                    "transport_method": "public_transport",
                    "work_style": "balanced"
                },
                "resources": {
                    "has_car": False,
                    "has_bike": False,
                    "kitchen_equipped": True,
                    "home_office": True
                }
            }
            
            # Save defaults
            self.profiles.save_profiles(default_profiles)
            self.context.save_context(default_context)
            
            print("✅ Configuration reset to defaults")
            return True
            
        except Exception as e:
            print(f"❌ Reset failed: {e}")
            return False
