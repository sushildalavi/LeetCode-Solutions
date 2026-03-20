# Pascal's Triangle

- LeetCode: https://leetcode.com/problems/pascals-triangle/
- Submission ID: 1820013261
- Submitted At: 2025-11-03T22:32:55+00:00
- Runtime: 0 ms
- Memory: 17.8 MB

## Approach
Iterate i from 0 to numRows-1, create a row of length i+1 filled with 1s, then for each inner index j (1..i-1) set row[j] = triangle[i-1][j-1] + triangle[i-1][j]; append each completed row to the triangle and return it.

## Complexity
- Time: O(numRows^2)
- Space: O(numRows^2)

## Revision Notes
- First and last elements of every row are always 1, so initialize rows with 1s and only compute inner entries.
- Inner loop runs only when i >= 2 (range 1..i-1), so numRows = 1 or 2 are handled correctly without entering the inner loop.
- Each element is computed once from two elements of the previous row, ensuring correctness and O(n^2) work overall.
