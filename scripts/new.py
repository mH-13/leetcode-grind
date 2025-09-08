#!/usr/bin/env python3
from __future__ import annotations
import argparse, shutil, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = {
    "py": {
        "leetcode-75": ROOT/"python/leetcode-75/_template.py",
        "top-interview-150": ROOT/"python/top-interview-150/_template.py",
        "misc": ROOT/"python/misc/_template.py",
    },
    "sql": {
        "sql-50": ROOT/"sql/sql-50/_template.sql",
        "misc": ROOT/"sql/misc/_template.sql",
    },
}

def sanitize_path_component(value: str) -> str:
    """Sanitize path components to prevent path traversal attacks."""
    # Remove any path traversal sequences and invalid characters
    # amazonq-ignore-next-line
    sanitized = re.sub(r'[./\\]', '', str(value))
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', sanitized)
    if not sanitized:
        raise ValueError(f"Invalid path component: {value}")
    return sanitized

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--type", choices=["py","sql"], required=True)
    # amazonq-ignore-next-line
    p.add_argument("--track", required=True)
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--title", required=True)
    args = p.parse_args()

    # Sanitize inputs to prevent path traversal
    safe_track = sanitize_path_component(args.track)
    # amazonq-ignore-next-line
    safe_slug = sanitize_path_component(args.slug)
    
    # Validate track exists in templates
    if safe_track not in TEMPLATES[args.type]:
        available = list(TEMPLATES[args.type].keys())
        raise SystemExit(f"Unknown track '{args.track}' for type '{args.type}'. Available: {available}")

    try:
        if args.type == "py":
            tpl = TEMPLATES["py"][safe_track]
            dest = ROOT / f"python/{safe_track}/{args.id:04d}_{safe_slug}.py"
            header = f'"""\n{args.id:04d} - {args.title} ({args.slug})\nIdea: \nTime:  | Space: \nTags: \nLink: https://leetcode.com/problems/{args.slug.replace("_","-")}/\n"""\n\n'
        else:
            tpl = TEMPLATES["sql"][safe_track]
            dest = ROOT / f"sql/{safe_track}/{args.id:04d}_{safe_slug}.sql"
            header = f"-- {args.id:04d} - {args.title} ({args.slug})\n-- Idea: \n-- Tags: \n-- Link: https://leetcode.com/problems/{args.slug.replace('_','-')}/\n\n"
        
        if not tpl.exists():
            raise SystemExit(f"Template not found: {tpl}")
        
        # Ensure destination is within expected directory
        if not str(dest.resolve()).startswith(str(ROOT.resolve())):
            raise SystemExit("Invalid destination path")
            
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy(tpl, dest)
            content = dest.read_text(encoding="utf-8")
            dest.write_text(header + content, encoding="utf-8")
        except (IOError, PermissionError, OSError) as e:
            raise SystemExit(f"File operation failed: {e}")
        print(f"Created: {dest}")
        
    except (IOError, PermissionError) as e:
        raise SystemExit(f"File operation failed: {e}")
    except Exception as e:
        raise SystemExit(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
