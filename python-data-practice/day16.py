# Problem 1: Reverse Linked List (LC #206)
# Difficulty: Easy
# Approach: iterative — track prev and current, reverse pointer direction
# Key insight: three pointers, one pass O(n) — classic interview warmup

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head):
    prev = None
    curr = head
    while curr:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    return prev

# test helper
def to_list(node):
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result

def to_linked(lst):
    if not lst:
        return None
    head = ListNode(lst[0])
    curr = head
    for val in lst[1:]:
        curr.next = ListNode(val)
        curr = curr.next
    return head

head = to_linked([1, 2, 3, 4, 5])
print(to_list(reverse_list(head)))   # [5, 4, 3, 2, 1]


# Problem 2: Merge Two Sorted Lists (LC #21)
# Difficulty: Easy
# Approach: dummy head pointer simplifies edge cases
# compare values at each step, attach smaller node
# Key insight: dummy node avoids special casing the head

def merge_two_lists(list1, list2):
    dummy = ListNode(0)
    curr = dummy
    while list1 and list2:
        if list1.val <= list2.val:
            curr.next = list1
            list1 = list1.next
        else:
            curr.next = list2
            list2 = list2.next
        curr = curr.next
    curr.next = list1 or list2
    return dummy.next

l1 = to_linked([1, 2, 4])
l2 = to_linked([1, 3, 4])
print(to_list(merge_two_lists(l1, l2)))   # [1, 1, 2, 3, 4, 4]


# Problem 3: Linked List Cycle (LC #141)
# Difficulty: Easy
# Approach: Floyd's cycle detection — slow moves 1, fast moves 2
# if they meet, there is a cycle
# Key insight: O(1) space vs O(n) set approach

def has_cycle(head):
    slow = head
    fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False

print(has_cycle(to_linked([3, 2, 0, -4])))   # False (no actual cycle in test)


# Problem 4: Maximum Depth of Binary Tree (LC #104)
# Difficulty: Easy
# Approach: recursive DFS — depth = 1 + max(left depth, right depth)
# Key insight: base case is None node returning 0

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def max_depth(root):
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))

root = TreeNode(3)
root.left = TreeNode(9)
root.right = TreeNode(20)
root.right.left = TreeNode(15)
root.right.right = TreeNode(7)
print(max_depth(root))   # 3


# Problem 5: Invert Binary Tree (LC #226)
# Difficulty: Easy
# Approach: recursively swap left and right children at every node
# Key insight: post-order or pre-order both work

def invert_tree(root):
    if not root:
        return None
    root.left, root.right = invert_tree(root.right), invert_tree(root.left)
    return root

root = TreeNode(4)
root.left = TreeNode(2)
root.right = TreeNode(7)
inverted = invert_tree(root)
print(inverted.left.val, inverted.right.val)   # 7, 2


# Problem 6: Climbing Stairs (LC #70)
# Difficulty: Easy
# Approach: DP — ways to reach step n = ways(n-1) + ways(n-2)
# same as fibonacci, use two variables instead of array
# Key insight: O(1) space — only need previous two values

def climb_stairs(n):
    if n <= 2:
        return n
    prev2, prev1 = 1, 2
    for _ in range(3, n + 1):
        curr = prev1 + prev2
        prev2 = prev1
        prev1 = curr
    return prev1

print(climb_stairs(2))   # 2
print(climb_stairs(3))   # 3
print(climb_stairs(5))   # 8


# Problem 7: House Robber (LC #198)
# Difficulty: Medium
# Approach: DP — at each house choose max of (rob current + prev prev) vs (skip)
# Key insight: rob[i] = max(rob[i-2] + nums[i], rob[i-1])

def rob(nums):
    if len(nums) == 1:
        return nums[0]
    prev2, prev1 = 0, 0
    for num in nums:
        curr = max(prev1, prev2 + num)
        prev2 = prev1
        prev1 = curr
    return prev1

print(rob([1, 2, 3, 1]))      # 4
print(rob([2, 7, 9, 3, 1]))   # 12


# Problem 8: Coin Change (LC #322)
# Difficulty: Medium
# Approach: bottom-up DP — build min coins for each amount 1 to target
# dp[i] = min coins to make amount i
# Key insight: for each coin, check if using it improves dp[i]

def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1

print(coin_change([1, 5, 11], 15))    # 3 (5+5+5)
print(coin_change([2], 3))            # -1 (impossible)
print(coin_change([1, 2, 5], 11))     # 3 (5+5+1)


# Problem 9: Daily Temperatures (LC #739)
# Difficulty: Medium
# Approach: monotonic decreasing stack stores indices
# when current temp > stack top temp, found the next warmer day
# Key insight: stack stores unresolved days waiting for a warmer day

def daily_temperatures(temperatures):
    result = [0] * len(temperatures)
    stack = []   # stores indices of unresolved days
    for i, temp in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < temp:
            idx = stack.pop()
            result[idx] = i - idx   # days until warmer
        stack.append(i)
    return result

print(daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]))
# [1, 1, 4, 2, 1, 1, 0, 0]


# Problem 10: Min Stack (LC #155)
# Difficulty: Medium
# Approach: maintain two stacks — main stack and min stack
# min stack tracks the minimum at each level
# Key insight: push to min stack only when value <= current min

class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []

    def push(self, val):
        self.stack.append(val)
        if not self.min_stack or val <= self.min_stack[-1]:
            self.min_stack.append(val)

    def pop(self):
        val = self.stack.pop()
        if val == self.min_stack[-1]:
            self.min_stack.pop()

    def top(self):
        return self.stack[-1]

    def get_min(self):
        return self.min_stack[-1]

ms = MinStack()
ms.push(-2)
ms.push(0)
ms.push(-3)
print(ms.get_min())   # -3
ms.pop()
print(ms.top())       # 0
print(ms.get_min())   # -2