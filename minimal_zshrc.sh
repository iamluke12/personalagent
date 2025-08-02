#!/bin/bash
# Minimal zsh configuration for personalAgent development
# Clean, readable terminal output

# Set a simple, minimal prompt
export PS1="%F{blue}[%~]%f $ "

# Basic zsh options for better usability
setopt AUTO_CD
setopt CORRECT
setopt HIST_VERIFY
setopt SHARE_HISTORY
setopt APPEND_HISTORY
setopt HIST_IGNORE_DUPS

# History settings
HISTSIZE=1000
SAVEHIST=1000
HISTFILE=~/.zsh_history

# Basic completion
autoload -U compinit
compinit

# Simple aliases for navigation
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'

# Git aliases
alias gs='git status'
alias gd='git diff'
alias gl='git log --oneline'

echo "🔧 Minimal zsh configuration loaded"
echo "💡 To restore oh-my-zsh, run: source ~/.zshrc.backup"
