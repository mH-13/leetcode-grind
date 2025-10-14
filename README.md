# leetcode-grind

Track-based LeetCode repo with pattern tags, interactive dashboard, and hassle-free daily workflow!

✨ **NEW**: Interactive CLI wizard, analytics dashboard, calendar heatmap, dark/light themes!

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
<!-- PROGRESS:lc75:start -->Leetcode 75: 4/76 (5%)<!-- PROGRESS:lc75:end -->
<!-- PROGRESS:ti150:start -->Top Interview 150: 0/5 (0%)<!-- PROGRESS:ti150:end -->
<!-- PROGRESS:sql50:start -->Sql 50: 1/4 (25%)<!-- PROGRESS:sql50:end -->

## Daily flow (NEW! 🎉)

**Quick method (recommended):**
```bash
./daily.sh
```
Interactive wizard handles everything: file creation, CSV updates, sync, git commit & push!

**Manual method:**
1. Append a row to the track CSV (id/title/slug/difficulty/category/tags).
2. Create `python/.../<id>_<slug>.py` or `sql/.../<id>_<slug>.sql` with the header block + code.
3. Run `python scripts/sync_all.py` to refresh checklists, README, and UI JSON.
4. Commit & push.

**See [NEW_FEATURES.md](./NEW_FEATURES.md) for complete guide!**

## UI (GitHub Pages)
Enable Pages for this repo (Settings → Pages → Source: `docs/`).
Live showcase: `https://mh-13.github.io/leetcode-grind/`

**💡 Seeing old version?** Press `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac) for hard reload.
See [CACHE_CLEARING_GUIDE.md](./CACHE_CLEARING_GUIDE.md) for detailed solutions.
