#!/usr/bin/env python3
from __future__ import annotations
import json, re, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"docs/data/index.json"

def parse_header_py(txt: str):
    m = re.search(r'"""(.*?)"""', txt, flags=re.S)
    if not m: return {}
    block = m.group(1)
    return parse_common(block)

def parse_header_sql(txt: str):
    # read leading comment lines only
    head_lines = []
    for line in txt.splitlines():
        if line.strip().startswith("--"):
            head_lines.append(line.strip()[2:].strip())
        elif line.strip() == "":
            continue
        else:
            break
    block = "\n".join(head_lines)
    return parse_common(block)

def parse_common(block: str):
    def grab(label):
        m = re.search(rf"^{label}\s*:\s*(.+)$", block, flags=re.M|re.I)
        return (m.group(1).strip() if m else "")
    title_line = next((l for l in block.splitlines() if " - " in l and "(" in l and ")" in l), "")
    m = re.match(r"(\d{4})\s*-\s*(.*?)\s*\((.*?)\)", title_line)
    pid, title, slug = (m.group(1), m.group(2), m.group(3)) if m else ("","","")
    idea = grab("Idea")
    time = grab("Time")
    space = grab("Space")
    tags = [t.strip() for t in grab("Tags").split(",") if t.strip()]
    link = grab("Link")
    return {
        "id": int(pid) if pid.isdigit() else None,
        "title": title, "slug": slug,
        "idea": idea, "time": time, "space": space,
        "tags": tags, "link": link
    }

def collect():
    items = []
    for path in (ROOT/"python").rglob("*.py"):
        if path.name.startswith("_"): continue
        track = path.parts[path.parts.index("python")+1]
        data = parse_header_py(path.read_text(encoding="utf-8"))
        if not data.get("id"): continue
        data.update({"type":"py","track":track,"path":str(path.relative_to(ROOT)).replace("\\","/")})
        items.append(data)
    for path in (ROOT/"sql").rglob("*.sql"):
        if path.name.startswith("_"): continue
        track = path.parts[path.parts.index("sql")+1]
        data = parse_header_sql(path.read_text(encoding="utf-8"))
        if not data.get("id"): continue
        data.update({"type":"sql","track":track,"path":str(path.relative_to(ROOT)).replace("\\","/")})
        items.append(data)
    items.sort(key=lambda x:(x["track"], x["type"], x["id"]))
    return items

if __name__ == "__main__":
    items = collect()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.datetime.utcnow().isoformat()+"Z",
        "tracks": sorted({i["track"] for i in items}),
        "tags": sorted({t for i in items for t in i["tags"]}),
        "items": items
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(items)} items)")
