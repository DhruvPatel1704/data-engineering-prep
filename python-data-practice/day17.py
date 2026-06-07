# Problem 1: Validate Binary Search Tree (LC #98)
# Difficulty: Medium
# Approach: pass min and max bounds down the tree recursively
# every node must be strictly within its valid range
# Key insight: bounds narrow as we go deeper — left gets upper bound, right gets lower

def is_valid_bst(root, min_val=float('-inf'), max_val=float('inf')):
    if not root:
        return True
    if root.val <= min_val or root.val >= max_val:
        return False
    return (is_valid_bst(root.left, min_val, root.val) and
            is_valid_bst(root.right, root.val, max_val))

root = TreeNode(2)
root.left = TreeNode(1)
root.right = TreeNode(3)
print(is_valid_bst(root))   # True

invalid = TreeNode(5)
invalid.left = TreeNode(1)
invalid.right = TreeNode(4)
invalid.right.left = TreeNode(3)
invalid.right.right = TreeNode(6)
print(is_valid_bst(invalid))   # False


# Problem 2: Level Order Traversal (LC #102)
# Difficulty: Medium
# Approach: BFS with queue — process one level at a time
# snapshot queue length at start of each level to know when level ends
# Key insight: len(queue) at start of each iteration = current level size

from collections import deque

def level_order(root):
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level_size = len(queue)
        level = []
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result

root = TreeNode(3)
root.left = TreeNode(9)
root.right = TreeNode(20)
root.right.left = TreeNode(15)
root.right.right = TreeNode(7)
print(level_order(root))   # [[3], [9, 20], [15, 7]]


# Problem 3: Binary Tree Right Side View (LC #199)
# Difficulty: Medium
# Approach: BFS level order, take the last element of each level
# Key insight: rightmost node at each level is the last one processed

def right_side_view(root):
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level_size = len(queue)
        for i in range(level_size):
            node = queue.popleft()
            if i == level_size - 1:
                result.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return result

root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.right = TreeNode(5)
root.right.right = TreeNode(4)
print(right_side_view(root))   # [1, 3, 4]


# Problem 4: Lowest Common Ancestor of BST (LC #235)
# Difficulty: Medium
# Approach: use BST property — if both nodes smaller go left, both larger go right
# when they diverge or one equals root, that is the LCA
# Key insight: no need to traverse whole tree — BST property guides direction

def lowest_common_ancestor(root, p, q):
    while root:
        if p.val < root.val and q.val < root.val:
            root = root.left
        elif p.val > root.val and q.val > root.val:
            root = root.right
        else:
            return root
    return None

root = TreeNode(6)
root.left = TreeNode(2)
root.right = TreeNode(8)
root.left.left = TreeNode(0)
root.left.right = TreeNode(4)
p, q = TreeNode(2), TreeNode(8)
print(lowest_common_ancestor(root, p, q).val)   # 6


# Problem 5: Number of Islands (LC #200)
# Difficulty: Medium
# Approach: DFS — when land cell found, flood fill the whole island with water
# count each flood fill as one island
# Key insight: modifying grid in place avoids visited set

def num_islands(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    count = 0

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == '0':
            return
        grid[r][c] = '0'   # mark visited by sinking the land
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                dfs(r, c)
                count += 1
    return count

grid1 = [["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]]
print(num_islands(grid1))   # 1

grid2 = [["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]
print(num_islands(grid2))   # 3


# Problem 6: Clone Graph (LC #133)
# Difficulty: Medium
# Approach: DFS with hashmap mapping original node to its clone
# visit each node once, create clone, recursively clone neighbors
# Key insight: hashmap prevents infinite loops and duplicate cloning

class GraphNode:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

def clone_graph(node):
    if not node:
        return None
    cloned = {}

    def dfs(n):
        if n in cloned:
            return cloned[n]
        clone = GraphNode(n.val)
        cloned[n] = clone
        for neighbor in n.neighbors:
            clone.neighbors.append(dfs(neighbor))
        return clone

    return dfs(node)


# Problem 7: Course Schedule (LC #207)
# Difficulty: Medium
# Approach: detect cycle in directed graph using DFS with three states
# 0 = unvisited, 1 = visiting (in current path), 2 = visited (safe)
# Key insight: if we reach a node currently being visited, cycle exists

def can_finish(num_courses, prerequisites):
    graph = [[] for _ in range(num_courses)]
    for course, prereq in prerequisites:
        graph[prereq].append(course)

    state = [0] * num_courses   # 0=unvisited 1=visiting 2=done

    def dfs(node):
        if state[node] == 1:
            return False   # cycle detected
        if state[node] == 2:
            return True    # already verified safe
        state[node] = 1
        for neighbor in graph[node]:
            if not dfs(neighbor):
                return False
        state[node] = 2
        return True

    return all(dfs(i) for i in range(num_courses))

print(can_finish(2, [[1, 0]]))          # True
print(can_finish(2, [[1, 0], [0, 1]])) # False (cycle)


# Problem 8: Pacific Atlantic Water Flow (LC #417)
# Difficulty: Medium
# Approach: reverse DFS from both oceans — find cells that can reach each ocean
# answer is intersection of both reachable sets
# Key insight: reverse direction — instead of water flowing down, flow UP from ocean

def pacific_atlantic(heights):
    rows, cols = len(heights), len(heights[0])
    pacific = set()
    atlantic = set()

    def dfs(r, c, visited, prev_height):
        if (r, c) in visited or r < 0 or r >= rows or c < 0 or c >= cols:
            return
        if heights[r][c] < prev_height:
            return
        visited.add((r, c))
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            dfs(r + dr, c + dc, visited, heights[r][c])

    for r in range(rows):
        dfs(r, 0, pacific, heights[r][0])
        dfs(r, cols - 1, atlantic, heights[r][cols - 1])
    for c in range(cols):
        dfs(0, c, pacific, heights[0][c])
        dfs(rows - 1, c, atlantic, heights[rows - 1][c])

    return list(pacific & atlantic)

print(len(pacific_atlantic([[1,2,2,3,5],[3,2,3,4,4],[2,4,5,3,1],[6,7,1,4,5],[5,1,1,2,4]])))   # 7


# Problem 9: Word Search (LC #79)
# Difficulty: Medium
# Approach: backtracking DFS from each cell — mark visited, explore, unmark
# Key insight: in-place marking avoids visited set, unmark on backtrack

def exist(board, word):
    rows, cols = len(board), len(board[0])

    def dfs(r, c, idx):
        if idx == len(word):
            return True
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return False
        if board[r][c] != word[idx]:
            return False
        temp = board[r][c]
        board[r][c] = '#'   # mark visited
        found = (dfs(r+1,c,idx+1) or dfs(r-1,c,idx+1) or
                 dfs(r,c+1,idx+1) or dfs(r,c-1,idx+1))
        board[r][c] = temp  # unmark on backtrack
        return found

    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0):
                return True
    return False

board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]]
print(exist(board, "ABCCED"))   # True
print(exist(board, "SEE"))      # True
print(exist(board, "ABCB"))     # False


# Problem 10: Subsets (LC #78)
# Difficulty: Medium
# Approach: backtracking — at each step choose to include or exclude element
# Key insight: add current subset at every recursive call, not just at leaf

def subsets(nums):
    result = []

    def backtrack(start, current):
        result.append(current[:])
        for i in range(start, len(nums)):
            current.append(nums[i])
            backtrack(i + 1, current)
            current.pop()

    backtrack(0, [])
    return result

print(subsets([1, 2, 3]))
# [[], [1], [1,2], [1,2,3], [1,3], [2], [2,3], [3]]


# Problem 11: Combination Sum (LC #39)
# Difficulty: Medium
# Approach: backtracking — can reuse same element, subtract from target
# Key insight: allow same index to be picked again (i not i+1)

def combination_sum(candidates, target):
    result = []

    def backtrack(start, current, remaining):
        if remaining == 0:
            result.append(current[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                break
            current.append(candidates[i])
            backtrack(i, current, remaining - candidates[i])
            current.pop()

    candidates.sort()
    backtrack(0, [], target)
    return result

print(combination_sum([2, 3, 6, 7], 7))   # [[2,2,3],[7]]
print(combination_sum([2, 3, 5], 8))       # [[2,2,2,2],[2,3,3],[3,5]]


# Problem 12: Permutations (LC #46)
# Difficulty: Medium
# Approach: backtracking — build permutation by swapping elements
# Key insight: swap element into current position, recurse, swap back

def permutations(nums):
    result = []

    def backtrack(start):
        if start == len(nums):
            result.append(nums[:])
            return
        for i in range(start, len(nums)):
            nums[start], nums[i] = nums[i], nums[start]
            backtrack(start + 1)
            nums[start], nums[i] = nums[i], nums[start]

    backtrack(0)
    return result

print(len(permutations([1, 2, 3])))   # 6


# Problem 13: Find Median from Data Stream (LC #295)
# Difficulty: Hard
# Approach: two heaps — max heap for lower half, min heap for upper half
# balance heaps so sizes differ by at most 1
# Key insight: Python only has min heap, negate values for max heap

import heapq

class MedianFinder:
    def __init__(self):
        self.small = []   # max heap (negated) for lower half
        self.large = []   # min heap for upper half

    def add_num(self, num):
        heapq.heappush(self.small, -num)
        if self.small and self.large and (-self.small[0] > self.large[0]):
            heapq.heappush(self.large, -heapq.heappop(self.small))
        if len(self.small) > len(self.large) + 1:
            heapq.heappush(self.large, -heapq.heappop(self.small))
        if len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))

    def find_median(self):
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0]) / 2

mf = MedianFinder()
mf.add_num(1)
mf.add_num(2)
print(mf.find_median())   # 1.5
mf.add_num(3)
print(mf.find_median())   # 2.0


# Problem 14: Kth Largest Element in Array (LC #215)
# Difficulty: Medium
# Approach: min heap of size k — maintain k largest elements seen
# top of heap is the kth largest
# Key insight: O(n log k) vs O(n log n) sorting

def find_kth_largest(nums, k):
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]

print(find_kth_largest([3, 2, 1, 5, 6, 4], 2))   # 5
print(find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4))   # 4


# Problem 15: Task Scheduler (LC #621)
# Difficulty: Medium
# Approach: most frequent task determines minimum intervals
# formula: (max_count - 1) * (n + 1) + tasks_with_max_count
# Key insight: greedy — always schedule most frequent remaining task

from collections import Counter

def least_interval(tasks, n):
    counts = Counter(tasks)
    max_count = max(counts.values())
    tasks_with_max = sum(1 for c in counts.values() if c == max_count)
    result = (max_count - 1) * (n + 1) + tasks_with_max
    return max(result, len(tasks))

print(least_interval(["A","A","A","B","B","B"], 2))   # 8
print(least_interval(["A","A","A","B","B","B"], 0))   # 6


# Problem 16: Unique Paths (LC #62)
# Difficulty: Medium
# Approach: DP — paths to cell (i,j) = paths from above + paths from left
# Key insight: first row and first column all have exactly 1 path

def unique_paths(m, n):
    dp = [[1] * n for _ in range(m)]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i-1][j] + dp[i][j-1]
    return dp[m-1][n-1]

print(unique_paths(3, 7))   # 28
print(unique_paths(3, 2))   # 3


# Problem 17: Jump Game (LC #55)
# Difficulty: Medium
# Approach: greedy — track maximum reachable index as we scan
# if current index exceeds max reach, we are stuck
# Key insight: O(n) one pass — no DP needed

def can_jump(nums):
    max_reach = 0
    for i, jump in enumerate(nums):
        if i > max_reach:
            return False
        max_reach = max(max_reach, i + jump)
    return True

print(can_jump([2, 3, 1, 1, 4]))   # True
print(can_jump([3, 2, 1, 0, 4]))   # False


# Problem 18: Longest Increasing Subsequence (LC #300)
# Difficulty: Medium
# Approach: patience sorting with binary search — maintain piles
# dp array stores smallest tail of each LIS length
# Key insight: O(n log n) with bisect vs O(n^2) naive DP

import bisect

def length_of_lis(nums):
    dp = []
    for num in nums:
        pos = bisect.bisect_left(dp, num)
        if pos == len(dp):
            dp.append(num)
        else:
            dp[pos] = num
    return len(dp)

print(length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]))   # 4
print(length_of_lis([0, 1, 0, 3, 2, 3]))              # 4


# Problem 19: Word Break (LC #139)
# Difficulty: Medium
# Approach: DP — dp[i] is True if s[:i] can be segmented using wordDict
# for each position check all possible last words ending there
# Key insight: build solution from smaller subproblems

def word_break(s, wordDict):
    word_set = set(wordDict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True   # empty string is always breakable
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break
    return dp[n]

print(word_break("leetcode", ["leet", "code"]))          # True
print(word_break("applepenapple", ["apple", "pen"]))     # True
print(word_break("catsandog", ["cats", "dog", "sand"]))  # False


# Problem 20: Decode Ways (LC #91)
# Difficulty: Medium
# Approach: DP — dp[i] = ways to decode s[:i]
# at each position check single digit and two digit decodings
# Key insight: leading zeros make single digit invalid, check both one and two char

def num_decodings(s):
    if not s or s[0] == '0':
        return 0
    n = len(s)
    dp = [0] * (n + 1)
    dp[0] = 1
    dp[1] = 1
    for i in range(2, n + 1):
        one_digit = int(s[i-1])
        two_digit = int(s[i-2:i])
        if one_digit != 0:
            dp[i] += dp[i-1]
        if 10 <= two_digit <= 26:
            dp[i] += dp[i-2]
    return dp[n]

print(num_decodings("12"))    # 2
print(num_decodings("226"))   # 3
print(num_decodings("06"))    # 0