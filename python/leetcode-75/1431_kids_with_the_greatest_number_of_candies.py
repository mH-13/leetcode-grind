"""
1431 - Kids With the Greatest Number of Candies (kids_with_the_greatest_number_of_candies)
Idea: find max, check if each kid + extra >= max
Time: O(n) | Space: O(1)
Tags: array
Link: https://leetcode.com/problems/kids-with-the-greatest-number-of-candies/
"""

class Solution:
    def kidsWithCandies(self, candies: list[int], extraCandies: int) -> list[bool]:
        max_candies = max(candies)
        return [candy + extraCandies >= max_candies for candy in candies]