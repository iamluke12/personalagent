#!/usr/bin/env python3
"""
Calendar configuration setup for personalAgent
Discover available calendars and let user select which ones to monitor
"""

import os
import json
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class CalendarConfigurator:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/personalAgent/config")
        self.config_file = os.path.join(self.config_dir, "calendar_config.json")
        self.service = None
        
    def authenticate(self):
        """Get authenticated Google Calendar service"""
        token_path = os.path.join(self.config_dir, "token.json")
        
        if not os.path.exists(token_path):
            print("🚫 No token.json found. Run the OAuth setup first!")
            return False
            
        creds = Credentials.from_authorized_user_file(token_path)
        self.service = build('calendar', 'v3', credentials=creds)
        return True
    
    def discover_calendars(self):
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
                    'access_role': cal.get('accessRole', 'reader'),
                    'background_color': cal.get('backgroundColor', '#9FC6E7'),
                    'foreground_color': cal.get('foregroundColor', '#000000'),
                    'time_zone': cal.get('timeZone', 'UTC')
                }
                calendar_info.append(info)
            
            return calendar_info
            
        except Exception as e:
            print(f"🚫 Error fetching calendars: {e}")
            return []
    
    def display_calendars(self, calendars):
        """Display available calendars for selection"""
        print("\n🌌 Available Calendars in the Gregorian Matrix:")
        print("=" * 60)
        
        for i, cal in enumerate(calendars, 1):
            primary_marker = " 🌟 [PRIMARY]" if cal['primary'] else ""
            print(f"{i:2d}. {cal['name']}{primary_marker}")
            print(f"    📧 {cal['id']}")
            print(f"    🔐 Access: {cal['access_role']}")
            print(f"    🌍 Timezone: {cal['time_zone']}")
            if cal['description']:
                print(f"    📝 {cal['description']}")
            print()
    
    def select_calendars(self, calendars):
        """Interactive calendar selection"""
        self.display_calendars(calendars)
        
        print("Calendar Selection Options:")
        print("  - Enter numbers (e.g., '1,3,5' for calendars 1, 3, and 5)")
        print("  - Enter 'all' to monitor all calendars")
        print("  - Enter 'primary' to monitor only your primary calendar")
        print("  - Press Enter to use current config (if exists)")
        
        while True:
            selection = input("\n🎯 Select calendars: ").strip().lower()
            
            if selection == '':
                # Use existing config if available
                if os.path.exists(self.config_file):
                    print("📋 Using existing calendar configuration")
                    return None
                else:
                    print("⚠️  No existing config found. Please make a selection.")
                    continue
            
            elif selection == 'all':
                return list(range(len(calendars)))
            
            elif selection == 'primary':
                primary_indices = [i for i, cal in enumerate(calendars) if cal['primary']]
                if primary_indices:
                    return primary_indices
                else:
                    print("🚫 No primary calendar found!")
                    continue
            
            else:
                try:
                    # Parse comma-separated numbers
                    indices = [int(x.strip()) - 1 for x in selection.split(',')]
                    
                    # Validate indices
                    if all(0 <= i < len(calendars) for i in indices):
                        return indices
                    else:
                        print("🚫 Invalid calendar numbers! Please try again.")
                        continue
                        
                except ValueError:
                    print("🚫 Invalid input format! Use numbers separated by commas.")
                    continue
    
    def save_config(self, calendars, selected_indices):
        """Save selected calendar configuration"""
        if selected_indices is None:
            return  # Keep existing config
        
        selected_calendars = [calendars[i] for i in selected_indices]
        
        config = {
            'created_at': datetime.now().isoformat(),
            'total_available': len(calendars),
            'selected_count': len(selected_calendars),
            'selected_calendars': selected_calendars,
            'calendar_ids': [cal['id'] for cal in selected_calendars]
        }
        
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n💾 Calendar configuration saved!")
        print(f"📊 Monitoring {len(selected_calendars)} calendar(s):")
        for cal in selected_calendars:
            primary_marker = " 🌟" if cal['primary'] else ""
            print(f"  📅 {cal['name']}{primary_marker}")
    
    def load_config(self):
        """Load existing calendar configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return None
    
    def show_current_config(self):
        """Display current calendar configuration"""
        config = self.load_config()
        
        if not config:
            print("🚫 No calendar configuration found. Run setup first!")
            return
        
        print("\n🌟 Current Calendar Configuration:")
        print("=" * 50)
        print(f"📅 Created: {config['created_at'][:19]}")
        print(f"📊 Monitoring {config['selected_count']} of {config['total_available']} calendars")
        print("\nSelected Calendars:")
        
        for cal in config['selected_calendars']:
            primary_marker = " 🌟 [PRIMARY]" if cal['primary'] else ""
            print(f"  📅 {cal['name']}{primary_marker}")
            print(f"      📧 {cal['id']}")

def main():
    configurator = CalendarConfigurator()
    
    print("🌌 Personal Agent Calendar Configurator")
    print("=" * 50)
    
    # Check for existing config
    existing_config = configurator.load_config()
    if existing_config:
        print("📋 Found existing configuration:")
        configurator.show_current_config()
        
        reconfigure = input("\n🔄 Reconfigure calendars? (y/N): ").lower().strip()
        if reconfigure != 'y':
            print("✅ Keeping existing configuration")
            return
    
    # Discover available calendars
    print("\n🔍 Discovering available calendars...")
    calendars = configurator.discover_calendars()
    
    if not calendars:
        print("🚫 No calendars found or authentication failed!")
        return
    
    # Let user select calendars
    selected_indices = configurator.select_calendars(calendars)
    
    # Save configuration
    configurator.save_config(calendars, selected_indices)
    
    print("\n✨ Calendar configuration complete!")
    print("🎯 You can now use: python scripts/fetchGregorian.py today")

if __name__ == "__main__":
    main()