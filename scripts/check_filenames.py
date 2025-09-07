#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BAD = []

def check_dir(d: Path, ext: str):
    pat = re.compile(r"^\d{4}_[a-z0-9_]+\." + re.escape(ext) + r"$")
    for f in d.rglob("*." + ext):
        if f.name.startswith("_"):
            continue
        if not pat.match(f.name):
            BAD.append(str(f))

if __name__ == "__main__":
    check_dir(ROOT/"python", "py")
    check_dir(ROOT/"sql", "sql")
    if BAD:
        print("Bad filenames:\n" + "\n".join(BAD))
        raise SystemExit(1)
    print("All filenames OK.")
