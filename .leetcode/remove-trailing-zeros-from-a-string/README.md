# Remove Trailing Zeros From a String

- LeetCode: https://leetcode.com/problems/remove-trailing-zeros-from-a-string/
- Submission ID: 1954529984
- Submitted At: 2026-03-21T06:59:37+00:00
- Runtime: 7 ms
- Memory: 19.3 MB


## Approach
The solution iterates from the end of the string, decrementing the index until it finds a non-zero character, and then returns the substring up to that index which effectively removes the trailing zeros.

## Complexity
- Time: O(n)
- Space: O(1)

## Revision Notes
- Handles strings up to 1000 characters efficiently.
- Iterates from the end, ensuring minimal checks.
- Returns the entire string if no zeros are found.
