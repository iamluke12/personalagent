#!/usr/bin/env python3
"""
Profile-Aware Activity Lister for personalAgent
Lists upcoming activities filtered by current calendar profile
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Import profile manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from profileManager import CalendarProfileManager

class ActivityLister:
    def __init__(self):
        self.data_dir = os.path.expanduser("~/personalAgent/data/cache")
        self.profile_manager = CalendarProfileManager()
    
    def get_latest_calendar_data(self):
        """Get the most recent calendar data"""
        if not os.path.exists(self.data_dir):
            return []
        
        cache_files = [f for f in os.listdir(self.data_dir) 
                      if f.startswith('gregorian_events_') and f.endswith('.json')]
        
        if not cache_files:
            return []
        
        latest_file = sorted(cache_files)[-1]
        file_path = os.path.join(self.data_dir, latest_file)
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get('events', [])
        except:
            return []
    
    def get_latest_todo_data(self):
        """Get the most recent TODO data"""
        if not os.path.exists(self.data_dir):
            return []
        
        cache_files = [f for f in os.listdir(self.data_dir) 
                      if f.startswith('todos_') and f.endswith('.json')]
        
        if not cache_files:
            return []
        
        latest_file = sorted(cache_files)[-1]
        file_path = os.path.join(self.data_dir, latest_file)
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get('todos', [])
        except:
            return []
    
    def parse_event_time(self, event):
        """Parse event start time"""
        try:
            time_str = event.get('start', '')
            if 'T' in time_str:
                # Has time component
                dt = datetime.fromisoformat(time_str.replace('Z', '').replace('+02:00', ''))
                return dt, True
            else:
                # All-day event
                dt = datetime.fromisoformat(time_str)
                return dt, False
        except:
            return datetime.now(), False
    
    def filter_events_by_timeframe(self, events, timeframe):
        """Filter events based on timeframe"""
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if timeframe == "today":
            start_range = today
            end_range = today + timedelta(days=1)
        elif timeframe == "tomorrow":
            start_range = today + timedelta(days=1)
            end_range = today + timedelta(days=2)
        elif timeframe == "week":
            start_range = today
            end_range = today + timedelta(days=7)
        elif timeframe == "month":
            start_range = today
            end_range = today + timedelta(days=30)
        else:
            # Default to today
            start_range = today
            end_range = today + timedelta(days=1)
        
        filtered_events = []
        for event in events:
            event_time, has_time = self.parse_event_time(event)
            if start_range <= event_time < end_range:
                filtered_events.append((event, event_time, has_time))
        
        return filtered_events
    
    def filter_todos_by_timeframe(self, todos, timeframe):
        """Filter TODOs based on timeframe (simple filtering for now)"""
        # For now, just return incomplete TODOs
        # Could be enhanced to filter by due dates
        return [todo for todo in todos if not todo.get('completed', False)]
    
    def format_event_time(self, event_time, has_time):
        """Format event time for display"""
        if has_time:
            return event_time.strftime("%H:%M")
        else:
            return "All day"
    
    def filter_events_by_profile(self, events, profile_name=None):
        """Filter events based on current profile settings"""
        if not profile_name:
            profile_name = self.profile_manager.get_current_profile()
        
        if not profile_name:
            return events  # No profile, show all events
        
        display_settings = self.profile_manager.get_profile_display_settings(profile_name)
        filter_keywords = self.profile_manager.get_filter_keywords(profile_name)
        
        # Get profile calendars
        profile_calendars = self.profile_manager.get_profile_calendars(profile_name)
        profile_calendar_ids = [cal['id'] for cal in profile_calendars]
        
        filtered_events = []
        
        for event in events:
            event_calendar_id = event.get('organizer', {}).get('email', '')
            event_title = event.get('summary', '').lower()
            event_desc = event.get('description', '').lower()
            
            # Always show events from profile's own calendars
            if event_calendar_id in profile_calendar_ids:
                filtered_events.append(event)
                continue
            
            # For work profile: show family events as busy blocks
            if profile_name == 'work':
                if display_settings.get('show_family_events', True):
                    # Check if this is a family event
                    family_keywords = self.profile_manager.get_filter_keywords('family')
                    is_family_event = any(keyword.lower() in event_title or keyword.lower() in event_desc 
                                        for keyword in family_keywords)
                    
                    if is_family_event:
                        # Mark as busy block for work view
                        event['__profile_view'] = 'busy'
                        filtered_events.append(event)
                        continue
            
            # For personal profile: show family events normally
            if profile_name == 'personal':
                if display_settings.get('show_family_events', True):
                    family_keywords = self.profile_manager.get_filter_keywords('family')
                    is_family_event = any(keyword.lower() in event_title or keyword.lower() in event_desc 
                                        for keyword in family_keywords)
                    
                    if is_family_event:
                        filtered_events.append(event)
                        continue
            
            # Filter by keywords if relevant to current profile
            if filter_keywords:
                event_text = f"{event_title} {event_desc}"
                if any(keyword.lower() in event_text for keyword in filter_keywords):
                    filtered_events.append(event)
        
        return filtered_events

    def list_activities(self, timeframe="today"):
        """List activities for the given timeframe with profile awareness"""
        current_profile = self.profile_manager.get_current_profile()
        profile_display = f" [{current_profile.upper()}]" if current_profile else ""
        
        print(f"📅 UPCOMING ACTIVITIES - {timeframe.upper()}{profile_display}")
        print("=" * 50)
        
        if current_profile:
            profile_info = self.profile_manager.profiles.get("profiles", {}).get(current_profile, {})
            profile_desc = profile_info.get("description", "")
            print(f"🔸 Profile: {profile_desc}")
            print("")
        
        # Get calendar events
        calendar_events = self.get_latest_calendar_data()
        
        # Filter by profile first, then by timeframe
        profile_filtered_events = self.filter_events_by_profile(calendar_events, current_profile)
        filtered_events = self.filter_events_by_timeframe(profile_filtered_events, timeframe)
        
        # Get TODOs
        todo_items = self.get_latest_todo_data()
        filtered_todos = self.filter_todos_by_timeframe(todo_items, timeframe)
        
        # Display calendar events
        if filtered_events:
            print("📅 CALENDAR EVENTS")
            print("-" * 30)
            
            # Sort by time
            filtered_events.sort(key=lambda x: x[1])
            
            for event, event_time, has_time in filtered_events:
                title = event.get('summary', 'No Title')
                time_str = self.format_event_time(event_time, has_time)
                date_str = event_time.strftime("%a %m/%d") if timeframe != "today" else ""
                
                # Handle busy view for work profile
                if event.get('__profile_view') == 'busy':
                    title = f"[BUSY] {title}"
                    time_icon = "🔒"
                else:
                    time_icon = "🕐"
                
                if date_str:
                    print(f"  {time_icon} {date_str} {time_str} | {title}")
                else:
                    print(f"  {time_icon} {time_str} | {title}")
                
                # Show location if available and not in busy view
                if event.get('location') and event.get('__profile_view') != 'busy':
                    print(f"      📍 {event['location']}")
        else:
            print("📅 No calendar events found")
        
        # Display TODOs
        if filtered_todos:
            print(f"\n📝 TODO ITEMS")
            print("-" * 30)
            
            # Group by section
            by_section = {}
            for todo in filtered_todos:
                section = todo.get('section', 'General')
                if section not in by_section:
                    by_section[section] = []
                by_section[section].append(todo)
            
            for section, todos in by_section.items():
                print(f"\n  📂 {section}")
                for todo in todos:
                    text = todo.get('text', 'Unknown task')
                    priority = todo.get('priority', '')
                    tags = todo.get('tags', [])
                    due_date = todo.get('due_date', '')
                    
                    # Priority indicator
                    priority_indicator = ""
                    if priority == 'high':
                        priority_indicator = "🔴 "
                    elif priority == 'medium':
                        priority_indicator = "🟡 "
                    
                    # Format output
                    task_line = f"    {priority_indicator}⭕ {text}"
                    print(task_line)
                    
                    # Show additional info
                    if due_date:
                        print(f"        📅 Due: {due_date}")
                    if tags:
                        print(f"        🏷️  {', '.join(tags)}")
        else:
            print(f"\n📝 No TODO items found")
        
        # Summary
        total_events = len(filtered_events)
        total_todos = len(filtered_todos)
        print(f"\n🎯 SUMMARY: {total_events} events, {total_todos} tasks")
        
        if total_events == 0 and total_todos == 0:
            print("✨ Looks like a free period! Perfect for deep work or rest.")

def main():
    """Main execution function"""
    timeframe = sys.argv[1] if len(sys.argv) > 1 else "today"
    
    # Validate timeframe
    valid_timeframes = ["today", "tomorrow", "week", "month"]
    if timeframe not in valid_timeframes:
        print(f"❌ Invalid timeframe: {timeframe}")
        print(f"Valid options: {', '.join(valid_timeframes)}")
        sys.exit(1)
    
    lister = ActivityLister()
    lister.list_activities(timeframe)

if __name__ == "__main__":
    main()
