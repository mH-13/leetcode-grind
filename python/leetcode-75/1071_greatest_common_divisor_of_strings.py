"""
1071 - Greatest Common Divisor of Strings (greatest_common_divisor_of_strings)
Idea:
Time: O() | Space: O()
Tags: math, string
Link: https://leetcode.com/problems/greatest-common-divisor-of-strings/
"""

class Solution:
    def gcdOfStrings(self, str1: str, str2: str) -> str:
        len1 = len(str1)
        len2 = len(str2)

        def validation(k):
            if len1 % k or len2 % k:
                return False

            n1 = len1 // k
            n2 = len2 // k
            base = str1[:k]
            #print("n1", n1, "n2", n2, "base", base)

            return str1 == n1 * base and str2 == n2*base

        for i in range(min(len1, len2), 0, -1):
            #print("i:  ", i)
            if validation(i):
                #print("str1[:i] ", str1[:i])
                return str1[:i]

        return ""

