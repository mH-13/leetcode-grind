# Daily Problem Solving

## Add New Problem

**Quick method:**
```bash
python scripts/new.py --type py --track leetcode-75 --id 1768 --slug merge_strings_alternately --title "Merge Strings Alternately"
```

**Manual method:**
1. Add to CSV: `tracks/leetcode-75.csv`
   ```csv
   1768,Merge Strings Alternately,merge_strings_alternately,Easy,Array / String,"string,two-pointers"
   ```

2. Create file: `python/leetcode-75/1768_merge_strings_alternately.py`
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

```bash
python scripts/sync_all.py
git add -A && git commit -m "feat(py): 1768 merge_strings_alternately"
git push
```

**File naming:** `<4-digit-id>_<snake_case_slug>.py`