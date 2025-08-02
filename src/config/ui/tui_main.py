#!/usr/bin/env python3
"""
PersonalAgent Configuration Client - Main TUI Interface
======================================================

Interactive terminal-based configuration manager for PersonalAgent.
Provides a user-friendly interface for managing profiles, context, and settings.
"""

import os
import sys
from typing import Dict, Any, List, Optional

# Rich imports for beautiful CLI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.layout import Layout
    from rich.text import Text
    from rich.columns import Columns
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class ConfigurationTUI:
    """Terminal User Interface for PersonalAgent configuration"""
    
    def __init__(self):
        """Initialize the configuration TUI"""
        self.console = Console() if RICH_AVAILABLE else None
        
        # Check if running in interactive mode
        self.is_interactive = sys.stdin.isatty() and sys.stdout.isatty()
        
        # Initialize configuration manager
        from src.config.config_manager import ConfigManager
        self.config_manager = ConfigManager()
        
        self.running = True
    
    def print(self, *args, **kwargs):
        """Print with rich formatting if available, fallback to regular print"""
        if self.console:
            self.console.print(*args, **kwargs)
        else:
            print(*args, **kwargs)
    
    def safe_input(self, prompt="Press Enter to continue"):
        """Safe input that handles EOF and keyboard interrupts"""
        if not self.is_interactive:
            return ""  # Skip input in non-interactive mode
        
        try:
            if RICH_AVAILABLE:
                return Prompt.ask(prompt, default="")
            else:
                return input(f"{prompt}: ")
        except (EOFError, KeyboardInterrupt):
            return ""  # Return empty string for non-interactive environments
    
    def show_banner(self):
        """Display welcome banner"""
        if RICH_AVAILABLE:
            banner = Panel.fit(
                "[bold blue]PersonalAgent Configuration Manager[/bold blue]\n"
                "[dim]Priority-based calendar management setup[/dim]",
                border_style="blue"
            )
            self.console.print(banner)
        else:
            print("=" * 50)
            print("PersonalAgent Configuration Manager")
            print("Priority-based calendar management setup")
            print("=" * 50)
    
    def show_main_menu(self) -> str:
        """Display main menu and get user choice"""
        menu_options = {
            "1": "📅 Profile Management",
            "2": "👤 Personal Context",
            "3": "🔒 Security & Credentials",
            "4": "💾 Backup & Restore",
            "5": "⚙️  Advanced Settings",
            "6": "📊 Configuration Status",
            "7": "🎯 Setup Wizard",
            "8": "❓ Help",
            "q": "🚪 Quit"
        }
        
        if RICH_AVAILABLE:
            # Create a beautiful menu table
            table = Table(title="Main Menu", box=box.ROUNDED)
            table.add_column("Option", style="cyan", width=8)
            table.add_column("Description", style="white")
            
            for key, description in menu_options.items():
                table.add_row(key, description)
            
            self.console.print(table)
            choice = Prompt.ask("\nSelect an option", choices=list(menu_options.keys()))
        else:
            print("\nMain Menu:")
            for key, description in menu_options.items():
                print(f"  {key}: {description}")
            
            choice = input("\nSelect an option: ").strip()
            if choice not in menu_options:
                print("Invalid choice. Please try again.")
                return self.show_main_menu()
        
        return choice
    
    def show_profile_menu(self):
        """Profile management submenu"""
        while True:
            if RICH_AVAILABLE:
                self.console.print("\n[bold]📅 Profile Management[/bold]")
            else:
                print("\n📅 Profile Management")
            
            profiles = self.config_manager.profiles.list_profiles()
            
            # Display current profiles
            if profiles:
                if RICH_AVAILABLE:
                    table = Table(title="Current Profiles", box=box.SIMPLE)
                    table.add_column("Priority", style="cyan", width=8)
                    table.add_column("Name", style="green")
                    table.add_column("Description", style="white")
                    table.add_column("Calendars", style="yellow", width=10)
                    table.add_column("Current", style="red", width=8)
                    
                    for profile in profiles:
                        current_marker = "✓" if profile['is_current'] else ""
                        table.add_row(
                            str(profile['priority']),
                            profile['name'],
                            profile['description'][:50] + "..." if len(profile['description']) > 50 else profile['description'],
                            str(profile['calendar_count']),
                            current_marker
                        )
                    
                    self.console.print(table)
                else:
                    print("\nCurrent Profiles:")
                    for profile in profiles:
                        current = " (CURRENT)" if profile['is_current'] else ""
                        print(f"  {profile['priority']}. {profile['name']}{current}")
                        print(f"     {profile['description']}")
                        print(f"     Calendars: {profile['calendar_count']}")
                        print()
            
            # Profile menu options
            options = {
                "1": "List all profiles",
                "2": "Create new profile",
                "3": "Edit profile",
                "4": "Delete profile",
                "5": "Set current profile",
                "6": "Add calendar to profile",
                "7": "Remove calendar from profile",
                "b": "Back to main menu"
            }
            
            if RICH_AVAILABLE:
                choice = Prompt.ask("\nProfile action", choices=list(options.keys()))
            else:
                print("\nOptions:")
                for key, desc in options.items():
                    print(f"  {key}: {desc}")
                choice = input("Choose action: ").strip()
            
            if choice == "b":
                break
            elif choice == "1":
                self.list_profiles_detailed()
            elif choice == "2":
                self.create_profile_wizard()
            elif choice == "3":
                self.edit_profile_wizard()
            elif choice == "4":
                self.delete_profile_wizard()
            elif choice == "5":
                self.set_current_profile_wizard()
            elif choice == "6":
                self.add_calendar_wizard()
            elif choice == "7":
                self.remove_calendar_wizard()
    
    def list_profiles_detailed(self):
        """Show detailed profile information"""
        profiles = self.config_manager.profiles.list_profiles()
        
        for profile in profiles:
            detailed = self.config_manager.profiles.get_profile(profile['id'])
            
            if RICH_AVAILABLE:
                # Create a panel for each profile
                content = f"[bold]Priority:[/bold] {detailed['priority']}\n"
                content += f"[bold]Description:[/bold] {detailed['description']}\n"
                content += f"[bold]Calendars:[/bold] {len(detailed.get('calendars', []))}\n"
                
                if detailed.get('calendars'):
                    content += "[bold]Calendar Details:[/bold]\n"
                    for cal in detailed['calendars']:
                        content += f"  • {cal['name']} ({cal['id'][:20]}...)\n"
                
                content += f"[bold]Conflict Resolution:[/bold]\n"
                cr = detailed.get('conflict_resolution', {})
                content += f"  • Blocks others: {cr.get('blocks_others', False)}\n"
                content += f"  • Can be moved: {cr.get('can_be_moved', True)}\n"
                content += f"  • Auto suggest: {cr.get('auto_suggest_alternatives', True)}\n"
                
                panel = Panel(content, title=f"Profile: {profile['name']}", border_style="green")
                self.console.print(panel)
            else:
                print(f"\nProfile: {profile['name']}")
                print(f"  Priority: {detailed['priority']}")
                print(f"  Description: {detailed['description']}")
                print(f"  Calendars: {len(detailed.get('calendars', []))}")
                if detailed.get('calendars'):
                    for cal in detailed['calendars']:
                        print(f"    - {cal['name']}")
        
        self.safe_input("\nPress Enter to continue")
    
    def create_profile_wizard(self):
        """Wizard for creating a new profile"""
        if RICH_AVAILABLE:
            self.console.print("\n[bold]🎯 Create New Profile[/bold]")
        else:
            print("\n🎯 Create New Profile")
        
        # Get profile details
        if RICH_AVAILABLE:
            profile_id = Prompt.ask("Profile ID (lowercase, no spaces)")
            name = Prompt.ask("Profile name")
            description = Prompt.ask("Description")
            priority = IntPrompt.ask("Priority (1=highest)", default=3)
        else:
            profile_id = input("Profile ID (lowercase, no spaces): ").strip()
            name = input("Profile name: ").strip()
            description = input("Description: ").strip()
            try:
                priority = int(input("Priority (1=highest, default=3): ") or "3")
            except ValueError:
                priority = 3
        
        # Conflict resolution settings
        if RICH_AVAILABLE:
            blocks_others = Confirm.ask("Should this profile block other events?", default=False)
            can_be_moved = Confirm.ask("Can events in this profile be moved?", default=True)
            auto_suggest = Confirm.ask("Auto-suggest alternative times?", default=True)
        else:
            blocks_others = input("Block other events? (y/n, default=n): ").lower().startswith('y')
            can_be_moved = not input("Can events be moved? (y/n, default=y): ").lower().startswith('n')
            auto_suggest = not input("Auto-suggest alternatives? (y/n, default=y): ").lower().startswith('n')
        
        # Create profile data
        profile_data = {
            "name": name,
            "description": description,
            "priority": priority,
            "calendars": [],
            "conflict_resolution": {
                "blocks_others": blocks_others,
                "can_be_moved": can_be_moved,
                "auto_suggest_alternatives": auto_suggest
            },
            "display_settings": {
                "show_as_busy": True,
                "filter_keywords": [profile_id.lower()]
            }
        }
        
        # Create the profile
        if self.config_manager.profiles.create_profile(profile_id, profile_data):
            self.print(f"✅ Profile '{name}' created successfully!")
        else:
            self.print("❌ Failed to create profile")
        
        self.safe_input("\nPress Enter to continue")
    
    def show_status_overview(self):
        """Show comprehensive configuration status"""
        status = self.config_manager.get_status()
        validation = self.config_manager.validate_config()
        
        if RICH_AVAILABLE:
            # Create status panels
            layout = Layout()
            
            # Configuration overview
            config_content = f"[bold]Configuration Directory:[/bold] {status['config_dir']}\n\n"
            config_content += f"[bold]Profiles:[/bold]\n"
            config_content += f"  • Total: {status['profiles']['count']}\n"
            config_content += f"  • Current: {status['profiles']['current']}\n"
            config_content += f"  • Available: {', '.join(status['profiles']['available'])}\n\n"
            config_content += f"[bold]Context:[/bold]\n"
            config_content += f"  • Location set: {'✓' if status['context']['location_set'] else '✗'}\n"
            config_content += f"  • Preferences set: {'✓' if status['context']['preferences_set'] else '✗'}\n"
            config_content += f"  • Resources set: {'✓' if status['context']['resources_set'] else '✗'}\n"
            
            config_panel = Panel(config_content, title="Configuration Status", border_style="blue")
            
            # Validation status
            validation_content = f"[bold]Overall Status:[/bold] {'✅ Valid' if validation['valid'] else '❌ Invalid'}\n\n"
            
            if validation['errors']:
                validation_content += "[bold red]Errors:[/bold red]\n"
                for error in validation['errors']:
                    validation_content += f"  • {error}\n"
                validation_content += "\n"
            
            if validation['warnings']:
                validation_content += "[bold yellow]Warnings:[/bold yellow]\n"
                for warning in validation['warnings']:
                    validation_content += f"  • {warning}\n"
            
            if not validation['errors'] and not validation['warnings']:
                validation_content += "[green]No issues found![/green]"
            
            validation_panel = Panel(validation_content, title="Validation Status", border_style="green" if validation['valid'] else "red")
            
            self.console.print(Columns([config_panel, validation_panel]))
        else:
            print("\n📊 Configuration Status:")
            print(f"  Directory: {status['config_dir']}")
            print(f"  Profiles: {status['profiles']['count']} (current: {status['profiles']['current']})")
            print(f"  Context configured: {status['context']['location_set']}")
            print(f"  Valid: {'Yes' if validation['valid'] else 'No'}")
            
            if validation['errors']:
                print("\nErrors:")
                for error in validation['errors']:
                    print(f"  - {error}")
            
            if validation['warnings']:
                print("\nWarnings:")
                for warning in validation['warnings']:
                    print(f"  - {warning}")
        
        self.safe_input("\nPress Enter to continue")
    
    def run(self):
        """Main application loop"""
        if not self.is_interactive:
            self.print("❌ Interactive mode requires a terminal (TTY)")
            self.print("Use command-line arguments for non-interactive mode:")
            self.print("  pa-config --status    # Show status")
            self.print("  pa-config --validate  # Validate config")
            self.print("  pa-config --help      # Show all options")
            return
        
        if not RICH_AVAILABLE:
            print("Note: Rich library not found. Using basic text interface.")
            print("Install with: pip install rich")
            print()
        
        self.show_banner()
        
        while self.running:
            try:
                choice = self.show_main_menu()
                
                if choice == "q":
                    self.running = False
                elif choice == "1":
                    self.show_profile_menu()
                elif choice == "6":
                    self.show_status_overview()
                else:
                    self.print(f"Feature '{choice}' coming soon!")
                    self.safe_input("Press Enter to continue")
            
            except KeyboardInterrupt:
                self.print("\n\n👋 Goodbye!")
                self.running = False
            except EOFError:
                # Handle non-interactive environments
                self.running = False
            except Exception as e:
                self.print(f"❌ Error: {e}")
                self.safe_input("Press Enter to continue")

def main():
    """Main entry point for configuration client"""
    app = ConfigurationTUI()
    app.run()

if __name__ == "__main__":
    main()
