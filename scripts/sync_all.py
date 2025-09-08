#!/usr/bin/env python3
from __future__ import annotations
import csv, json, re, unicodedata, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "tracks/registry.json"
README = ROOT / "README.md"
INDEX_JSON = ROOT / "docs/data/index.json"


# Tag normalization mapping
TAG_NORMALIZE = {
    "Two Pointers": "two-pointers",
    "Sliding Window": "sliding-window",
    "Prefix Sum": "prefix-sum",
    "Hash Table": "hashmap",
    "Hash Map": "hashmap",
    "Set": "set",
    "Matrix": "matrix",
    "Array": "array",
    "String": "string",
    "Binary Search": "binary-search",
    "Greedy": "greedy",
    "Depth-First Search": "dfs",
    "Breadth-First Search": "bfs",
    "Union Find": "union-find",
    "Heap (Priority Queue)": "heap",
    "Priority Queue": "heap",
    "Stack": "stack",
    "Queue": "queue",
    "Graph": "graph",
    "Tree": "tree",
    "Binary Tree": "binary-tree",
    "Binary Search Tree": "bst",
    "Dynamic Programming": "dp",
    "Memoization": "memo",
    "Combinatorics": "combinatorics",
    "Sorting": "sorting",
    "Design": "design",
    "Simulation": "simulation",
    "Bit Manipulation": "bit",
    "Interactive": "interactive",
    "Window Functions": "window"
}

# Category mapping from tags
FAMILY_FROM_TAG = {
    "two-pointers": "Two Pointers",
    "sliding-window": "Sliding Window",
    "prefix-sum": "Prefix Sum",
    "hashmap": "Hash Map / Set",
    "set": "Hash Map / Set",
    "array": "Array / String",
    "string": "Array / String",
    "binary-search": "Binary Search",
    "greedy": "Greedy",
    "dfs": "Graphs - DFS",
    "bfs": "Graphs - BFS",
    "union-find": "Graphs - DFS",
    "heap": "Heap / Priority Queue",
    "stack": "Monotonic Stack",
    "queue": "Queue",
    "graph": "Graphs - BFS",
    "tree": "Binary Tree - DFS",
    "binary-tree": "Binary Tree - DFS",
    "bst": "Binary Search Tree",
    "dp": "DP - 1D",
    "memo": "DP - 1D",
    "sorting": "Intervals",
    "simulation": "Stack",
    "bit": "Bit Manipulation",
    "window": "Window Functions",
    "join": "JOINs",
    "self-join": "JOINs",
    "matrix": "Binary Tree - BFS",
    "deque": "Sliding Window",
    "grid": "Graphs - BFS",
    "trie": "Trie",
    "combinatorics": "DP - Multidimensional"
}

# Track key mappings
TRACK_KEY_MAP = {
    "leetcode-75": "lc75",
    "top-interview-150": "ti150",
    "sql-50": "sql50"
}

TRACK_NAME_MAP = {
    "leetcode-75": "Leetcode 75",
    "top-interview-150": "Top Interview 150",
    "sql-50": "Sql 50"
}

def slugify(title: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFKD", title) if ord(c) < 128)
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s

def auto_category(tags: list[str], default="Uncategorized") -> str:
    for t in tags:
        fam = FAMILY_FROM_TAG.get(t)
        if fam: return fam
    return default

def normalize_tags(raw_tags: str) -> list[str]:
    """Normalize and clean tag list."""
    if not raw_tags:
        return []
    tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    normalized = []
    for t in tags:
        normalized_tag = TAG_NORMALIZE.get(t, t)
        normalized.append(normalized_tag.lower().replace(" ", "-"))
    return normalized

def parse_csv_row(row: dict) -> dict:
    """Parse a single CSV row into standardized format."""
    try:
        tags = normalize_tags(row.get("tags", ""))
        category = row.get("category", "").strip() or auto_category(tags)
        # amazonq-ignore-next-line
        slug = row["slug"].strip()
        
        return {
            "id": int(row["id"]),
            "title": row["title"].strip(),
            "slug": slug,
            "difficulty": row.get("difficulty", "").strip(),
            "category": category,
            "tags": tags,
            "link": f'https://leetcode.com/problems/{slug.replace("_", "-")}/'
        }
    except (ValueError, KeyError) as e:
        print(f"Warning: Invalid CSV row {row}: {e}")
        return None

def parse_csv(csv_path: Path) -> list[dict]:
    """Parse CSV file into list of problem dictionaries."""
    items = []
    try:
        with csv_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                item = parse_csv_row(row)
                if item:
                    items.append(item)
    except (FileNotFoundError, PermissionError) as e:
        print(f"Error reading CSV {csv_path}: {e}")
        return []
    
    items.sort(key=lambda x: x["id"])
    return items

def scan_solved_files(track: dict) -> set[int]:
    """Scan directories for solved problem files."""
    solved_ids = set()
    id_pattern = re.compile(r"(\d{4})_")
    
    for dir_key, ext in [("dir_py", "*.py"), ("dir_sql", "*.sql")]:
        if not track.get(dir_key):
            continue
        base = ROOT / track[dir_key]
        if not base.exists():
            continue
        for path in base.glob(ext):
            if path.name.startswith("_"):
                continue
            match = id_pattern.match(path.name)
            if match:
                solved_ids.add(int(match.group(1)))
    return solved_ids

def generate_checklist_markdown(track: dict, items: list[dict], solved_ids: set[int]) -> str:
    """Generate markdown checklist grouped by category."""
    by_cat = {}
    for item in items:
        category = item["category"] or "Uncategorized"
        by_cat.setdefault(category, []).append(item)
    
    md_lines = [f"# {track['name']} — Progress\n"]
    for category in sorted(by_cat.keys()):
        md_lines.append(f"\n## {category}\n")
        for item in sorted(by_cat[category], key=lambda x: x["id"]):
            mark = "x" if item["id"] in solved_ids else " "
            md_lines.append(f"- [{mark}] {item['id']:04d} — {item['slug']}")
    return "\n".join(md_lines) + "\n"

def write_plan_and_checklist(track: dict, items: list[dict]) -> None:
    """Write plan JSON and checklist markdown for a track."""
    try:
        # Write plan JSON
        plan_json = ROOT / track["plan_json"]
        plan_data = {"plan": track["key"], "items": items}
        plan_json.write_text(json.dumps(plan_data, indent=2), encoding="utf-8")
        
        # Scan for solved files
        solved_ids = scan_solved_files(track)
        
        # Generate and write checklist
        checklist_md = generate_checklist_markdown(track, items, solved_ids)
        checklist_path = ROOT / track["checklist_md"]
        checklist_path.write_text(checklist_md, encoding="utf-8")
        
        # Update track statistics
        track["solved"] = len([item for item in items if item["id"] in solved_ids])
        track["total_eff"] = len(items) or track.get("total", 0)
        
    except (IOError, KeyError) as e:
        print(f"Error writing plan/checklist for {track.get('key', 'unknown')}: {e}")

def update_readme_progress(tracks: list[dict]):
    """Update progress markers in README.md."""
    try:
        txt = README.read_text(encoding="utf-8")
        
        for track in tracks:
            key = TRACK_KEY_MAP.get(track["key"], track["key"])
            name = TRACK_NAME_MAP.get(track["key"], track["name"])
            total = track["total_eff"] or 1
            pct = int(round((track["solved"] / total) * 100))
            
            pattern = re.compile(
                rf"(<!-- PROGRESS:{key}:start -->)(.*?)(<!-- PROGRESS:{key}:end -->)", 
                re.S | re.I
            )
            replacement = rf"\1{name}: {track['solved']}/{track['total_eff']} ({pct}%)\3"
            
            # amazonq-ignore-next-line
            if pattern.search(txt):
                txt = pattern.sub(replacement, txt)
            else:
                txt += f"\n<!-- PROGRESS:{key}:start -->{name}: {track['solved']}/{track['total_eff']} ({pct}%)<!-- PROGRESS:{key}:end -->\n"
        
        README.write_text(txt, encoding="utf-8")
    except (FileNotFoundError, PermissionError) as e:
        print(f"Error updating README: {e}")
        raise SystemExit(1)

def extract_header_field(block: str, label: str) -> str:
    """Extract a field value from header block."""
    match = re.search(rf"^{label}\s*:\s*(.+)$", block, flags=re.M|re.I)
    return match.group(1).strip() if match else ""

def parse_title_line(block: str) -> tuple[int | None, str, str]:
    """Parse title line to extract ID, title, and slug."""
    title_line = next((l for l in block.splitlines() if re.search(r"^\d{4}\s*-\s*.+\(.+\)", l)), "")
    match = re.match(r"(\d{4})\s*-\s*(.*?)\s*\((.*?)\)", title_line)
    if match:
        return int(match.group(1)), match.group(2), match.group(3)
    return None, "", ""

def parse_header_py(txt: str) -> dict:
    """Parse Python file header block."""
    match = re.search(r'"""(.*?)"""', txt, flags=re.S)
    if not match:
        return {"id": None, "title": "", "slug": "", "idea": "", "time": "", "space": "", "tags": [], "link": ""}
    
    block = match.group(1)
    pid, title, slug = parse_title_line(block)
    tags = [t.strip().lower() for t in extract_header_field(block, "Tags").split(",") if t.strip()]
    
    return {
        "id": pid, "title": title, "slug": slug,
        "idea": extract_header_field(block, "Idea"),
        "time": extract_header_field(block, "Time"),
        "space": extract_header_field(block, "Space"),
        "tags": tags,
        "link": extract_header_field(block, "Link")
    }

def extract_sql_header_block(txt: str) -> str:
    """Extract header comment block from SQL file."""
    header_lines = []
    for line in txt.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            header_lines.append(stripped[2:].strip())
        elif stripped == "":
            continue
        else:
            break
    return "\n".join(header_lines)

def parse_header_sql(txt: str) -> dict:
    """Parse SQL file header block."""
    block = extract_sql_header_block(txt)
    pid, title, slug = parse_title_line(block)
    tags = [t.strip().lower() for t in extract_header_field(block, "Tags").split(",") if t.strip()]
    
    return {
        "id": pid, "title": title, "slug": slug,
        "idea": extract_header_field(block, "Idea"),
        "time": extract_header_field(block, "Time"),
        "space": extract_header_field(block, "Space"),
        "tags": tags,
        "link": extract_header_field(block, "Link")
    }

def load_plans_all() -> dict[tuple[str, int], dict]:
    """Load all plan metadata indexed by (track, id)."""
    plans = {}
    tracks_dir = ROOT / "tracks"
    if not tracks_dir.exists():
        return plans
        
    for path in tracks_dir.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            track_key = path.stem
            for item in data.get("items", []):
                if "id" in item:
                    plans[(track_key, int(item["id"]))] = item
        except (json.JSONDecodeError, ValueError, IOError) as e:
            print(f"Warning: Failed to load plan {path}: {e}")
            continue
    return plans

def process_track_files(track: dict, plan_meta: dict, file_type: str) -> list[dict]:
    """Process files for a specific track and type."""
    items = []
    dir_key = f"dir_{file_type}"
    if not track.get(dir_key):
        return items
        
    base = ROOT / track[dir_key]
    if not base.exists():
        return items
        
    parser = parse_header_py if file_type == "py" else parse_header_sql
    extension = f"*.{file_type}" if file_type != "py" else "*.py"
    
    for path in base.glob(extension):
        if path.name.startswith("_"):
            continue
        try:
            header = parser(path.read_text(encoding="utf-8"))
            if not header["id"]:
                continue
                
            meta = plan_meta.get((track["key"], header["id"]), {})
            tags = list(dict.fromkeys((header["tags"] or []) + (meta.get("tags") or [])))
            category = meta.get("category") or auto_category(tags, "SQL" if file_type == "sql" else "Uncategorized")
            
            items.append({
                "id": header["id"], "title": header["title"], "slug": header["slug"],
                "idea": header["idea"], "time": header["time"], "space": header["space"],
                "tags": tags, "link": header["link"] or meta.get("link"),
                "difficulty": meta.get("difficulty", ""), "category": category,
                "track": track["key"], "type": file_type,
                "path": str(path.relative_to(ROOT)).replace("\\", "/")
            })
        except (IOError, UnicodeDecodeError) as e:
            print(f"Warning: Failed to process {path}: {e}")
            continue
    return items

def rebuild_index_dataset(tracks: list[dict]):
    """Rebuild the index dataset for the UI."""
    try:
        plan_meta = load_plans_all()
        items = []
        
        for track in tracks:
            items.extend(process_track_files(track, plan_meta, "py"))
            items.extend(process_track_files(track, plan_meta, "sql"))
        
        items.sort(key=lambda x: (x["track"], x["type"], x["id"]))
        
        # Generate aggregated data
        tracks_list = sorted({item["track"] for item in items})
        tags_list = sorted({tag for item in items for tag in item["tags"]})
        cats_list = sorted({item["category"] for item in items if item.get("category")})
        
        # Write index file
        INDEX_JSON.parent.mkdir(parents=True, exist_ok=True)
        index_data = {
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "tracks": tracks_list,
            "tags": tags_list,
            "categories": cats_list,
            "items": items
        }
        INDEX_JSON.write_text(json.dumps(index_data, indent=2), encoding="utf-8")
        
    except Exception as e:
        print(f"Error rebuilding index dataset: {e}")
        raise SystemExit(1)

if __name__ == "__main__":
    try:
        # Load registry configuration
        registry_data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        tracks = registry_data["tracks"]

        # Build plans and checklists for each track
        for track in tracks:
            csv_path = ROOT / track["csv"]
            items = parse_csv(csv_path)
            if items:
                write_plan_and_checklist(track, items)
            else:
                print(f"Warning: No items found for track {track['key']}")

        # Update README progress markers
        update_readme_progress(tracks)

        # Rebuild UI dataset
        rebuild_index_dataset(tracks)

        print("sync_all: completed successfully.")
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading registry: {e}")
        raise SystemExit(1)
    except Exception as e:
        print(f"Unexpected error during sync: {e}")
        raise SystemExit(1)
