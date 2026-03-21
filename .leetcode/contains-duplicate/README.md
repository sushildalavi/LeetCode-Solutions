# Contains Duplicate

- LeetCode: https://leetcode.com/problems/contains-duplicate/
- Submission ID: 1954530092
- Submitted At: 2026-03-21T06:59:46+00:00
- Runtime: 1 ms
- Memory: 31.1 MB


## Approach
The solution checks if the length of the array `nums` is different from the length of the set created from `nums`, which automatically removes duplicates. If the lengths differ, it means there are duplicates in the array.

## Complexity
- Time: O(n)
- Space: O(n)

## Revision Notes
- Using a set efficiently checks for duplicates since it stores only unique items.
- An edge case is an empty array, which returns false since there are no elements.
- The approach handles negative numbers and large value ranges as the set can contain any integers.
