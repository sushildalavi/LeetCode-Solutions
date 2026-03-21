# Remove Trailing Zeros From a String

- LeetCode: https://leetcode.com/problems/remove-trailing-zeros-from-a-string/
- Submission ID: 1955026216
- Submitted At: 2026-03-21T18:24:08+00:00
- Runtime: 7 ms
- Memory: 19.3 MB


## Approach
The solution iterates from the end of the string to find the last non-zero character, effectively trimming all trailing zeros by slicing the string up to that index.

## Complexity
- Time: O(n)
- Space: O(1)

## Revision Notes
- Iterating from the end ensures we only check until the last non-zero digit.
- Handles strings of length up to 1000 efficiently.
- Returns the original string up to the identified index, thus avoiding unnecessary conversions.
