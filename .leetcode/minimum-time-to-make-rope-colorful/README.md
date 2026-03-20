# Minimum Time to Make Rope Colorful

- LeetCode: https://leetcode.com/problems/minimum-time-to-make-rope-colorful/
- Submission ID: 1820020133
- Submitted At: 2025-11-03T22:49:46+00:00
- Runtime: 96 ms
- Memory: 26.4 MB

## Approach
Iterate through colors and neededTime together, track the previous color and the maximum removal time in the current run of identical colors; when the current balloon matches the previous color, add the smaller of (current time, prev_max) to the answer and update prev_max to the larger time, otherwise start a new group.

## Complexity
- Time: O(n)
- Space: O(1)

## Revision Notes
- Invariant: prev_max is the maximum neededTime seen so far in the current consecutive-color group.
- When encountering a same-color balloon, adding min(prev_max, t) effectively deletes the cheaper balloon so only the most expensive remains.
- Edge cases: single-character or already colorful strings produce total = 0; initialization with prev_color='' and prev_max=0 handles the first element.
