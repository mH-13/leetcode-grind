# Daily Problem Solving

## Add New Problem

**🎉 NEW: Interactive Wizard (Easiest!):**
```bash
./daily.sh
```
- 🧙 Guided wizard walks you through each step
- ✨ Auto-creates files with proper headers
- 📝 Updates CSV automatically
- 🔄 Syncs all trackers
- 🎯 Optional git commit & push - all in one command!

**Command-line method:**
```bash
python scripts/new.py --type py --track leetcode-75 --id 1768 --slug merge_strings_alternately --title "Merge Strings Alternately"
```
- Creates file automatically with proper header
- Adds CSV entry if missing
- Ready to code - just add your solution

**Manual method (only if you prefer):**
1. Create file: `python/leetcode-75/1768_merge_strings_alternately.py`
   ```python
   """
   1768 - Merge Strings Alternately (merge_strings_alternately)
   Idea:
   Time: O() | Space: O()
   Tags:
   Link: https://leetcode.com/problems/merge-strings-alternately/
   """

   class Solution:
       def mergeAlternately(self, word1: str, word2: str) -> str:
           # Your solution
           pass
   ```

## Sync Changes

**If using interactive wizard:** All done automatically! 🎉

**If using manual method:**
```bash
python scripts/sync_all.py
git add -A && git commit -m "feat(py): 1768 merge_strings_alternately"
git push
```

---

## 🌟 New Features

### Interactive Dashboard
Visit your GitHub Pages URL to see:
- 📊 Progress analytics with animated counters
- 📅 GitHub-style activity heatmap
- 🔥 Streak tracker
- 📈 Difficulty distribution charts
- 🏷️ Tag cloud visualization
- 🌓 Dark/Light theme toggle

### Easier Workflow
The new wizard (`./daily.sh`) makes daily problem tracking effortless:
1. Answer a few questions
2. Get a perfectly formatted file
3. Optional auto-commit and push
4. Start coding immediately!

**See [NEW_FEATURES.md](./NEW_FEATURES.md) for detailed guide!**