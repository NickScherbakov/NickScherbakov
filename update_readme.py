#!/usr/bin/env python3
"""
Script to update README.md with a random daily tip/advice.
Updates content between <!-- START_DAILY_TIP --> and <!-- END_DAILY_TIP --> markers.
"""

import random
import re
from pathlib import Path


# List of tips related to programming, IT, and personal productivity
TIPS = [
    "The code you don't have to write is the best code. Always look for ready-made solutions before writing your own.",
    "Commit often with clear messages. Your future self will thank you.",
    "Refactoring is not a waste of time, it's an investment in your project's future.",
    "Learn one new tool or technology every month. Continuous learning is the key to growth.",
    "Document code for people, not for computers. Clarity is more important than brevity.",
    "Test your code. A bug found during development costs 10 times less than in production.",
    "Take breaks. The best solutions often come when you're not staring at the monitor.",
    "Code review is not criticism, but an opportunity to learn something new from colleagues.",
    "Automate routine tasks. If you do something more than twice — write a script.",
    "Security is not an option, it's a necessity. Never commit secrets and API keys to a repository.",
]

# Markers to identify the section in README.md
START_MARKER = "<!-- START_DAILY_TIP -->"
END_MARKER = "<!-- END_DAILY_TIP -->"


def get_random_tip():
    """Select and format a random tip."""
    tip = random.choice(TIPS)
    return f"\n> 💡 **Tip of the Day:** {tip}\n"


def update_readme(readme_path):
    """
    Update README.md file with a new random tip.
    
    Args:
        readme_path: Path to the README.md file
        
    Returns:
        bool: True if file was updated, False otherwise
    """
    try:
        # Read the current README content
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if markers exist
        if START_MARKER not in content or END_MARKER not in content:
            print(f"Error: Markers not found in {readme_path}")
            print(f"Please add {START_MARKER} and {END_MARKER} to your README.md")
            return False
        
        # Get a random tip
        new_tip = get_random_tip()
        
        # Replace content between markers
        pattern = f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}"
        replacement = f"{START_MARKER}{new_tip}{END_MARKER}"
        
        updated_content = re.sub(
            pattern,
            replacement,
            content,
            flags=re.DOTALL
        )
        
        # Check if content actually changed
        if updated_content == content:
            print("Content is already up to date")
            return False
        
        # Write updated content back to file
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ Successfully updated {readme_path}")
        print(f"New tip: {new_tip.strip()}")
        return True
        
    except FileNotFoundError:
        print(f"Error: {readme_path} not found")
        return False
    except Exception as e:
        print(f"Error updating README: {e}")
        return False


def main():
    """Main function to run the update."""
    readme_path = Path(__file__).parent / "README.md"
    
    print("🔄 Starting README update...")
    success = update_readme(readme_path)
    
    if success:
        print("✨ Update completed successfully!")
    else:
        print("⚠️  Update failed or no changes needed")


if __name__ == "__main__":
    main()
