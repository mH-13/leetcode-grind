"""
0001 - Two Sum (two_sum)
Idea: Hash map value->index (single pass)
Time: O(n) | Space: O(n)
Tags: hashmap, array
Link: https://leetcode.com/problems/two-sum/
"""
from typing import List

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}
        for i, x in enumerate(nums):
            need = target - x
            if need in seen:
                return [seen[need], i]
            seen[x] = i
        return []
