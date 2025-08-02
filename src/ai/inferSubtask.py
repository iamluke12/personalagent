#!/usr/bin/env python3
"""
Intelligent Subtask Inference for personalAgent
Analyzes tasks and infers required subtasks based on context and patterns
Uses rule-based AI and LLM integration for intelligent task breakdown
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LLM Integration
try:
    import openai
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

class LLMInterface:
    """Interface for LLM-powered subtask inference"""
    
    def __init__(self):
        self.provider = os.getenv('LLM_PROVIDER', 'openai').lower()
        self.model = os.getenv('LLM_MODEL', 'gpt-4o-mini')
        
        # Initialize clients
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_client = None
        
        if self.provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key and api_key != 'your_openai_key_here':
                self.openai_client = OpenAI(api_key=api_key)
        
        elif self.provider == 'openrouter':
            api_key = os.getenv('OPENROUTER_API_KEY')
            if api_key and api_key != 'your_openrouter_key_here':
                # OpenRouter uses OpenAI-compatible API
                self.openai_client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key
                )
                # Use the OpenRouter model
                self.model = os.getenv('LLM_MODEL', 'google/gemma-2-9b-it:free')
        
        elif self.provider == 'gemini' and HAS_GEMINI:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key and api_key != 'your_gemini_key_here':
                genai.configure(api_key=api_key)
                self.gemini_client = genai.GenerativeModel(
                    model_name=self.model if self.model.startswith('gemini-') else 'gemini-1.5-flash'
                )
        
        elif self.provider == 'anthropic' and HAS_ANTHROPIC:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key and api_key != 'your_anthropic_key_here':
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
    
    def is_available(self):
        """Check if LLM is available"""
        if self.provider in ['openai', 'openrouter']:
            return self.openai_client is not None
        elif self.provider == 'anthropic':
            return self.anthropic_client is not None
        elif self.provider == 'gemini':
            return self.gemini_client is not None
        return False
    
    def generate_subtasks(self, task_description, context_info, existing_rules=None):
        """Generate intelligent subtasks using LLM"""
        if not self.is_available():
            return None
        
        prompt = self._build_subtask_prompt(task_description, context_info, existing_rules)
        
        try:
            if self.provider in ['openai', 'openrouter']:
                # Prepare extra headers for OpenRouter
                extra_headers = {}
                extra_body = {}
                
                if self.provider == 'openrouter':
                    extra_headers = {
                        "HTTP-Referer": "https://github.com/personalAgent",
                        "X-Title": "Personal Agent Task Breakdown"
                    }
                
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an intelligent task breakdown assistant. You analyze tasks and create detailed, actionable subtasks with realistic time estimates and optimal sequencing."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=2000,
                    **({"extra_headers": extra_headers} if self.provider == 'openrouter' else {}),
                    **({"extra_body": extra_body} if self.provider == 'openrouter' else {})
                )
                return self._parse_llm_response(response.choices[0].message.content)
            
            elif self.provider == 'gemini':
                # Combine system message with user prompt for Gemini
                full_prompt = f"""You are an intelligent task breakdown assistant. You analyze tasks and create detailed, actionable subtasks with realistic time estimates and optimal sequencing.

{prompt}"""
                
                response = self.gemini_client.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=2000,
                    )
                )
                return self._parse_llm_response(response.text)
            
            elif self.provider == 'anthropic':
                response = self.anthropic_client.messages.create(
                    model=self.model if 'claude' in self.model else 'claude-3-haiku-20240307',
                    max_tokens=2000,
                    temperature=0.3,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                return self._parse_llm_response(response.content[0].text)
        
        except Exception as e:
            print(f"⚠️ LLM API Error: {e}")
            return None
    
    def _build_subtask_prompt(self, task_description, context_info, existing_rules):
        """Build comprehensive prompt for LLM"""
        prompt = f"""
TASK BREAKDOWN REQUEST

Main Task: "{task_description}"

Personal Context:
- Location: {context_info.get('location', {}).get('home', {}).get('address', 'Unknown')}
- Transport: {context_info.get('preferences', {}).get('transport_method', 'unknown')}
- Work Style: {context_info.get('preferences', {}).get('work_style', 'unknown')}
- Available Resources: {context_info.get('resources', {})}

Please break down this task into specific, actionable subtasks. For each subtask, provide:

1. **Task Name**: Clear, actionable description
2. **Duration**: Realistic time estimate in minutes
3. **Timing**: When to do it (before/during/after main task, with specific time offset)
4. **Priority**: high/medium/low
5. **Location**: Where this happens (if relevant)
6. **Dependencies**: What needs to be done first
7. **Context**: Why this subtask is necessary

Return the response as a JSON array of subtasks with this structure:
```json
[
  {{
    "task": "Subtask description",
    "duration": 15,
    "timing_type": "before",
    "time_offset": 30,
    "priority": "high",
    "location": "home/office/store/etc",
    "dependencies": ["other subtask"],
    "category": "preparation/execution/cleanup",
    "description": "Why this is needed and any tips",
    "optional": false
  }}
]
```

Focus on:
- Realistic time estimates based on the personal context
- Logical sequencing and dependencies
- Practical considerations (travel time, preparation, cleanup)
- Personal efficiency (energy patterns, work style)
- Location-specific optimizations

Avoid:
- Overly generic subtasks
- Unrealistic time estimates
- Missing dependencies
- Ignoring personal context
"""
        return prompt
    
    def _parse_llm_response(self, response_text):
        """Parse LLM response into structured subtasks"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'```json\s*(\[.*?\])\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Look for array structure
                json_match = re.search(r'(\[.*\])', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    return None
            
            subtasks = json.loads(json_str)
            
            # Validate and standardize structure
            standardized_subtasks = []
            for subtask in subtasks:
                if isinstance(subtask, dict) and 'task' in subtask:
                    standardized = {
                        'task': subtask.get('task', ''),
                        'duration': int(subtask.get('duration', 10)),
                        'timing_type': subtask.get('timing_type', 'before'),
                        'time_offset': int(subtask.get('time_offset', 0)),
                        'priority': subtask.get('priority', 'medium'),
                        'location': subtask.get('location', ''),
                        'dependencies': subtask.get('dependencies', []),
                        'category': subtask.get('category', 'general'),
                        'description': subtask.get('description', ''),
                        'optional': subtask.get('optional', False),
                        'source': 'llm_inference'
                    }
                    standardized_subtasks.append(standardized)
            
            return standardized_subtasks
        
        except Exception as e:
            print(f"⚠️ Error parsing LLM response: {e}")
            return None

class SubtaskInference:
    def __init__(self):
        self.data_dir = os.path.expanduser("~/personalAgent/data/cache")
        self.config_dir = os.path.expanduser("~/personalAgent/config")
        self.context = self.load_personal_context()
        self.rules = self.load_inference_rules()
        self.llm = LLMInterface()
        self.use_llm = self.llm.is_available()
        
        if self.use_llm:
            print("🤖 LLM-powered subtask inference enabled")
        else:
            print("📝 Using rule-based subtask inference")
    
    def load_personal_context(self):
        """Load personal context and circumstances"""
        context_file = os.path.join(self.config_dir, "personal_context.json")
        
        default_context = {
            "location": {
                "home": {"address": "Leipzig, Germany", "has_kitchen": True, "has_car": False},
                "work": {"remote": True, "office_location": ""},
                "grocery_stores": ["REWE", "Edeka", "Aldi"],
                "gym": "Local Gym"
            },
            "preferences": {
                "cooking_skill": "intermediate",
                "transport_method": "public_transport",
                "work_style": "deep_focus",
                "energy_patterns": {
                    "peak": ["09:00", "14:00"],
                    "low": ["13:00", "16:00"]
                }
            },
            "resources": {
                "has_car": False,
                "has_bike": True,
                "kitchen_equipped": True,
                "home_office": True
            },
            "patterns": {
                "typical_meal_prep": 30,
                "commute_time": 15,
                "meeting_prep": 10
            }
        }
        
        if os.path.exists(context_file):
            try:
                with open(context_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Create default context file
        os.makedirs(self.config_dir, exist_ok=True)
        with open(context_file, 'w') as f:
            json.dump(default_context, f, indent=2)
        
        print(f"📋 Created default personal context: {context_file}")
        return default_context
    
    def load_inference_rules(self):
        """Load task inference rules with better categorization"""
        return {
            "presentation": {
                "keywords": ["presentation", "present", "demo", "pitch", "slides", "keynote", "powerpoint"],
                "exclude_keywords": ["cooking", "meal", "dinner"],
                "subtasks": [
                    {"task": "Review and update slides", "time_before": 60, "duration": 30},
                    {"task": "Practice presentation", "time_before": 30, "duration": 15},
                    {"task": "Test technical setup", "time_before": 15, "duration": 10},
                    {"task": "Prepare backup materials", "time_before": 45, "duration": 10},
                    {"task": "Arrive early and setup", "time_before": 10, "duration": 0}
                ]
            },
            "meeting": {
                "keywords": ["meeting", "call", "zoom", "conference", "interview", "discussion"],
                "exclude_keywords": ["cooking", "meal"],
                "subtasks": [
                    {"task": "Review agenda and materials", "time_before": 30, "duration": 15},
                    {"task": "Prepare questions and notes", "time_before": 20, "duration": 10},
                    {"task": "Test tech setup (camera/mic)", "time_before": 10, "duration": 5},
                    {"task": "Join call or arrive early", "time_before": 5, "duration": 0}
                ]
            },
            "cooking": {
                "keywords": ["cook", "prepare", "meal", "dinner", "lunch", "breakfast", "recipe", "bake", "kitchen"],
                "subtasks": [
                    {"task": "Check ingredients available", "time_before": 60, "duration": 5},
                    {"task": "Buy missing ingredients", "time_before": 120, "duration": 30, "condition": "missing_ingredients"},
                    {"task": "Prep cooking space and tools", "time_before": 15, "duration": 5},
                    {"task": "Clean up kitchen", "time_after": 0, "duration": 15}
                ]
            },
            "shopping": {
                "keywords": ["shop", "buy", "purchase", "grocery", "groceries", "store", "mall", "market"],
                "exclude_keywords": ["online", "digital"],
                "subtasks": [
                    {"task": "Make detailed shopping list", "time_before": 60, "duration": 10},
                    {"task": "Check store hours and location", "time_before": 30, "duration": 5},
                    {"task": "Plan efficient route", "time_before": 20, "duration": 5},
                    {"task": "Travel to store", "time_before": 15, "duration": 15}
                ]
            },
            "travel": {
                "keywords": ["travel", "trip", "flight", "train", "airport", "station", "journey", "vacation"],
                "subtasks": [
                    {"task": "Check weather at destination", "time_before": 1440, "duration": 5},  # 24h before
                    {"task": "Pack luggage", "time_before": 180, "duration": 30},
                    {"task": "Check transportation to departure", "time_before": 120, "duration": 10},
                    {"task": "Leave for departure point", "time_before": 90, "duration": 60},
                    {"task": "Check-in or arrive at departure", "time_before": 30, "duration": 0}
                ]
            },
            "work_research": {
                "keywords": ["research", "analyze", "study", "investigate", "explore", "review", "tools", "compare"],
                "exclude_keywords": ["cooking", "recipe"],
                "subtasks": [
                    {"task": "Define research criteria and goals", "time_before": 15, "duration": 10},
                    {"task": "Gather initial resources and bookmarks", "time_before": 10, "duration": 10},
                    {"task": "Set up organized workspace", "time_before": 5, "duration": 5},
                    {"task": "Take structured notes", "time_during": 0, "duration": 0},
                    {"task": "Summarize findings and next steps", "time_after": 0, "duration": 10}
                ]
            },
            "work_project": {
                "keywords": ["project", "develop", "build", "create", "code", "write", "design"],
                "exclude_keywords": ["cooking", "meal"],
                "subtasks": [
                    {"task": "Gather required materials and files", "time_before": 30, "duration": 10},
                    {"task": "Set up focused workspace", "time_before": 15, "duration": 5},
                    {"task": "Plan break schedule", "time_before": 5, "duration": 2},
                    {"task": "Save work and organize files", "time_after": 0, "duration": 5}
                ]
            },
            "health": {
                "keywords": ["gym", "workout", "exercise", "yoga", "run", "fitness", "sport", "training"],
                "subtasks": [
                    {"task": "Prepare workout clothes and gear", "time_before": 60, "duration": 5},
                    {"task": "Light snack (if needed)", "time_before": 45, "duration": 10},
                    {"task": "Warm up routine", "time_before": 10, "duration": 10},
                    {"task": "Cool down and stretch", "time_after": 0, "duration": 15},
                    {"task": "Shower and change", "time_after": 15, "duration": 20}
                ]
            },
            "learning": {
                "keywords": ["learn", "course", "tutorial", "practice", "certification", "exam", "study"],
                "exclude_keywords": ["research", "tools"],
                "subtasks": [
                    {"task": "Prepare study materials and notes", "time_before": 15, "duration": 5},
                    {"task": "Eliminate distractions", "time_before": 10, "duration": 5},
                    {"task": "Set learning goals for session", "time_before": 5, "duration": 2},
                    {"task": "Review and summarize learnings", "time_after": 0, "duration": 10}
                ]
            }
        }
    
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
    
    def classify_task(self, task_text):
        """Classify task based on keywords with exclusion logic and return matching rules"""
        task_lower = task_text.lower()
        
        # Find all potential matches
        potential_matches = []
        
        for category, rules in self.rules.items():
            # Check if any keywords match
            keyword_matches = sum(1 for keyword in rules['keywords'] if keyword in task_lower)
            
            # Check for exclusion keywords
            exclude_keywords = rules.get('exclude_keywords', [])
            has_exclusions = any(exclude_keyword in task_lower for exclude_keyword in exclude_keywords)
            
            if keyword_matches > 0 and not has_exclusions:
                potential_matches.append((category, rules, keyword_matches))
        
        if not potential_matches:
            return None, None
        
        # Sort by number of keyword matches (most specific first)
        potential_matches.sort(key=lambda x: x[2], reverse=True)
        
        # Return the best match
        category, rules, _ = potential_matches[0]
        print(f"🎯 Classified '{task_text}' as '{category}' category")
        return category, rules
    
    def parse_event_duration(self, event):
        """Parse event duration in minutes"""
        try:
            start = datetime.fromisoformat(event['start'].replace('Z', ''))
            end = datetime.fromisoformat(event['end'].replace('Z', ''))
            return int((end - start).total_seconds() / 60)
        except:
            return 60  # Default 1 hour
    
    def parse_event_start_time(self, event):
        """Parse event start time"""
        try:
            return datetime.fromisoformat(event['start'].replace('Z', ''))
        except:
            return datetime.now()
    
    def generate_subtasks_for_event(self, event):
        """Generate subtasks for a calendar event using LLM or rules"""
        title = event.get('summary', '')
        description = event.get('description', '')
        combined_text = f"{title} {description}".strip()
        
        # Try LLM first if available
        if self.use_llm and combined_text:
            llm_subtasks = self.llm.generate_subtasks(
                task_description=combined_text,
                context_info=self.context,
                existing_rules=self.rules
            )
            
            if llm_subtasks:
                # Convert LLM subtasks to event-specific format
                start_time = self.parse_event_start_time(event)
                duration = self.parse_event_duration(event)
                
                processed_subtasks = []
                for subtask in llm_subtasks:
                    processed = self._convert_llm_subtask_to_event(subtask, event, start_time, duration)
                    if processed:
                        processed_subtasks.append(processed)
                
                if processed_subtasks:
                    print(f"🤖 Generated {len(processed_subtasks)} LLM subtasks for: {title}")
                    return processed_subtasks
        
        # Fallback to rule-based approach
        return self._generate_rule_based_event_subtasks(event)
    
    def _convert_llm_subtask_to_event(self, llm_subtask, event, start_time, duration):
        """Convert LLM subtask format to event subtask format"""
        try:
            subtask = {
                'parent_event_id': event.get('id', ''),
                'parent_title': event.get('summary', ''),
                'category': llm_subtask.get('category', 'general'),
                'task': llm_subtask['task'],
                'duration': llm_subtask.get('duration', 10),
                'priority': llm_subtask.get('priority', 'medium'),
                'location': llm_subtask.get('location', ''),
                'description': llm_subtask.get('description', ''),
                'dependencies': llm_subtask.get('dependencies', []),
                'optional': llm_subtask.get('optional', False),
                'source': 'llm_inference'
            }
            
            # Calculate timing based on LLM output
            timing_type = llm_subtask.get('timing_type', 'before')
            time_offset = llm_subtask.get('time_offset', 0)
            
            if timing_type == 'before':
                subtask_time = start_time - timedelta(minutes=time_offset)
                subtask['scheduled_time'] = subtask_time.isoformat()
                subtask['timing'] = f"{time_offset} minutes before"
            
            elif timing_type == 'after':
                end_time = start_time + timedelta(minutes=duration)
                subtask_time = end_time + timedelta(minutes=time_offset)
                subtask['scheduled_time'] = subtask_time.isoformat()
                subtask['timing'] = f"{time_offset} minutes after"
            
            elif timing_type == 'during':
                subtask_time = start_time + timedelta(minutes=time_offset)
                subtask['scheduled_time'] = subtask_time.isoformat()
                subtask['timing'] = f"During event (+{time_offset}min)"
            
            return subtask
        
        except Exception as e:
            print(f"⚠️ Error converting LLM subtask: {e}")
            return None
    
    def _generate_rule_based_event_subtasks(self, event):
        """Original rule-based event subtask generation"""
        title = event.get('summary', '')
        description = event.get('description', '')
        combined_text = f"{title} {description}"
        
        category, rules = self.classify_task(combined_text)
        
        if not category or not rules:
            return []
        
        start_time = self.parse_event_start_time(event)
        duration = self.parse_event_duration(event)
        
        subtasks = []
        
        for subtask_rule in rules['subtasks']:
            subtask = {
                'parent_event_id': event.get('id', ''),
                'parent_title': title,
                'category': category,
                'task': subtask_rule['task'],
                'duration': subtask_rule.get('duration', 10),
                'source': 'inference_engine'
            }
            
            # Calculate timing
            if 'time_before' in subtask_rule:
                subtask_time = start_time - timedelta(minutes=subtask_rule['time_before'])
                subtask['scheduled_time'] = subtask_time.isoformat()
                subtask['timing'] = f"{subtask_rule['time_before']} minutes before"
            
            elif 'time_after' in subtask_rule:
                end_time = start_time + timedelta(minutes=duration)
                subtask_time = end_time + timedelta(minutes=subtask_rule['time_after'])
                subtask['scheduled_time'] = subtask_time.isoformat()
                subtask['timing'] = f"{subtask_rule['time_after']} minutes after"
            
            elif 'time_during' in subtask_rule:
                if subtask_rule.get('repeat'):
                    # Create multiple subtasks during the event
                    for i in range(0, duration, subtask_rule['time_during']):
                        repeat_subtask = subtask.copy()
                        repeat_time = start_time + timedelta(minutes=i)
                        repeat_subtask['scheduled_time'] = repeat_time.isoformat()
                        repeat_subtask['task'] = f"{subtask_rule['task']} ({i//60+1})"
                        repeat_subtask['timing'] = f"During event (every {subtask_rule['time_during']}min)"
                        subtasks.append(repeat_subtask)
                    continue
                else:
                    subtask_time = start_time + timedelta(minutes=subtask_rule['time_during'])
                    subtask['scheduled_time'] = subtask_time.isoformat()
                    subtask['timing'] = f"During event"
            
            # Apply personal context adjustments
            subtask = self.apply_personal_context(subtask, category)
            
            subtasks.append(subtask)
        
        return subtasks
    
    def apply_personal_context(self, subtask, category):
        """Apply personal context to adjust subtask details"""
        # Adjust travel time based on transport method
        if "travel" in subtask['task'].lower() or "route" in subtask['task'].lower():
            transport = self.context['preferences']['transport_method']
            if transport == 'public_transport':
                subtask['notes'] = "Check public transport schedules and delays"
                subtask['duration'] = max(subtask['duration'], 20)  # Add buffer time
        
        # Adjust cooking tasks based on skill level
        if category == 'cooking':
            skill = self.context['preferences']['cooking_skill']
            if skill == 'beginner':
                subtask['duration'] = int(subtask['duration'] * 1.5)  # Take longer
                subtask['notes'] = "Take extra time as you're learning"
        
        # Add location context
        if 'shop' in subtask['task'].lower() or 'buy' in subtask['task'].lower():
            stores = self.context['location']['grocery_stores']
            subtask['suggestions'] = f"Nearby options: {', '.join(stores)}"
        
        return subtask
    
    def generate_subtasks_for_todo(self, todo):
        """Generate subtasks for TODO items using LLM or rules"""
        task_text = todo.get('text', '')
        
        # Try LLM first if available
        if self.use_llm and task_text:
            # Add todo context to the task description
            context_text = task_text
            if todo.get('section'):
                context_text += f" (from {todo['section']} section)"
            if todo.get('due_date'):
                context_text += f" (due: {todo['due_date']})"
            if todo.get('tags'):
                context_text += f" (tags: {', '.join(todo['tags'])})"
            
            llm_subtasks = self.llm.generate_subtasks(
                task_description=context_text,
                context_info=self.context,
                existing_rules=self.rules
            )
            
            if llm_subtasks:
                # Convert LLM subtasks to TODO-specific format
                processed_subtasks = []
                for subtask in llm_subtasks:
                    processed = self._convert_llm_subtask_to_todo(subtask, todo)
                    if processed:
                        processed_subtasks.append(processed)
                
                if processed_subtasks:
                    print(f"🤖 Generated {len(processed_subtasks)} LLM subtasks for: {task_text}")
                    return processed_subtasks
        
        # Fallback to rule-based approach
        return self._generate_rule_based_todo_subtasks(todo)
    
    def _convert_llm_subtask_to_todo(self, llm_subtask, todo):
        """Convert LLM subtask format to TODO subtask format"""
        try:
            subtask = {
                'parent_todo': todo.get('text', ''),
                'category': llm_subtask.get('category', 'general'),
                'task': llm_subtask['task'],
                'duration': llm_subtask.get('duration', 10),
                'priority': llm_subtask.get('priority', todo.get('priority', 'medium')),
                'location': llm_subtask.get('location', ''),
                'description': llm_subtask.get('description', ''),
                'dependencies': llm_subtask.get('dependencies', []),
                'optional': llm_subtask.get('optional', False),
                'source': 'llm_inference'
            }
            
            # Calculate timing
            timing_type = llm_subtask.get('timing_type', 'before')
            time_offset = llm_subtask.get('time_offset', 0)
            
            if timing_type == 'before':
                subtask['timing'] = f"{time_offset} minutes before main task"
            elif timing_type == 'after':
                subtask['timing'] = f"{time_offset} minutes after main task"
            else:
                subtask['timing'] = "During main task"
            
            return subtask
        
        except Exception as e:
            print(f"⚠️ Error converting LLM subtask: {e}")
            return None
    
    def _generate_rule_based_todo_subtasks(self, todo):
        """Original rule-based TODO subtask generation"""
        task_text = todo.get('text', '')
        category, rules = self.classify_task(task_text)
        
        if not category or not rules:
            return []
        
        # For TODOs without specific times, create relative subtasks
        subtasks = []
        base_time = datetime.now()
        
        if todo.get('due_date'):
            try:
                base_time = datetime.fromisoformat(todo['due_date'])
            except:
                pass
        
        for subtask_rule in rules['subtasks']:
            if 'time_before' in subtask_rule:
                subtask = {
                    'parent_todo': task_text,
                    'category': category,
                    'task': subtask_rule['task'],
                    'duration': subtask_rule.get('duration', 10),
                    'timing': f"{subtask_rule['time_before']} minutes before main task",
                    'source': 'rule_based',
                    'priority': todo.get('priority', 'normal')
                }
                
                subtasks.append(subtask)
        
        return subtasks
    
    def infer_all_subtasks(self, timeframe="today"):
        """Generate subtasks for all calendar events and TODOs"""
        print(f"🧠 Inferring dimensional subtasks for: {timeframe}")
        
        # Get calendar events
        calendar_events = self.get_latest_calendar_data()
        todo_items = self.get_latest_todo_data()
        
        all_subtasks = []
        
        # Process calendar events
        print(f"📅 Processing {len(calendar_events)} calendar events...")
        for event in calendar_events:
            event_subtasks = self.generate_subtasks_for_event(event)
            all_subtasks.extend(event_subtasks)
        
        # Process TODO items
        print(f"📝 Processing {len(todo_items)} TODO items...")
        for todo in todo_items:
            if not todo.get('completed'):  # Only process incomplete TODOs
                todo_subtasks = self.generate_subtasks_for_todo(todo)
                all_subtasks.extend(todo_subtasks)
        
        print(f"🎯 Generated {len(all_subtasks)} intelligent subtasks")
        
        return all_subtasks
    
    def save_subtasks(self, subtasks, timeframe):
        """Save inferred subtasks to cache"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"subtasks_{timeframe}_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        data = {
            'timeframe': timeframe,
            'inferred_at': datetime.now().isoformat(),
            'subtask_count': len(subtasks),
            'subtasks': subtasks
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    def display_subtasks(self, subtasks):
        """Display inferred subtasks beautifully"""
        if not subtasks:
            print("🤖 No subtasks inferred - all activities are atomic!")
            return
        
        print(f"\n🧠 INFERRED SUBTASKS")
        print("=" * 50)
        
        # Group by parent activity
        by_parent = {}
        for subtask in subtasks:
            parent = subtask.get('parent_title') or subtask.get('parent_todo', 'Unknown')
            if parent not in by_parent:
                by_parent[parent] = []
            by_parent[parent].append(subtask)
        
        for parent, parent_subtasks in by_parent.items():
            print(f"\n🎯 {parent}")
            print("-" * 40)
            
            # Sort by scheduled time if available
            parent_subtasks.sort(key=lambda x: x.get('scheduled_time', '99:99'))
            
            for subtask in parent_subtasks:
                time_str = subtask.get('scheduled_time', '')
                duration_str = f" ({subtask.get('estimated_duration', subtask.get('duration', '?'))} min)" if subtask.get('estimated_duration') or subtask.get('duration') else ""
                location_str = f" @ {subtask['location']}" if subtask.get('location') else ""
                
                # Use 'task' field if 'title' doesn't exist
                task_title = subtask.get('title', subtask.get('task', 'Unknown'))
                
                print(f"  🔸 {time_str} {task_title}{duration_str}{location_str}")
                if subtask.get('description'):
                    print(f"     💡 {subtask['description']}")
                elif subtask.get('timing'):
                    print(f"     💡 {subtask['timing']}")

def main():
    """Main execution function"""
    timeframe = sys.argv[1] if len(sys.argv) > 1 else "today"
    
    print(f"🧠 Inferring dimensional subtasks for: {timeframe}")
    
    inference = SubtaskInference()
    
    # Infer subtasks from recent TODO and calendar data
    subtasks = inference.infer_all_subtasks(timeframe)
    
    if subtasks:
        # Save inferred subtasks
        filepath = inference.save_subtasks(subtasks, timeframe)
        
        # Display subtasks
        inference.display_subtasks(subtasks)
        
        print(f"\n💾 Subtasks saved to: {filepath}")
    else:
        print("🤖 No subtasks inferred - all activities are atomic!")
    
    print("✨ Subtask inference complete!")

if __name__ == "__main__":
    main()