# Valid Anagram

- LeetCode: https://leetcode.com/problems/valid-anagram/
- Submission ID: 1955026472
- Submitted At: 2026-03-21T18:24:25+00:00
- Runtime: 11 ms
- Memory: 19.3 MB


## Approach
The solution checks if two strings are anagrams by counting the frequency of each character in the first string and then decrementing those counts with characters from the second string, returning false if any character count goes negative or if characters are mismatched.

## Complexity
- Time: O(n)
- Space: O(1)

## Revision Notes
- Properly handles different character frequencies by using a dictionary to count characters.
- If the lengths of the strings differ, it immediately returns false.
- Counter values must remain non-negative throughout the comparison.
