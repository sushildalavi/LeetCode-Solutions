# Minimum Time to Make Rope Colorful

<!-- metadata:begin -->
- LeetCode: https://leetcode.com/problems/minimum-time-to-make-rope-colorful/
- Difficulty: Medium
- Topic Tags: Array, String, Dynamic Programming, Greedy
- Tracked In: General Practice
- Suggested Data Structures / Patterns: Array, String, Dynamic Programming, Greedy
- Synced Solution Paths:
  - `.leetcode/minimum-time-to-make-rope-colorful/minimum-time-to-make-rope-colorful.py`
<!-- metadata:end -->

## Problem Statement
<!-- problem:begin -->
Alice has `n` balloons arranged on a rope. You are given a **0-indexed** string `colors` where `colors[i]` is the color of the `ith` balloon.

Alice wants the rope to be **colorful**. She does not want **two consecutive balloons** to be of the same color, so she asks Bob for help. Bob can remove some balloons from the rope to make it **colorful**. You are given a **0-indexed** integer array `neededTime` where `neededTime[i]` is the time (in seconds) that Bob needs to remove the `ith` balloon from the rope.

Return *the **minimum time** Bob needs to make the rope **colorful***.

**Example 1:**

```text

**Input:** colors = "abaac", neededTime = [1,2,3,4,5]
**Output:** 3
**Explanation:** In the above image, 'a' is blue, 'b' is red, and 'c' is green.
Bob can remove the blue balloon at index 2. This takes 3 seconds.
There are no longer two consecutive balloons of the same color. Total time = 3.
```

**Example 2:**

```text

**Input:** colors = "abc", neededTime = [1,2,3]
**Output:** 0
**Explanation:** The rope is already colorful. Bob does not need to remove any balloons from the rope.
```

**Example 3:**

```text

**Input:** colors = "aabaa", neededTime = [1,2,3,4,1]
**Output:** 2
**Explanation:** Bob will remove the balloons at indices 0 and 4. Each balloons takes 1 second to remove.
There are no longer two consecutive balloons of the same color. Total time = 1 + 1 = 2.
```

**Constraints:**

- `n == colors.length == neededTime.length`
- `1 <= n <= 105`
- `1 <= neededTime[i] <= 104`
- `colors` contains only lowercase English letters.
<!-- problem:end -->

## Problem Summary
Scan colors once and for each group of consecutive identical letters, remove all but the most expensive balloon in that group by accumulating the cheaper removal times. The solution uses a running max and total to compute the minimum cost.

## Data Structures Used
- Greedy
- Two Variables

## Approach
Iterate through paired (neededTime, color) values; if the color matches the previous one add the smaller of the current time and the running max to total (meaning remove the cheaper balloon) and update the running max to the larger time; if the color changes reset the running max to the current time and update prev color.

## Complexity
- Time: O(n)
- Space: O(1)

## Revision Notes
- Invariant: prev_max always stores the maximum removal time seen so far within the current consecutive-color group.
- When encountering the same color, add min(prev_max, t) — this effectively sums all times in the group except the maximum, which we keep.
- Handles edge cases naturally: single characters or all distinct colors produce total = 0; groups of length k remove sum(group) - max(group).
