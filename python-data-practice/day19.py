# Python LeetCode — Problems

# Problem 1: Palindrome Number (LC #9)
# Difficulty: Easy
# Approach: convert to string, compare with reverse
# Key insight: negative numbers are never palindromes

def is_palindrome(x):
    if x < 0:
        return False
    s = str(x)
    return s == s[::-1]
print(is_palindrome(121))
print(is_palindrome(-121))

# Problem 2: Fizz Buzz (LC #412)
# Difficulty: Easy
# Approach: check divisibility in order — 15 first, then 3, then 5
# Key insight: check 15 before 3 and 5 to catch the combined case

def fizz_buzz(n):
    result=[]
    for i in range(1,n+1):
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 ==0:
            result.append("Buff")
        else:
            result.append(str(i))
    return result
print(fizz_buzz(25))

# Problem 3: Longest Palindromic Substring (LC #5)
# Difficulty: Medium
# Approach: expand around center for each character
# two cases: odd length (single center) and even length (two centers)
# Key insight: O(n²) expand around center vs O(n³) brute force

def longest_palindrome(s):
    if not s:
        return ""
    
    start, maxlen = 0, 1
    def expand(left, right):
        nonlocal start, maxlen
        while left>=0 and right<len(s) and s[left] == s[right]:
            if right-left+1 > maxlen:
                start=left
                maxlen=right-left+1
            left -=1
            right +=1
    for i in range(len(s)):
        expand(i,i)
        expand(i,i+1)
    return s[start:start+maxlen]
print(longest_palindrome("babad"))
print(longest_palindrome("cbbd"))
print(longest_palindrome("racecar"))

# Problem 2: Spiral Matrix (LC #54)
# Difficulty: Medium
# Approach: shrink boundaries after traversing each side
# top, bottom, left, right boundaries move inward
# Key insight: simulate the spiral by adjusting 4 boundaries

def spiral_order(matrix):
    result=[]
    top, bottom = 0, len(matrix)-1
    left, right = 0, len(matrix[0])-1
    while top<=bottom and left<=right:
        # Traversing Right
        for col in range(left, right+1):
            result.append(matrix[top][col])
        top+=1
        #traversing bottom
        for row in range(top, bottom+1):
            result.append(matrix[row][right])
        right-=1
        #traversing left
        if top<=bottom:
            for col in range(right, left-1, -1):
                result.append(matrix[bottom][col])
            bottom-=1
        if left<=right:
            for row in range(bottom, top-1, -1):
                result.append(matrix[row][left])
            left+=1
    return result
matrix1 = [[1,2,3],[4,5,6],[7,8,9]]
print(spiral_order(matrix1))

matrix2 = [[1,2,3,4],[5,6,7,8],[9,10,11,12]]
print(spiral_order(matrix2))