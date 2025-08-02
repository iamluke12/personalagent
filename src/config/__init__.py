"""
PersonalAgent Configuration Management System
============================================

A comprehensive configuration management system for PersonalAgent that provides:
- Priority-based calendar profile management
- Personal context configuration
- Secure credential management
- Interactive CLI interface
- Configuration validation and backup

Main Components:
- ConfigManager: Core configuration engine
- ProfileManager: Calendar profile CRUD operations
- ContextManager: Personal context management
- SecurityManager: Credential management
- BackupManager: Configuration backup/restore
"""

__version__ = "1.0.0"

from .config_manager import ConfigManager
from .profile_manager import ProfileManager
from .context_manager import ContextManager
from .security_manager import SecurityManager
from .backup_manager import BackupManager

__all__ = [
    "ConfigManager",
    "ProfileManager", 
    "ContextManager",
    "SecurityManager",
    "BackupManager"
]
