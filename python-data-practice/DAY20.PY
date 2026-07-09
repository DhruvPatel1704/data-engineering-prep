# Python LeetCode — String and Array Problems

# Problem 1: Roman to Integer (LC #13)
# Difficulty: Easy
# Approach: hashmap for values, add or subtract based on next character
# Key insight: if current value < next value, subtract it instead of adding

def roman_to_int(s):
    values = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }
    result = 0
    for i in range(len(s)):
        if i + 1 < len(s) and values[s[i]] < values[s[i + 1]]:
            result -= values[s[i]]
        else:
            result += values[s[i]]
    return result

print(roman_to_int("III"))     # 3
print(roman_to_int("LVIII"))   # 58
print(roman_to_int("MCMXCIV")) # 1994


# Problem 2: Merge Sorted Array (LC #88)
# Difficulty: Easy
# Approach: three pointers from the end — fill from back to avoid overwriting
# Key insight: start from the end so you never overwrite unprocessed elements

def merge(nums1, m, nums2, n):
    p1, p2, p = m - 1, n - 1, m + n - 1
    while p1 >= 0 and p2 >= 0:
        if nums1[p1] > nums2[p2]:
            nums1[p] = nums1[p1]
            p1 -= 1
        else:
            nums1[p] = nums2[p2]
            p2 -= 1
        p -= 1
    while p2 >= 0:
        nums1[p] = nums2[p2]
        p2 -= 1
        p -= 1
    return nums1

print(merge([1,2,3,0,0,0], 3, [2,5,6], 3))  # [1,2,2,3,5,6]
print(merge([1], 1, [], 0))                   # [1]