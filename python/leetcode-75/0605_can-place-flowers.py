"""
0605 - Can Place Flowers (can-place-flowers)
Idea:
Time: O() | Space: O()
Tags: array, greedy
Link: https://leetcode.com/problems/can-place-flowers/
"""
from typing import List
class Solution:
    def canPlaceFlowers(self, flowerbed: List[int], n: int) -> bool:
        length = len(flowerbed)
        res = False
        count = 0
        if length >1:
            if flowerbed[0] == 0 and flowerbed[1] == 0:
                count += 1
                flowerbed[0] = 1
        
        # print("coutn",count)

            for i in range(1, length-1):
                # print("I: ", i)
                if flowerbed[i] == 1:
                    # print("yo:",[flowerbed[i]])
                    continue
                elif flowerbed[i-1] == 0 and flowerbed[i+1] == 0:
                    # print("h", flowerbed[i])
                    flowerbed[i] = 1
                    count += 1
            if flowerbed[length-2] == 0 and flowerbed[length-1]== 0:
                count += 1
            # print("coutn",count)

        else:
            if flowerbed[0] == 0:
                count+=1
        
        if count >= n: 
            res = True
        return res


if __name__ == "__main__":
    s = Solution()
    print(s.canPlaceFlowers([1,0,0,0,1], 1))  # True
    print(s.canPlaceFlowers([1,0,0,0,1], 2))  # False
    print(s.canPlaceFlowers([0], 1))          # True
    print(s.canPlaceFlowers([0,0], 1))        # True
    print(s.canPlaceFlowers([1,0], 1))        # False
