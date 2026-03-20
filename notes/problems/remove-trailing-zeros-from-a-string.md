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
Scan from the end to drop trailing '0' characters and return the prefix up to the last non-zero digit. Uses a single backward scan and a slice to produce the result.

## Data Structures Used
- String
- Index pointer

## Approach
Initialize an index i at the last character, decrement while characters are '0', then return the substring num[:i+1] which includes up to the last non-zero digit. This avoids building new strings in a loop.

## Complexity
- Time: O(n)
- Space: O(1)

## Revision Notes
- Invariant: loop stops at the last non-zero digit (or i = -1 if all chars were '0'), so slicing num[:i+1] yields the correct prefix.
- Edge case: input like '123' (no trailing zeros) leaves i at len(num)-1 so the full string is returned.
- Per constraints, fully-zero input ('0') is not expected; if it occurred the code would return an empty string (i = -1).
