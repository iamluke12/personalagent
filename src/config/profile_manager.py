#!/usr/bin/env python3
"""
Profile Manager for PersonalAgent
=================================

Manages calendar profiles with priority-based hierarchy and conflict resolution.
Handles CRUD operations for profiles and calendar assignments.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class ProfileManager:
    """Manages calendar profiles and their configurations"""
    
    def __init__(self, config_paths):
        """Initialize profile manager with configuration paths"""
        self.paths = config_paths
        self.profiles_file = self.paths.profiles
    
    def load_profiles(self) -> Dict[str, Any]:
        """Load profiles from configuration file"""
        try:
            if self.profiles_file.exists():
                with open(self.profiles_file, 'r') as f:
                    return json.load(f)
            else:
                return self._get_default_profiles()
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"⚠️ Error loading profiles: {e}")
            return self._get_default_profiles()
    
    def save_profiles(self, profiles_data: Dict[str, Any]) -> bool:
        """Save profiles to configuration file"""
        try:
            # Create backup before saving
            if self.profiles_file.exists():
                backup_name = f"profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_path = self.paths.backup_dir / backup_name
                import shutil
                shutil.copy2(self.profiles_file, backup_path)
            
            with open(self.profiles_file, 'w') as f:
                json.dump(profiles_data, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving profiles: {e}")
            return False
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """Get list of all profiles with summary information"""
        profiles_data = self.load_profiles()
        profiles_list = []
        
        for profile_id, profile in profiles_data.get('profiles', {}).items():
            profiles_list.append({
                'id': profile_id,
                'name': profile.get('name', profile_id),
                'description': profile.get('description', ''),
                'priority': profile.get('priority', 999),
                'calendar_count': len(profile.get('calendars', [])),
                'is_current': profile_id == profiles_data.get('current_profile')
            })
        
        # Sort by priority
        profiles_list.sort(key=lambda x: x['priority'])
        return profiles_list
    
    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific profile"""
        profiles_data = self.load_profiles()
        return profiles_data.get('profiles', {}).get(profile_id)
    
    def create_profile(self, profile_id: str, profile_data: Dict[str, Any]) -> bool:
        """Create a new profile"""
        profiles_data = self.load_profiles()
        
        if profile_id in profiles_data.get('profiles', {}):
            print(f"❌ Profile '{profile_id}' already exists")
            return False
        
        # Validate required fields
        required_fields = ['name', 'description', 'priority']
        for field in required_fields:
            if field not in profile_data:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Add default structure
        profile_data.setdefault('calendars', [])
        profile_data.setdefault('conflict_resolution', {
            'blocks_others': False,
            'can_be_moved': True,
            'auto_suggest_alternatives': True
        })
        profile_data.setdefault('display_settings', {
            'show_as_busy': True,
            'filter_keywords': []
        })
        
        # Add to profiles
        if 'profiles' not in profiles_data:
            profiles_data['profiles'] = {}
        
        profiles_data['profiles'][profile_id] = profile_data
        
        # Set as current if it's the first profile
        if len(profiles_data['profiles']) == 1:
            profiles_data['current_profile'] = profile_id
        
        return self.save_profiles(profiles_data)
    
    def update_profile(self, profile_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing profile"""
        profiles_data = self.load_profiles()
        
        if profile_id not in profiles_data.get('profiles', {}):
            print(f"❌ Profile '{profile_id}' not found")
            return False
        
        # Update the profile
        profiles_data['profiles'][profile_id].update(updates)
        
        return self.save_profiles(profiles_data)
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile"""
        profiles_data = self.load_profiles()
        
        if profile_id not in profiles_data.get('profiles', {}):
            print(f"❌ Profile '{profile_id}' not found")
            return False
        
        # Don't allow deleting the only profile
        if len(profiles_data.get('profiles', {})) <= 1:
            print("❌ Cannot delete the only profile")
            return False
        
        # Remove profile
        del profiles_data['profiles'][profile_id]
        
        # Update current profile if needed
        if profiles_data.get('current_profile') == profile_id:
            # Set to first available profile
            remaining_profiles = list(profiles_data['profiles'].keys())
            if remaining_profiles:
                profiles_data['current_profile'] = remaining_profiles[0]
        
        return self.save_profiles(profiles_data)
    
    def set_current_profile(self, profile_id: str) -> bool:
        """Set the current active profile"""
        profiles_data = self.load_profiles()
        
        if profile_id not in profiles_data.get('profiles', {}):
            print(f"❌ Profile '{profile_id}' not found")
            return False
        
        profiles_data['current_profile'] = profile_id
        return self.save_profiles(profiles_data)
    
    def add_calendar_to_profile(self, profile_id: str, calendar_data: Dict[str, Any]) -> bool:
        """Add a calendar to a profile"""
        profiles_data = self.load_profiles()
        
        if profile_id not in profiles_data.get('profiles', {}):
            print(f"❌ Profile '{profile_id}' not found")
            return False
        
        # Validate calendar data
        required_fields = ['id', 'name']
        for field in required_fields:
            if field not in calendar_data:
                print(f"❌ Missing required calendar field: {field}")
                return False
        
        # Add defaults
        calendar_data.setdefault('role', 'primary')
        calendar_data.setdefault('access', 'owner')
        calendar_data.setdefault('color', '#4ECDC4')
        
        # Check if calendar already exists in profile
        profile = profiles_data['profiles'][profile_id]
        for existing_cal in profile.get('calendars', []):
            if existing_cal['id'] == calendar_data['id']:
                print(f"❌ Calendar '{calendar_data['id']}' already in profile")
                return False
        
        # Add calendar
        if 'calendars' not in profile:
            profile['calendars'] = []
        
        profile['calendars'].append(calendar_data)
        
        return self.save_profiles(profiles_data)
    
    def remove_calendar_from_profile(self, profile_id: str, calendar_id: str) -> bool:
        """Remove a calendar from a profile"""
        profiles_data = self.load_profiles()
        
        if profile_id not in profiles_data.get('profiles', {}):
            print(f"❌ Profile '{profile_id}' not found")
            return False
        
        profile = profiles_data['profiles'][profile_id]
        calendars = profile.get('calendars', [])
        
        # Find and remove calendar
        for i, calendar in enumerate(calendars):
            if calendar['id'] == calendar_id:
                calendars.pop(i)
                return self.save_profiles(profiles_data)
        
        print(f"❌ Calendar '{calendar_id}' not found in profile")
        return False
    
    def validate(self) -> Dict[str, Any]:
        """Validate profiles configuration"""
        status = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            profiles_data = self.load_profiles()
            
            # Check basic structure
            if 'profiles' not in profiles_data:
                status['errors'].append("Missing 'profiles' section")
                status['valid'] = False
                return status
            
            if not profiles_data['profiles']:
                status['errors'].append("No profiles defined")
                status['valid'] = False
                return status
            
            # Validate each profile
            priorities = []
            for profile_id, profile in profiles_data['profiles'].items():
                # Check required fields
                for field in ['name', 'priority']:
                    if field not in profile:
                        status['errors'].append(f"Profile '{profile_id}' missing '{field}'")
                        status['valid'] = False
                
                # Check priority uniqueness
                priority = profile.get('priority')
                if priority in priorities:
                    status['warnings'].append(f"Duplicate priority {priority} in profile '{profile_id}'")
                priorities.append(priority)
                
                # Validate calendars
                for calendar in profile.get('calendars', []):
                    if 'id' not in calendar or 'name' not in calendar:
                        status['errors'].append(f"Invalid calendar in profile '{profile_id}'")
                        status['valid'] = False
            
            # Check current profile
            current = profiles_data.get('current_profile')
            if current and current not in profiles_data['profiles']:
                status['errors'].append(f"Current profile '{current}' does not exist")
                status['valid'] = False
            
        except Exception as e:
            status['errors'].append(f"Validation error: {str(e)}")
            status['valid'] = False
        
        return status
    
    def _get_default_profiles(self) -> Dict[str, Any]:
        """Get default profiles configuration"""
        return {
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
