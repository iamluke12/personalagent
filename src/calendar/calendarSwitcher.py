#!/usr/bin/env python3
"""
Calendar Switcher for personalAgent
Quick switching between different calendar contexts (work, family, etc.)
"""

import os
import json
import sys
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class CalendarSwitcher:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/personalAgent/config")
        self.config_file = os.path.join(self.config_dir, "calendar_config.json")
        self.profiles_file = os.path.join(self.config_dir, "calendar_profiles.json")
        self.service = None
        
    def authenticate(self):
        """Get authenticated Google Calendar service"""
        token_path = os.path.join(self.config_dir, "token.json")
        
        if not os.path.exists(token_path):
            print("🚫 No token.json found. Please authenticate first!")
            return False
            
        creds = Credentials.from_authorized_user_file(token_path)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
        self.service = build('calendar', 'v3', credentials=creds)
        return True
    
    def get_all_calendars(self):
        """Fetch all available calendars"""
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            calendars_result = self.service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])
            
            calendar_info = []
            for cal in calendars:
                info = {
                    'id': cal['id'],
                    'name': cal.get('summary', 'Unknown Calendar'),
                    'description': cal.get('description', ''),
                    'primary': cal.get('primary', False),
                    'access_role': cal.get('accessRole', 'reader')
                }
                calendar_info.append(info)
                
            return calendar_info
        except Exception as e:
            print(f"❌ Error fetching calendars: {e}")
            return []
    
    def load_profiles(self):
        """Load saved calendar profiles"""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading profiles: {e}")
        
        return {"profiles": {}, "current_profile": None}
    
    def save_profiles(self, profiles_data):
        """Save calendar profiles"""
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.profiles_file, 'w') as f:
            json.dump(profiles_data, f, indent=2)
    
    def get_current_calendar(self):
        """Get currently active calendar"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    if config.get('selected_calendars'):
                        return config['selected_calendars'][0]  # First selected calendar
            except Exception as e:
                print(f"⚠️  Error reading current config: {e}")
        return None
    
    def set_active_calendar(self, calendar_id, calendar_name=None):
        """Set a specific calendar as active"""
        # Find the calendar details if name not provided
        if not calendar_name:
            calendars = self.get_all_calendars()
            calendar_info = next((cal for cal in calendars if cal['id'] == calendar_id), None)
            if not calendar_info:
                print(f"❌ Calendar {calendar_id} not found!")
                return False
        else:
            calendar_info = {'id': calendar_id, 'name': calendar_name}
        
        # Update the main calendar config
        config = {
            'created_at': datetime.now().isoformat(),
            'total_available': 1,
            'selected_count': 1,
            'selected_calendars': [calendar_info],
            'calendar_ids': [calendar_id]
        }
        
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return True
    
    def list_calendars(self):
        """List all available calendars"""
        print("📅 AVAILABLE CALENDARS")
        print("=" * 50)
        
        calendars = self.get_all_calendars()
        current = self.get_current_calendar()
        current_id = current['id'] if current else None
        
        for i, cal in enumerate(calendars, 1):
            primary_marker = " 🌟" if cal['primary'] else ""
            active_marker = " ✅" if cal['id'] == current_id else ""
            description = f" - {cal['description']}" if cal['description'] else ""
            
            print(f"{i:2}. {cal['name']}{primary_marker}{active_marker}{description}")
            print(f"    📧 {cal['id']}")
            print(f"    🔑 {cal['access_role']}")
            print()
        
        return calendars
    
    def create_profile(self, profile_name, calendar_id):
        """Create a new calendar profile"""
        profiles_data = self.load_profiles()
        
        # Find calendar info
        calendars = self.get_all_calendars()
        calendar_info = next((cal for cal in calendars if cal['id'] == calendar_id), None)
        
        if not calendar_info:
            print(f"❌ Calendar {calendar_id} not found!")
            return False
        
        profiles_data["profiles"][profile_name] = {
            "calendar_id": calendar_id,
            "calendar_name": calendar_info['name'],
            "created_at": datetime.now().isoformat()
        }
        
        self.save_profiles(profiles_data)
        print(f"✅ Profile '{profile_name}' created for calendar '{calendar_info['name']}'")
        return True
    
    def switch_to_profile(self, profile_name):
        """Switch to a saved profile"""
        profiles_data = self.load_profiles()
        
        if profile_name not in profiles_data["profiles"]:
            print(f"❌ Profile '{profile_name}' not found!")
            self.list_profiles()
            return False
        
        profile = profiles_data["profiles"][profile_name]
        if self.set_active_calendar(profile["calendar_id"], profile["calendar_name"]):
            profiles_data["current_profile"] = profile_name
            self.save_profiles(profiles_data)
            print(f"✅ Switched to '{profile_name}' calendar: {profile['calendar_name']}")
            return True
        
        return False
    
    def list_profiles(self):
        """List all saved profiles"""
        profiles_data = self.load_profiles()
        current_profile = profiles_data.get("current_profile")
        
        print("👤 CALENDAR PROFILES")
        print("=" * 50)
        
        if not profiles_data["profiles"]:
            print("No profiles created yet.")
            print("\n💡 Create profiles with: pacal-profile create <name> <calendar_number>")
            return
        
        for name, profile in profiles_data["profiles"].items():
            active_marker = " ✅" if name == current_profile else ""
            print(f"📋 {name}{active_marker}")
            print(f"   📅 {profile['calendar_name']}")
            print(f"   📧 {profile['calendar_id']}")
            print()
    
    def show_current(self):
        """Show current active calendar"""
        current = self.get_current_calendar()
        profiles_data = self.load_profiles()
        current_profile = profiles_data.get("current_profile")
        
        if current:
            primary_marker = " 🌟" if current.get('primary') else ""
            profile_marker = f" (Profile: {current_profile})" if current_profile else ""
            
            print(f"📅 CURRENT CALENDAR")
            print("=" * 30)
            print(f"📋 {current['name']}{primary_marker}{profile_marker}")
            print(f"📧 {current['id']}")
            if current.get('description'):
                print(f"📝 {current['description']}")
        else:
            print("❌ No calendar currently configured")
            print("💡 Run 'pacal-setup' to configure calendars")

def main():
    switcher = CalendarSwitcher()
    
    if len(sys.argv) < 2:
        switcher.show_current()
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        switcher.list_calendars()
    
    elif command == "current":
        switcher.show_current()
    
    elif command == "profiles":
        switcher.list_profiles()
    
    elif command == "switch":
        if len(sys.argv) < 3:
            print("Usage: pacal-switch switch <profile_name>")
            switcher.list_profiles()
            return
        
        profile_name = sys.argv[2]
        switcher.switch_to_profile(profile_name)
    
    elif command == "quick":
        if len(sys.argv) < 3:
            print("Usage: pacal-switch quick <calendar_number>")
            calendars = switcher.list_calendars()
            return
        
        try:
            cal_number = int(sys.argv[2])
            calendars = switcher.get_all_calendars()
            if 1 <= cal_number <= len(calendars):
                calendar = calendars[cal_number - 1]
                if switcher.set_active_calendar(calendar['id'], calendar['name']):
                    print(f"✅ Switched to: {calendar['name']}")
            else:
                print(f"❌ Invalid calendar number. Choose 1-{len(calendars)}")
        except ValueError:
            print("❌ Please provide a valid number")
    
    elif command == "profile":
        if len(sys.argv) < 4:
            print("Usage: pacal-switch profile <profile_name> <calendar_number>")
            switcher.list_calendars()
            return
        
        profile_name = sys.argv[2]
        try:
            cal_number = int(sys.argv[3])
            calendars = switcher.get_all_calendars()
            if 1 <= cal_number <= len(calendars):
                calendar = calendars[cal_number - 1]
                switcher.create_profile(profile_name, calendar['id'])
            else:
                print(f"❌ Invalid calendar number. Choose 1-{len(calendars)}")
        except ValueError:
            print("❌ Please provide a valid number")
    
    else:
        print("📅 CALENDAR SWITCHER")
        print("=" * 40)
        print("Usage:")
        print("  pacal-switch                    Show current calendar")
        print("  pacal-switch list               List all calendars")
        print("  pacal-switch current            Show current calendar")
        print("  pacal-switch quick <number>     Quick switch by number")
        print("  pacal-switch profiles           List saved profiles")
        print("  pacal-switch switch <profile>   Switch to profile")
        print("  pacal-switch profile <name> <#> Create new profile")
        print()
        print("💡 Examples:")
        print("  pacal-switch quick 2            Switch to calendar #2")
        print("  pacal-switch profile work 1     Create 'work' profile")
        print("  pacal-switch switch work        Switch to work calendar")

if __name__ == "__main__":
    main()
