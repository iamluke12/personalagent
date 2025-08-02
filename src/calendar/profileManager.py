#!/usr/bin/env python3
"""
Calendar Profile Manager for personalAgent
Manages calendar profiles with priority hierarchy and conflict resolution
Family > Personal > Work > External priority system
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import argparse

class CalendarProfileManager:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/personalAgent/config")
        self.profiles_file = os.path.join(self.config_dir, "calendar_profiles.json")
        self.profiles = self.load_profiles()
        
    def load_profiles(self) -> Dict:
        """Load calendar profiles configuration"""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading profiles: {e}")
                return self.create_default_profiles()
        else:
            return self.create_default_profiles()
    
    def create_default_profiles(self) -> Dict:
        """Create default profile configuration"""
        # This would be created with the actual calendar data
        # For now, return basic structure
        return {
            "profiles": {},
            "current_profile": "family",
            "settings": {
                "auto_switch_on_keyword": True,
                "override_mode": False,
                "conflict_notification": True,
                "smart_suggestions": True,
                "terminal_prompt_integration": False
            }
        }
    
    def save_profiles(self):
        """Save profiles configuration"""
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.profiles_file, 'w') as f:
            json.dump(self.profiles, f, indent=2)
    
    def get_current_profile(self) -> Optional[str]:
        """Get currently active profile"""
        return self.profiles.get("current_profile")
    
    def set_current_profile(self, profile_name: str) -> bool:
        """Set current active profile"""
        if profile_name in self.profiles.get("profiles", {}):
            self.profiles["current_profile"] = profile_name
            self.save_profiles()
            print(f"✅ Switched to {profile_name} profile")
            return True
        else:
            print(f"❌ Profile '{profile_name}' not found")
            return False
    
    def list_profiles(self):
        """List all available profiles"""
        current = self.get_current_profile()
        profiles = self.profiles.get("profiles", {})
        
        if not profiles:
            print("📝 No profiles configured")
            return
            
        print("📋 CALENDAR PROFILES")
        print("=" * 40)
        
        # Sort by priority
        sorted_profiles = sorted(
            profiles.items(), 
            key=lambda x: x[1].get("priority", 999)
        )
        
        for name, profile in sorted_profiles:
            current_marker = "🔸" if name == current else "  "
            priority = profile.get("priority", "?")
            description = profile.get("description", "No description")
            calendar_count = len(profile.get("calendars", []))
            
            print(f"{current_marker} {name.upper()} (Priority {priority})")
            print(f"   📅 {calendar_count} calendar(s) - {description}")
    
    def get_profile_calendars(self, profile_name: str = None) -> List[Dict]:
        """Get calendars for specific profile or current profile"""
        if not profile_name:
            profile_name = self.get_current_profile()
            
        if not profile_name:
            return []
            
        profile = self.profiles.get("profiles", {}).get(profile_name, {})
        return profile.get("calendars", [])
    
    def get_primary_calendar_id(self, profile_name: str = None) -> Optional[str]:
        """Get primary calendar ID for profile"""
        calendars = self.get_profile_calendars(profile_name)
        
        for calendar in calendars:
            if calendar.get("role") == "primary":
                return calendar.get("id")
        
        # Return first calendar if no primary found
        if calendars:
            return calendars[0].get("id")
            
        return None
    
    def check_conflict(self, start_time: datetime, end_time: datetime, profile_name: str = None) -> Tuple[bool, List[Dict]]:
        """Check for conflicts with higher priority profiles"""
        if not profile_name:
            profile_name = self.get_current_profile()
            
        current_profile = self.profiles.get("profiles", {}).get(profile_name, {})
        current_priority = current_profile.get("priority", 999)
        
        conflicts = []
        
        # Check against higher priority profiles
        for name, profile in self.profiles.get("profiles", {}).items():
            if profile.get("priority", 999) < current_priority:
                # This is a higher priority profile, check for conflicts
                # For now, we'll simulate conflict checking
                # In real implementation, this would query the calendar API
                conflicts.extend(self._simulate_conflict_check(name, start_time, end_time))
        
        return len(conflicts) > 0, conflicts
    
    def _simulate_conflict_check(self, profile_name: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Simulate conflict checking (would use real calendar API)"""
        # This is a placeholder - real implementation would check calendar events
        return []
    
    def suggest_alternative_times(self, requested_start: datetime, duration_minutes: int, profile_name: str = None) -> List[Dict]:
        """Suggest alternative times for scheduling"""
        if not profile_name:
            profile_name = self.get_current_profile()
            
        suggestions = []
        
        # Generate suggestions for the same day
        base_date = requested_start.date()
        
        # Suggest 30 minutes later
        alt1 = requested_start + timedelta(minutes=30)
        suggestions.append({
            "start_time": alt1,
            "end_time": alt1 + timedelta(minutes=duration_minutes),
            "reason": "30 minutes later"
        })
        
        # Suggest 1 hour later
        alt2 = requested_start + timedelta(hours=1)
        suggestions.append({
            "start_time": alt2,
            "end_time": alt2 + timedelta(minutes=duration_minutes),
            "reason": "1 hour later"
        })
        
        # Suggest next available slot (simplified)
        alt3 = requested_start + timedelta(hours=2)
        suggestions.append({
            "start_time": alt3,
            "end_time": alt3 + timedelta(minutes=duration_minutes),
            "reason": "Next available slot"
        })
        
        return suggestions
    
    def get_profile_display_settings(self, profile_name: str = None) -> Dict:
        """Get display settings for profile"""
        if not profile_name:
            profile_name = self.get_current_profile()
            
        profile = self.profiles.get("profiles", {}).get(profile_name, {})
        return profile.get("display_settings", {})
    
    def should_show_family_events(self, profile_name: str = None) -> bool:
        """Check if family events should be shown in this profile"""
        settings = self.get_profile_display_settings(profile_name)
        return settings.get("show_family_events", True)
    
    def get_filter_keywords(self, profile_name: str = None) -> List[str]:
        """Get filter keywords for profile"""
        settings = self.get_profile_display_settings(profile_name)
        return settings.get("filter_keywords", [])
    
    def auto_detect_profile(self, event_title: str, event_description: str = "") -> Optional[str]:
        """Auto-detect appropriate profile based on keywords"""
        if not self.profiles.get("settings", {}).get("auto_switch_on_keyword", False):
            return None
            
        text = f"{event_title} {event_description}".lower()
        
        # Check each profile for keyword matches
        best_match = None
        max_matches = 0
        
        for name, profile in self.profiles.get("profiles", {}).items():
            keywords = self.get_filter_keywords(name)
            matches = sum(1 for keyword in keywords if keyword.lower() in text)
            
            if matches > max_matches:
                max_matches = matches
                best_match = name
        
        return best_match if max_matches > 0 else None
    
    def export_current_context(self) -> Dict:
        """Export current profile context for other scripts"""
        current_profile = self.get_current_profile()
        
        if not current_profile:
            return {}
            
        profile = self.profiles.get("profiles", {}).get(current_profile, {})
        primary_calendar_id = self.get_primary_calendar_id(current_profile)
        
        return {
            "profile_name": current_profile,
            "profile_priority": profile.get("priority", 999),
            "primary_calendar_id": primary_calendar_id,
            "calendars": self.get_profile_calendars(current_profile),
            "display_settings": self.get_profile_display_settings(current_profile),
            "conflict_resolution": profile.get("conflict_resolution", {}),
            "filter_keywords": self.get_filter_keywords(current_profile)
        }

def main():
    parser = argparse.ArgumentParser(description="Calendar Profile Manager")
    parser.add_argument("action", choices=["switch", "list", "current", "context", "conflicts"], 
                       help="Action to perform")
    parser.add_argument("--profile", "-p", help="Profile name for switch action")
    parser.add_argument("--start", help="Start time for conflict check (ISO format)")
    parser.add_argument("--duration", type=int, default=60, help="Duration in minutes for conflict check")
    
    args = parser.parse_args()
    
    manager = CalendarProfileManager()
    
    if args.action == "switch":
        if not args.profile:
            print("❌ Profile name required for switch action")
            sys.exit(1)
        manager.set_current_profile(args.profile)
        
    elif args.action == "list":
        manager.list_profiles()
        
    elif args.action == "current":
        current = manager.get_current_profile()
        if current:
            profile = manager.profiles.get("profiles", {}).get(current, {})
            print(f"📍 Current Profile: {current.upper()}")
            print(f"   Priority: {profile.get('priority', '?')}")
            print(f"   Description: {profile.get('description', 'No description')}")
            
            calendars = manager.get_profile_calendars()
            print(f"   Calendars: {len(calendars)}")
            for cal in calendars:
                role_marker = "🔸" if cal.get("role") == "primary" else "  "
                print(f"   {role_marker} {cal.get('name', 'Unknown')} ({cal.get('access', 'unknown')})")
        else:
            print("❌ No profile currently selected")
            
    elif args.action == "context":
        context = manager.export_current_context()
        print(json.dumps(context, indent=2))
        
    elif args.action == "conflicts":
        if not args.start:
            print("❌ Start time required for conflict check")
            sys.exit(1)
            
        try:
            start_time = datetime.fromisoformat(args.start)
            end_time = start_time + timedelta(minutes=args.duration)
            
            has_conflicts, conflicts = manager.check_conflict(start_time, end_time)
            
            if has_conflicts:
                print(f"⚠️ CONFLICTS DETECTED for {start_time.strftime('%Y-%m-%d %H:%M')}")
                for conflict in conflicts:
                    print(f"   🔸 {conflict}")
                    
                print("\n💡 SUGGESTED ALTERNATIVES:")
                suggestions = manager.suggest_alternative_times(start_time, args.duration)
                for i, suggestion in enumerate(suggestions, 1):
                    start_str = suggestion["start_time"].strftime('%H:%M')
                    end_str = suggestion["end_time"].strftime('%H:%M')
                    print(f"   {i}. {start_str}-{end_str} ({suggestion['reason']})")
            else:
                print(f"✅ No conflicts for {start_time.strftime('%Y-%m-%d %H:%M')}")
                
        except ValueError:
            print("❌ Invalid start time format. Use ISO format (YYYY-MM-DDTHH:MM)")
            sys.exit(1)

if __name__ == "__main__":
    main()
