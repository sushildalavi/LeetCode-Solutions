# Valid Anagram

- LeetCode: https://leetcode.com/problems/valid-anagram/
- Submission ID: 1954530510
- Submitted At: 2026-03-21T07:00:21+00:00
- Runtime: 11 ms
- Memory: 19.2 MB


## Approach
The solution checks if two strings are anagrams by first ensuring they are of the same length, then counting the occurrences of each character in the first string, and subsequently decrementing the counts based on the second string. If any count goes negative or a character from the second string is missing, it returns false.

## Complexity
- Time: O(n)
- Space: O(1)

## Revision Notes
- Length check ensures early exit for unequal lengths, optimizing runtime.
- Character counts handle duplicates correctly, making it suitable for varying character occurrences.
- The solution utilizes a dictionary which effectively manages character frequency counts.
