# Problem 1: Best Time to Buy and Sell Stock II (LC #122)
# Difficulty: Medium
# Approach: greedy — add every positive difference between consecutive days
# Key insight: capturing every upward move = maximum profit


def max_profit(prices):
    profit = 0
    for i in range(1, len(prices)):
        if prices[i] > prices[i - 1]:
            profit += prices[i] - prices[i - 1]
    return profit


# test
print(max_profit([7, 1, 5, 3, 6, 4]))  # 7
print(max_profit([1, 2, 3, 4, 5]))  # 4
print(max_profit([7, 6, 4, 3, 1]))  # 0


# Problem 2: Longest Substring Without Repeating Characters (LC #3)
# Difficulty: Medium
# Approach: sliding window with hashmap tracking last seen index
# shrink window left when duplicate found
# Key insight: jump left pointer directly to duplicate position + 1


def length_of_longest_substring(s):
    seen = {}
    left = 0
    max_len = 0
    for right, char in enumerate(s):
        if char in seen and seen[char] >= left:
            left = seen[char] + 1
        seen[char] = right
        max_len = max(max_len, right - left + 1)
    return max_len


# test
print(length_of_longest_substring("abcabcbb"))  # 3
print(length_of_longest_substring("bbbbb"))  # 1
print(length_of_longest_substring("pwwkew"))  # 3


# Problem 3: Minimum Window Substring (LC #76)
# Difficulty: Hard
# Approach: sliding window expand right until all chars covered
# then shrink left to minimize window size
# Key insight: track have vs need counts to know when window is valid

from collections import Counter


def min_window(s, t):
    if not t or not s:
        return ""
    need = Counter(t)
    have = {}
    formed = 0
    required = len(need)
    left = 0
    min_len = float("inf")
    result = ""
    for right, char in enumerate(s):
        have[char] = have.get(char, 0) + 1
        if char in need and have[char] == need[char]:
            formed += 1
        while formed == required:
            if right - left + 1 < min_len:
                min_len = right - left + 1
                result = s[left : right + 1]
            left_char = s[left]
            have[left_char] -= 1
            if left_char in need and have[left_char] < need[left_char]:
                formed -= 1
            left += 1
    return result


# test
print(min_window("ADOBECODEBANC", "ABC"))  # "BANC"
print(min_window("a", "a"))  # "a"
print(min_window("a", "aa"))  # ""


# Problem 4: Find Minimum in Rotated Sorted Array (LC #153)
# Difficulty: Medium
# Approach: binary search — compare mid to right to decide which half is sorted
# minimum is always at the boundary of the rotation
# Key insight: if mid > right, min is in right half, else left half


def find_min(nums):
    left, right = 0, len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if nums[mid] > nums[right]:
            left = mid + 1
        else:
            right = mid
    return nums[left]


# test
print(find_min([3, 4, 5, 1, 2]))  # 1
print(find_min([4, 5, 6, 7, 0, 1, 2]))  # 0
print(find_min([11, 13, 15, 17]))  # 11


# Problem 5: Search in Rotated Sorted Array (LC #33)
# Difficulty: Medium
# Approach: binary search with rotation awareness
# determine which half is sorted, check if target falls in it
# Key insight: one half is always sorted in a rotated array


def search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1


# test
print(search([4, 5, 6, 7, 0, 1, 2], 0))  # 4
print(search([4, 5, 6, 7, 0, 1, 2], 3))  # -1
print(search([1], 0))  # -1


# Problem 6: 3Sum (LC #15)
# Difficulty: Medium
# Approach: sort array, fix one element, two pointer for remaining two
# skip duplicates to avoid duplicate triplets
# Key insight: sorting enables two pointer and duplicate skipping


def three_sum(nums):
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1
    return result


# test
print(three_sum([-1, 0, 1, 2, -1, -4]))  # [[-1,-1,2],[-1,0,1]]
print(three_sum([0, 1, 1]))  # []
print(three_sum([0, 0, 0]))  # [[0,0,0]]


# Problem 7: Container With Most Water (LC #11)
# Difficulty: Medium
# Approach: two pointers from both ends, move the shorter side inward
# Key insight: moving the taller side can never increase area


def max_area(height):
    left, right = 0, len(height) - 1
    max_water = 0
    while left < right:
        water = min(height[left], height[right]) * (right - left)
        max_water = max(max_water, water)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_water


# test
print(max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]))  # 49
print(max_area([1, 1]))  # 1


# Problem 8: Sliding Window Maximum (LC #239)
# Difficulty: Hard
# Approach: deque stores indices of useful elements in decreasing order
# front of deque is always the max of current window
# Key insight: pop from front when out of window, pop from back when smaller

from collections import deque


def max_sliding_window(nums, k):
    dq = deque()
    result = []
    for i, num in enumerate(nums):
        while dq and dq[0] < i - k + 1:
            dq.popleft()
        while dq and nums[dq[-1]] < num:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result


# test
print(max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3))  # [3,3,5,5,6,7]
print(max_sliding_window([1], 1))  # [1]


# Problem 9: Subarray Sum Equals K (LC #560)
# Difficulty: Medium
# Approach: prefix sum + hashmap
# count subarrays where prefix[j] - prefix[i] = k
# Key insight: if current_sum - k exists in map, found a valid subarray


def subarray_sum(nums, k):
    count = 0
    current_sum = 0
    prefix_counts = {0: 1}
    for num in nums:
        current_sum += num
        if current_sum - k in prefix_counts:
            count += prefix_counts[current_sum - k]
        prefix_counts[current_sum] = prefix_counts.get(current_sum, 0) + 1
    return count


# test
print(subarray_sum([1, 1, 1], 2))  # 2
print(subarray_sum([1, 2, 3], 3))  # 2


# Problem 10: Minimum Size Subarray Sum (LC #209)
# Difficulty: Medium
# Approach: sliding window — expand right, shrink left when sum >= target
# track minimum window length where sum meets condition
# Key insight: O(n) sliding window vs O(n²) brute force


def min_subarray_len(target, nums):
    left = 0
    current_sum = 0
    min_len = float("inf")
    for right in range(len(nums)):
        current_sum += nums[right]
        while current_sum >= target:
            min_len = min(min_len, right - left + 1)
            current_sum -= nums[left]
            left += 1
    return 0 if min_len == float("inf") else min_len


# test
print(min_subarray_len(7, [2, 3, 1, 2, 4, 3]))  # 2
print(min_subarray_len(4, [1, 4, 4]))  # 1
print(min_subarray_len(11, [1, 1, 1, 1, 1, 1, 1, 1]))  # 0
