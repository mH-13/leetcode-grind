#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Track configuration
TRACK_CONFIG = {
    "lc75": {"file": "tracks/leetcode-75.md", "total": 75, "name": "Leetcode 75"},
    "ti150": {"file": "tracks/top-interview-150.md", "total": 150, "name": "Top Interview 150"},
    "sql50": {"file": "tracks/sql-50.md", "total": 50, "name": "Sql 50"},
}

# amazonq-ignore-next-line
def count_progress(track_file: Path) -> tuple[int, int]:
    """Count completed and total items from markdown checklist."""
    try:
        txt = track_file.read_text(encoding="utf-8")
        done = len(re.findall(r"^\s*-\s*\[x\]", txt, flags=re.I|re.M))
        total = len(re.findall(r"^\s*-\s*\[(?: |x)\]", txt, flags=re.I|re.M))
        return done, total
    except (FileNotFoundError, PermissionError) as e:
        print(f"Warning: Could not read {track_file}: {e}")
        return 0, 0

def update_readme():
    """Update progress markers in README.md."""
    readme_path = ROOT / "README.md"
    try:
        readme = readme_path.read_text(encoding="utf-8")
        
        for key, config in TRACK_CONFIG.items():
            done, total = count_progress(ROOT / config["file"])
            total = total or config["total"]
            pct = int(round((done / total) * 100)) if total else 0
            
            pattern = re.compile(
                rf"(<!-- PROGRESS:{key}:start -->)(.*?)(<!-- PROGRESS:{key}:end -->)", 
                re.S | re.I
            )
            replacement = rf"\1{config['name']}: {done}/{total} ({pct}%)\3"
            readme = pattern.sub(replacement, readme)
        
        readme_path.write_text(readme, encoding="utf-8")
        print("README progress updated.")
        
    except (FileNotFoundError, PermissionError) as e:
        print(f"Error updating README: {e}")
        raise SystemExit(1)

if __name__ == "__main__":
    try:
        update_readme()
    except Exception as e:
        print(f"Failed to update progress: {e}")
        raise SystemExit(1)
