#!/usr/bin/env python3
"""
Add a new track to your LeetCode grind.
Usage: python scripts/add_track.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "tracks/registry.json"

def main():
    print("\n" + "="*60)
    print("🎯 Add New Track")
    print("="*60 + "\n")

    # Get track details
    track_name = input("Track name (e.g., 'neetcode-150'): ").strip().lower()
    display_name = input("Display name (e.g., 'NeetCode 150'): ").strip()
    language = input("Language (py/sql): ").strip().lower()

    if language not in ['py', 'sql']:
        print("❌ Language must be 'py' or 'sql'")
        return

    # Create directories
    if language == 'py':
        folder = ROOT / f"python/{track_name}"
        template_src = ROOT / "python/leetcode-75/_template.py"
    else:
        folder = ROOT / f"sql/{track_name}"
        template_src = ROOT / "sql/sql-50/_template.sql"

    folder.mkdir(parents=True, exist_ok=True)

    # Copy template
    template_dest = folder / f"_template.{language}"
    if template_src.exists():
        import shutil
        shutil.copy(template_src, template_dest)

    # Create CSV
    csv_file = ROOT / f"tracks/{track_name}.csv"
    csv_file.write_text("id,title,slug,difficulty,category,tags\n", encoding="utf-8")

    # Update registry
    with open(REGISTRY, 'r') as f:
        registry = json.load(f)

    new_track = {
        "key": track_name,
        "name": display_name,
        "csv": f"tracks/{track_name}.csv",
        "plan_json": f"tracks/{track_name}.json",
        "checklist_md": f"tracks/{track_name}.md"
    }

    if language == 'py':
        new_track["dir_py"] = f"python/{track_name}"
    else:
        new_track["dir_sql"] = f"sql/{track_name}"

    registry["tracks"].append(new_track)

    with open(REGISTRY, 'w') as f:
        json.dump(registry, f, indent=2)

    print(f"\n✅ Track created!")
    print(f"   Folder: {folder}")
    print(f"   CSV: {csv_file}")
    print(f"   Template: {template_dest}")

    # Update daily.py
    print(f"\n📝 To use in wizard, add to scripts/daily.py:")
    print(f'   TRACKS["{len(registry["tracks"])}"] = {{"name": "{track_name}", "display": "{display_name}"}}')

    print(f"\n🚀 Now you can:")
    print(f"   1. Run: python scripts/sync_all.py")
    print(f"   2. Use in wizard: ./daily.sh")

if __name__ == "__main__":
    main()
