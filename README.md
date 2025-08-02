# PersonalAgent 🤖📅

> **Intelligent Calendar Management with AI-Powered Task Automation**

PersonalAgent is a sophisticated, priority-based multi-calendar management system that respects your life priorities while providing intelligent conflict resolution and AI-powered task automation.

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/personalagent/personalagent)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

## 🌟 Key Features

### 🏆 **Priority-Based Calendar System**
- **Family First**: Family events are immovable anchors that other calendars adapt around
- **Smart Hierarchy**: Personal > Work priority with intelligent conflict resolution
- **Context Switching**: Seamlessly switch between life contexts (Family, Personal, Work)

### 🧠 **AI-Powered Intelligence**
- **Multiple LLM Support**: OpenAI GPT-4, Google Gemini, Anthropic Claude, OpenRouter (200+ models)
- **Intelligent Subtask Inference**: Automatically break down complex tasks into actionable steps
- **Smart Scheduling**: AI-powered conflict detection and alternative time suggestions

### ⚡ **Streamlined Workflow**
- **Profile-Aware Operations**: All commands respect your current calendar context
- **Conflict Prevention**: Automatic detection prevents double-booking
- **Quick Commands**: Lightning-fast task creation and activity listing

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Calendar API credentials
- OpenAI/Gemini/Claude API keys (optional, for AI features)

### Installation

```bash
# Clone the repository
git clone https://github.com/personalagent/personalagent.git
cd personalagent

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up Google Calendar credentials
# (Follow Google Calendar API setup guide)

# Add aliases to your shell
cat zshrc_aliases.txt >> ~/.zshrc
source ~/.zshrc
```

### Basic Usage

```bash
# Main system - fetch latest data
pagent

# Quick activity overview
pa-list today

# Switch calendar profiles
pa-family    # Switch to family calendar
pa-work      # Switch to work calendar
pa-personal  # Switch to personal calendar

# Create profile-aware tasks
pa-create --title "Team meeting" --when "tomorrow 14:00"

# Manage existing activities
pamanage edit T1  # Edit first TODO item
```

## 📁 Project Structure

```
personalAgent/
├── 📂 src/                    # Source code modules
│   ├── 📂 core/               # Core system functionality
│   │   ├── fetchGregorian.py  # Sacred calendar integration
│   │   ├── fetchTodos.py      # TODO management
│   │   └── getLatest.sh       # Main data fetcher
│   ├── 📂 calendar/           # Calendar management
│   │   ├── profileManager.py  # Profile system core
│   │   ├── createTask.py      # Task creation with conflict detection
│   │   ├── listActivities.py  # Profile-aware activity listing
│   │   └── manageActivities.py # Activity management
│   ├── 📂 ai/                 # AI integration
│   │   ├── inferSubtask.py    # LLM-powered subtask inference
│   │   └── setModel.py        # Multi-provider LLM management
│   └── 📂 utils/              # Utility functions
│       ├── promptHelper.py    # Terminal prompt integration
│       └── help.py            # Help system
├── 📂 bin/                    # Executable entry points
│   ├── pagent                 # Main entry point
│   ├── pa-profiles            # Profile manager
│   ├── pa-list                # Activity lister
│   └── pa-create              # Task creator
├── 📂 config/                 # Configuration files
├── 📂 docs/                   # Documentation
├── 📂 tests/                  # Test files
└── 📂 data/                   # Data cache
```

## 🎯 Calendar Profile System

PersonalAgent's core innovation is its **priority-based calendar management**:

### Priority Hierarchy
1. **👨‍👩‍👧‍👦 Family Profile** (Priority 1)
   - Highest priority - events are immovable
   - Other calendars automatically adapt around family time
   - Keywords: `family`, `kids`, `home`, `personal`

2. **🏠 Personal Profile** (Priority 2)
   - Can coexist with family events
   - Schedules around family commitments
   - Keywords: `personal`, `self`, `appointment`, `health`

3. **💼 Work Profile** (Priority 3)
   - Fills available free slots only
   - Shows family events as `[BUSY]` blocks
   - Auto-suggests alternatives for conflicts
   - Keywords: `work`, `meeting`, `project`, `deadline`

### Smart Conflict Resolution

When creating work events that conflict with family time:
1. 🔍 **Automatic Detection** - Identifies conflicts with higher priority calendars
2. 📋 **Clear Notification** - Shows exactly what conflicts exist
3. 💡 **Smart Suggestions** - Offers 3 alternative times automatically
4. ✏️ **Custom Options** - Allows manual time entry
5. 🚨 **Override Available** - Emergency override for critical situations

## 🤖 AI Integration

### Multi-Provider LLM Support
```bash
# List available models
pamodels list

# Switch providers
pamodel-openai    # Use OpenAI GPT models
pamodel-gemini    # Use Google Gemini
pamodel-claude    # Use Anthropic Claude
pamodel-router    # Use OpenRouter (200+ models)
```

### Intelligent Subtask Inference
```bash
# Generate subtasks for calendar events and TODOs
pasubtasks today
```

The AI analyzes your tasks and automatically generates:
- **Preparation steps** (research, gather materials)
- **Execution subtasks** (with realistic time estimates)
- **Follow-up actions** (cleanup, documentation)
- **Context awareness** (location, energy level, dependencies)

## 📱 Command Reference

### Profile Management
```bash
# View current profile
pacal-current

# List all profiles
pacal-list

# Switch profiles
pa-family / pa-personal / pa-work

# Profile context (for scripts)
pacal-context
```

### Activity Management
```bash
# Quick activity listing
palist today / tomorrow / week / month

# Full system update
pagent today / week

# Create tasks
pacreate --interactive
pacreate --title "Meeting" --type WORK --when "tomorrow 15:00"

# Manage existing items
pamanage edit T1    # Edit TODO item #1
pamanage complete T2 # Complete TODO item #2
padelete E1         # Delete calendar event #1
```

### AI & Analysis
```bash
# Subtask inference
pasubtasks today

# Model management
pamodels
pamodel-list
```

## 🔧 Configuration

### Environment Variables
```bash
# Google Calendar (required)
GOOGLE_CALENDAR_CREDENTIALS_PATH=~/personalAgent/config/credentials.json

# AI Providers (optional)
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
ANTHROPIC_API_KEY=your_claude_key
OPENROUTER_API_KEY=your_openrouter_key

# Default LLM settings
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
```

### Profile Customization
Edit `config/calendar_profiles.json` to customize:
- Calendar mappings
- Priority rules
- Conflict resolution behavior
- Display preferences
- Keyword filters

## 🚦 Current Status

### ✅ **Production Ready**
- ✅ Multi-calendar Google Calendar integration
- ✅ Priority-based profile system
- ✅ Conflict detection and resolution
- ✅ AI-powered subtask inference
- ✅ Multi-provider LLM support (OpenAI, Gemini, Claude, OpenRouter)
- ✅ Profile-aware task creation and management
- ✅ Quick activity listing and overview
- ✅ Comprehensive alias system
- ✅ Terminal integration ready

### 🔄 **In Development**
- 🔄 Terminal prompt integration (oh-my-zsh themes)
- 🔄 Advanced calendar synchronization
- 🔄 Web-based dashboard
- 🔄 Mobile companion app

### 📋 **Upcoming Features**
- 📋 GUI Desktop Application
- 📋 Real-time calendar synchronization
- 📋 Advanced AI scheduling optimization
- 📋 Team collaboration features
- 📋 Integration with external productivity tools
- 📋 Voice interface integration
- 📋 Smart notification system

## 🎨 Future UI Vision

### Desktop Application (Planned)
- **Modern React/Electron Interface**
- **Drag-and-drop calendar management**
- **Real-time conflict visualization**
- **AI-powered scheduling assistant**
- **Multi-calendar timeline view**
- **Smart notification center**

### Mobile App (Planned)
- **Quick task capture**
- **Voice-to-calendar integration**
- **Location-aware scheduling**
- **Offline capability**
- **Push notifications for conflicts**

## 🤝 Contributing

We welcome contributions! This project is designed to be:
- **Modular**: Easy to extend with new features
- **Well-documented**: Clear code structure and documentation
- **Test-friendly**: Comprehensive test coverage
- **AI-first**: Built for intelligent automation

### Development Setup
```bash
# Clone and setup
git clone https://github.com/personalagent/personalagent.git
cd personalagent

# Development environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Test profile system
./bin/pa-profiles list
```

### Areas for Contribution
- 🎨 **UI/UX Design** - Desktop and mobile interfaces
- 🧠 **AI Enhancement** - Better scheduling algorithms
- 📱 **Mobile Development** - React Native app
- 🔧 **Integrations** - Other calendar systems, productivity tools
- 📚 **Documentation** - Tutorials, guides, examples
- 🧪 **Testing** - Unit tests, integration tests

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Calendar API** for robust calendar integration
- **OpenAI, Anthropic, Google** for AI/LLM capabilities
- **Open Source Community** for inspiration and tools

---

**PersonalAgent** - *Where AI meets intentional living* 🤖✨
