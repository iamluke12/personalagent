# Personal Agent

<div align="center">

![PersonalAgent Logo](https://img.shields.io/badge/PersonalAgent-v1.0.0-blue?style=for-the-badge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg?style=for-the-badge)](https://www.python.org/downloads/)
[![Security Audit](https://img.shields.io/badge/Security-Audited-green?style=for-the-badge)](#security)

**Priority-Based Calendar Management with AI-Powered Task Automation**

*Family events take priority. Work adapts to life.*

[Quick Start](#quick-start) •
[Features](#features) •
[Installation](#installation) •
[Documentation](#documentation) •
[Contributing](#contributing)

</div>

---

## 🎯 **What Makes PersonalAgent Different?**

Traditional calendar apps treat all events equally. **PersonalAgent uses a priority hierarchy**:

1. **👨‍👩‍👧‍👦 Family (Priority 1)** - Immovable anchor events
2. **🏠 Personal (Priority 2)** - Important but flexible  
3. **💼 Work (Priority 3)** - Fills available slots, adapts to life

### 🔥 **Key Innovation**
When you're in **Work mode**, family events appear as `[BUSY]` blocks. When conflicts arise, PersonalAgent automatically suggests alternative meeting times that respect your family commitments.

## ✨ **Features**

### 🏆 **Priority-Based Scheduling**
- **Family-First Design**: Family events are sacred, immovable anchors
- **Intelligent Context Switching**: Seamlessly switch between family/personal/work views
- **Conflict Prevention**: Automatic detection with smart alternative suggestions
- **Profile-Aware Creation**: New events respect current profile priority

### 🤖 **AI-Powered Automation**
- **Multi-LLM Support**: OpenAI GPT-4, Google Gemini, Anthropic Claude, OpenRouter (200+ models)
- **Intelligent Subtask Inference**: Automatically breaks down complex tasks
- **Context-Aware Analysis**: AI understands your calendar patterns and preferences
- **Dynamic Model Switching**: Easy switching between AI providers

### 🔒 **Security-First Design**
- **Encrypted Credential Storage**: Military-grade Fernet encryption for API keys
- **Machine-Specific Keys**: PBKDF2 key derivation with hardware fingerprinting
- **Secure Permissions**: Automatic file permission management (600 for sensitive files)
- **Security Audit Tools**: Built-in comprehensive security scanning

### ⚡ **Lightning-Fast CLI**
- **60+ Productivity Aliases**: `pa-family`, `pa-create`, `activities`, `consciousness`
- **Terminal Integration**: oh-my-zsh prompt integration ready
- **Quick Commands**: One-command task creation, activity listing, conflict resolution
- **Cross-Platform**: Works on macOS, Linux, Windows with zsh/bash/fish

## 🚀 **Quick Start**

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/personalagent.git
cd personalagent
./setup.sh

# 2. Set up Google Calendar (one-time)
# Follow the setup wizard to connect your calendars

# 3. Start using immediately
pa-family          # Switch to family profile
pa-list today      # See today's schedule
pa-create          # Create a new task
consciousness      # Quick status overview
```

## 📦 **Installation**

### Prerequisites
- Python 3.8+
- Google Calendar API access
- (Optional) AI API keys for enhanced features

### Automated Setup
```bash
git clone https://github.com/yourusername/personalagent.git
cd personalagent
./setup.sh
```

The setup script will:
- ✅ Create virtual environment and install dependencies
- ✅ Set up secure credential storage
- ✅ Configure shell aliases
- ✅ Run security audit and compatibility tests
- ✅ Guide you through Google Calendar setup

### Manual Installation
See [INSTALLATION.md](docs/INSTALLATION.md) for detailed manual setup instructions.

## 🎮 **Quick Usage Examples**

### Profile Management
```bash
# Switch contexts instantly
pa-family           # Family mode - see all family events
pa-personal         # Personal mode - include personal appointments  
pa-work            # Work mode - family events show as [BUSY]

# Check current profile and conflicts
pa-profiles current
pa-profiles conflicts
```

### Task Creation with AI
```bash
# Create tasks that respect priorities
pa-create "Family dinner at 6pm tomorrow"     # Family priority
pa-create "Doctor appointment next week"      # Personal priority
pa-create "Team meeting Thursday 2pm"         # Work priority (checks for conflicts)

# AI-powered subtask generation
pa-subtasks "Plan birthday party"             # Auto-generates: venue, invites, cake, etc.
```

### Activity Management
```bash
# Quick activity overview
activities                    # Today's schedule
pa-list week                 # Week view
pa-list month               # Month view

# Interactive management
manage                      # Interactive activity manager
pa-edit T1                 # Edit specific task
pa-complete "presentation" # Mark task complete
```

## 🏗️ **Architecture**

PersonalAgent uses a modular architecture designed for extensibility:

```
src/
├── calendar/          # Profile management and calendar integration
│   ├── profileManager.py     # Core profile system
│   ├── createTask.py         # Priority-aware task creation
│   └── listActivities.py     # Profile-filtered activity listing
├── ai/               # Multi-LLM integration
│   ├── setModel.py          # Dynamic model switching
│   └── inferSubtask.py      # AI task breakdown
├── core/             # System core
│   ├── fetchGregorian.py    # Calendar data fetching
│   └── fetchTodos.py        # Task management
└── utils/            # Security and utilities
    ├── secure_credentials.py # Encrypted credential storage
    ├── security_audit.py     # Security validation
    └── cross_platform_test.py # Compatibility testing
```

## 🔒 **Security**

PersonalAgent takes security seriously:

- **🔐 Encrypted Storage**: All API keys stored with Fernet encryption
- **🔑 Secure Key Derivation**: PBKDF2 with machine-specific salts
- **📂 File Permissions**: Automatic secure permissions (600) for sensitive files
- **🛡️ Security Auditing**: Built-in security scanning with scoring
- **🔒 No Plaintext Secrets**: Zero plaintext API keys in code or config

Run security audit: `pa-security` or `python3 src/utils/security_audit.py`

## 🌍 **Compatibility**

Tested and verified on:
- **Operating Systems**: macOS, Linux (Ubuntu, CentOS, Arch), Windows 10/11
- **Python Versions**: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- **Shells**: zsh, bash, fish
- **Terminals**: Terminal.app, iTerm2, GNOME Terminal, Windows Terminal

Run compatibility test: `pa-test-compat` or `python3 src/utils/cross_platform_test.py`

## 📚 **Documentation**

- [📖 User Guide](docs/USER_GUIDE.md) - Complete usage documentation
- [🔧 Installation Guide](docs/INSTALLATION.md) - Detailed setup instructions
- [👨‍💻 API Reference](docs/API_REFERENCE.md) - Developer documentation
- [🔒 Security Guide](docs/SECURITY.md) - Security best practices
- [🤝 Contributing Guide](CONTRIBUTING.md) - How to contribute
- [📋 Changelog](CHANGELOG.md) - Version history and changes

## 🤝 **Contributing**

We welcome contributions! PersonalAgent is designed to be family-first, and we want to make it work for families everywhere.

### Ways to Contribute
- 🐛 **Bug Reports**: Found an issue? [Report it](https://github.com/yourusername/personalagent/issues)
- 💡 **Feature Requests**: Have an idea? [Share it](https://github.com/yourusername/personalagent/issues)
- 📝 **Documentation**: Help improve our docs
- 🔧 **Code Contributions**: Submit pull requests
- 🌍 **Translations**: Help make PersonalAgent multilingual

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 🗺️ **Roadmap**

### v1.1.0 - Desktop GUI (Q3 2025)
- 🖥️ Electron-based desktop application
- 📅 Visual calendar timeline with drag-and-drop
- 🎯 Real-time conflict visualization
- 🤖 AI scheduling assistant dashboard

### v1.2.0 - Mobile App (Q4 2025)
- 📱 React Native iOS/Android application
- 🎤 Voice-to-calendar integration
- 📍 Location-aware scheduling
- 🔔 Smart conflict notifications

### v1.3.0 - Enhanced AI (Q1 2026)
- 🧠 Natural language event creation
- 📊 Predictive scheduling based on patterns
- 🎯 Smart meeting optimization
- 📈 Calendar analytics and insights

## 📊 **Project Stats**

![GitHub stars](https://img.shields.io/github/stars/yourusername/personalagent?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/personalagent?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/personalagent)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/personalagent)

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- Google Calendar API for robust calendar integration
- OpenAI, Anthropic, Google for AI/LLM capabilities
- The open source community for inspiration and tools
- Families everywhere who deserve technology that adapts to their priorities

---

<div align="center">

**Made with ❤️ for families who want technology to serve life, not the other way around.**

[⭐ Star this repo](https://github.com/yourusername/personalagent) • [🐛 Report Bug](https://github.com/yourusername/personalagent/issues) • [💡 Request Feature](https://github.com/yourusername/personalagent/issues)

</div>
