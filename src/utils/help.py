#!/usr/bin/env python3
"""
Personal Agent Help Command
Shows comprehensive help for all available commands
"""

def print_help():
    help_text = """
🌟 PERSONAL AGENT - COMMAND REFERENCE
════════════════════════════════════════════════════════════════

🚀 MAIN SYSTEM COMMANDS:
  pagent                    Run full personal agent system
  patoday                   Run system for today only  
  paweek                    Run system for week
  consciousness            Quick status + today's matrix
  matrix                   Alias for pagent

📋 ACTIVITY MANAGEMENT:
  palist [timeframe]       Quick activity list (today/tomorrow/week/month)
  palist-today             Today's activities
  palist-tomorrow          Tomorrow's activities  
  palist-week              This week's activities
  palist-month             This month's activities
  activities               Alias for palist
  upcoming                 Alias for palist

✏️  TODO MANAGEMENT:
  pamanage                 Interactive TODO manager
  paedit T1                Edit TODO by ID (T1, T2, etc.)
  padelete "text"          Delete TODO by partial text or ID
  pacomplete T3            Mark TODO as complete
  paadd                    Add new TODO
  manage                   Alias for pamanage
  edit-todo                Alias for paedit

🤖 AI & SUBTASKS:
  pasubtasks               Generate intelligent subtasks
  pademo                   Test subtask generation
  subtasks                 Alias for pasubtasks

🔧 MODEL MANAGEMENT:
  pamodels                 Model management interface
  pamodel-list [provider]  List models (openai/gemini/claude/openrouter)
  pamodel-gpt4             Switch to GPT-4o-mini
  pamodel-gemini-flash     Switch to Gemini 1.5 Flash
  pamodel-gemini-pro       Switch to Gemini 1.5 Pro
  pamodel-claude           Switch to Claude Haiku

📅 CALENDAR & TIME:
  pacal                    Fetch calendar events
  patzolkin                Sacred calendar calculations
  galactic                 Alias for patzolkin
  pacal-switch             Calendar management interface
  pacal-current            Show current active calendar
  pacal-list               List all available calendars
  pacal-profiles           Show saved calendar profiles
  pacal-setup              Initial calendar configuration
  cal-switch               Alias for pacal-switch
  calendars                Alias for pacal-list

🔍 SYSTEM STATUS:
  pastatus                 Complete system health check
  pacheck                  Quick connectivity test
  padata                   View recent cache files
  palogs                   View recent logs
  paconfig                 Show configuration (safe)

🛠️  DEVELOPMENT & FILES:
  pa                       Go to personalAgent directory
  pavenv                   Activate virtual environment
  painstall                Install/update dependencies
  paupdate                 Pull updates + install deps
  paedit-context           Edit personal context
  paedit-env               Edit environment variables

🚀 QUICK WORKFLOWS:
  panow                    Current reality matrix
  paquick                  Fast calendar + subtask run
  pahelp                   Show this help

💡 COMMON WORKFLOWS:
  ┌─ Quick Check ─────────┐  ┌─ Task Management ─────┐  ┌─ AI Features ─────────┐
  │ activities             │  │ manage                │  │ pasubtasks            │
  │ pastatus              │  │ paedit T1             │  │ pamodel-list openai   │
  │ consciousness         │  │ pacomplete T2         │  │ pamodel-gpt4          │
  └───────────────────────┘  └───────────────────────┘  └───────────────────────┘

🎯 EXAMPLES:
  activities                    # See what's coming up
  manage                        # Interactive TODO management  
  paedit T2                     # Edit TODO #2
  padelete "old task"           # Remove by partial text
  pamodel-list openai           # See available OpenAI models
  consciousness                 # Full system status

════════════════════════════════════════════════════════════════
💡 TIP: Type any command without arguments to see its specific help
💡 All commands are aliased for quick access - no need for long paths!
"""
    print(help_text)

if __name__ == "__main__":
    print_help()
