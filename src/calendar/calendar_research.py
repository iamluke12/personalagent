#!/usr/bin/env python3
"""
Google Calendar API Research Tool
Explore available calendars and understand the API structure
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def research_calendar_api():
    """Research what calendars are available and how the API works"""
    config_dir = os.path.expanduser("~/personalAgent/config")
    token_path = os.path.join(config_dir, "token.json")
    
    if not os.path.exists(token_path):
        print("🚫 No token.json found. Please authenticate first!")
        return
    
    # Authenticate
    creds = Credentials.from_authorized_user_file(token_path)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    service = build('calendar', 'v3', credentials=creds)
    
    print("🔍 GOOGLE CALENDAR API RESEARCH")
    print("=" * 60)
    
    # 1. List all available calendars
    print("\n📅 AVAILABLE CALENDARS:")
    print("-" * 40)
    
    try:
        calendars_result = service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])
        
        print(f"Total calendars found: {len(calendars)}")
        print()
        
        for i, cal in enumerate(calendars, 1):
            print(f"{i:2}. {cal.get('summary', 'Unknown')}")
            print(f"    📧 ID: {cal['id']}")
            print(f"    🏠 Primary: {cal.get('primary', False)}")
            print(f"    🔑 Access: {cal.get('accessRole', 'unknown')}")
            print(f"    🎨 Color: {cal.get('backgroundColor', 'default')}")
            if cal.get('description'):
                print(f"    📝 Description: {cal.get('description')}")
            print(f"    🌍 Timezone: {cal.get('timeZone', 'unknown')}")
            print(f"    👁️  Selected: {cal.get('selected', True)}")
            if cal.get('summaryOverride'):
                print(f"    🏷️  Override: {cal.get('summaryOverride')}")
            print()
        
        # 2. Test fetching events from different calendars
        print("\n📋 EVENTS BY CALENDAR:")
        print("-" * 40)
        
        from datetime import datetime, timedelta
        time_min = datetime.now().isoformat() + 'Z'
        time_max = (datetime.now() + timedelta(days=7)).isoformat() + 'Z'
        
        total_events = 0
        for cal in calendars[:3]:  # Test first 3 calendars
            calendar_id = cal['id']
            calendar_name = cal.get('summary', 'Unknown')
            
            try:
                events_result = service.events().list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=10,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                events = events_result.get('items', [])
                print(f"📅 {calendar_name}: {len(events)} events")
                
                for event in events[:3]:  # Show first 3 events
                    title = event.get('summary', 'No title')
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    print(f"   • {title} ({start})")
                
                total_events += len(events)
                if events:
                    print()
                    
            except Exception as e:
                print(f"   ❌ Error accessing {calendar_name}: {e}")
        
        print(f"\nTotal events across calendars: {total_events}")
        
        # 3. Check current configuration
        print("\n⚙️  CURRENT CONFIGURATION:")
        print("-" * 40)
        
        config_file = os.path.join(config_dir, "calendar_config.json")
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print("Current selected calendars:")
            for cal in config.get('selected_calendars', []):
                print(f"  📅 {cal.get('name', 'Unknown')} ({cal.get('id', 'unknown')})")
        else:
            print("No calendar configuration found")
        
        # 4. API Insights
        print("\n💡 API INSIGHTS:")
        print("-" * 40)
        print("• Each Google account can have multiple calendars")
        print("• You can subscribe to external calendars (like coworkers')")
        print("• Each calendar has a unique ID (usually email@domain.com)")
        print("• You can fetch events from specific calendars or all at once")
        print("• Primary calendar is usually your main Google account calendar")
        print("• Access roles: owner, reader, writer, freeBusyReader")
        
        # 5. Save research results
        research_data = {
            "research_date": datetime.now().isoformat(),
            "total_calendars": len(calendars),
            "calendars": [
                {
                    "name": cal.get('summary'),
                    "id": cal['id'],
                    "primary": cal.get('primary', False),
                    "access": cal.get('accessRole'),
                    "selected": cal.get('selected', True),
                    "description": cal.get('description', '')
                }
                for cal in calendars
            ]
        }
        
        research_file = os.path.join(config_dir, "calendar_research.json")
        with open(research_file, 'w') as f:
            json.dump(research_data, f, indent=2)
        
        print(f"\n💾 Research saved to: {research_file}")
        
    except Exception as e:
        print(f"❌ Error researching calendars: {e}")

if __name__ == "__main__":
    research_calendar_api()
