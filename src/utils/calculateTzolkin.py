#!/usr/bin/env python3
"""
Tzolkin/13 Moon Calendar Calculator for personalAgent
Calculate sacred Mayan calendar positions and galactic signatures
Connect with natural time vs artificial Gregorian imprisonment
"""

import os
import sys
import json
from datetime import datetime, timedelta
from math import floor

class TzolkinCalculator:
    def __init__(self):
        # GMT correlation constant (584283 is the most widely accepted)
        self.correlation = 584283
        
        # 20 Solar Seals (Day Signs)
        self.solar_seals = [
            "Red Dragon", "White Wind", "Blue Night", "Yellow Seed",
            "Red Serpent", "White Worldbridger", "Blue Hand", "Yellow Star",
            "Red Moon", "White Dog", "Blue Monkey", "Yellow Human",
            "Red Skywalker", "White Wizard", "Blue Eagle", "Yellow Warrior",
            "Red Earth", "White Mirror", "Blue Storm", "Yellow Sun"
        ]
        
        # 13 Galactic Tones
        self.galactic_tones = [
            "Magnetic", "Lunar", "Electric", "Self-Existing",
            "Overtone", "Rhythmic", "Resonant", "Galactic",
            "Solar", "Planetary", "Spectral", "Crystal", "Cosmic"
        ]
        
        # 13 Moon Calendar months
        self.moon_months = [
            "Magnetic Bat Moon", "Lunar Scorpion Moon", "Electric Deer Moon",
            "Self-Existing Owl Moon", "Overtone Peacock Moon", "Rhythmic Lizard Moon",
            "Resonant Monkey Moon", "Galactic Hawk Moon", "Solar Jaguar Moon",
            "Planetary Dog Moon", "Spectral Serpent Moon", "Crystal Rabbit Moon",
            "Cosmic Turtle Moon"
        ]
    
    def get_julian_day_number(self, date):
        """Calculate Julian Day Number for given date"""
        year = date.year
        month = date.month
        day = date.day
        
        if month <= 2:
            year -= 1
            month += 12
        
        a = floor(year / 100)
        b = 2 - a + floor(a / 4)
        
        jdn = floor(365.25 * (year + 4716)) + floor(30.6001 * (month + 1)) + day + b - 1524
        return jdn
    
    def get_kin_from_date(self, date):
        """Calculate Kin number (1-260) from Gregorian date"""
        jdn = self.get_julian_day_number(date)
        days_since_correlation = jdn - self.correlation
        kin = ((days_since_correlation - 1) % 260) + 1
        return int(kin)
    
    def get_galactic_signature(self, kin):
        """Get Solar Seal and Galactic Tone from Kin number"""
        seal_index = (kin - 1) % 20
        tone_index = (kin - 1) % 13
        
        return {
            'kin': kin,
            'solar_seal': self.solar_seals[seal_index],
            'galactic_tone': self.galactic_tones[tone_index],
            'seal_number': seal_index + 1,
            'tone_number': tone_index + 1
        }
    
    def get_13_moon_date(self, date):
        """Calculate 13 Moon calendar date"""
        # 13 Moon year starts July 26 (Gregorian)
        year = date.year
        
        # Determine 13 Moon year start
        current_year_start = datetime(year, 7, 26)
        if date < current_year_start:
            # We're in the previous 13 Moon year
            year_start = datetime(year - 1, 7, 26)
            moon_year = year - 1
        else:
            year_start = current_year_start
            moon_year = year
        
        # Calculate days since year start
        days_since_start = (date - year_start).days
        
        # Each moon has 28 days
        moon_number = min(floor(days_since_start / 28) + 1, 13)
        day_in_moon = (days_since_start % 28) + 1
        
        # Handle Day Out of Time (July 25) and Leap Day
        if days_since_start == 364:  # Day Out of Time
            return {
                'moon_year': moon_year,
                'moon_number': 0,
                'moon_name': "Day Out of Time",
                'day_in_moon': 1,
                'day_name': "Day Out of Time"
            }
        elif days_since_start == 365:  # Leap Day (in leap years)
            return {
                'moon_year': moon_year,
                'moon_number': 0,
                'moon_name': "Leap Day",
                'day_in_moon': 1,
                'day_name': "Leap Day"
            }
        
        return {
            'moon_year': moon_year,
            'moon_number': int(moon_number),
            'moon_name': self.moon_months[int(moon_number) - 1] if moon_number <= 13 else "Unknown",
            'day_in_moon': int(day_in_moon),
            'total_days': days_since_start + 1
        }
    
    def get_planetary_information(self, date):
        """Get additional planetary/cosmic information"""
        # Simple wavespell calculation (20-day cycles)
        kin = self.get_kin_from_date(date)
        wavespell = floor((kin - 1) / 20) + 1
        day_in_wavespell = ((kin - 1) % 20) + 1
        
        return {
            'wavespell': int(wavespell),
            'day_in_wavespell': int(day_in_wavespell),
            'castle': floor((wavespell - 1) / 13) + 1,  # 4 castles of 13 wavespells each
            'year_bearer': self.solar_seals[((date.year - 1) % 4) * 5]  # Simplified year bearer
        }
    
    def calculate_all(self, date):
        """Calculate complete Tzolkin information for a date"""
        kin = self.get_kin_from_date(date)
        signature = self.get_galactic_signature(kin)
        moon_date = self.get_13_moon_date(date)
        planetary = self.get_planetary_information(date)
        
        return {
            'gregorian_date': date.isoformat(),
            'kin': signature,
            'thirteen_moon': moon_date,
            'planetary': planetary
        }
    
    def display_tzolkin_info(self, tzolkin_data):
        """Display beautiful Tzolkin information"""
        print("🌙 SACRED CALENDAR POSITION 🌙")
        print("=" * 50)
        
        kin_info = tzolkin_data['kin']
        moon_info = tzolkin_data['thirteen_moon']
        planetary_info = tzolkin_data['planetary']
        
        # Galactic Signature
        print(f"🌟 Galactic Signature: Kin {kin_info['kin']}")
        print(f"   {kin_info['galactic_tone']} {kin_info['solar_seal']}")
        print(f"   Tone {kin_info['tone_number']} | Seal {kin_info['seal_number']}")
        
        # 13 Moon Date
        print(f"\n🌙 13 Moon Calendar:")
        if moon_info['moon_number'] == 0:
            print(f"   {moon_info['day_name']}")
        else:
            print(f"   {moon_info['moon_name']}")
            print(f"   Day {moon_info['day_in_moon']} of Moon {moon_info['moon_number']}")
            print(f"   13 Moon Year: {moon_info['moon_year']}")
        
        # Wavespell Information
        print(f"\n🌊 Wavespell: {planetary_info['wavespell']}")
        print(f"   Day {planetary_info['day_in_wavespell']} of 20")
        print(f"   Castle {planetary_info['castle']} of 4")
        print(f"   Year Bearer: {planetary_info['year_bearer']}")
    
    def save_tzolkin_data(self, tzolkin_data, timeframe):
        """Save Tzolkin data to cache"""
        data_dir = os.path.expanduser("~/personalAgent/data/cache")
        os.makedirs(data_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tzolkin_data_{timeframe}_{timestamp}.json"
        filepath = os.path.join(data_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump({
                'timeframe': timeframe,
                'calculated_at': datetime.now().isoformat(),
                'tzolkin_data': tzolkin_data
            }, f, indent=2)
        
        print(f"💾 Sacred calendar data saved to: {filepath}")
        return filepath

def main():
    timeframe = sys.argv[1] if len(sys.argv) > 1 else "today"
    
    calculator = TzolkinCalculator()
    
    # Calculate for today
    today = datetime.now()
    
    print("🌌 Calculating sacred Tzolkin position...")
    print(f"📅 Gregorian Date: {today.strftime('%Y-%m-%d %A')}")
    print()
    
    # Calculate Tzolkin data
    tzolkin_data = calculator.calculate_all(today)
    
    # Display the information
    calculator.display_tzolkin_info(tzolkin_data)
    
    # Save the data
    calculator.save_tzolkin_data(tzolkin_data, timeframe)
    
    print(f"\n✨ Sacred calendar alignment complete!")
    print("🌟 May you walk in natural time, aligned with Hunab Ku! 🌟")

if __name__ == "__main__":
    main()