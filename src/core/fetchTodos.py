#!/usr/bin/env python3
"""
TODO Consciousness Fetcher for personalAgent
Aggregates TODO items from multiple sources and dimensions
"""

import os
import sys
import json
from datetime import datetime, timedelta
import subprocess

class TodoFetcher:
    def __init__(self):
        self.data_dir = os.path.expanduser("~/personalAgent/data/cache")
        self.config_dir = os.path.expanduser("~/personalAgent/config")
        self.todo_sources = []
        
    def load_todo_config(self):
        """Load TODO source configuration"""
        config_file = os.path.join(self.config_dir, "todo_config.json")
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('sources', [])
        
        # Default sources if no config
        return [
            {'type': 'file', 'path': '~/todo.txt', 'name': 'Local TODO'},
            {'type': 'file', 'path': '~/personalAgent/todos.md', 'name': 'Agent TODO'},
            {'type': 'calendar', 'source': 'tasks', 'name': 'Calendar Tasks'}
        ]
    
    def fetch_file_todos(self, file_path, name):
        """Fetch TODOs from text/markdown files"""
        expanded_path = os.path.expanduser(file_path)
        todos = []
        
        if not os.path.exists(expanded_path):
            print(f"📝 Creating new TODO file: {expanded_path}")
            # Create basic TODO template
            os.makedirs(os.path.dirname(expanded_path), exist_ok=True)
            with open(expanded_path, 'w') as f:
                f.write(f"# {name}\n\n")
                f.write("## Today\n")
                f.write("- [ ] Example task\n\n")
                f.write("## This Week\n")
                f.write("- [ ] Example weekly task\n\n")
                f.write("## Someday/Maybe\n")
                f.write("- [ ] Example future task\n\n")
            return []
        
        try:
            with open(expanded_path, 'r') as f:
                lines = f.readlines()
            
            current_section = "General"
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Detect sections (markdown headers)
                if line.startswith('#'):
                    current_section = line.lstrip('#').strip()
                    continue
                
                # Parse TODO items
                if line.startswith('- [ ]') or line.startswith('- [x]') or line.startswith('- [X]'):
                    completed = '[x]' in line.lower()
                    task_text = line[5:].strip()  # Remove "- [ ] "
                    
                    # Parse priority if exists (!, !!, !!!)
                    priority = 'normal'
                    if task_text.startswith('!!!'):
                        priority = 'urgent'
                        task_text = task_text[3:].strip()
                    elif task_text.startswith('!!'):
                        priority = 'high'
                        task_text = task_text[2:].strip()
                    elif task_text.startswith('!'):
                        priority = 'medium'
                        task_text = task_text[1:].strip()
                    
                    # Parse due date if exists (due:YYYY-MM-DD)
                    due_date = None
                    if 'due:' in task_text:
                        parts = task_text.split('due:')
                        if len(parts) > 1:
                            try:
                                due_str = parts[1].split()[0]
                                due_date = datetime.strptime(due_str, '%Y-%m-%d').isoformat()
                                task_text = task_text.replace(f'due:{due_str}', '').strip()
                            except:
                                pass
                    
                    # Parse tags (#tag)
                    tags = []
                    words = task_text.split()
                    task_words = []
                    for word in words:
                        if word.startswith('#'):
                            tags.append(word[1:])
                        else:
                            task_words.append(word)
                    task_text = ' '.join(task_words)
                    
                    todos.append({
                        'source': name,
                        'source_type': 'file',
                        'file_path': file_path,
                        'line_number': line_num,
                        'section': current_section,
                        'text': task_text,
                        'completed': completed,
                        'priority': priority,
                        'due_date': due_date,
                        'tags': tags,
                        'created_at': datetime.now().isoformat()
                    })
                
                # Also parse plain bullet points as potential TODOs
                elif line.startswith('- ') and not line.startswith('- ['):
                    task_text = line[2:].strip()
                    if task_text:  # Not empty
                        todos.append({
                            'source': name,
                            'source_type': 'file',
                            'file_path': file_path,
                            'line_number': line_num,
                            'section': current_section,
                            'text': task_text,
                            'completed': False,
                            'priority': 'normal',
                            'due_date': None,
                            'tags': [],
                            'created_at': datetime.now().isoformat()
                        })
        
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")
        
        return todos
    
    def fetch_calendar_tasks(self):
        """Fetch tasks from calendar events that have task-like characteristics"""
        # This would integrate with calendar events that are marked as tasks
        # For now, we'll return placeholder data
        tasks = []
        
        # Check if there are recent calendar events that look like tasks
        cache_files = []
        if os.path.exists(self.data_dir):
            cache_files = [f for f in os.listdir(self.data_dir) 
                          if f.startswith('gregorian_events_') and f.endswith('.json')]
        
        if cache_files:
            # Get the most recent calendar data
            latest_file = sorted(cache_files)[-1]
            file_path = os.path.join(self.data_dir, latest_file)
            
            try:
                with open(file_path, 'r') as f:
                    calendar_data = json.load(f)
                
                for event in calendar_data.get('events', []):
                    # Look for events that seem like tasks
                    summary = event.get('summary', '')
                    description = event.get('description', '')
                    
                    # Check if event looks like a task
                    task_indicators = ['TODO', 'TASK', '[WORK]', '[PERSONAL]', '[HEALTH]', 
                                     '[LEARN]', '[CREATE]', '[ADMIN]', 'Review', 'Complete', 'Finish']
                    
                    is_task = any(indicator in summary.upper() for indicator in task_indicators)
                    
                    if is_task:
                        tasks.append({
                            'source': 'Calendar Tasks',
                            'source_type': 'calendar',
                            'calendar_name': event.get('calendar', ''),
                            'event_id': event.get('id', ''),
                            'text': summary,
                            'description': description,
                            'start_time': event.get('start', ''),
                            'location': event.get('location', ''),
                            'completed': False,
                            'priority': 'normal',
                            'due_date': event.get('start', ''),
                            'tags': [],
                            'created_at': datetime.now().isoformat()
                        })
            
            except Exception as e:
                print(f"⚠️ Error reading calendar data: {e}")
        
        return tasks
    
    def fetch_all_todos(self, timeframe="today"):
        """Fetch TODOs from all configured sources"""
        sources = self.load_todo_config()
        all_todos = []
        
        print(f"📝 Fetching TODO consciousness for timeframe: {timeframe}")
        
        for source in sources:
            source_todos = []
            
            if source['type'] == 'file':
                source_todos = self.fetch_file_todos(source['path'], source['name'])
            elif source['type'] == 'calendar':
                source_todos = self.fetch_calendar_tasks()
            
            if source_todos:
                print(f"   📋 {source['name']}: {len(source_todos)} items")
                all_todos.extend(source_todos)
            else:
                print(f"   📋 {source['name']}: No items")
        
        # Filter by timeframe if relevant
        filtered_todos = self.filter_by_timeframe(all_todos, timeframe)
        
        return filtered_todos
    
    def filter_by_timeframe(self, todos, timeframe):
        """Filter TODOs based on timeframe"""
        if timeframe == "today":
            # Show high priority, due today, or in "Today" sections
            today = datetime.now().date()
            
            filtered = []
            for todo in todos:
                include = False
                
                # Include if high priority
                if todo.get('priority') in ['urgent', 'high']:
                    include = True
                
                # Include if due today
                if todo.get('due_date'):
                    try:
                        due_date = datetime.fromisoformat(todo['due_date']).date()
                        if due_date <= today:
                            include = True
                    except:
                        pass
                
                # Include if in "Today" section
                if 'today' in todo.get('section', '').lower():
                    include = True
                
                # Include uncompleted calendar tasks for today
                if todo.get('source_type') == 'calendar':
                    if todo.get('start_time'):
                        try:
                            start_date = datetime.fromisoformat(todo['start_time'].replace('Z', '')).date()
                            if start_date == today:
                                include = True
                        except:
                            pass
                
                if include:
                    filtered.append(todo)
            
            return filtered
        
        # For other timeframes, return all for now
        return todos
    
    def display_todos(self, todos):
        """Display TODOs in a beautiful format"""
        if not todos:
            print("✨ No TODOs found - consciousness is clear!")
            return
        
        print(f"\n📝 TODO CONSCIOUSNESS OVERVIEW")
        print("=" * 50)
        
        # Group by source
        by_source = {}
        for todo in todos:
            source = todo.get('source', 'Unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(todo)
        
        for source, source_todos in by_source.items():
            print(f"\n📋 {source} ({len(source_todos)} items)")
            print("-" * 30)
            
            for todo in source_todos:
                # Status icon
                status = "✅" if todo.get('completed') else "⭕"
                
                # Priority icon
                priority_icons = {
                    'urgent': '🚨',
                    'high': '🔴',
                    'medium': '🟡',
                    'normal': '⚪'
                }
                priority_icon = priority_icons.get(todo.get('priority', 'normal'), '⚪')
                
                # Build display line
                text = todo.get('text', 'No description')
                section = todo.get('section', '')
                
                print(f"  {status} {priority_icon} {text}")
                
                if section and section != 'General':
                    print(f"      📂 {section}")
                
                if todo.get('due_date'):
                    print(f"      📅 Due: {todo['due_date'][:10]}")
                
                if todo.get('tags'):
                    tags_str = ' '.join(f"#{tag}" for tag in todo['tags'])
                    print(f"      🏷️  {tags_str}")
    
    def save_todos(self, todos, timeframe):
        """Save TODO data to cache"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"todos_{timeframe}_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump({
                'timeframe': timeframe,
                'fetched_at': datetime.now().isoformat(),
                'todo_count': len(todos),
                'todos': todos
            }, f, indent=2)
        
        print(f"💾 TODO data saved to: {filepath}")
        return filepath

def main():
    timeframe = sys.argv[1] if len(sys.argv) > 1 else "today"
    
    fetcher = TodoFetcher()
    todos = fetcher.fetch_all_todos(timeframe)
    
    fetcher.display_todos(todos)
    fetcher.save_todos(todos, timeframe)
    
    print(f"\n✨ TODO consciousness scan complete!")

if __name__ == "__main__":
    main()