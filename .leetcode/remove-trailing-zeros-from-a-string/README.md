# Remove Trailing Zeros From a String

- LeetCode: https://leetcode.com/problems/remove-trailing-zeros-from-a-string/
- Submission ID: 1953612618
- Submitted At: 2026-03-20T05:03:20+00:00
- Runtime: 7 ms
- Memory: 19.1 MB

## Approach
Initialize i to the last index, decrement i while num[i] == '0', then return num[:i+1]; this removes all trailing '0' characters by finding the last non-zero position and slicing.

## Complexity
- Time: O(n)
- Space: O(1)

## Revision Notes
- Invariant: after the loop, i points to the last non-zero digit (or -1 if none found).
- Edge case: if there are no trailing zeros the slice returns the original string; if all characters are '0' the result is an empty string (not expected for positive non-zero inputs).
- Slicing up to i+1 produces the prefix containing the number without trailing zeros without character-by-character reconstruction.
