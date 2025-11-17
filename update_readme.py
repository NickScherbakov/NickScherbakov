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
    "Код, который не нужно писать — это лучший код. Всегда ищите готовые решения перед тем, как писать свой.",
    "Делайте коммиты часто и с понятными сообщениями. Ваше будущее 'я' скажет вам спасибо.",
    "Рефакторинг — это не трата времени, это инвестиция в будущее вашего проекта.",
    "Изучайте один новый инструмент или технологию каждый месяц. Постоянное обучение — ключ к росту.",
    "Документируйте код для людей, а не для компьютера. Ясность важнее краткости.",
    "Тестируйте свой код. Баг, найденный во время разработки, стоит в 10 раз дешевле, чем на продакшене.",
    "Делайте перерывы. Лучшие решения часто приходят, когда вы не смотрите в монитор.",
    "Code review — это не критика, а возможность научиться чему-то новому от коллег.",
    "Автоматизируйте рутину. Если делаете что-то больше двух раз — напишите скрипт.",
    "Безопасность — это не опция, а необходимость. Никогда не коммитьте секреты и API ключи в репозиторий.",
]

# Markers to identify the section in README.md
START_MARKER = "<!-- START_DAILY_TIP -->"
END_MARKER = "<!-- END_DAILY_TIP -->"


def get_random_tip():
    """Select and format a random tip."""
    tip = random.choice(TIPS)
    return f"\n> 💡 **Совет дня:** {tip}\n"


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
