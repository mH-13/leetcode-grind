"""
0151 - Reverse Words in a String (reverse_words_in_a_string)
Idea:
Time: O() | Space: O()
Tags: two-pointers, string
Link: https://leetcode.com/problems/reverse-words-in-a-string/
"""

class Solution:
    def reverseWords(self, s: str) -> str:
        return " ".join(reversed(s.split())) 
    # In short, split the string by whitespace, reverse the list of words, and join them with a single space.

        """# Alternative approach using two pointers
        n = len(s)
        left, right = 0, n - 1
        # Trim leading spaces
        while left <= right and s[left] == ' ':
            left += 1
        # Trim trailing spaces
        while left <= right and s[right] == ' ':
            right -= 1  
        # Reverse the entire string
        s = list(s[left:right + 1])
        reverse(s, 0, len(s) - 1)
        # Reverse each word in the reversed string
        start = 0
        for i in range(len(s)):
            if s[i] == ' ':
                reverse(s, start, i - 1)
                start = i + 1
        reverse(s, start, len(s) - 1)
        return ''.join(s)   """
    