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
Scan the rope once grouping consecutive equal colors and for each group remove all but the most expensive balloon to minimize total removal time. The solution keeps running totals while iterating colors and times.

## Data Structures Used
- Two Pointers
- Variables

## Approach
Iterate through colors and neededTime together, track the previous color and the maximum removal time in the current run of identical colors; when the current balloon matches the previous color, add the smaller of (current time, prev_max) to the answer and update prev_max to the larger time, otherwise start a new group.

## Complexity
- Time: O(n)
- Space: O(1)

## Revision Notes
- Invariant: prev_max is the maximum neededTime seen so far in the current consecutive-color group.
- When encountering a same-color balloon, adding min(prev_max, t) effectively deletes the cheaper balloon so only the most expensive remains.
- Edge cases: single-character or already colorful strings produce total = 0; initialization with prev_color='' and prev_max=0 handles the first element.
