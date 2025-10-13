#!/usr/bin/env python3
"""
Interactive CLI wizard for hassle-free daily problem solving.
Usage: python scripts/daily.py
"""
from __future__ import annotations
import sys
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

try:
    from new import sanitize_path_component, TEMPLATES
except ImportError:
    print("Error: Cannot import required modules")
    sys.exit(1)

TRACKS = {
    "1": {"name": "leetcode-75", "display": "LeetCode 75"},
    "2": {"name": "top-interview-150", "display": "Top Interview 150"},
    "3": {"name": "sql-50", "display": "SQL 50"},
}

DIFFICULTIES = ["Easy", "Medium", "Hard"]

def colored(text: str, color: str) -> str:
    """Return colored text for terminal."""
    colors = {
        "green": "\033[92m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "cyan": "\033[96m",
        "magenta": "\033[95m",
        "reset": "\033[0m",
        "bold": "\033[1m",
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"

def print_header():
    """Print welcome header."""
    print("\n" + "="*60)
    print(colored("🚀 LeetCode Daily Problem Wizard", "cyan"))
    print(colored("   Hassle-free problem tracking!", "blue"))
    print("="*60 + "\n")

def prompt(question: str, default: str = "") -> str:
    """Prompt user for input with optional default."""
    if default:
        question = f"{question} [{colored(default, 'yellow')}]"
    response = input(f"{colored('?', 'blue')} {question}: ").strip()
    return response if response else default

def choose(question: str, options: list[str]) -> str:
    """Let user choose from a list of options."""
    print(f"\n{colored('?', 'blue')} {question}")
    for i, opt in enumerate(options, 1):
        print(f"  {colored(str(i), 'yellow')}. {opt}")

    while True:
        choice = input(f"{colored('>', 'green')} Enter choice (1-{len(options)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print(colored("Invalid choice. Try again.", "red"))

def confirm(question: str, default: bool = True) -> bool:
    """Ask yes/no question."""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{colored('?', 'blue')} {question} [{default_str}]: ").strip().lower()
    if not response:
        return default
    return response in ('y', 'yes')

def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{colored('⚙', 'yellow')} {description}...")
    try:
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if result.returncode == 0:
            print(colored("✓ Success!", "green"))
            return True
        else:
            print(colored(f"✗ Failed: {result.stderr}", "red"))
            return False
    except Exception as e:
        print(colored(f"✗ Error: {e}", "red"))
        return False

def get_problem_details():
    """Collect problem details from user."""
    print_header()

    # Track selection
    print(colored("\n📚 Select Track:", "bold"))
    for key, track in TRACKS.items():
        print(f"  {colored(key, 'yellow')}. {track['display']}")

    while True:
        track_choice = input(f"{colored('>', 'green')} Enter choice (1-3): ").strip()
        if track_choice in TRACKS:
            selected_track = TRACKS[track_choice]["name"]
            break
        print(colored("Invalid choice. Try again.", "red"))

    # Type selection
    if "sql" in selected_track:
        file_type = "sql"
    else:
        type_choice = choose("\n💻 Select Language:", ["Python", "SQL"])
        file_type = "py" if type_choice == "Python" else "sql"

    # Problem details
    print(f"\n{colored('📝 Problem Details:', 'bold')}")

    problem_id = prompt("Problem ID (e.g., 1768)", "")
    while not problem_id.isdigit():
        print(colored("ID must be a number!", "red"))
        problem_id = prompt("Problem ID", "")

    problem_title = prompt("Problem Title (e.g., Merge Strings Alternately)", "")

    # Generate slug from title
    default_slug = problem_title.lower().replace(" ", "_").replace("-", "_")
    default_slug = "".join(c for c in default_slug if c.isalnum() or c == "_")
    problem_slug = prompt("Problem Slug", default_slug)

    difficulty = choose("\n⚡ Difficulty:", DIFFICULTIES)

    category = prompt("Category (optional, will auto-detect from tags)", "")

    tags = prompt("Tags (comma-separated, e.g., string, two-pointers)", "")

    return {
        "track": selected_track,
        "type": file_type,
        "id": int(problem_id),
        "slug": problem_slug,
        "title": problem_title,
        "difficulty": difficulty,
        "category": category,
        "tags": tags,
    }

def create_problem_file(details: dict):
    """Create solution file with header."""
    try:
        safe_track = sanitize_path_component(details["track"])
        safe_slug = sanitize_path_component(details["slug"])

        # Create file
        if details["type"] == "py":
            tpl = TEMPLATES["py"].get(safe_track)
            dest = ROOT / f"python/{safe_track}/{details['id']:04d}_{safe_slug}.py"
            header = f'''"""
{details['id']:04d} - {details['title']} ({details['slug']})
Idea:
Time: O() | Space: O()
Tags: {details['tags']}
Link: https://leetcode.com/problems/{details['slug'].replace("_", "-")}/
"""

class Solution:
    pass
'''
        else:
            tpl = TEMPLATES["sql"].get(safe_track)
            dest = ROOT / f"sql/{safe_track}/{details['id']:04d}_{safe_slug}.sql"
            header = f"""-- {details['id']:04d} - {details['title']} ({details['slug']})
-- Idea:
-- Tags: {details['tags']}
-- Link: https://leetcode.com/problems/{details['slug'].replace('_', '-')}/

-- Your solution here
"""

        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(header, encoding="utf-8")

        print(f"\n{colored('✓', 'green')} Created: {colored(str(dest.relative_to(ROOT)), 'cyan')}")
        return str(dest)

    except Exception as e:
        print(colored(f"✗ Failed to create file: {e}", "red"))
        return None

def update_csv(details: dict):
    """Add entry to track CSV if not exists."""
    try:
        csv_path = ROOT / f"tracks/{details['track']}.csv"

        if not csv_path.exists():
            print(colored(f"✗ CSV not found: {csv_path}", "red"))
            return False

        # Check if entry exists
        content = csv_path.read_text(encoding="utf-8")
        if f"{details['id']}," in content:
            print(f"{colored('ℹ', 'yellow')} Entry already exists in CSV")
            return True

        # Add entry
        csv_line = f"{details['id']},{details['title']},{details['slug']},{details['difficulty']},{details['category']},\"{details['tags']}\"\n"

        with csv_path.open("a", encoding="utf-8") as f:
            f.write(csv_line)

        print(f"{colored('✓', 'green')} Added entry to CSV")
        return True

    except Exception as e:
        print(colored(f"✗ Failed to update CSV: {e}", "red"))
        return False

def main():
    """Main workflow."""
    try:
        # Get problem details
        details = get_problem_details()

        # Show summary
        print(f"\n{colored('📋 Summary:', 'bold')}")
        print(f"  Track:      {details['track']}")
        print(f"  Type:       {details['type'].upper()}")
        print(f"  ID:         {details['id']}")
        print(f"  Title:      {details['title']}")
        print(f"  Difficulty: {details['difficulty']}")
        print(f"  Tags:       {details['tags']}")

        if not confirm("\nProceed with creation?", True):
            print(colored("\n✗ Cancelled", "red"))
            return

        # Create file
        file_path = create_problem_file(details)
        if not file_path:
            return

        # Update CSV
        update_csv(details)

        # Sync
        if confirm("\nRun sync_all.py to update trackers?", True):
            run_command([sys.executable, str(ROOT / "scripts/sync_all.py")], "Syncing all tracks")

        # Git workflow
        if confirm("\nCommit and push changes?", True):
            # Git add
            run_command(["git", "add", "-A"], "Staging changes")

            # Generate commit message
            commit_msg = f"feat({details['type']}): {details['id']} {details['slug']}"
            if details['tags']:
                commit_msg += f" [{details['tags'].replace(', ', ',')}]"

            print(f"\n{colored('📝 Commit message:', 'bold')}")
            print(f"  {commit_msg}")

            custom_msg = prompt("\nCustom commit message (or press Enter to use above)", "")
            if custom_msg:
                commit_msg = custom_msg

            # Commit
            run_command(["git", "commit", "-m", commit_msg], "Committing changes")

            # Push
            if confirm("\nPush to remote?", True):
                run_command(["git", "push"], "Pushing to remote")

        print(f"\n{colored('🎉 All done!', 'green')} Happy coding! 🚀\n")
        print(f"📂 Open file: {colored(file_path, 'cyan')}")
        print(f"🌐 View UI: {colored('https://mh-13.github.io/leetcode-grind/', 'cyan')}\n")

    except KeyboardInterrupt:
        print(colored("\n\n✗ Cancelled by user", "red"))
        sys.exit(1)
    except Exception as e:
        print(colored(f"\n✗ Unexpected error: {e}", "red"))
        sys.exit(1)

if __name__ == "__main__":
    main()
