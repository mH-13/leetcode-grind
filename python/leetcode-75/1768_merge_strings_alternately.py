"""
1768 - Merge Strings Alternately (merge_strings_alternately)
Idea: two pointers, alternate characters from both strings
Time: O(n) | Space: O(1)
Tags: string, two-pointers
Link: https://leetcode.com/problems/merge-strings-alternately/
"""

class Solution:
    def mergeAlternately(self, word1: str, word2: str) -> str:
        res = []
        i = j = 0
        
        while i < len(word1) and j < len(word2):
            res.append(word1[i])
            res.append(word2[j])
            i += 1
            j += 1
        
        res.extend(word1[i:])
        res.extend(word2[j:])
        
        return ''.join(res)
