from typing import List

class Solution:
    def minCost(self, colors: str, neededTime: List[int]) -> int:
        total = 0
        prev_color = ''
        prev_max = 0  

        for t, c in zip(neededTime, colors):
            if c == prev_color:
                total += min(prev_max, t) 
                prev_max = max(prev_max, t)
            else:
                prev_color = c
                prev_max = t

        return total