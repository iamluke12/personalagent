#!/usr/bin/env python3
"""
Context Manager for PersonalAgent
=================================

Manages personal context information including location, preferences,
resources, and behavioral patterns.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class ContextManager:
    """Manages personal context configuration"""
    
    def __init__(self, config_paths):
        """Initialize context manager with configuration paths"""
        self.paths = config_paths
        self.context_file = self.paths.context
    
    def load_context(self) -> Dict[str, Any]:
        """Load context from configuration file"""
        try:
            if self.context_file.exists():
                with open(self.context_file, 'r') as f:
                    return json.load(f)
            else:
                return self._get_default_context()
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"⚠️ Error loading context: {e}")
            return self._get_default_context()
    
    def save_context(self, context_data: Dict[str, Any]) -> bool:
        """Save context to configuration file"""
        try:
            # Create backup before saving
            if self.context_file.exists():
                backup_name = f"context_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_path = self.paths.backup_dir / backup_name
                import shutil
                shutil.copy2(self.context_file, backup_path)
            
            with open(self.context_file, 'w') as f:
                json.dump(context_data, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving context: {e}")
            return False
    
    def update_location(self, location_data: Dict[str, Any]) -> bool:
        """Update location information"""
        context = self.load_context()
        context.setdefault('location', {})
        context['location'].update(location_data)
        return self.save_context(context)
    
    def update_preferences(self, preferences_data: Dict[str, Any]) -> bool:
        """Update user preferences"""
        context = self.load_context()
        context.setdefault('preferences', {})
        context['preferences'].update(preferences_data)
        return self.save_context(context)
    
    def update_resources(self, resources_data: Dict[str, Any]) -> bool:
        """Update available resources"""
        context = self.load_context()
        context.setdefault('resources', {})
        context['resources'].update(resources_data)
        return self.save_context(context)
    
    def update_patterns(self, patterns_data: Dict[str, Any]) -> bool:
        """Update behavioral patterns"""
        context = self.load_context()
        context.setdefault('patterns', {})
        context['patterns'].update(patterns_data)
        return self.save_context(context)
    
    def get_location_info(self) -> Dict[str, Any]:
        """Get location information"""
        context = self.load_context()
        return context.get('location', {})
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences"""
        context = self.load_context()
        return context.get('preferences', {})
    
    def get_resources(self) -> Dict[str, Any]:
        """Get available resources"""
        context = self.load_context()
        return context.get('resources', {})
    
    def get_patterns(self) -> Dict[str, Any]:
        """Get behavioral patterns"""
        context = self.load_context()
        return context.get('patterns', {})
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of context configuration"""
        context = self.load_context()
        
        location = context.get('location', {})
        preferences = context.get('preferences', {})
        resources = context.get('resources', {})
        patterns = context.get('patterns', {})
        
        return {
            'location': {
                'home_set': bool(location.get('home', {}).get('address')),
                'work_location': location.get('work', {}).get('office_location', 'Remote'),
                'has_car': location.get('home', {}).get('has_car', False),
                'grocery_stores': len(location.get('grocery_stores', []))
            },
            'preferences': {
                'transport_method': preferences.get('transport_method', 'Not set'),
                'work_style': preferences.get('work_style', 'Not set'),
                'cooking_skill': preferences.get('cooking_skill', 'Not set'),
                'energy_patterns_set': bool(preferences.get('energy_patterns'))
            },
            'resources': {
                'transportation': {
                    'car': resources.get('has_car', False),
                    'bike': resources.get('has_bike', False)
                },
                'home': {
                    'kitchen': resources.get('kitchen_equipped', False),
                    'office': resources.get('home_office', False)
                }
            },
            'patterns': {
                'meal_prep_time': patterns.get('typical_meal_prep', 'Not set'),
                'commute_time': patterns.get('commute_time', 'Not set'),
                'meeting_prep': patterns.get('meeting_prep', 'Not set')
            }
        }
    
    def setup_wizard_questions(self) -> List[Dict[str, Any]]:
        """Get questions for context setup wizard"""
        return [
            {
                'section': 'location',
                'questions': [
                    {
                        'key': 'home.address',
                        'prompt': 'Home address (city, country)',
                        'type': 'string',
                        'required': True
                    },
                    {
                        'key': 'home.has_car',
                        'prompt': 'Do you have a car?',
                        'type': 'boolean',
                        'default': False
                    },
                    {
                        'key': 'work.remote',
                        'prompt': 'Do you work remotely?',
                        'type': 'boolean',
                        'default': True
                    },
                    {
                        'key': 'work.office_location',
                        'prompt': 'Office location (if not remote)',
                        'type': 'string',
                        'condition': 'work.remote == False'
                    }
                ]
            },
            {
                'section': 'preferences',
                'questions': [
                    {
                        'key': 'transport_method',
                        'prompt': 'Primary transport method',
                        'type': 'choice',
                        'choices': ['car', 'public_transport', 'bike', 'walking'],
                        'default': 'public_transport'
                    },
                    {
                        'key': 'work_style',
                        'prompt': 'Work style preference',
                        'type': 'choice',
                        'choices': ['deep_focus', 'collaborative', 'balanced', 'flexible'],
                        'default': 'balanced'
                    },
                    {
                        'key': 'cooking_skill',
                        'prompt': 'Cooking skill level',
                        'type': 'choice',
                        'choices': ['beginner', 'intermediate', 'advanced'],
                        'default': 'intermediate'
                    }
                ]
            },
            {
                'section': 'resources',
                'questions': [
                    {
                        'key': 'has_bike',
                        'prompt': 'Do you have a bike?',
                        'type': 'boolean',
                        'default': False
                    },
                    {
                        'key': 'kitchen_equipped',
                        'prompt': 'Is your kitchen well-equipped?',
                        'type': 'boolean',
                        'default': True
                    },
                    {
                        'key': 'home_office',
                        'prompt': 'Do you have a home office?',
                        'type': 'boolean',
                        'default': True
                    }
                ]
            },
            {
                'section': 'patterns',
                'questions': [
                    {
                        'key': 'typical_meal_prep',
                        'prompt': 'Typical meal prep time (minutes)',
                        'type': 'integer',
                        'default': 30
                    },
                    {
                        'key': 'commute_time',
                        'prompt': 'Typical commute time (minutes)',
                        'type': 'integer',
                        'default': 15
                    },
                    {
                        'key': 'meeting_prep',
                        'prompt': 'Meeting preparation time (minutes)',
                        'type': 'integer',
                        'default': 10
                    }
                ]
            }
        ]
    
    def validate(self) -> Dict[str, Any]:
        """Validate context configuration"""
        status = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            context = self.load_context()
            
            # Check if major sections exist
            required_sections = ['location', 'preferences', 'resources']
            for section in required_sections:
                if section not in context:
                    status['warnings'].append(f"Missing '{section}' section")
            
            # Validate location section
            location = context.get('location', {})
            if location:
                home = location.get('home', {})
                if not home.get('address'):
                    status['warnings'].append("Home address not set")
                
                work = location.get('work', {})
                if not work.get('remote') and not work.get('office_location'):
                    status['warnings'].append("Office location not set for non-remote work")
            
            # Validate preferences
            preferences = context.get('preferences', {})
            valid_transport = ['car', 'public_transport', 'bike', 'walking']
            if preferences.get('transport_method') not in valid_transport:
                status['warnings'].append("Invalid transport method")
            
            # Validate patterns (numeric values)
            patterns = context.get('patterns', {})
            for key, value in patterns.items():
                if isinstance(value, (int, float)) and value < 0:
                    status['warnings'].append(f"Negative value for {key}: {value}")
            
        except Exception as e:
            status['errors'].append(f"Validation error: {str(e)}")
            status['valid'] = False
        
        return status
    
    def _get_default_context(self) -> Dict[str, Any]:
        """Get default context configuration"""
        return {
            "location": {
                "home": {
                    "address": "",
                    "has_kitchen": True,
                    "has_car": False
                },
                "work": {
                    "remote": True,
                    "office_location": ""
                },
                "grocery_stores": [],
                "gym": ""
            },
            "preferences": {
                "cooking_skill": "intermediate",
                "transport_method": "public_transport",
                "work_style": "balanced",
                "energy_patterns": {
                    "peak": ["09:00", "14:00"],
                    "low": ["13:00", "16:00"]
                }
            },
            "resources": {
                "has_car": False,
                "has_bike": False,
                "kitchen_equipped": True,
                "home_office": True
            },
            "patterns": {
                "typical_meal_prep": 30,
                "commute_time": 15,
                "meeting_prep": 10
            }
        }
