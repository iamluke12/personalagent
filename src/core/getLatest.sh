#!/bin/bash
# ~/personalAgent/scripts/getLatest.sh
# Main orchestrator for Personal Agent consciousness management

TIMEFRAME=${1:-"today"}  # Default to today
SCRIPT_DIR="$HOME/personalAgent/scripts"
VENV_DIR="$HOME/personalAgent/venv"

# Colors for dimensional output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌌 Fetching consciousness schedule for: ${TIMEFRAME}${NC}"

# Activate virtual environment
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
    echo -e "${GREEN}✨ Virtual environment activated${NC}"
else
    echo -e "${RED}⚠️  Virtual environment not found at $VENV_DIR${NC}"
    echo -e "${YELLOW}💡 Run: python3 -m venv ~/personalAgent/venv${NC}"
fi

# Check if we're in the right directory
cd "$HOME/personalAgent" || {
    echo -e "${RED}🚫 Cannot find personalAgent directory${NC}"
    exit 1
}

echo -e "${BLUE}📍 Working from: $(pwd)${NC}"

# Show current calendar context
echo -e "\n${YELLOW}📅 Current Calendar Context:${NC}"
if [ -f "$SCRIPT_DIR/calendarSwitcher.py" ]; then
    python3 "$SCRIPT_DIR/calendarSwitcher.py" current
else
    echo -e "${BLUE}📧 Default calendar active${NC}"
fi

# 1. Fetch Gregorian calendar data
echo -e "\n${YELLOW}📅 Fetching Gregorian calendar matrix...${NC}"
if [ -f "$SCRIPT_DIR/fetchGregorian.py" ]; then
    python3 "$SCRIPT_DIR/fetchGregorian.py" "$TIMEFRAME"
else
    echo -e "${RED}🚫 fetchGregorian.py not found${NC}"
fi

# 2. Calculate Tzolkin/13 Moon calendar data
echo -e "\n${YELLOW}🌙 Calculating sacred Tzolkin position...${NC}"
if [ -f "$SCRIPT_DIR/calculateTzolkin.py" ]; then
    python3 "$SCRIPT_DIR/calculateTzolkin.py" "$TIMEFRAME"
else
    echo -e "${YELLOW}⚠️  Tzolkin calculator not yet created${NC}"
    echo -e "${BLUE}💡 Next: Build the 13 Moon calendar system${NC}"
fi

# 3. Fetch TODO lists (placeholder for now)
echo -e "\n${YELLOW}📝 Fetching TODO consciousness...${NC}"
if [ -f "$SCRIPT_DIR/fetchTodos.py" ]; then
    python3 "$SCRIPT_DIR/fetchTodos.py" "$TIMEFRAME"
else
    echo -e "${YELLOW}⚠️  TODO fetcher not yet created${NC}"
    echo -e "${BLUE}💡 Next: Connect to your TODO system${NC}"
fi

# 4. Infer subtasks based on context
echo -e "\n${YELLOW}🧠 Inferring dimensional subtasks...${NC}"
if [ -f "$SCRIPT_DIR/inferSubtask.py" ]; then
    python3 "$SCRIPT_DIR/inferSubtask.py" "$TIMEFRAME"
else
    echo -e "${YELLOW}⚠️  Subtask inference not yet created${NC}"
    echo -e "${BLUE}💡 Next: Build the context-aware task breakdown${NC}"
fi

echo -e "\n${GREEN}✨ Consciousness scan complete. Reality matrix updated.${NC}"
echo -e "${BLUE}🌟 Current dimensional alignment: $(date)${NC}"