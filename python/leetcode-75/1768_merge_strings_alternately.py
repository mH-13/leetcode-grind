"""
1768 - Merge Strings Alternately (merge_strings_alternately)
Idea: two pointers, alternate characters from both strings
Time: O(n) | Space: O(1)
Tags: string, two-pointers
Link: https://leetcode.com/problems/merge-strings-alternately/
"""

class Solution:
    def mergeAlternately(self, word1: str, word2: str) -> str:
        result = []
        i = j = 0
        
        while i < len(word1) and j < len(word2):
            result.append(word1[i])
            result.append(word2[j])
            i += 1
            j += 1
        
        result.extend(word1[i:])
        result.extend(word2[j:])
        
        return ''.join(result)
