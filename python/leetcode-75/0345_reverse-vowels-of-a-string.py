"""
0345 - Reverse Vowels of a String (reverse-vowels-of-a-string)
Idea:
Time: O() | Space: O()
Tags: two-pointers, string
Link: https://leetcode.com/problems/reverse-vowels-of-a-string/
"""

class Solution:
    def reverseVowels(self, s: str) -> str:
        vowels = ['A','a', 'E','e', 'I','i', 'O','o', 'U','u']
        n =  len(s)
        # print(l)
        l = 0
        r = len(s) -1
        s = list(s)
        while(l<r):
            # print('l ',l, 'r ', r)
            if s[l] in vowels and s[r] in vowels:
                temp = s[l]
                s[l] = s[r]
                s[r] = temp
                
                l+=1
                r-=1
            elif s[l] in vowels and s[r] not in vowels:
                r-=1

            elif s[l] not in vowels and s[r] in vowels:
                l+=1
            else:
                l+=1
                r-=1
        
        return ''.join(s)


