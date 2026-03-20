# Remove Duplicates from Sorted List

<!-- metadata:begin -->
- LeetCode: https://leetcode.com/problems/remove-duplicates-from-sorted-list/
- Difficulty: Easy
- Topic Tags: Linked List
- Tracked In: General Practice
- Suggested Data Structures / Patterns: Linked List
- Synced Solution Paths:
  - `.leetcode/remove-duplicates-from-sorted-list/remove-duplicates-from-sorted-list.py`
<!-- metadata:end -->

## Problem Statement
<!-- problem:begin -->
Given the `head` of a sorted linked list, *delete all duplicates such that each element appears only once*. Return *the linked list **sorted** as well*.

**Example 1:**

```text

**Input:** head = [1,1,2]
**Output:** [1,2]
```

**Example 2:**

```text

**Input:** head = [1,1,2,3,3]
**Output:** [1,2,3]
```

**Constraints:**

- The number of nodes in the list is in the range `[0, 300]`.
- `-100 <= Node.val <= 100`
- The list is guaranteed to be **sorted** in ascending order.
<!-- problem:end -->

## Problem Summary
Iterate the sorted linked list once and remove consecutive nodes with duplicate values by skipping them in-place.

## Data Structures Used
- Linked List
- Pointer

## Approach
Use a single pointer curr starting at head; while curr and curr.next exist, compare curr.val with curr.next.val — if equal, remove the next node by setting curr.next = curr.next.next (do not advance curr), otherwise advance curr to curr.next. Return head.

## Complexity
- Time: O(n)
- Space: O(1)

## Revision Notes
- The list is sorted, so duplicates (if any) always appear as consecutive nodes — only need to compare curr and curr.next.
- When a duplicate is removed, do not advance curr so multiple same-valued nodes in a row are all skipped.
- Handles edge cases naturally: empty list or single-node list return head unchanged.
