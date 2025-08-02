#!/usr/bin/env python3
"""
Backup Manager for PersonalAgent
===============================

Handles configuration backup, restore, and version management.
Provides safety mechanisms for configuration changes.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class BackupManager:
    """Manages configuration backups and restore operations"""
    
    def __init__(self, config_paths):
        """Initialize backup manager with configuration paths"""
        self.paths = config_paths
        self.backup_dir = self.paths.backup_dir
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, label: str = None) -> bool:
        """Create a backup of current configuration"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if label:
                backup_name = f"{timestamp}_{label}"
            else:
                backup_name = timestamp
            
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            # Backup profiles
            if self.paths.profiles.exists():
                shutil.copy2(self.paths.profiles, backup_path / 'calendar_profiles.json')
            
            # Backup context
            if self.paths.context.exists():
                shutil.copy2(self.paths.context, backup_path / 'personal_context.json')
            
            # Create backup metadata
            metadata = {
                'created_at': datetime.now().isoformat(),
                'label': label,
                'files': {
                    'profiles': self.paths.profiles.exists(),
                    'context': self.paths.context.exists()
                }
            }
            
            with open(backup_path / 'backup_info.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Backup created: {backup_name}")
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups with metadata"""
        backups = []
        
        try:
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir():
                    info_file = backup_dir / 'backup_info.json'
                    
                    backup_info = {
                        'name': backup_dir.name,
                        'path': str(backup_dir),
                        'created_at': 'Unknown',
                        'label': None,
                        'files': {}
                    }
                    
                    # Load metadata if available
                    if info_file.exists():
                        try:
                            with open(info_file, 'r') as f:
                                metadata = json.load(f)
                                backup_info.update(metadata)
                        except:
                            pass
                    else:
                        # Fallback: parse from directory name
                        try:
                            timestamp_part = backup_dir.name.split('_')[0]
                            date_obj = datetime.strptime(timestamp_part, '%Y%m%d')
                            backup_info['created_at'] = date_obj.isoformat()
                        except:
                            pass
                    
                    # Check which files exist
                    backup_info['files'] = {
                        'profiles': (backup_dir / 'calendar_profiles.json').exists(),
                        'context': (backup_dir / 'personal_context.json').exists()
                    }
                    
                    backups.append(backup_info)
        
        except Exception as e:
            print(f"⚠️ Error listing backups: {e}")
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        return backups
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restore configuration from a backup"""
        try:
            backup_path = self.backup_dir / backup_name
            
            if not backup_path.exists():
                print(f"❌ Backup '{backup_name}' not found")
                return False
            
            # Create current backup before restore
            self.create_backup("before_restore")
            
            # Restore profiles
            profiles_backup = backup_path / 'calendar_profiles.json'
            if profiles_backup.exists():
                shutil.copy2(profiles_backup, self.paths.profiles)
                print("✅ Restored calendar_profiles.json")
            
            # Restore context
            context_backup = backup_path / 'personal_context.json'
            if context_backup.exists():
                shutil.copy2(context_backup, self.paths.context)
                print("✅ Restored personal_context.json")
            
            print(f"✅ Restore completed from backup: {backup_name}")
            return True
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def delete_backup(self, backup_name: str) -> bool:
        """Delete a backup"""
        try:
            backup_path = self.backup_dir / backup_name
            
            if not backup_path.exists():
                print(f"❌ Backup '{backup_name}' not found")
                return False
            
            shutil.rmtree(backup_path)
            print(f"✅ Deleted backup: {backup_name}")
            return True
            
        except Exception as e:
            print(f"❌ Delete failed: {e}")
            return False
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """Clean up old backups, keeping only the most recent ones"""
        try:
            backups = self.list_backups()
            
            if len(backups) <= keep_count:
                return 0
            
            backups_to_delete = backups[keep_count:]
            deleted_count = 0
            
            for backup in backups_to_delete:
                if self.delete_backup(backup['name']):
                    deleted_count += 1
            
            print(f"✅ Cleaned up {deleted_count} old backups")
            return deleted_count
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            return 0
    
    def export_backup(self, backup_name: str, export_path: str) -> bool:
        """Export a backup to external location"""
        try:
            backup_path = self.backup_dir / backup_name
            export_path = Path(export_path)
            
            if not backup_path.exists():
                print(f"❌ Backup '{backup_name}' not found")
                return False
            
            # Create export archive
            archive_name = f"personalagent_backup_{backup_name}"
            shutil.make_archive(
                str(export_path / archive_name),
                'zip',
                str(backup_path)
            )
            
            print(f"✅ Backup exported to: {export_path / archive_name}.zip")
            return True
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
    
    def import_backup(self, import_path: str, backup_name: str = None) -> bool:
        """Import a backup from external location"""
        try:
            import_path = Path(import_path)
            
            if not import_path.exists():
                print(f"❌ Import file not found: {import_path}")
                return False
            
            if backup_name is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"{timestamp}_imported"
            
            backup_path = self.backup_dir / backup_name
            
            # Extract archive
            shutil.unpack_archive(str(import_path), str(backup_path))
            
            print(f"✅ Backup imported as: {backup_name}")
            return True
            
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return False
    
    def get_backup_size(self, backup_name: str = None) -> Dict[str, Any]:
        """Get size information for backups"""
        try:
            if backup_name:
                # Single backup size
                backup_path = self.backup_dir / backup_name
                if not backup_path.exists():
                    return {'error': f"Backup '{backup_name}' not found"}
                
                total_size = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
                return {
                    'backup': backup_name,
                    'size_bytes': total_size,
                    'size_mb': round(total_size / (1024 * 1024), 2)
                }
            else:
                # All backups size
                total_size = 0
                backup_count = 0
                
                for backup_dir in self.backup_dir.iterdir():
                    if backup_dir.is_dir():
                        backup_count += 1
                        total_size += sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file())
                
                return {
                    'total_backups': backup_count,
                    'total_size_bytes': total_size,
                    'total_size_mb': round(total_size / (1024 * 1024), 2),
                    'average_size_mb': round(total_size / (1024 * 1024) / max(backup_count, 1), 2)
                }
                
        except Exception as e:
            return {'error': f"Size calculation failed: {e}"}
