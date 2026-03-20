# Remove Trailing Zeros From a String

<!-- metadata:begin -->
- LeetCode: https://leetcode.com/problems/remove-trailing-zeros-from-a-string/
- Difficulty: Easy
- Topic Tags: String
- Tracked In: General Practice
- Suggested Data Structures / Patterns: String
- Synced Solution Paths:
  - `.leetcode/remove-trailing-zeros-from-a-string/remove-trailing-zeros-from-a-string.py`
<!-- metadata:end -->

## Problem Statement
<!-- problem:begin -->
Given a **positive** integer `num` represented as a string, return *the integer *`num`* without trailing zeros as a string*.

**Example 1:**

```text

**Input:** num = "51230100"
**Output:** "512301"
**Explanation:** Integer "51230100" has 2 trailing zeros, we remove them and return integer "512301".
```

**Example 2:**

```text

**Input:** num = "123"
**Output:** "123"
**Explanation:** Integer "123" has no trailing zeros, we return integer "123".
```

**Constraints:**

- `1 <= num.length <= 1000`
- `num` consists of only digits.
- `num` doesn't have any leading zeros.
<!-- problem:end -->

## Problem Summary
Scan from the string's end to find the last non-zero digit and return the prefix up to it. The solution decrements an index while characters are '0' and slices the string.

## Data Structures Used
- String

## Approach
Initialize i to the last index, decrement i while num[i] == '0', then return num[:i+1]; this removes all trailing '0' characters by finding the last non-zero position and slicing.

## Complexity
- Time: O(n)
- Space: O(1)

## Revision Notes
- Invariant: after the loop, i points to the last non-zero digit (or -1 if none found).
- Edge case: if there are no trailing zeros the slice returns the original string; if all characters are '0' the result is an empty string (not expected for positive non-zero inputs).
- Slicing up to i+1 produces the prefix containing the number without trailing zeros without character-by-character reconstruction.
