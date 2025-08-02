#!/usr/bin/env python3
"""
Terminal Prompt Integration Helper for personalAgent
Returns current calendar profile for oh-my-zsh prompt integration
"""

import os
import sys
import json

def get_prompt_info():
    """Get minimal profile info for terminal prompt"""
    config_dir = os.path.expanduser("~/personalAgent/config")
    profiles_file = os.path.join(config_dir, "calendar_profiles.json")
    
    if not os.path.exists(profiles_file):
        return ""
    
    try:
        with open(profiles_file, 'r') as f:
            data = json.load(f)
            
        current_profile = data.get("current_profile")
        if not current_profile:
            return ""
        
        # Return short indicator for prompt
        profile_indicators = {
            "family": "👨‍👩‍👧‍👦",
            "personal": "🏠", 
            "work": "💼"
        }
        
        indicator = profile_indicators.get(current_profile, "📅")
        
        # For terminal prompt, keep it minimal
        if len(sys.argv) > 1 and sys.argv[1] == "--short":
            return indicator
        else:
            return f"{indicator}{current_profile}"
            
    except Exception:
        return ""

if __name__ == "__main__":
    print(get_prompt_info(), end="")
