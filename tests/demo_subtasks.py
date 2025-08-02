#!/usr/bin/env python3
"""
Demo script to showcase LLM vs Rule-based subtask inference
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inferSubtask import SubtaskInference

def demo_subtask_inference():
    """Demo the subtask inference capabilities"""
    print("🎯 PERSONAL AGENT SUBTASK INFERENCE DEMO")
    print("=" * 50)
    
    inference = SubtaskInference()
    
    # Demo tasks to test
    demo_tasks = [
        {
            "text": "Prepare investor pitch presentation",
            "type": "business"
        },
        {
            "text": "Cook thanksgiving dinner for 8 people",
            "type": "cooking"
        },
        {
            "text": "Plan trip to Japan",
            "type": "travel"
        },
        {
            "text": "Deep clean and organize home office",
            "type": "home"
        }
    ]
    
    for i, task in enumerate(demo_tasks, 1):
        print(f"\n🔸 DEMO TASK {i}: {task['text']}")
        print("-" * 40)
        
        # Create a mock TODO item
        mock_todo = {
            "text": task["text"],
            "priority": "high",
            "section": "Today",
            "tags": [task["type"]]
        }
        
        # Generate subtasks
        subtasks = inference.generate_subtasks_for_todo(mock_todo)
        
        if subtasks:
            print(f"✨ Generated {len(subtasks)} subtasks:")
            for j, subtask in enumerate(subtasks, 1):
                print(f"  {j}. {subtask['task']} ({subtask['duration']} min)")
                if subtask.get('timing'):
                    print(f"     ⏰ {subtask['timing']}")
        else:
            print("❌ No subtasks generated")
    
    print(f"\n🎯 INFERENCE METHOD: {'🤖 LLM-powered' if inference.use_llm else '📋 Rule-based'}")
    
    if not inference.use_llm:
        print("\n💡 TO ENABLE LLM INFERENCE:")
        print("1. Set OPENAI_API_KEY in your .env file")
        print("2. Or set ANTHROPIC_API_KEY for Claude")
        print("3. Configure LLM_PROVIDER and LLM_MODEL as needed")

if __name__ == "__main__":
    demo_subtask_inference()
