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
Traverse the sorted linked list and remove consecutive nodes that have the same value by skipping them, returning the modified head. The solution modifies the list in-place without extra data structures.

## Data Structures Used
- Linked List
- Pointers

## Approach
Use a single pointer curr starting at head; while curr and curr.next exist, if curr.val equals curr.next.val skip the next node by setting curr.next = curr.next.next, otherwise advance curr to curr.next. Continue until end and return head.

## Complexity
- Time: O(n)
- Space: O(1)

## Revision Notes
- Invariant: list remains sorted, so duplicates only appear in consecutive positions — it's sufficient to compare curr.val with curr.next.val.
- Edge cases: handles empty list (head is None) and single-node list because the while condition requires curr and curr.next.
- In-place removal is done by relinking curr.next to curr.next.next; do not advance curr when deleting to catch multiple duplicates in a row.
