#!/usr/bin/env python3
from __future__ import annotations
import csv, json, re, unicodedata, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "tracks/registry.json"
README = ROOT / "README.md"
INDEX_JSON = ROOT / "docs/data/index.json"

TAG_NORMALIZE = {
    "Two Pointers": "two-pointers","Sliding Window": "sliding-window","Prefix Sum": "prefix-sum",
    "Hash Table": "hashmap","Hash Map": "hashmap","Set":"set","Matrix":"matrix","Array":"array",
    "String":"string","Binary Search":"binary-search","Greedy":"greedy","Depth-First Search":"dfs",
    "Breadth-First Search":"bfs","Union Find":"union-find","Heap (Priority Queue)":"heap","Priority Queue":"heap",
    "Stack":"stack","Queue":"queue","Graph":"graph","Tree":"tree","Binary Tree":"binary-tree",
    "Binary Search Tree":"bst","Dynamic Programming":"dp","Memoization":"memo","Combinatorics":"combinatorics",
    "Sorting":"sorting","Design":"design","Simulation":"simulation","Bit Manipulation":"bit","Interactive":"interactive",
    "Window Functions":"window"
}

FAMILY_FROM_TAG = {
    "two-pointers":"Two Pointers","sliding-window":"Sliding Window","prefix-sum":"Prefix Sum",
    "hashmap":"Hash Map / Set","set":"Hash Map / Set","array":"Array / String","string":"Array / String",
    "binary-search":"Binary Search","greedy":"Greedy","dfs":"Graphs - DFS","bfs":"Graphs - BFS",
    "union-find":"Graphs - DFS","heap":"Heap / Priority Queue","stack":"Monotonic Stack",
    "queue":"Queue","graph":"Graphs - BFS","tree":"Binary Tree - DFS","binary-tree":"Binary Tree - DFS",
    "bst":"Binary Search Tree","dp":"DP - 1D","memo":"DP - 1D","sorting":"Intervals",
    "simulation":"Stack","bit":"Bit Manipulation","window":"Window Functions","join":"JOINs","self-join":"JOINs",
    "matrix":"Binary Tree - BFS","deque":"Sliding Window","grid":"Graphs - BFS","trie":"Trie","combinatorics":"DP - Multidimensional"
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

def parse_csv(csv_path: Path) -> list[dict]:
    out = []
    with csv_path.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            tags = [t.strip() for t in (row.get("tags","") or "").split(",") if t.strip()]
            # normalize mixed labels
            tags = [TAG_NORMALIZE.get(t, t).lower().replace(" ","-") for t in tags]
            cat = row.get("category","").strip() or auto_category(tags)
            out.append({
                "id": int(row["id"]),
                "title": row["title"].strip(),
                "slug": row["slug"].strip(),
                "difficulty": row.get("difficulty","").strip(),
                "category": cat,
                "tags": tags,
                "link": f'https://leetcode.com/problems/{row["slug"].strip().replace("_","-")}/'
            })
    out.sort(key=lambda x: x["id"])
    return out

def write_plan_and_checklist(track: dict, items: list[dict]) -> None:
    plan_json = ROOT / track["plan_json"]
    plan_json.write_text(json.dumps({"plan": track["key"], "items": items}, indent=2), encoding="utf-8")

    # detect solved from present files
    solved_ids = set()
    if track.get("dir_py"):
        base = ROOT/track["dir_py"]
        if base.exists():
            for p in base.glob("*.py"):
                if p.name.startswith("_"): continue
                m = re.match(r"(\d{4})_", p.name)
                if m: solved_ids.add(int(m.group(1)))
    if track.get("dir_sql"):
        base = ROOT/track["dir_sql"]
        if base.exists():
            for p in base.glob("*.sql"):
                if p.name.startswith("_"): continue
                m = re.match(r"(\d{4})_", p.name)
                if m: solved_ids.add(int(m.group(1)))

    # grouped markdown by category with checkboxes
    by_cat = {}
    for it in items:
        by_cat.setdefault(it["category"] or "Uncategorized", []).append(it)
    md = [f"# {track['name']} — Progress\n"]
    for cat in sorted(by_cat.keys()):
        md.append(f"\n## {cat}\n")
        for it in sorted(by_cat[cat], key=lambda x: x["id"]):
            mark = "x" if it["id"] in solved_ids else " "
            md.append(f"- [{mark}] {it['id']:04d} — {it['slug']}")
    (ROOT/track["checklist_md"]).write_text("\n".join(md) + "\n", encoding="utf-8")

    track["solved"] = sum(1 for it in items if it["id"] in solved_ids)
    track["total_eff"] = len(items) or track.get("total", 0)

def update_readme_progress(tracks: list[dict]):
    txt = README.read_text(encoding="utf-8")
    for t in tracks:
        key = {"leetcode-75":"lc75","top-interview-150":"ti150","sql-50":"sql50"}.get(t["key"], t["key"])
        name = {"leetcode-75":"Leetcode 75","top-interview-150":"Top Interview 150","sql-50":"Sql 50"}.get(t["key"], t["name"])
        pct = int(round((t["solved"]/(t["total_eff"] or 1))*100))
        pat = re.compile(rf"(<!-- PROGRESS:{key}:start -->)(.*?)(<!-- PROGRESS:{key}:end -->)", re.S|re.I)
        repl = rf"\1{name}: {t['solved']}/{t['total_eff']} ({pct}%)\3"
        if pat.search(txt):
            txt = pat.sub(repl, txt)
        else:
            txt += f"\n<!-- PROGRESS:{key}:start -->{name}: {t['solved']}/{t['total_eff']} ({pct}%)<!-- PROGRESS:{key}:end -->\n"
    README.write_text(txt, encoding="utf-8")

def parse_header_py(txt: str):
    m = re.search(r'"""(.*?)"""', txt, flags=re.S)
    block = m.group(1) if m else ""
    def grab(label):
        mm = re.search(rf"^{label}\s*:\s*(.+)$", block, flags=re.M|re.I)
        return (mm.group(1).strip() if mm else "")
    line = next((l for l in block.splitlines() if re.search(r"^\d{4}\s*-\s*.+\(.+\)", l)), "")
    mm = re.match(r"(\d{4})\s*-\s*(.*?)\s*\((.*?)\)", line)
    pid, title, slug = (int(mm.group(1)), mm.group(2), mm.group(3)) if mm else (None,"","")
    tags = [t.strip() for t in grab("Tags").split(",") if t.strip()]
    return {"id": pid, "title": title, "slug": slug, "idea": grab("Idea"), "time": grab("Time"), "space": grab("Space"), "tags": [t.lower() for t in tags], "link": grab("Link")}

def parse_header_sql(txt: str):
    head = []
    for line in txt.splitlines():
        if line.strip().startswith("--"): head.append(line.strip()[2:].strip())
        elif line.strip() == "": continue
        else: break
    block = "\n".join(head)
    def grab(label):
        mm = re.search(rf"^{label}\s*:\s*(.+)$", block, flags=re.M|re.I)
        return (mm.group(1).strip() if mm else "")
    line = next((l for l in block.splitlines() if re.search(r"^\d{4}\s*-\s*.+\(.+\)", l)), "")
    mm = re.match(r"(\d{4})\s*-\s*(.*?)\s*\((.*?)\)", line)
    pid, title, slug = (int(mm.group(1)), mm.group(2), mm.group(3)) if mm else (None,"","")
    tags = [t.strip() for t in grab("Tags").split(",") if t.strip()]
    return {"id": pid, "title": title, "slug": slug, "idea": grab("Idea"), "time": grab("Time"), "space": grab("Space"), "tags": [t.lower() for t in tags], "link": grab("Link")}

def load_plans_all() -> dict[tuple[str,int], dict]:
    by = {}
    for p in (ROOT/"tracks").glob("*.json"):
        data = json.loads(p.read_text(encoding="utf-8"))
        key = p.stem  # e.g., leetcode-75
        for it in data.get("items", []):
            by[(key, int(it["id"]))] = it
    return by

def rebuild_index_dataset(tracks: list[dict]):
    plan_meta = load_plans_all()
    items = []
    for t in tracks:
        # Python
        if t.get("dir_py"):
            base = ROOT/t["dir_py"]
            if base.exists():
                for path in base.glob("*.py"):
                    if path.name.startswith("_"): continue
                    head = parse_header_py(path.read_text(encoding="utf-8"))
                    if not head["id"]: continue
                    meta = plan_meta.get((t["key"], head["id"]), {})
                    tags = list(dict.fromkeys((head["tags"] or []) + (meta.get("tags") or [])))
                    category = meta.get("category") or auto_category(tags)
                    items.append({
                        "id": head["id"], "title": head["title"], "slug": head["slug"],
                        "idea": head["idea"], "time": head["time"], "space": head["space"],
                        "tags": tags, "link": head["link"] or meta.get("link"),
                        "difficulty": meta.get("difficulty",""), "category": category,
                        "track": t["key"], "type":"py",
                        "path": str(path.relative_to(ROOT)).replace("\\","/")
                    })
        # SQL
        if t.get("dir_sql"):
            base = ROOT/t["dir_sql"]
            if base.exists():
                for path in base.glob("*.sql"):
                    if path.name.startswith("_"): continue
                    head = parse_header_sql(path.read_text(encoding="utf-8"))
                    if not head["id"]: continue
                    meta = plan_meta.get((t["key"], head["id"]), {})
                    tags = list(dict.fromkeys((head["tags"] or []) + (meta.get("tags") or [])))
                    category = meta.get("category") or auto_category(tags, default="SQL")
                    items.append({
                        "id": head["id"], "title": head["title"], "slug": head["slug"],
                        "idea": head["idea"], "time": head["time"], "space": head["space"],
                        "tags": tags, "link": head["link"] or meta.get("link"),
                        "difficulty": meta.get("difficulty",""), "category": category,
                        "track": t["key"], "type":"sql",
                        "path": str(path.relative_to(ROOT)).replace("\\","/")
                    })

    items.sort(key=lambda x: (x["track"], x["type"], x["id"]))
    tracks_list = sorted({i["track"] for i in items})
    tags_list = sorted({t for i in items for t in i["tags"]})
    cats_list = sorted({i["category"] for i in items if i.get("category")})
    INDEX_JSON.parent.mkdir(parents=True, exist_ok=True)
    INDEX_JSON.write_text(json.dumps({
        "generated_at": datetime.datetime.utcnow().isoformat()+"Z",
        "tracks": tracks_list, "tags": tags_list, "categories": cats_list, "items": items
    }, indent=2), encoding="utf-8")

if __name__ == "__main__":
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    tracks = reg["tracks"]

    # build plans + checklists
    for t in tracks:
        items = parse_csv(ROOT / t["csv"])
        write_plan_and_checklist(t, items)

    # update README progress markers
    update_readme_progress(tracks)

    # rebuild UI dataset
    rebuild_index_dataset(tracks)

    print("sync_all: done.")
