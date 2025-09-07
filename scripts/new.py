#!/usr/bin/env python3
from __future__ import annotations
import argparse, shutil
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

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--type", choices=["py","sql"], required=True)
    p.add_argument("--track", required=True)
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--title", required=True)
    args = p.parse_args()

    if args.type == "py":
        tpl = TEMPLATES["py"].get(args.track)
        dest = ROOT / f"python/{args.track}/{args.id:04d}_{args.slug}.py"
        header = f'"""\n{args.id:04d} - {args.title} ({args.slug})\nIdea: \nTime:  | Space: \nTags: \nLink: https://leetcode.com/problems/{args.slug.replace("_","-")}/\n"""\n\n'
    else:
        tpl = TEMPLATES["sql"].get(args.track)
        dest = ROOT / f"sql/{args.track}/{args.id:04d}_{args.slug}.sql"
        header = f"-- {args.id:04d} - {args.title} ({args.slug})\n-- Idea: \n-- Tags: \n-- Link: https://leetcode.com/problems/{args.slug.replace('_','-')}/\n\n"
    if tpl is None or not tpl.exists():
        raise SystemExit(f"Unknown track '{args.track}' for type '{args.type}'")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(tpl, dest)
    content = dest.read_text(encoding="utf-8")
    dest.write_text(header + content, encoding="utf-8")
    print(f"Created: {dest}")

if __name__ == "__main__":
    main()
