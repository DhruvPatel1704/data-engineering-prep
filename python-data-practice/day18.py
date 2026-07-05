# Problem 1: Number of Connected Components in Undirected Graph (LC #323)
# Difficulty: Medium
# Approach: Union-Find (Disjoint Set Union) — merge connected nodes
# count remaining distinct roots after all edges processed
# Key insight: Union-Find is O(alpha(n)) near constant time per operation


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.components = n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        self.components -= 1
        return True


def count_components(n, edges):
    uf = UnionFind(n)
    for u, v in edges:
        uf.union(u, v)
    return uf.components


print(count_components(5, [[0, 1], [1, 2], [3, 4]]))  # 2
print(count_components(5, [[0, 1], [1, 2], [2, 3], [3, 4]]))  # 1


# Problem 2: Graph Valid Tree (LC #261)
# Difficulty: Medium
# Approach: valid tree needs exactly n-1 edges and no cycles
# use Union-Find — cycle detected when merging already connected nodes
# Key insight: tree = connected + acyclic = n-1 edges + all nodes reachable


def valid_tree(n, edges):
    if len(edges) != n - 1:
        return False
    uf = UnionFind(n)
    for u, v in edges:
        if not uf.union(u, v):
            return False  # cycle detected
    return True


print(valid_tree(5, [[0, 1], [0, 2], [0, 3], [1, 4]]))  # True
print(valid_tree(5, [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]]))  # False


# Problem 3: Redundant Connection (LC #684)
# Difficulty: Medium
# Approach: process edges one by one, add to Union-Find
# first edge that connects two already-connected nodes is redundant
# Key insight: redundant edge creates the first cycle


def find_redundant_connection(edges):
    n = len(edges)
    uf = UnionFind(n + 1)
    for u, v in edges:
        if not uf.union(u, v):
            return [u, v]
    return []


print(find_redundant_connection([[1, 2], [1, 3], [2, 3]]))  # [2, 3]
print(find_redundant_connection([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]))  # [1, 4]


# Problem 4: Implement Trie (LC #208)
# Difficulty: Medium
# Approach: tree of TrieNodes, each node has 26 children and end flag
# insert walks the tree creating nodes, search and prefix check walk without creating
# Key insight: Trie enables O(m) word search where m = word length


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end

    def starts_with(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True


trie = Trie()
trie.insert("apple")
print(trie.search("apple"))  # True
print(trie.search("app"))  # False
print(trie.starts_with("app"))  # True
trie.insert("app")
print(trie.search("app"))  # True


# Problem 5: Word Search II (LC #212)
# Difficulty: Hard
# Approach: build Trie from word list, DFS on board using Trie
# prune search when no Trie node matches current path
# Key insight: Trie + DFS avoids searching board for each word separately


def find_words(board, words):
    root = TrieNode()
    for word in words:
        node = root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    rows, cols = len(board), len(board[0])
    result = set()

    def dfs(r, c, node, path):
        if node.is_end:
            result.add(path)
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return
        char = board[r][c]
        if char not in node.children:
            return
        board[r][c] = "#"
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            dfs(r + dr, c + dc, node.children[char], path + char)
        board[r][c] = char

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, root, "")
    return list(result)


board = [
    ["o", "a", "a", "n"],
    ["e", "t", "a", "e"],
    ["i", "h", "k", "r"],
    ["i", "f", "l", "v"],
]
words = ["oath", "pea", "eat", "rain"]
print(sorted(find_words(board, words)))  # ['eat', 'oath']


# Problem 6: Merge Intervals (LC #56)
# Difficulty: Medium
# Approach: sort by start time, merge overlapping intervals greedily
# current interval overlaps next if current end >= next start
# Key insight: after sorting, only need to compare with last merged interval


def merge(intervals):
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


print(merge([[1, 3], [2, 6], [8, 10], [15, 18]]))  # [[1,6],[8,10],[15,18]]
print(merge([[1, 4], [4, 5]]))  # [[1,5]]


# Problem 7: Insert Interval (LC #57)
# Difficulty: Medium
# Approach: three phases — add intervals before new, merge overlapping, add after
# Key insight: no need to sort again, existing intervals are already sorted


def insert(intervals, new_interval):
    result = []
    i = 0
    n = len(intervals)
    # add all intervals that end before new interval starts
    while i < n and intervals[i][1] < new_interval[0]:
        result.append(intervals[i])
        i += 1
    # merge all overlapping intervals
    while i < n and intervals[i][0] <= new_interval[1]:
        new_interval[0] = min(new_interval[0], intervals[i][0])
        new_interval[1] = max(new_interval[1], intervals[i][1])
        i += 1
    result.append(new_interval)
    # add remaining intervals
    while i < n:
        result.append(intervals[i])
        i += 1
    return result


print(insert([[1, 3], [6, 9]], [2, 5]))  # [[1,5],[6,9]]
print(
    insert([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8])
)  # [[1,2],[3,10],[12,16]]


# Problem 8: Non-overlapping Intervals (LC #435)
# Difficulty: Medium
# Approach: greedy — sort by end time, greedily keep intervals that end earliest
# count intervals that must be removed (overlap with last kept)
# Key insight: keeping earliest-ending interval leaves most room for future ones


def erase_overlap_intervals(intervals):
    intervals.sort(key=lambda x: x[1])
    removed = 0
    last_end = float("-inf")
    for start, end in intervals:
        if start >= last_end:
            last_end = end
        else:
            removed += 1
    return removed


print(erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]]))  # 1
print(erase_overlap_intervals([[1, 2], [1, 2], [1, 2]]))  # 2


# Problem 9: Meeting Rooms II (LC #253)
# Difficulty: Medium
# Approach: sort by start, use min heap to track earliest ending meeting
# if new meeting starts after earliest end, reuse that room
# Key insight: heap size at end = minimum rooms needed

import heapq


def min_meeting_rooms(intervals):
    if not intervals:
        return 0
    intervals.sort(key=lambda x: x[0])
    heap = []  # stores end times of ongoing meetings
    for start, end in intervals:
        if heap and heap[0] <= start:
            heapq.heapreplace(heap, end)
        else:
            heapq.heappush(heap, end)
    return len(heap)


print(min_meeting_rooms([[0, 30], [5, 10], [15, 20]]))  # 2
print(min_meeting_rooms([[7, 10], [2, 4]]))  # 1


# Problem 10: Rotting Oranges (LC #994)
# Difficulty: Medium
# Approach: multi-source BFS starting from all rotten oranges simultaneously
# each BFS level = one minute passing
# Key insight: multi-source BFS not single-source — all rotten start together

from collections import deque


def oranges_rotting(grid):
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c, 0))
            elif grid[r][c] == 1:
                fresh += 1
    minutes = 0
    while queue:
        r, c, time = queue.popleft()
        minutes = time
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2
                fresh -= 1
                queue.append((nr, nc, time + 1))
    return minutes if fresh == 0 else -1


print(oranges_rotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]]))  # 4
print(oranges_rotting([[2, 1, 1], [0, 1, 1], [1, 0, 1]]))  # -1


# Problem 11: Jump Game II (LC #45)
# Difficulty: Medium
# Approach: greedy — track current jump boundary and next jump boundary
# increment jumps when we cross current boundary
# Key insight: O(n) greedy — only update jump count at each boundary


def jump(nums):
    jumps = 0
    current_end = 0
    farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == current_end:
            jumps += 1
            current_end = farthest
    return jumps


print(jump([2, 3, 1, 1, 4]))  # 2
print(jump([2, 3, 0, 1, 4]))  # 2


# Problem 12: Gas Station (LC #134)
# Difficulty: Medium
# Approach: if total gas >= total cost, solution always exists
# start from 0, reset start whenever running total goes negative
# Key insight: if we can not reach a station, any station before it also fails


def can_complete_circuit(gas, cost):
    total = 0
    tank = 0
    start = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        total += gas[i] - cost[i]
        if tank < 0:
            start = i + 1
            tank = 0
    return start if total >= 0 else -1


print(can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]))  # 3
print(can_complete_circuit([2, 3, 4], [3, 4, 3]))  # -1


# Problem 13: Hand of Straights (LC #846)
# Difficulty: Medium
# Approach: sort and greedily form groups starting from smallest card
# use Counter to track remaining cards
# Key insight: always start group from the smallest available card

from collections import Counter


def is_n_straight_hand(hand, group_size):
    if len(hand) % group_size != 0:
        return False
    count = Counter(hand)
    for card in sorted(count):
        if count[card] > 0:
            times = count[card]
            for i in range(group_size):
                if count[card + i] < times:
                    return False
                count[card + i] -= times
    return True


print(is_n_straight_hand([1, 2, 3, 6, 2, 3, 4, 7, 8], 3))  # True
print(is_n_straight_hand([1, 2, 3, 4, 5], 4))  # False


# Problem 14: Partition Labels (LC #763)
# Difficulty: Medium
# Approach: record last occurrence of each character
# greedily expand partition until all chars in it have no occurrence outside
# Key insight: partition ends when current index = max last occurrence seen so far


def partition_labels(s):
    last = {char: i for i, char in enumerate(s)}
    result = []
    start = 0
    end = 0
    for i, char in enumerate(s):
        end = max(end, last[char])
        if i == end:
            result.append(end - start + 1)
            start = i + 1
    return result


print(partition_labels("ababcbacadefegdehijhklij"))
# [9, 7, 8]


# Problem 15: Largest Rectangle in Histogram (LC #84)
# Difficulty: Hard
# Approach: monotonic increasing stack — pop when smaller bar found
# area for each popped bar = height * (current index - stack top - 1)
# Key insight: each bar is processed once, O(n) total


def largest_rectangle_area(heights):
    stack = []  # stores indices
    max_area = 0
    heights.append(0)  # sentinel to flush remaining stack at end
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)
    heights.pop()
    return max_area


print(largest_rectangle_area([2, 1, 5, 6, 2, 3]))  # 10
print(largest_rectangle_area([2, 4]))  # 4
