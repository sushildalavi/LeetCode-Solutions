# Contains Duplicate

- LeetCode: https://leetcode.com/problems/contains-duplicate/
- Submission ID: 1953690435
- Submitted At: 2026-03-20T06:45:37+00:00
- Runtime: 12 ms
- Memory: 32.3 MB


## Approach
The solution leverages a set to identify duplicates by comparing the length of the original list `nums` with the length of the set created from `nums`. If there are duplicates, the set will have fewer elements, leading to a boolean return value.

## Complexity
- Time: O(n)
- Space: O(n)

## Revision Notes
- Using a set efficiently checks for duplicates since it only keeps unique items.
- Key invariant: if the lengths differ, then at least one duplicate exists.
- Handles edge cases of empty arrays or arrays with a single element, returning false.
