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

# Regex pattern for title parsing: "1234 - Problem Title (slug)"
TITLE_PATTERN = re.compile(r"(\d{4})\s*-\s*(.*?)\s*\((.*?)\)")

def parse_common(block: str):
    def grab(label):
        m = re.search(rf"^{label}\s*:\s*(.+)$", block, flags=re.M|re.I)
        return (m.group(1).strip() if m else "")
    
    title_line = next((l for l in block.splitlines() if " - " in l and "(" in l and ")" in l), "")
    m = TITLE_PATTERN.match(title_line)
    pid, title, slug = (m.group(1), m.group(2), m.group(3)) if m else ("","","")
    
    return {
        "id": int(pid) if pid.isdigit() else None,
        "title": title, "slug": slug,
        "idea": grab("Idea"), "time": grab("Time"), "space": grab("Space"),
        "tags": [t.strip() for t in grab("Tags").split(",") if t.strip()],
        "link": grab("Link")
    }

def collect_files(base_dir: str, extension: str, parser_func) -> list[dict]:
    """Collect and parse files from a directory."""
    items = []
    base_path = ROOT / base_dir
    if not base_path.exists():
        return items
        
    for path in base_path.rglob(f"*.{extension}"):
        if path.name.startswith("_"): 
            continue
        try:
            track = path.parts[path.parts.index(base_dir) + 1]
            data = parser_func(path.read_text(encoding="utf-8"))
            if not data.get("id"): 
                continue
            data.update({
                "type": "py" if extension == "py" else "sql",
                "track": track,
                "path": str(path.relative_to(ROOT)).replace("\\", "/")
            })
            items.append(data)
        except (ValueError, IndexError, IOError) as e:
            print(f"Warning: Failed to process {path}: {e}")
            continue
    return items

def collect():
    items = []
    items.extend(collect_files("python", "py", parse_header_py))
    items.extend(collect_files("sql", "sql", parse_header_sql))
    items.sort(key=lambda x: (x["track"], x["type"], x["id"]))
    return items

if __name__ == "__main__":
    try:
        items = collect()
        OUT.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "tracks": sorted({i["track"] for i in items}),
            "tags": sorted({t for i in items for t in i["tags"]}),
            "categories": sorted({i.get("category", "") for i in items if i.get("category")}),
            "items": items
        }
        OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Wrote {OUT} ({len(items)} items)")
    except Exception as e:
        print(f"Error generating index: {e}")
        raise SystemExit(1)
