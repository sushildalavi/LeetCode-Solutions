# Pascal's Triangle

<!-- metadata:begin -->
- LeetCode: https://leetcode.com/problems/pascals-triangle/
- Difficulty: Easy
- Topic Tags: Array, Dynamic Programming
- Tracked In: Striver's SDE Sheet (LeetCode-backed)
- Suggested Data Structures / Patterns: Array, Dynamic Programming
- Synced Solution Paths:
  - `.leetcode/pascals-triangle/pascals-triangle.py`
<!-- metadata:end -->

## Problem Statement
<!-- problem:begin -->
Given an integer `numRows`, return the first numRows of **Pascal's triangle**.

In **Pascal's triangle**, each number is the sum of the two numbers directly above it as shown:

**Example 1:**

```text
**Input:** numRows = 5
**Output:** [[1],[1,1],[1,2,1],[1,3,3,1],[1,4,6,4,1]]
```

**Example 2:**

```text
**Input:** numRows = 1
**Output:** [[1]]
```

**Constraints:**

- `1 <= numRows <= 30`
<!-- problem:end -->

## Problem Summary
Builds Pascal's triangle row by row using previously computed rows. Each row is initialized with 1s and inner elements are filled as sums of two values from the prior row.

## Data Structures Used
- Array
- List

## Approach
Iterate i from 0 to numRows-1, create a row of length i+1 filled with 1s, and for each inner index j (1..i-1) set row[j] = triangle[i-1][j-1] + triangle[i-1][j]; append the row to the result.

## Complexity
- Time: O(numRows^2)
- Space: O(numRows^2)

## Revision Notes
- First and last elements of each row remain 1, only fill indices 1..i-1 from previous row.
- Works for edge case numRows = 1 since loop runs once producing [1].
- Triangle stores all rows so later rows reference triangle[i-1] directly.
