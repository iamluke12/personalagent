#!/usr/bin/env python3
"""
Test Profile System for personalAgent
Verify profile management and calendar switching functionality
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from profileManager import CalendarProfileManager

def test_profile_system():
    print("🧪 TESTING CALENDAR PROFILE SYSTEM")
    print("=" * 50)
    
    manager = CalendarProfileManager()
    
    # Test 1: Load profiles
    print("\n1️⃣ Testing profile loading...")
    profiles = manager.profiles.get("profiles", {})
    print(f"   ✅ Loaded {len(profiles)} profiles")
    
    # Test 2: List profiles
    print("\n2️⃣ Testing profile listing...")
    manager.list_profiles()
    
    # Test 3: Get current profile
    print("\n3️⃣ Testing current profile...")
    current = manager.get_current_profile()
    print(f"   📍 Current profile: {current}")
    
    # Test 4: Get calendar for profile
    print("\n4️⃣ Testing calendar retrieval...")
    primary_cal = manager.get_primary_calendar_id()
    print(f"   📅 Primary calendar: {primary_cal}")
    
    # Test 5: Export context
    print("\n5️⃣ Testing context export...")
    context = manager.export_current_context()
    print(f"   📋 Context keys: {list(context.keys())}")
    
    # Test 6: Auto-detection
    print("\n6️⃣ Testing auto-detection...")
    test_cases = [
        ("Team meeting with project updates", "work"),
        ("Family dinner at grandma's house", "family"),
        ("Doctor appointment for checkup", "personal"),
        ("Kids birthday party planning", "family")
    ]
    
    for title, expected in test_cases:
        detected = manager.auto_detect_profile(title)
        status = "✅" if detected == expected else "❌"
        print(f"   {status} '{title}' -> {detected} (expected: {expected})")
    
    print("\n🎯 Profile system test complete!")

if __name__ == "__main__":
    test_profile_system()
