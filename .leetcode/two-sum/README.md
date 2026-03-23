# Two Sum

- LeetCode: https://leetcode.com/problems/two-sum/
- Submission ID: 1956424045
- Submitted At: 2026-03-23T06:40:20+00:00
- Runtime: 0 ms
- Memory: 20.5 MB


## Approach
The solution uses a hash map to store indices of previously seen numbers, allowing for efficient lookup of the complement needed to reach the target sum while iterating through the list once.

## Complexity
- Time: O(n)
- Space: O(n)

## Revision Notes
- The hash map 'seen' maps each number to its index for quick retrieval.
- Each number's complement (target - current number) is checked against the hash map.
- Only one valid solution exists, which simplifies the search process.
