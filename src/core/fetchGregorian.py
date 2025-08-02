#!/usr/bin/env python3
"""
Google Calendar fetcher for the personalAgent consciousness management system
Extracts events from the Gregorian imprisonment system
"""

import os
import sys
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

class GregorianCalendarFetcher:
    def __init__(self):
        # Use environment variables for paths
        project_root = os.getenv('PROJECT_ROOT', os.path.expanduser('~/personalAgent'))
        self.credentials_path = os.path.join(project_root, os.getenv('GOOGLE_CREDENTIALS_PATH', 'config/credentials.json'))
        self.token_path = os.path.join(project_root, os.getenv('GOOGLE_TOKEN_PATH', 'config/token.json'))
        self.data_dir = os.path.join(project_root, 'data/cache')
        self.scopes = ['https://www.googleapis.com/auth/calendar.readonly']
        self.service = None
        
    def authenticate(self):
        """Establish connection to the Gregorian calendar matrix"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
        
        # If no valid credentials, initiate OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    print("🚫 No credentials.json found. Please download from Google Cloud Console.")
                    sys.exit(1)
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.scopes)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
        print("✨ Connected to Gregorian calendar matrix")
    
    def get_time_range(self, timeframe):
        """Calculate time boundaries based on requested timeframe"""
        now = datetime.now()
        
        if timeframe == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif timeframe == "tomorrow":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            end = start + timedelta(days=1)
        elif timeframe == "thisweek":
            # Start from Monday
            days_since_monday = now.weekday()
            start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
            end = start + timedelta(days=7)
        elif timeframe == "nextweek":
            days_since_monday = now.weekday()
            start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday) + timedelta(days=7)
            end = start + timedelta(days=7)
        elif timeframe == "thismonth":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end = start.replace(year=now.year + 1, month=1)
            else:
                end = start.replace(month=now.month + 1)
        else:
            # Default to today
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        
        return start.isoformat() + 'Z', end.isoformat() + 'Z'
    
    def load_calendar_config(self):
        """Load selected calendar configuration"""
        config_file = os.path.join(os.path.dirname(self.credentials_path), "calendar_config.json")
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('calendar_ids', [])
        
        # Fallback: use all calendars
        print("⚠️  No calendar config found. Run: python scripts/setup_calendars.py")
        return None

    def fetch_events(self, timeframe="today", max_results=50):
        """Extract events from the dimensional prison of scheduled time"""
        if not self.service:
            self.authenticate()
        
        time_min, time_max = self.get_time_range(timeframe)
        
        print(f"🌌 Fetching events for timeframe: {timeframe}")
        print(f"📅 Range: {time_min} to {time_max}")
        
        # Load configured calendars
        selected_calendar_ids = self.load_calendar_config()
        
        try:
            all_events = []
            
            if selected_calendar_ids is None:
                # Fallback: get all calendars
                calendars_result = self.service.calendarList().list().execute()
                calendars = calendars_result.get('items', [])
                calendar_list = [(cal['id'], cal.get('summary', 'Unknown')) for cal in calendars]
            else:
                # Use configured calendars
                calendar_list = []
                for cal_id in selected_calendar_ids:
                    try:
                        cal_info = self.service.calendars().get(calendarId=cal_id).execute()
                        calendar_list.append((cal_id, cal_info.get('summary', 'Unknown')))
                    except:
                        print(f"⚠️  Warning: Calendar {cal_id} not accessible")
            
            print(f"📊 Fetching from {len(calendar_list)} configured calendar(s)")
            
            for calendar_id, calendar_name in calendar_list:
                # Fetch events from this calendar
                events_result = self.service.events().list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                events = events_result.get('items', [])
                
                for event in events:
                    event_data = {
                        'calendar': calendar_name,
                        'calendar_id': calendar_id,
                        'id': event.get('id'),
                        'summary': event.get('summary', 'No Title'),
                        'description': event.get('description', ''),
                        'location': event.get('location', ''),
                        'start': event['start'].get('dateTime', event['start'].get('date')),
                        'end': event['end'].get('dateTime', event['end'].get('date')),
                        'attendees': [attendee.get('email') for attendee in event.get('attendees', [])],
                        'created': event.get('created'),
                        'updated': event.get('updated')
                    }
                    all_events.append(event_data)
            
            print(f"📊 Retrieved {len(all_events)} events from {len(calendar_list)} calendars")
            return all_events
            
        except Exception as error:
            print(f"🚫 Error accessing calendar matrix: {error}")
            return []
    
    def save_events(self, events, timeframe):
        """Save events to local dimensional storage"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gregorian_events_{timeframe}_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump({
                'timeframe': timeframe,
                'fetched_at': datetime.now().isoformat(),
                'event_count': len(events),
                'events': events
            }, f, indent=2)
        
        print(f"💾 Events saved to: {filepath}")
        return filepath

def main():
    timeframe = sys.argv[1] if len(sys.argv) > 1 else "today"
    
    fetcher = GregorianCalendarFetcher()
    events = fetcher.fetch_events(timeframe)
    
    if events:
        filepath = fetcher.save_events(events, timeframe)
        
        # Display summary
        print("\n🌟 EVENT SUMMARY:")
        for event in events[:5]:  # Show first 5 events
            start_time = event['start'][:16] if 'T' in event['start'] else event['start']
            print(f"  📅 {start_time} | {event['summary']} ({event['calendar']})")
        
        if len(events) > 5:
            print(f"  ... and {len(events) - 5} more events")
    else:
        print("🌌 No events found in this timeframe - consciousness is free!")

if __name__ == "__main__":
    main()