-- Problem 1: Managers with at Least 5 Direct Reports (LC #570)
-- Difficulty: Medium
-- Approach: Self-join Employee table to itself
-- e1 is the manager side, e2 is the direct report side
-- Group by manager and count how many reports they have
-- Key insight: Self-join is the standard pattern for same-table hierarchies

SELECT e1.name
FROM Employee e1
JOIN Employee e2 ON e1.id = e2.managerId
GROUP BY e1.id, e1.name
HAVING COUNT(e2.id) >= 5;

-- Problem 2: Person Address Join (LC #175)
-- Difficulty: Easy
-- Approach: LEFT JOIN to keep all persons even without an address
-- Key insight: INNER JOIN would drop persons with no address entry
-- LEFT JOIN preserves all rows from left table, NULLs fill missing right side

SELECT p.firstName, p.lastName, a.city, a.state
FROM Person p
LEFT JOIN Address a ON p.personId = a.personId;

-- Problem 3: Game Play Analysis IV (LC #550)
-- Difficulty: Medium
-- Approach: Find each player's first login date, then check if they logged in the next day
-- Step 1: Get first login date per player using MIN(event_date)
-- Step 2: Join back to Activity to find rows where event_date = first_login + 1 day
-- Step 3: Divide players who came back by total distinct players
-- Key insight: COUNT(a2.player_id) only counts matched rows, NULLs are ignored automatically

SELECT ROUND(
    COUNT(a2.player_id) / COUNT(DISTINCT a1.player_id),
    2
) AS fraction
FROM (
    SELECT player_id, MIN(event_date) AS first_login
    FROM Activity
    GROUP BY player_id
) a1
LEFT JOIN Activity a2
    ON a1.player_id = a2.player_id
    AND a2.event_date = DATE_ADD(a1.first_login, INTERVAL 1 DAY);

-- Problem 4: Consecutive Numbers (LC #180)
-- Difficulty: Medium
-- Approach: Self-join Logs table 3 times aligning consecutive rows by id
-- Compare l1.num = l2.num = l3.num to find same value in 3 consecutive rows
-- DISTINCT needed because same number could appear in multiple consecutive groups
-- Key insight: id is autoincrement so id+1 and id+2 guarantee consecutive rows

SELECT DISTINCT l1.num AS ConsecutiveNums
FROM Logs l1
JOIN Logs l2 ON l2.id = l1.id + 1
JOIN Logs l3 ON l3.id = l1.id + 2
WHERE l1.num = l2.num
AND l2.num = l3.num;

-- Problem 5: Nth Highest Salary (LC #177)
-- Difficulty: Medium
-- Approach: Skip the top N-1 distinct salaries using OFFSET, take 1 row with LIMIT
-- DISTINCT handles duplicate salaries so they dont count as separate ranks
-- Subquery removes duplicates first, then LIMIT/OFFSET picks the correct rank
-- Key insight: OFFSET N-1 skips N-1 rows, whatever is left at top is the Nth highest
-- Edge case: if fewer than N distinct salaries exist, query returns NULL automatically

CREATE FUNCTION getNthHighestSalary(N INT) RETURNS INT
BEGIN
  SET N = N - 1;
  RETURN (
      SELECT DISTINCT salary
      FROM Employee
      ORDER BY salary DESC
      LIMIT 1 OFFSET N
  );
END