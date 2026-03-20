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
Construct Pascal's triangle row by row, initializing each row with 1s and filling inner entries by summing two values from the previous row.

## Data Structures Used
- Array
- List

## Approach
Iterate i from 0 to numRows-1, create a row of length i+1 filled with 1s, then for each inner index j (1..i-1) set row[j] = triangle[i-1][j-1] + triangle[i-1][j]; append each completed row to the triangle and return it.

## Complexity
- Time: O(numRows^2)
- Space: O(numRows^2)

## Revision Notes
- First and last elements of every row are always 1, so initialize rows with 1s and only compute inner entries.
- Inner loop runs only when i >= 2 (range 1..i-1), so numRows = 1 or 2 are handled correctly without entering the inner loop.
- Each element is computed once from two elements of the previous row, ensuring correctness and O(n^2) work overall.
