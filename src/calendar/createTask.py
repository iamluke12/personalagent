#!/usr/bin/env python3
"""
Contextual Task Creator for personalAgent
Create calendar events with rich metadata for AI processing
Supports both quick creation and detailed context gathering
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Import profile manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from profileManager import CalendarProfileManager

class ContextualTaskCreator:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/personalAgent/config")
        self.service = None
        self.profile_manager = CalendarProfileManager()
        
        # Task type categories
        self.task_types = {
            'WORK': {'color': '9', 'emoji': '💼'},
            'PERSONAL': {'color': '10', 'emoji': '🏠'},
            'HEALTH': {'color': '4', 'emoji': '💪'},
            'LEARN': {'color': '5', 'emoji': '📚'},
            'CREATE': {'color': '6', 'emoji': '🎨'},
            'CONNECT': {'color': '11', 'emoji': '🤝'},
            'TRAVEL': {'color': '8', 'emoji': '✈️'},
            'ADMIN': {'color': '3', 'emoji': '📋'},
            'RITUAL': {'color': '2', 'emoji': '🔮'},
            'URGENT': {'color': '1', 'emoji': '🚨'}
        }
        
        # Energy levels for scheduling optimization
        self.energy_levels = ['low', 'medium', 'high', 'peak']
        
        # Context dependencies
        self.context_types = ['tools', 'people', 'location', 'prep', 'followup']
    
    def authenticate(self):
        """Get authenticated Google Calendar service with write permissions"""
        token_path = os.path.join(self.config_dir, "token_write.json")
        creds_path = os.path.join(self.config_dir, "credentials.json")
        
        # Scopes for both read and write
        scopes = ['https://www.googleapis.com/auth/calendar']
        
        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, scopes)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(creds_path):
                    print("🚫 No credentials.json found!")
                    return False
                
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, scopes)
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
        print("✨ Connected to Google Calendar with write permissions")
        return True
    
    def get_calendar_selection(self):
        """Get calendar based on current profile or let user select"""
        current_profile = self.profile_manager.get_current_profile()
        
        if current_profile:
            # Use current profile's primary calendar
            primary_calendar_id = self.profile_manager.get_primary_calendar_id()
            
            if primary_calendar_id:
                profile_info = self.profile_manager.profiles.get("profiles", {}).get(current_profile, {})
                profile_name = profile_info.get("name", current_profile)
                print(f"📅 Using {profile_name} calendar")
                return primary_calendar_id
        
        # Fallback to manual selection if no profile or calendar found
        try:
            calendars_result = self.service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])
            
            # Filter to only writable calendars
            writable_calendars = [cal for cal in calendars 
                                if cal.get('accessRole') in ['owner', 'writer']]
            
            if not writable_calendars:
                print("🚫 No writable calendars found!")
                return None
            
            if len(writable_calendars) == 1:
                return writable_calendars[0]['id']
            
            print(f"\n📅 Select calendar for task creation:")
            for i, cal in enumerate(writable_calendars, 1):
                primary = " 🌟 [PRIMARY]" if cal.get('primary') else ""
                print(f"  {i}. {cal.get('summary', 'Unknown')}{primary}")
            
            while True:
                try:
                    choice = int(input("\nCalendar number: ")) - 1
                    if 0 <= choice < len(writable_calendars):
                        return writable_calendars[choice]['id']
                    else:
                        print("🚫 Invalid selection!")
                except ValueError:
                    print("🚫 Please enter a number!")
        
        except Exception as e:
            print(f"🚫 Error fetching calendars: {e}")
            return None
    
    def parse_time_input(self, time_str, date_str=None):
        """Parse flexible time input"""
        now = datetime.now()
        
        # Handle relative dates
        if date_str:
            if date_str.lower() == 'today':
                base_date = now.date()
            elif date_str.lower() == 'tomorrow':
                base_date = (now + timedelta(days=1)).date()
            elif date_str.lower() in ['monday', 'tuesday', 'wednesday', 'thursday', 
                                    'friday', 'saturday', 'sunday']:
                # Find next occurrence of that weekday
                weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 
                           'friday', 'saturday', 'sunday']
                target_weekday = weekdays.index(date_str.lower())
                days_ahead = target_weekday - now.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                base_date = (now + timedelta(days=days_ahead)).date()
            else:
                try:
                    base_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except:
                    base_date = now.date()
        else:
            base_date = now.date()
        
        # Parse time
        try:
            if ':' in time_str:
                time_obj = datetime.strptime(time_str, '%H:%M').time()
            else:
                hour = int(time_str)
                time_obj = datetime.strptime(f'{hour}:00', '%H:%M').time()
            
            return datetime.combine(base_date, time_obj)
        except:
            # Default to current time if parsing fails
            return now
    
    def build_rich_description(self, context_data):
        """Build structured description with context metadata"""
        description_parts = []
        
        # Add main description
        if context_data.get('description'):
            description_parts.append(context_data['description'])
            description_parts.append('')
        
        # Add context metadata in YAML-like format
        description_parts.append('--- CONTEXT METADATA ---')
        
        if context_data.get('energy_level'):
            description_parts.append(f'energy_required: {context_data["energy_level"]}')
        
        if context_data.get('estimated_duration'):
            description_parts.append(f'estimated_duration: {context_data["estimated_duration"]}')
        
        if context_data.get('tools'):
            description_parts.append(f'tools_needed: {", ".join(context_data["tools"])}')
        
        if context_data.get('people'):
            description_parts.append(f'people_involved: {", ".join(context_data["people"])}')
        
        if context_data.get('prep_tasks'):
            description_parts.append(f'preparation_required: {", ".join(context_data["prep_tasks"])}')
        
        if context_data.get('followup_tasks'):
            description_parts.append(f'followup_actions: {", ".join(context_data["followup_tasks"])}')
        
        if context_data.get('dependencies'):
            description_parts.append(f'dependencies: {", ".join(context_data["dependencies"])}')
        
        if context_data.get('outcome'):
            description_parts.append(f'desired_outcome: {context_data["outcome"]}')
        
        return '\n'.join(description_parts)
    
    def interactive_task_creation(self):
        """Interactive mode for detailed task creation"""
        print("🌟 Interactive Task Creator")
        print("=" * 40)
        
        # Basic info
        title = input("📝 Task title: ").strip()
        if not title:
            print("🚫 Title required!")
            return None
        
        # Task type
        print(f"\n📋 Task types:")
        for i, (type_key, type_info) in enumerate(self.task_types.items(), 1):
            print(f"  {i:2d}. {type_info['emoji']} {type_key}")
        
        try:
            type_choice = int(input("Task type number: ")) - 1
            task_type = list(self.task_types.keys())[type_choice]
        except:
            task_type = 'PERSONAL'
        
        # Timing
        date_str = input("📅 Date (today/tomorrow/monday/2025-08-15): ").strip() or 'today'
        time_str = input("⏰ Time (14:30 or 14): ").strip() or '09:00'
        duration = input("⏳ Duration (30m/1h/2h): ").strip() or '1h'
        
        # Context gathering
        print(f"\n🔍 Context Information (optional, press Enter to skip):")
        
        context = {}
        context['description'] = input("📖 Description: ").strip()
        context['energy_level'] = input(f"⚡ Energy level ({'/'.join(self.energy_levels)}): ").strip()
        context['estimated_duration'] = duration
        
        # Tools and resources
        tools_input = input("🔧 Tools/resources needed (comma-separated): ").strip()
        if tools_input:
            context['tools'] = [t.strip() for t in tools_input.split(',')]
        
        # People involved
        people_input = input("👥 People involved (comma-separated): ").strip()
        if people_input:
            context['people'] = [p.strip() for p in people_input.split(',')]
        
        # Location
        location = input("📍 Location: ").strip()
        
        # Preparation tasks
        prep_input = input("📋 Preparation needed (comma-separated): ").strip()
        if prep_input:
            context['prep_tasks'] = [p.strip() for p in prep_input.split(',')]
        
        # Followup tasks
        followup_input = input("➡️  Followup actions (comma-separated): ").strip()
        if followup_input:
            context['followup_tasks'] = [f.strip() for f in followup_input.split(',')]
        
        # Dependencies
        deps_input = input("🔗 Dependencies (comma-separated): ").strip()
        if deps_input:
            context['dependencies'] = [d.strip() for d in deps_input.split(',')]
        
        # Desired outcome
        context['outcome'] = input("🎯 Desired outcome: ").strip()
        
        return self.create_task(
            title=title,
            task_type=task_type,
            start_time=self.parse_time_input(time_str, date_str),
            duration=duration,
            location=location,
            context=context
        )
    
    def quick_task_creation(self, title, task_type='PERSONAL', when='today 09:00', duration='1h', location=''):
        """Quick task creation from command line"""
        # Parse when parameter
        when_parts = when.split(' ')
        date_str = when_parts[0] if len(when_parts) > 1 else 'today'
        time_str = when_parts[1] if len(when_parts) > 1 else '09:00'
        
        start_time = self.parse_time_input(time_str, date_str)
        
        return self.create_task(
            title=title,
            task_type=task_type.upper(),
            start_time=start_time,
            duration=duration,
            location=location,
            context={'description': f'Quick task: {title}'}
        )
    
    def create_task(self, title, task_type, start_time, duration, location='', context=None):
        """Create the actual calendar event with conflict detection"""
        if not self.service:
            if not self.authenticate():
                return None
        
        calendar_id = self.get_calendar_selection()
        if not calendar_id:
            return None
        
        # Parse duration
        duration_minutes = 60  # default
        if duration:
            if 'm' in duration:
                duration_minutes = int(duration.replace('m', ''))
            elif 'h' in duration:
                duration_minutes = int(float(duration.replace('h', '')) * 60)
        
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Check for conflicts with higher priority calendars
        current_profile = self.profile_manager.get_current_profile()
        has_conflicts, conflicts = self.profile_manager.check_conflict(start_time, end_time, current_profile)
        
        # Handle conflicts for work profile
        if has_conflicts and current_profile == 'work':
            print(f"\n⚠️ CONFLICT DETECTED for {start_time.strftime('%Y-%m-%d %H:%M')}")
            print("🔸 This time conflicts with higher priority events:")
            for conflict in conflicts:
                print(f"   • {conflict}")
            
            print("\n💡 SUGGESTED ALTERNATIVES:")
            suggestions = self.profile_manager.suggest_alternative_times(start_time, duration_minutes, current_profile)
            
            for i, suggestion in enumerate(suggestions, 1):
                start_str = suggestion["start_time"].strftime('%H:%M')
                end_str = suggestion["end_time"].strftime('%H:%M')
                print(f"   {i}. {start_str}-{end_str} ({suggestion['reason']})")
            
            print(f"   {len(suggestions) + 1}. Enter custom time")
            print(f"   {len(suggestions) + 2}. Force create anyway (override)")
            
            while True:
                try:
                    choice = input(f"\nSelect option (1-{len(suggestions) + 2}): ").strip()
                    choice_num = int(choice)
                    
                    if 1 <= choice_num <= len(suggestions):
                        # Use suggested time
                        suggestion = suggestions[choice_num - 1]
                        start_time = suggestion["start_time"]
                        end_time = suggestion["end_time"]
                        print(f"✅ Rescheduled to {start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}")
                        break
                    elif choice_num == len(suggestions) + 1:
                        # Custom time
                        custom_time = input("Enter new time (HH:MM): ").strip()
                        custom_date = input("Enter new date (YYYY-MM-DD or 'today'/'tomorrow'): ").strip()
                        start_time = self.parse_time_input(custom_time, custom_date)
                        end_time = start_time + timedelta(minutes=duration_minutes)
                        print(f"✅ Rescheduled to {start_time.strftime('%Y-%m-%d %H:%M')}")
                        break
                    elif choice_num == len(suggestions) + 2:
                        # Force create
                        print("⚠️ Creating event despite conflicts")
                        break
                    else:
                        print("🚫 Invalid selection!")
                except ValueError:
                    print("🚫 Please enter a number!")
        
        # Auto-detect appropriate profile based on task content
        detected_profile = self.profile_manager.auto_detect_profile(title, context.get('description', '') if context else '')
        if detected_profile and detected_profile != current_profile:
            print(f"💡 Detected this might be a {detected_profile} task. Current profile: {current_profile}")
            switch = input("Switch to appropriate profile? (y/N): ").strip().lower()
            if switch == 'y':
                self.profile_manager.set_current_profile(detected_profile)
                # Re-get calendar for new profile
                calendar_id = self.get_calendar_selection()
        
        # Build event object
        task_info = self.task_types.get(task_type, self.task_types['PERSONAL'])
        formatted_title = f"{task_info['emoji']} [{task_type}] {title}"
        
        event = {
            'summary': formatted_title,
            'location': location,
            'description': self.build_rich_description(context or {}),
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Europe/Berlin',  # Adjust for your timezone
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Europe/Berlin',
            },
            'colorId': task_info['color'],
            'extendedProperties': {
                'private': {
                    'task_type': task_type,
                    'created_by': 'personalAgent',
                    'context_rich': 'true',
                    'profile': current_profile or 'unknown'
                }
            }
        }
        
        try:
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            
            profile_info = f" [{current_profile.upper()}]" if current_profile else ""
            print(f"\n✨ Task created successfully!{profile_info}")
            print(f"📅 {formatted_title}")
            print(f"⏰ {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}")
            print(f"📍 {location if location else 'No location'}")
            print(f"🔗 Event ID: {created_event['id']}")
            
            return created_event
            
        except Exception as e:
            print(f"🚫 Error creating task: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description='Create contextual calendar tasks')
    parser.add_argument('--title', help='Task title')
    parser.add_argument('--type', default='PERSONAL', help='Task type (WORK, PERSONAL, etc.)')
    parser.add_argument('--when', default='today 09:00', help='When (e.g., "tomorrow 14:30")')
    parser.add_argument('--duration', default='1h', help='Duration (e.g., "30m", "2h")')
    parser.add_argument('--location', default='', help='Location')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    creator = ContextualTaskCreator()
    
    if args.interactive or not args.title:
        # Interactive mode
        creator.interactive_task_creation()
    else:
        # Quick mode
        creator.quick_task_creation(
            title=args.title,
            task_type=args.type,
            when=args.when,
            duration=args.duration,
            location=args.location
        )

if __name__ == "__main__":
    main()