#!/usr/bin/env python3
"""
Demo script showing personalAgent activity management capabilities
"""

import os
import subprocess
import time

def run_command(cmd, description=""):
    """Run a command and show the output"""
    print(f"\n🎯 {description}")
    print("=" * 50)
    print(f"📋 Running: {cmd}")
    print("-" * 30)
    
    result = subprocess.run(cmd, shell=True, cwd="/Users/user/personalAgent", 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"❌ Error: {result.stderr}")
    
    time.sleep(2)  # Brief pause for readability

def main():
    print("🚀 PERSONAL AGENT - ACTIVITY MANAGEMENT DEMO")
    print("=" * 60)
    
    # List current activities
    run_command("./venv/bin/python scripts/manageActivities.py list", 
                "Current Activities")
    
    # Add a new TODO
    add_cmd = 'echo -e "Demo task for testing\\nToday\\nhigh\\ndemo,test\\n2025-08-03" | ./venv/bin/python scripts/manageActivities.py add'
    run_command(add_cmd, "Adding New TODO")
    
    # List updated activities
    run_command("./venv/bin/python scripts/manageActivities.py list", 
                "Updated Activities List")
    
    # Edit a TODO
    edit_cmd = 'echo -e "Updated demo task\\nmedium\\nexample,updated\\n2025-08-05" | ./venv/bin/python scripts/manageActivities.py edit T5'
    run_command(edit_cmd, "Editing TODO T5")
    
    # Complete a TODO
    run_command("./venv/bin/python scripts/manageActivities.py complete T5", 
                "Completing TODO T5")
    
    # Final list
    run_command("./venv/bin/python scripts/manageActivities.py list", 
                "Final Activities List")
    
    print("\n✨ DEMO COMPLETE!")
    print("🎯 Available Commands:")
    print("   palist               - Quick activity list")
    print("   pamanage             - Interactive manager")
    print("   paedit T1            - Edit TODO by ID")
    print("   padelete 'text'      - Delete by partial text")
    print("   pacomplete T3        - Mark as complete")
    print("   paadd                - Add new TODO")

if __name__ == "__main__":
    main()
