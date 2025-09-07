#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACKS = {
    "lc75": ("tracks/leetcode-75.md", 75),
    "ti150": ("tracks/top-interview-150.md", 150),
    "sql50": ("tracks/sql-50.md", 50),
}

def count(track_file: Path):
    txt = track_file.read_text(encoding="utf-8")
    done = len(re.findall(r"^\s*-\s*\[x\]", txt, flags=re.I|re.M))
    total = len(re.findall(r"^\s*-\s*\[(?: |x)\]", txt, flags=re.I|re.M))
    return done, total or None

def update_readme():
    readme_p = ROOT/"README.md"
    readme = readme_p.read_text(encoding="utf-8")
    for key, (rel, default_total) in TRACKS.items():
        d, t = count(ROOT/rel)
        t = t or default_total
        pct = int(round((d/t)*100)) if t else 0
        pat = re.compile(rf"(<!-- PROGRESS:{key}:start -->)(.*?)(<!-- PROGRESS:{key}:end -->)", re.S|re.I)
        name = {"lc75":"Leetcode 75","ti150":"Top Interview 150","sql50":"Sql 50"}[key]
        repl = rf"\1{name}: {d}/{t} ({pct}%)\3"
        readme = pat.sub(repl, readme)
    readme_p.write_text(readme, encoding="utf-8")
    print("README progress updated.")

if __name__ == "__main__":
    update_readme()
