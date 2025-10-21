"""
1431 - Kids With the Greatest Number of Candies (kids_with_the_greatest_number_of_candies)
Idea:
Time: O() | Space: O()
Tags: Array
Link: https://leetcode.com/problems/kids-with-the-greatest-number-of-candies/
"""
from typing import List
class Solution:
    def kidsWithCandies(self, candies: List[int], extraCandies: int) -> List[bool]:
        # newlist = list(candies)
        newlist= sorted(candies, reverse = True)
        # print(candies)
        # print(newlist[0])
        mx = newlist[0]
        n = len(candies)
        res = [False] * n
        for i in range(0, n):
            check = candies[i] + extraCandies
            # print(candies[i], check)
            if (check>= mx):
                res[i] = True
        return res

        

# from typing import List
# class Solution:
#     def kidsWithCandies(self, candies: List[int], extraCandies: int) -> List[bool]:
#         mx = max(candies)
#         return [candy + extraCandies >= mx for candy in candies]

if __name__ == "__main__":
    s = Solution()
    print(s.kidsWithCandies([2,3,5,1,3], 3))
