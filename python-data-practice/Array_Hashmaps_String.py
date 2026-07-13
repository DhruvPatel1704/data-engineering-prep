# Python LeetCode — 10 Mixed Problems
# Arrays, Hashmaps, Strings

from collections import Counter

# Problem 1: Two Sum II - Input Array Is Sorted (LC #167)
# Difficulty: Medium
# Approach: two pointers from both ends — no extra space needed
# Key insight: sorted array lets you move pointers based on sum comparison


def two_sum_sorted(numbers, target):
    left, right = 0, len(numbers) - 1
    while left < right:
        current = numbers[left] + numbers[right]
        if current == target:
            return [left + 1, right + 1]
        elif current < target:
            left += 1
        else:
            right -= 1
    return []


print(two_sum_sorted([2, 7, 11, 15], 9))  # [1, 2]
print(two_sum_sorted([2, 3, 4], 6))  # [1, 3]


# Problem 2: Valid Palindrome (LC #125)
# Difficulty: Easy
# Approach: two pointers, skip non-alphanumeric, compare lowercase
# Key insight: isalnum() filters out spaces and punctuation


def is_palindrome(s):
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True


print(is_palindrome("A man, a plan, a canal: Panama"))  # True
print(is_palindrome("race a car"))  # False
print(is_palindrome(" "))  # True


# Problem 3: Ransom Note (LC #383)
# Difficulty: Easy
# Approach: count characters in magazine, check if ransom note can be formed
# Key insight: Counter subtraction handles frequency comparison cleanly


def can_construct(ransom_note, magazine):
    mag_count = Counter(magazine)
    for char in ransom_note:
        if mag_count[char] == 0:
            return False
        mag_count[char] -= 1
    return True


print(can_construct("a", "b"))  # False
print(can_construct("aa", "ab"))  # False
print(can_construct("aa", "aab"))  # True


# Problem 4: Isomorphic Strings (LC #205)
# Difficulty: Easy
# Approach: two hashmaps — one for s→t mapping, one for t→s mapping
# Key insight: both directions must be consistent — "egg" and "add" map both ways


def is_isomorphic(s, t):
    s_to_t = {}
    t_to_s = {}
    for cs, ct in zip(s, t):
        if cs in s_to_t and s_to_t[cs] != ct:
            return False
        if ct in t_to_s and t_to_s[ct] != cs:
            return False
        s_to_t[cs] = ct
        t_to_s[ct] = cs
    return True


print(is_isomorphic("egg", "add"))  # True
print(is_isomorphic("foo", "bar"))  # False
print(is_isomorphic("paper", "title"))  # True


# Problem 5: Word Pattern (LC #290)
# Difficulty: Easy
# Approach: split string into words, map pattern chars to words bidirectionally
# Key insight: same as isomorphic strings but chars map to words


def word_pattern(pattern, s):
    words = s.split()
    if len(pattern) != len(words):
        return False
    char_to_word = {}
    word_to_char = {}
    for char, word in zip(pattern, words):
        if char in char_to_word and char_to_word[char] != word:
            return False
        if word in word_to_char and word_to_char[word] != char:
            return False
        char_to_word[char] = word
        word_to_char[word] = char
    return True


print(word_pattern("abba", "dog cat cat dog"))  # True
print(word_pattern("abba", "dog cat cat fish"))  # False
print(word_pattern("aaaa", "dog cat cat dog"))  # False


# Problem 6: Contains Duplicate II (LC #219)
# Difficulty: Easy
# Approach: sliding window with hashmap storing last seen index
# Key insight: check if same value seen within k distance


def contains_nearby_duplicate(nums, k):
    seen = {}
    for i, num in enumerate(nums):
        if num in seen and i - seen[num] <= k:
            return True
        seen[num] = i
    return False


print(contains_nearby_duplicate([1, 2, 3, 1], 3))  # True
print(contains_nearby_duplicate([1, 0, 1, 1], 1))  # True
print(contains_nearby_duplicate([1, 2, 3, 1, 2, 3], 2))  # False


# Problem 7: Summary Ranges (LC #228)
# Difficulty: Easy
# Approach: iterate and extend current range or start new one
# Key insight: check if current number continues the previous range


def summary_ranges(nums):
    if not nums:
        return []
    result = []
    start = nums[0]
    for i in range(1, len(nums)):
        if nums[i] != nums[i - 1] + 1:
            if start == nums[i - 1]:
                result.append(str(start))
            else:
                result.append(f"{start}->{nums[i - 1]}")
            start = nums[i]
    if start == nums[-1]:
        result.append(str(start))
    else:
        result.append(f"{start}->{nums[-1]}")
    return result


print(summary_ranges([0, 1, 2, 4, 5, 7]))  # ["0->2","4->5","7"]
print(summary_ranges([0, 2, 3, 4, 6, 8, 9]))  # ["0","2->4","6","8->9"]


# Problem 8: Merge Sorted Array (LC #88)
# already in day19 — replaced with:
# Majority Element (LC #169)
# Difficulty: Easy
# Approach: Boyer-Moore voting algorithm — O(n) time O(1) space
# Key insight: majority element count > n/2 so it survives vote cancellation


def majority_element(nums):
    candidate = None
    count = 0
    for num in nums:
        if count == 0:
            candidate = num
        count += 1 if num == candidate else -1
    return candidate


print(majority_element([3, 2, 3]))  # 3
print(majority_element([2, 2, 1, 1, 1, 2, 2]))  # 2


# Problem 9: Roman to Integer (LC #13)
# already in day19 — replaced with:
# Length of Last Word (LC #58)
# Difficulty: Easy
# Approach: strip trailing spaces, find last space, calculate length
# Key insight: rstrip removes trailing spaces before counting


def length_of_last_word(s):
    s = s.rstrip()
    return len(s) - s.rfind(" ") - 1


print(length_of_last_word("Hello World"))  # 5
print(length_of_last_word("   fly me   to the moon  "))  # 4
print(length_of_last_word("luffy is still joyboy"))  # 6


# Problem 10: Find the Index of the First Occurrence in a String (LC #28)
# Difficulty: Easy
# Approach: sliding window — check each substring of length needle
# Key insight: built-in str.find() exists but understand the manual approach


def str_str(haystack, needle):
    if not needle:
        return 0
    n, m = len(haystack), len(needle)
    for i in range(n - m + 1):
        if haystack[i : i + m] == needle:
            return i
    return -1


print(str_str("sadbutsad", "sad"))  # 0
print(str_str("leetcode", "leeto"))  # -1
print(str_str("hello", "ll"))  # 2
