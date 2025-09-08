#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def check_dir(d: Path, ext: str) -> list[str]:
    pat = re.compile(r"^\d{4}_[a-z0-9_]+\." + re.escape(ext) + r"$")
    bad_files = []
    for f in d.rglob("*." + ext):
        if f.name.startswith("_"):
            continue
        if not pat.match(f.name):
            bad_files.append(str(f))
    return bad_files

if __name__ == "__main__":
    bad_files = check_dir(ROOT/"python", "py") + check_dir(ROOT/"sql", "sql")
    if bad_files:
        print("Bad filenames:\n" + "\n".join(bad_files))
        raise SystemExit(1)
    print("All filenames OK.")
