# Calendar Profile System Documentation

## Overview
The Calendar Profile System implements a priority-based multi-calendar management system for personalAgent. It allows context switching between different life areas (Family, Personal, Work) with intelligent conflict resolution and filtering.

## Priority Hierarchy
1. **Family Profile** (Priority 1)
   - Highest priority calendar
   - Events are immovable anchors
   - Other calendars adapt around family events
   - Keywords: family, kids, home, personal

2. **Personal Profile** (Priority 2) 
   - Second priority
   - Can coexist with family events
   - Avoids family conflicts when possible
   - Keywords: personal, self, appointment, health

3. **Work Profile** (Priority 3)
   - Lowest priority - fills free slots only
   - Shows family events as [BUSY] blocks
   - Auto-suggests alternatives for conflicts
   - Keywords: work, meeting, project, deadline, business

## Core Components

### 1. Profile Manager (`scripts/profileManager.py`)
Main controller for profile management and calendar context switching.

**Key Features:**
- Profile switching and current profile tracking
- Conflict detection with higher priority calendars
- Alternative time suggestions for work events
- Auto-detection of appropriate profile based on event content
- Context export for other scripts

**Usage:**
```bash
./venv/bin/python scripts/profileManager.py switch --profile work
./venv/bin/python scripts/profileManager.py current
./venv/bin/python scripts/profileManager.py list
./venv/bin/python scripts/profileManager.py context
```

### 2. Profile Configuration (`config/calendar_profiles.json`)
Central configuration file defining:
- Calendar mappings for each profile
- Conflict resolution rules
- Display settings and filters
- Priority hierarchy

### 3. Enhanced Task Creation (`scripts/createTask.py`)
Profile-aware task creation with conflict resolution.

**New Features:**
- Uses current profile's primary calendar automatically
- Detects conflicts for work profile events
- Suggests alternative times when conflicts occur
- Auto-detects appropriate profile based on task content
- Option to switch profiles during task creation

**Conflict Resolution for Work Events:**
1. Detects conflicts with family/personal calendars
2. Shows conflicting events
3. Offers 3 alternative times
4. Allows custom time entry
5. Provides override option

### 4. Profile-Aware Activity Listing (`scripts/listActivities.py`)
Enhanced activity viewer that respects profile context.

**Profile-Specific Behavior:**
- **Family Profile**: Shows family events and related personal items
- **Personal Profile**: Shows personal + family events normally  
- **Work Profile**: Shows work events + family events as [BUSY] blocks

### 5. Terminal Prompt Integration (`scripts/promptHelper.py`)
Lightweight helper for oh-my-zsh prompt integration.

**Usage:**
```bash
# Full profile name with icon
./venv/bin/python scripts/promptHelper.py
# Output: 👨‍👩‍👧‍👦family

# Icon only
./venv/bin/python scripts/promptHelper.py --short  
# Output: 👨‍👩‍👧‍👦
```

## Updated Aliases

### Profile Management
```bash
# Profile switching
pacal-switch     # Switch profile (interactive)
pacal-current    # Show current profile 
pacal-list       # List all profiles
pacal-context    # Export current profile context

# Quick profile switching
pa-family        # Switch to family profile
pa-personal      # Switch to personal profile  
pa-work          # Switch to work profile

# Terminal prompt integration
pa-prompt        # Get profile for prompt (full)
pa-prompt-short  # Get profile icon only
```

### Profile-Aware Commands
All existing commands now respect the current profile:
- `palist` - Profile-filtered activity listing
- `pacreate` - Profile-aware task creation with conflict detection
- `pamanage` - Activity management in current profile context

## Configuration Structure

```json
{
  "profiles": {
    "family": {
      "priority": 1,
      "calendars": [...],
      "conflict_resolution": {
        "blocks_others": true,
        "can_be_moved": false
      }
    },
    "personal": {
      "priority": 2, 
      "conflict_resolution": {
        "avoid_family_conflicts": true
      }
    },
    "work": {
      "priority": 3,
      "conflict_resolution": {
        "free_slots_only": true,
        "auto_suggest_alternatives": true
      }
    }
  },
  "current_profile": "family",
  "settings": {
    "auto_switch_on_keyword": true,
    "override_mode": false,
    "conflict_notification": true
  }
}
```

## Smart Features

### 1. Auto Profile Detection
The system analyzes event titles and descriptions to suggest the appropriate profile:
- "Team meeting" → work profile
- "Family dinner" → family profile  
- "Doctor appointment" → personal profile

### 2. Intelligent Conflict Resolution
- **Family events**: Never moved, block other calendars
- **Personal events**: Can coexist with family, avoid conflicts when possible
- **Work events**: Must find free slots, get suggestions for conflicts

### 3. Context-Aware Display
- Work profile shows family events as [BUSY] to indicate unavailable time
- Personal profile shows family events normally for coordination
- Family profile is the primary view for all family-related scheduling

## Future Enhancements

### 1. Terminal Prompt Integration
Complete oh-my-zsh theme integration showing current profile:
```bash
# Example prompt enhancement
user@computer [👨‍👩‍👧‍👦family] ~/personalAgent $
```

### 2. Override Mode
Temporary override for emergency scheduling:
```bash
./venv/bin/python scripts/profileManager.py --override-mode on
```

### 3. Smart Scheduling
LLM-powered intelligent scheduling that understands:
- Optimal times for different activities
- Energy levels and productivity patterns
- Automatic conflict avoidance

## Testing

The system includes comprehensive testing via `scripts/testProfiles.py`:
- Profile loading and configuration
- Context switching and export
- Auto-detection accuracy
- Calendar integration

## Benefits

1. **Clear Priority System**: Family-first approach ensures personal time is protected
2. **Conflict Prevention**: Automatic detection prevents double-booking
3. **Context Switching**: Easy switching between life areas with appropriate filters
4. **Intelligent Suggestions**: Smart alternatives when conflicts occur
5. **Visual Clarity**: Clear indicators for different profile contexts
6. **Seamless Integration**: Works with existing personalAgent commands

This system transforms personalAgent from a single-calendar tool into a sophisticated multi-context calendar manager that respects life priorities and prevents scheduling conflicts.
