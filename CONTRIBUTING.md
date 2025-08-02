# Contributing to PersonalAgent

We're excited that you're interested in contributing to PersonalAgent! This document provides guidelines and information for contributors.

## 🎯 **Project Vision**

PersonalAgent is designed to be an intelligent, priority-based calendar management system that respects life priorities (Family > Personal > Work) while leveraging AI to enhance productivity and prevent conflicts.

## 🤝 **How to Contribute**

### 🐛 **Reporting Bugs**

1. **Check existing issues** first to avoid duplicates
2. **Use the bug report template** when creating new issues
3. **Include relevant details**:
   - Operating system and version
   - Python version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages or logs

### 💡 **Suggesting Enhancements**

1. **Search existing issues** for similar suggestions
2. **Describe the problem** you're trying to solve
3. **Explain your proposed solution** with examples
4. **Consider the project scope** - does this align with our vision?

### 🔧 **Code Contributions**

#### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/personalagent.git
cd personalagent

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

#### Code Standards

- **Python Style**: Follow PEP 8, use Black for formatting
- **Type Hints**: Use type hints for function signatures
- **Documentation**: Include docstrings for all public functions
- **Testing**: Write tests for new features and bug fixes

#### Architecture Guidelines

**Module Organization**:
```
src/
├── core/      # Core system functionality (data fetching, main loops)
├── calendar/  # Calendar management and profile system
├── ai/        # LLM integration and AI-powered features
└── utils/     # Utility functions and helpers
```

**Key Design Principles**:
- **Modularity**: Each module should have a clear, single responsibility
- **Profile Awareness**: All calendar operations should respect the current profile
- **AI Integration**: LLM features should gracefully degrade if APIs are unavailable
- **User Experience**: Commands should be fast, intuitive, and provide helpful feedback

### 🧪 **Testing**

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Run specific test file
python -m pytest tests/test_profiles.py

# Test the profile system manually
./bin/pa-profiles list
```

**Testing Guidelines**:
- Write unit tests for individual functions
- Write integration tests for complex workflows
- Test error conditions and edge cases
- Mock external APIs in tests

### 📚 **Documentation**

- **Code Comments**: Explain complex logic, not obvious code
- **Docstrings**: Use Google-style docstrings
- **README Updates**: Update README.md if you add new features
- **Changelog**: Add entries to CHANGELOG.md for notable changes

## 🏗️ **Project Structure Deep Dive**

### Core Components

#### 1. Profile System (`src/calendar/profileManager.py`)
- Manages calendar profiles and priority hierarchy
- Handles conflict detection and resolution
- Provides context switching for other modules

#### 2. Task Management (`src/calendar/`)
- **createTask.py**: Profile-aware task creation with conflict detection
- **listActivities.py**: Profile-filtered activity listing
- **manageActivities.py**: Activity editing, completion, deletion

#### 3. AI Integration (`src/ai/`)
- **inferSubtask.py**: LLM-powered subtask generation
- **setModel.py**: Multi-provider LLM management

#### 4. Core System (`src/core/`)
- **getLatest.sh**: Main data fetching orchestrator
- **fetchGregorian.py**: Calendar data retrieval
- **fetchTodos.py**: TODO management

### Configuration System

- **calendar_profiles.json**: Profile definitions and calendar mappings
- **personal_context.json**: User preferences and patterns
- Environment variables for API keys and global settings

## 🎨 **Areas for Contribution**

### 🚀 **High Priority**

1. **Desktop GUI Application**
   - React/Electron interface
   - Drag-and-drop calendar management
   - Real-time conflict visualization
   - AI scheduling assistant

2. **Mobile App Development**
   - React Native iOS/Android app
   - Voice-to-calendar integration
   - Location-aware scheduling
   - Offline synchronization

3. **Advanced AI Features**
   - Better scheduling algorithms
   - Energy-based optimization
   - Predictive conflict detection
   - Integration with more LLM providers

### 🔧 **Medium Priority**

4. **Integration Enhancements**
   - Other calendar systems (Outlook, Apple Calendar)
   - Productivity tools (Notion, Todoist, Asana)
   - Time tracking applications
   - Communication platforms (Slack, Discord)

5. **Performance Optimization**
   - Faster data synchronization
   - Better caching strategies
   - Reduced API calls
   - Improved startup time

### 📝 **Lower Priority**

6. **Documentation & Tutorials**
   - Video tutorials
   - Setup guides for different platforms
   - Advanced configuration examples
   - API documentation

7. **Testing & Quality**
   - Increase test coverage
   - Performance benchmarks
   - Cross-platform testing
   - Continuous integration improvements

## 🔄 **Pull Request Process**

1. **Create a feature branch** from main
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Write or update tests** for your changes

4. **Update documentation** if needed

5. **Test your changes** thoroughly
   ```bash
   python -m pytest
   ./bin/pa-profiles list  # Test manually
   ```

6. **Commit with clear messages**
   ```bash
   git commit -m "feat: add drag-and-drop calendar interface
   
   - Implement React component for calendar view
   - Add drag-and-drop event management
   - Include conflict visualization
   
   Closes #123"
   ```

7. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Describe your changes** in the PR description:
   - What does this change do?
   - Why is this change needed?
   - How has it been tested?
   - Any breaking changes?

## 🎯 **Contribution Guidelines**

### ✅ **Do**
- Follow the existing code style and patterns
- Write clear, descriptive commit messages
- Include tests for new features
- Update documentation when appropriate
- Be respectful and constructive in discussions
- Ask questions if you're unsure about anything

### ❌ **Don't**
- Break existing functionality without good reason
- Add dependencies without discussion
- Make large architectural changes without prior discussion
- Ignore test failures
- Submit untested code

## 🏷️ **Issue Labels**

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `priority-high`: Should be addressed soon
- `ai-feature`: Related to AI/LLM functionality
- `ui-ux`: User interface or experience improvements

## 💬 **Getting Help**

- **Discussions**: Use GitHub Discussions for questions and ideas
- **Issues**: Create issues for bugs and specific feature requests
- **Email**: Contact maintainers for private discussions

## 🎉 **Recognition**

Contributors will be recognized in:
- README.md contributor section
- CHANGELOG.md for significant contributions
- GitHub releases and project announcements

Thank you for contributing to PersonalAgent! Together, we're building a tool that helps people manage their time with intention and intelligence. 🚀
