# Remove Duplicates from Sorted List

- LeetCode: https://leetcode.com/problems/remove-duplicates-from-sorted-list/
- Submission ID: 1953657092
- Submitted At: 2026-03-20T06:02:54+00:00
- Runtime: 3 ms
- Memory: 19.3 MB

## Approach
Use a single pointer curr starting at head; while curr and curr.next exist, compare curr.val with curr.next.val — if equal, remove the next node by setting curr.next = curr.next.next (do not advance curr), otherwise advance curr to curr.next. Return head.

## Complexity
- Time: O(n)
- Space: O(1)

## Revision Notes
- The list is sorted, so duplicates (if any) always appear as consecutive nodes — only need to compare curr and curr.next.
- When a duplicate is removed, do not advance curr so multiple same-valued nodes in a row are all skipped.
- Handles edge cases naturally: empty list or single-node list return head unchanged.
