# leetcode-grind

Track-based LeetCode repo with pattern tags and a tiny filterable UI.

## Tracks
- LeetCode 75 (Python)
- Top Interview 150 (Python)
- SQL 50 (SQL)

## Folders
- `tracks/*.csv` — source of truth lists
- `python/<track>/<id>_<slug>.py` — solutions (Python)
- `sql/<track>/<id>_<slug>.sql` — solutions (SQL)
- `docs/` — static UI (GitHub Pages)
- `scripts/` — helper scripts

## Progress
<!-- PROGRESS:lc75:start -->Leetcode 75: 2/75 (3%)<!-- PROGRESS:lc75:end -->
<!-- PROGRESS:ti150:start -->Top Interview 150: 0/5 (0%)<!-- PROGRESS:ti150:end -->
<!-- PROGRESS:sql50:start -->Sql 50: 1/4 (25%)<!-- PROGRESS:sql50:end -->

## Daily flow
1. Append a row to the track CSV (id/title/slug/difficulty/category/tags).
2. Create `python/.../<id>_<slug>.py` or `sql/.../<id>_<slug>.sql` with the header block + code.
3. Run `python scripts/sync_all.py` to refresh checklists, README, and UI JSON.
4. Commit & push.

## UI (GitHub Pages)
Enable Pages for this repo (Settings → Pages → Source: `docs/`).  
Live showcase: `https://mh-13.github.io/leetcode-grind/`
