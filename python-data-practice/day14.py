# Problem 1: Two Sum (LC #1)
# Difficulty: Easy
# Approach: hashmap stores value -> index as we iterate
# check if complement (target - num) already seen
# Key insight: one pass, O(n) time vs O(n²) brute force

def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# test
print(two_sum([2, 7, 11, 15], 9))   # [0, 1]
print(two_sum([3, 2, 4], 6))        # [1, 2]


# Problem 2: Valid Anagram (LC #242)
# Difficulty: Easy
# Approach: count character frequencies using dict
# two strings are anagrams if their frequency maps are equal
# Key insight: Counter comparison is O(n), sorting is O(n log n)

from collections import Counter

def is_anagram(s, t):
    return Counter(s) == Counter(t)

# test
print(is_anagram("anagram", "nagaram"))  # True
print(is_anagram("rat", "car"))          # False


# Problem 3: Contains Duplicate (LC #217)
# Difficulty: Easy
# Approach: set lookup is O(1), add each element and check if seen
# Key insight: len(set) vs len(list) is cleaner but less explicit

def contains_duplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

# test
print(contains_duplicate([1, 2, 3, 1]))     # True
print(contains_duplicate([1, 2, 3, 4]))     # False


# Problem 4: Best Time to Buy and Sell Stock (LC #121)
# Difficulty: Easy
# Approach: track minimum price seen so far, compute profit at each step
# Key insight: one pass — no need for nested loops

def max_profit(prices):
    min_price = float('inf')
    max_profit_val = 0
    for price in prices:
        if price < min_price:
            min_price = price
        elif price - min_price > max_profit_val:
            max_profit_val = price - min_price
    return max_profit_val

# test
print(max_profit([7, 1, 5, 3, 6, 4]))  # 5
print(max_profit([7, 6, 4, 3, 1]))     # 0


# Problem 5: Valid Parentheses (LC #20)
# Difficulty: Easy
# Approach: stack — push open brackets, pop and match on close
# Key insight: stack naturally handles nesting order

def is_valid(s):
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in mapping:
            top = stack.pop() if stack else '#'
            if mapping[char] != top:
                return False
        else:
            stack.append(char)
    return not stack

# test
print(is_valid("()[]{}"))   # True
print(is_valid("(]"))       # False
print(is_valid("{[]}"))     # True


# Problem 6: Maximum Subarray (LC #53)
# Difficulty: Medium
# Approach: Kadane's algorithm — track current sum and max sum
# reset current sum to 0 when it goes negative
# Key insight: O(n) single pass, classic DE interview question

def max_subarray(nums):
    max_sum = nums[0]
    current_sum = nums[0]
    for num in nums[1:]:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    return max_sum

# test
print(max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]))  # 6
print(max_subarray([1]))                                 # 1
print(max_subarray([5, 4, -1, 7, 8]))                   # 23


# Problem 7: Group Anagrams (LC #49)
# Difficulty: Medium
# Approach: sort each word as key, group words with same sorted key
# Key insight: sorted chars are the canonical form of an anagram group

from collections import defaultdict

def group_anagrams(strs):
    groups = defaultdict(list)
    for word in strs:
        key = tuple(sorted(word))
        groups[key].append(word)
    return list(groups.values())

# test
print(group_anagrams(["eat","tea","tan","ate","nat","bat"]))
# [['eat','tea','ate'], ['tan','nat'], ['bat']]


# Problem 8: Product of Array Except Self (LC #238)
# Difficulty: Medium
# Approach: prefix product left pass, suffix product right pass
# multiply both arrays to get result without division
# Key insight: O(n) without using division — classic interview trick

def product_except_self(nums):
    n = len(nums)
    result = [1] * n
    prefix = 1
    for i in range(n):
        result[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(n - 1, -1, -1):
        result[i] *= suffix
        suffix *= nums[i]
    return result

# test
print(product_except_self([1, 2, 3, 4]))   # [24, 12, 8, 6]
print(product_except_self([-1, 1, 0, -3, 3]))  # [0, 0, 9, 0, 0]


# Problem 9: Longest Consecutive Sequence (LC #128)
# Difficulty: Medium
# Approach: convert to set, only start counting from sequence start
# sequence start = num where num-1 is NOT in set
# Key insight: O(n) because each number is visited at most twice

def longest_consecutive(nums):
    num_set = set(nums)
    longest = 0
    for num in num_set:
        if num - 1 not in num_set:
            current = num
            streak = 1
            while current + 1 in num_set:
                current += 1
                streak += 1
            longest = max(longest, streak)
    return longest

# test
print(longest_consecutive([100, 4, 200, 1, 3, 2]))  # 4
print(longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]))  # 9


# Problem 10: Top K Frequent Elements (LC #347)
# Difficulty: Medium
# Approach: count frequencies, use bucket sort by frequency
# bucket index = frequency, each bucket holds list of nums
# Key insight: bucket sort gives O(n) vs O(n log n) heap approach

def top_k_frequent(nums, k):
    count = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, freq in count.items():
        buckets[freq].append(num)
    result = []
    for i in range(len(buckets) - 1, 0, -1):
        for num in buckets[i]:
            result.append(num)
            if len(result) == k:
                return result
    return result

# test
print(top_k_frequent([1, 1, 1, 2, 2, 3], 2))  # [1, 2]
print(top_k_frequent([1], 1))                   # [1]