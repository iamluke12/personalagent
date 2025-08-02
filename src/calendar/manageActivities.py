#!/usr/bin/env python3
"""
Interactive Activity Manager for personalAgent
Quick edit and delete activities with simple ID or partial matching
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta

class ActivityManager:
    def __init__(self):
        self.data_dir = os.path.expanduser("~/personalAgent/data/cache")
        self.todos_file = None
        self.todos_data = None
        self.calendar_events = []
    
    def load_latest_todos(self):
        """Load the most recent TODO data"""
        if not os.path.exists(self.data_dir):
            print("❌ No data directory found")
            return False
        
        cache_files = [f for f in os.listdir(self.data_dir) 
                      if f.startswith('todos_') and f.endswith('.json')]
        
        if not cache_files:
            print("❌ No TODO files found")
            return False
        
        latest_file = sorted(cache_files)[-1]
        self.todos_file = os.path.join(self.data_dir, latest_file)
        
        try:
            with open(self.todos_file, 'r') as f:
                self.todos_data = json.load(f)
                return True
        except Exception as e:
            print(f"❌ Error loading TODOs: {e}")
            return False
    
    def load_latest_calendar_events(self):
        """Load the most recent calendar data (read-only info)"""
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
    
    def save_todos(self):
        """Save updated TODO data"""
        if not self.todos_data or not self.todos_file:
            return False
        
        try:
            # Create backup
            backup_file = self.todos_file + '.backup'
            with open(self.todos_file, 'r') as f:
                backup_data = f.read()
            with open(backup_file, 'w') as f:
                f.write(backup_data)
            
            # Save updated data
            with open(self.todos_file, 'w') as f:
                json.dump(self.todos_data, f, indent=2)
            
            print(f"✅ TODOs saved successfully (backup: {os.path.basename(backup_file)})")
            return True
        except Exception as e:
            print(f"❌ Error saving TODOs: {e}")
            return False
    
    def build_todo_id_map(self):
        """Build the TODO ID mapping"""
        if not self.todos_data or not self.todos_data.get('todos'):
            return
        
        todos = self.todos_data['todos']
        incomplete_todos = [todo for todo in todos if not todo.get('completed', False)]
        
        # Group by section
        by_section = {}
        for todo in incomplete_todos:
            section = todo.get('section', 'General')
            if section not in by_section:
                by_section[section] = []
            by_section[section].append(todo)
        
        todo_id = 1
        self.todo_id_map = {}  # Map ID to todo index in original list
        
        for section, section_todos in by_section.items():
            for todo in section_todos:
                # Find original index
                original_index = todos.index(todo)
                self.todo_id_map[todo_id] = original_index
                todo_id += 1
    
    def list_activities_with_ids(self, show_calendar=True):
        """List all activities with IDs for easy reference"""
        print("📋 CURRENT ACTIVITIES")
        print("=" * 50)
        
        activity_count = 0
        
        # Show calendar events (read-only)
        if show_calendar:
            self.calendar_events = self.load_latest_calendar_events()
            if self.calendar_events:
                print("\n📅 CALENDAR EVENTS (read-only)")
                print("-" * 30)
                for i, event in enumerate(self.calendar_events, 1):
                    title = event.get('summary', 'No Title')
                    start_time = event.get('start', '')
                    if 'T' in start_time:
                        try:
                            dt = datetime.fromisoformat(start_time.replace('Z', '').replace('+02:00', ''))
                            time_str = dt.strftime("%H:%M")
                        except:
                            time_str = "Time TBD"
                    else:
                        time_str = "All day"
                    
                    print(f"  📅 C{i} | {time_str} | {title}")
                    if event.get('location'):
                        print(f"        📍 {event['location']}")
                activity_count += len(self.calendar_events)
        
        # Show TODOs (editable)
        if self.todos_data and self.todos_data.get('todos'):
            todos = self.todos_data['todos']
            incomplete_todos = [todo for todo in todos if not todo.get('completed', False)]
            
            if incomplete_todos:
                print("\n📝 TODO ITEMS (editable)")
                print("-" * 30)
                
                # Group by section
                by_section = {}
                for todo in incomplete_todos:
                    section = todo.get('section', 'General')
                    if section not in by_section:
                        by_section[section] = []
                    by_section[section].append(todo)
                
                todo_id = 1
                self.build_todo_id_map()  # Build the ID mapping first
                
                for section, section_todos in by_section.items():
                    print(f"\n  📂 {section}")
                    for todo in section_todos:
                        # Find the TODO ID from the mapping
                        todo_id = None
                        original_index = todos.index(todo)
                        for tid, oidx in self.todo_id_map.items():
                            if oidx == original_index:
                                todo_id = tid
                                break
                        
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
                        
                        print(f"    ⭕ T{todo_id} | {priority_indicator}{text}")
                        
                        # Show additional info
                        if due_date:
                            print(f"           📅 Due: {due_date}")
                        if tags:
                            print(f"           🏷️  {', '.join(tags)}")
                        
                activity_count += len(incomplete_todos)
        
        print(f"\n🎯 Total: {activity_count} activities")
        print("\n💡 Usage:")
        print("   📝 Edit TODO: T1, T2, etc.")
        print("   🗑️  Delete TODO: Use 'delete' command")
        print("   📅 Calendar events are read-only (managed via Google Calendar)")
    
    def find_todo_by_id_or_text(self, identifier):
        """Find TODO by ID (T1, T2) or partial text match"""
        if not self.todos_data:
            return None
            
        # Build ID mapping if not already done
        if not hasattr(self, 'todo_id_map'):
            self.build_todo_id_map()
        
        # Try ID first (T1, T2, etc.)
        if identifier.upper().startswith('T') and identifier[1:].isdigit():
            todo_id = int(identifier[1:])
            if hasattr(self, 'todo_id_map') and todo_id in self.todo_id_map:
                original_index = self.todo_id_map[todo_id]
                return original_index
        
        # Try partial text match
        todos = self.todos_data['todos']
        identifier_lower = identifier.lower()
        
        matches = []
        for i, todo in enumerate(todos):
            if not todo.get('completed', False):
                text = todo.get('text', '').lower()
                if identifier_lower in text:
                    matches.append(i)
        
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            print(f"🤔 Multiple matches found for '{identifier}':")
            for match_idx in matches:
                todo = todos[match_idx]
                # Find display ID
                display_id = None
                if hasattr(self, 'todo_id_map'):
                    for tid, oidx in self.todo_id_map.items():
                        if oidx == match_idx:
                            display_id = f"T{tid}"
                            break
                print(f"   {display_id or '?'} | {todo.get('text', '')}")
            print("💡 Use specific ID (e.g., T1) or more specific text")
            return None
        
        return None
    
    def edit_todo(self, identifier):
        """Edit a TODO item"""
        todo_index = self.find_todo_by_id_or_text(identifier)
        if todo_index is None:
            print(f"❌ TODO '{identifier}' not found")
            return False
        
        todo = self.todos_data['todos'][todo_index]
        current_text = todo.get('text', '')
        current_priority = todo.get('priority', '')
        current_tags = todo.get('tags', [])
        current_due = todo.get('due_date', '')
        
        print(f"\n📝 EDITING TODO")
        print("-" * 30)
        print(f"Current: {current_text}")
        print(f"Priority: {current_priority or 'none'}")
        print(f"Tags: {', '.join(current_tags) if current_tags else 'none'}")
        print(f"Due: {current_due or 'none'}")
        print()
        
        # Edit text
        new_text = input(f"New text (press Enter to keep current): ").strip()
        if new_text:
            todo['text'] = new_text
        
        # Edit priority
        print("Priority options: high, medium, low, or press Enter for none")
        new_priority = input(f"Priority (current: {current_priority or 'none'}): ").strip().lower()
        if new_priority in ['high', 'medium', 'low']:
            todo['priority'] = new_priority
        elif new_priority == '':
            pass  # Keep current
        elif new_priority == 'none':
            todo['priority'] = ''
        
        # Edit tags
        new_tags_input = input(f"Tags (comma-separated, current: {', '.join(current_tags)}): ").strip()
        if new_tags_input:
            if new_tags_input.lower() == 'none':
                todo['tags'] = []
            else:
                new_tags = [tag.strip() for tag in new_tags_input.split(',') if tag.strip()]
                todo['tags'] = new_tags
        
        # Edit due date
        new_due = input(f"Due date (YYYY-MM-DD or 'none', current: {current_due or 'none'}): ").strip()
        if new_due:
            if new_due.lower() == 'none':
                todo['due_date'] = ''
            else:
                # Simple date validation
                try:
                    datetime.fromisoformat(new_due)
                    todo['due_date'] = new_due
                except:
                    print("⚠️  Invalid date format, keeping current")
        
        print(f"\n✅ TODO updated: {todo['text']}")
        return True
    
    def delete_todo(self, identifier):
        """Delete a TODO item"""
        todo_index = self.find_todo_by_id_or_text(identifier)
        if todo_index is None:
            print(f"❌ TODO '{identifier}' not found")
            return False
        
        todo = self.todos_data['todos'][todo_index]
        todo_text = todo.get('text', '')
        
        # Confirmation
        confirm = input(f"🗑️  Delete '{todo_text}'? (y/N): ").strip().lower()
        if confirm == 'y':
            del self.todos_data['todos'][todo_index]
            print(f"✅ Deleted: {todo_text}")
            return True
        else:
            print("❌ Deletion cancelled")
            return False
    
    def complete_todo(self, identifier):
        """Mark a TODO as completed"""
        todo_index = self.find_todo_by_id_or_text(identifier)
        if todo_index is None:
            print(f"❌ TODO '{identifier}' not found")
            return False
        
        todo = self.todos_data['todos'][todo_index]
        todo['completed'] = True
        todo['completed_at'] = datetime.now().isoformat()
        
        print(f"✅ Completed: {todo.get('text', '')}")
        return True
    
    def add_todo(self):
        """Add a new TODO item"""
        print("\n➕ ADD NEW TODO")
        print("-" * 30)
        
        text = input("Task description: ").strip()
        if not text:
            print("❌ Task description required")
            return False
        
        section = input("Section (default: Today): ").strip() or "Today"
        
        priority = input("Priority (high/medium/low): ").strip().lower()
        if priority not in ['high', 'medium', 'low']:
            priority = ''
        
        tags_input = input("Tags (comma-separated): ").strip()
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()] if tags_input else []
        
        due_input = input("Due date (YYYY-MM-DD): ").strip()
        due_date = ''
        if due_input:
            try:
                datetime.fromisoformat(due_input)
                due_date = due_input
            except:
                print("⚠️  Invalid date format, skipping due date")
        
        new_todo = {
            'text': text,
            'section': section,
            'completed': False,
            'created_at': datetime.now().isoformat()
        }
        
        if priority:
            new_todo['priority'] = priority
        if tags:
            new_todo['tags'] = tags
        if due_date:
            new_todo['due_date'] = due_date
        
        self.todos_data['todos'].append(new_todo)
        print(f"✅ Added: {text}")
        return True
    
    def interactive_mode(self):
        """Interactive command mode"""
        print("\n🎮 INTERACTIVE MODE")
        print("Commands: list, edit <id>, delete <id>, complete <id>, add, save, quit")
        print("Examples: edit T1, delete presentation, complete T3")
        print()
        
        while True:
            try:
                command = input("📋 Command: ").strip()
                if not command:
                    continue
                
                parts = command.split(' ', 1)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ''
                
                if cmd in ['quit', 'exit', 'q']:
                    break
                
                elif cmd == 'list':
                    self.list_activities_with_ids()
                
                elif cmd in ['edit', 'e']:
                    if not arg:
                        print("❌ Usage: edit <id or text>")
                        continue
                    if self.edit_todo(arg):
                        print("💡 Don't forget to 'save' your changes!")
                
                elif cmd in ['delete', 'del', 'd']:
                    if not arg:
                        print("❌ Usage: delete <id or text>")
                        continue
                    if self.delete_todo(arg):
                        print("💡 Don't forget to 'save' your changes!")
                
                elif cmd in ['complete', 'done', 'c']:
                    if not arg:
                        print("❌ Usage: complete <id or text>")
                        continue
                    if self.complete_todo(arg):
                        print("💡 Don't forget to 'save' your changes!")
                
                elif cmd in ['add', 'new', 'a']:
                    if self.add_todo():
                        print("💡 Don't forget to 'save' your changes!")
                
                elif cmd in ['save', 's']:
                    self.save_todos()
                
                elif cmd in ['help', 'h']:
                    print("Commands:")
                    print("  list                 - Show all activities")
                    print("  edit <id>           - Edit TODO (e.g., edit T1)")
                    print("  delete <id>         - Delete TODO")
                    print("  complete <id>       - Mark TODO as done")
                    print("  add                 - Add new TODO")
                    print("  save                - Save changes")
                    print("  quit                - Exit")
                
                else:
                    print(f"❌ Unknown command: {cmd}")
                    print("💡 Type 'help' for available commands")
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main execution function"""
    manager = ActivityManager()
    
    # Load data
    if not manager.load_latest_todos():
        print("❌ Could not load TODO data")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        # Interactive mode
        manager.list_activities_with_ids()
        manager.interactive_mode()
    else:
        command = sys.argv[1].lower()
        
        if command == 'list':
            manager.list_activities_with_ids()
        
        elif command in ['edit', 'e'] and len(sys.argv) > 2:
            identifier = sys.argv[2]
            if manager.edit_todo(identifier):
                manager.save_todos()
        
        elif command in ['delete', 'del', 'd'] and len(sys.argv) > 2:
            identifier = sys.argv[2]
            if manager.delete_todo(identifier):
                manager.save_todos()
        
        elif command in ['complete', 'done', 'c'] and len(sys.argv) > 2:
            identifier = sys.argv[2]
            if manager.complete_todo(identifier):
                manager.save_todos()
        
        elif command in ['add', 'new', 'a']:
            if manager.add_todo():
                manager.save_todos()
        
        else:
            print("Usage:")
            print("  python manageActivities.py                    # Interactive mode")
            print("  python manageActivities.py list               # List activities")
            print("  python manageActivities.py edit <id>          # Edit TODO")
            print("  python manageActivities.py delete <id>        # Delete TODO")
            print("  python manageActivities.py complete <id>      # Complete TODO")
            print("  python manageActivities.py add               # Add TODO")

if __name__ == "__main__":
    main()
