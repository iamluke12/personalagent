#!/usr/bin/env python3
"""
Setup script to configure personalAgent aliases in .zshrc
"""

import os
import subprocess

def setup_aliases():
    """Setup personalAgent aliases in .zshrc"""
    home_dir = os.path.expanduser("~")
    zshrc_path = os.path.join(home_dir, ".zshrc")
    aliases_path = os.path.join(home_dir, "personalAgent", "zshrc_aliases.txt")
    
    print("🚀 PERSONAL AGENT SETUP")
    print("=" * 40)
    
    # Check if aliases file exists
    if not os.path.exists(aliases_path):
        print(f"❌ Aliases file not found: {aliases_path}")
        return False
    
    # Check if .zshrc exists
    if not os.path.exists(zshrc_path):
        print(f"⚠️  .zshrc not found at {zshrc_path}")
        print("Creating .zshrc file...")
        with open(zshrc_path, 'w') as f:
            f.write("# Personal zsh configuration\n\n")
    
    # Check if already sourced
    with open(zshrc_path, 'r') as f:
        content = f.read()
    
    source_line = f"source {aliases_path}"
    
    if source_line in content:
        print("✅ personalAgent aliases already configured in .zshrc")
        print(f"📁 Sourcing: {aliases_path}")
    else:
        # Add source line
        with open(zshrc_path, 'a') as f:
            f.write(f"\n# Personal Agent aliases\n")
            f.write(f"{source_line}\n")
        
        print("✅ Added personalAgent aliases to .zshrc")
        print(f"📁 Added: {source_line}")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Reload your shell: source ~/.zshrc")
    print("2. Test with: pahelp")
    print("3. Quick start: activities")
    
    print("\n💡 QUICK COMMANDS TO TRY:")
    print("  pahelp                # Complete command reference")
    print("  activities            # See upcoming activities")
    print("  manage                # Interactive TODO manager")
    print("  consciousness         # Full system status")
    
    return True

def main():
    """Main setup function"""
    try:
        setup_aliases()
        print(f"\n🌟 Setup complete! Run 'source ~/.zshrc' to activate aliases.")
    except Exception as e:
        print(f"❌ Setup failed: {e}")

if __name__ == "__main__":
    main()
