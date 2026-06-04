-- Problem 1: Find Median Given Frequency of Numbers (LC #571)
-- Difficulty: Hard
-- Approach: cumulative frequency from both directions
-- median sits where both cumulative counts cross the midpoint
-- Key insight: no MEDIAN function, no ROW_NUMBER — pure frequency math

WITH cumulative AS (
    SELECT num,
           frequency,
           SUM(frequency) OVER (ORDER BY num)              AS cum_asc,
           SUM(frequency) OVER (ORDER BY num DESC)         AS cum_desc,
           SUM(frequency) OVER ()                          AS total
    FROM Numbers
)
SELECT ROUND(AVG(num), 1) AS median
FROM cumulative
WHERE cum_asc  >= total / 2.0
  AND cum_desc >= total / 2.0;


-- Problem 2: Tournament Winners (LC #1194)
-- Difficulty: Hard
-- Approach: UNION ALL both player columns into one with group_id
-- sum points per player per group, RANK within group
-- handle tie by returning lower player_id
-- Key insight: unpivot before aggregating, RANK handles tie on player_id

WITH all_scores AS (
    SELECT p.group_id,
           m.first_player  AS player_id,
           m.first_score   AS score
    FROM Players p
    INNER JOIN Matches m ON p.player_id = m.first_player
    UNION ALL
    SELECT p.group_id,
           m.second_player,
           m.second_score
    FROM Players p
    INNER JOIN Matches m ON p.player_id = m.second_player
),
totals AS (
    SELECT group_id,
           player_id,
           SUM(score) AS total_score
    FROM all_scores
    GROUP BY group_id, player_id
),
ranked AS (
    SELECT group_id,
           player_id,
           RANK() OVER (
               PARTITION BY group_id
               ORDER BY total_score DESC, player_id ASC
           ) AS rnk
    FROM totals
)
SELECT group_id,
       player_id
FROM ranked
WHERE rnk = 1
ORDER BY group_id;


-- Problem 3: Trips and Users (LC #262)
-- Difficulty: Hard
-- Approach: filter banned users on BOTH client and driver side
-- conditional aggregation for cancellation rate in date window
-- Key insight: two joins to same Users table with different aliases

SELECT t.request_at AS Day,
       ROUND(
           SUM(CASE WHEN t.status LIKE 'cancelled%' THEN 1 ELSE 0 END)
           * 1.0 / COUNT(*), 2
       ) AS 'Cancellation Rate'
FROM Trips t
INNER JOIN Users u1 ON t.client_id = u1.users_id AND u1.banned = 'No'
INNER JOIN Users u2 ON t.driver_id = u2.users_id AND u2.banned = 'No'
WHERE t.request_at BETWEEN '2013-10-01' AND '2013-10-03'
GROUP BY t.request_at
ORDER BY t.request_at;


-- Problem 4: The Number of Seniors and Juniors to Join the Company (LC #2004)
-- Difficulty: Hard
-- Approach: rank each experience group by salary ascending
-- running cost tells you how many fit in budget
-- seniors get first pick of 70000, juniors get the remainder
-- Key insight: two separate window sums, budget math done in outer query

WITH senior_ranked AS (
    SELECT employee_id,
           salary,
           SUM(salary) OVER (
               ORDER BY salary
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
           ) AS running_cost
    FROM Candidates
    WHERE experience = 'Senior'
),
junior_ranked AS (
    SELECT employee_id,
           salary,
           SUM(salary) OVER (
               ORDER BY salary
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
           ) AS running_cost
    FROM Candidates
    WHERE experience = 'Junior'
),
senior_spend AS (
    SELECT COALESCE(SUM(salary), 0) AS spent
    FROM senior_ranked
    WHERE running_cost <= 70000
)
SELECT 'Senior'  AS experience,
       COUNT(*)  AS accepted_candidates
FROM senior_ranked, senior_spend
WHERE running_cost <= 70000
UNION ALL
SELECT 'Junior',
       COUNT(*)
FROM junior_ranked, senior_spend
WHERE running_cost <= 70000 - spent;


-- Problem 5: Consecutive Numbers (LC #180) — Advanced Version
-- Difficulty: Hard
-- Approach: three-way self join on consecutive IDs
-- DISTINCT handles numbers repeating more than 3 times
-- then extend to find longest consecutive sequence using island trick
-- Key insight: combines self join pattern with island detection

WITH consecutive AS (
    SELECT DISTINCT l1.num AS ConsecutiveNums
    FROM Logs l1
    INNER JOIN Logs l2 ON l2.id = l1.id + 1 AND l2.num = l1.num
    INNER JOIN Logs l3 ON l3.id = l1.id + 2 AND l3.num = l1.num
),
island_groups AS (
    SELECT num,
           id,
           id - ROW_NUMBER() OVER (
               PARTITION BY num
               ORDER BY id
           ) AS grp
    FROM Logs
),
longest_streak AS (
    SELECT num,
           COUNT(*) AS streak_length
    FROM island_groups
    GROUP BY num, grp
    ORDER BY streak_length DESC
    LIMIT 1
)
SELECT c.ConsecutiveNums,
       ls.streak_length AS max_consecutive_count
FROM consecutive c
LEFT JOIN longest_streak ls ON c.ConsecutiveNums = ls.num
ORDER BY c.ConsecutiveNums;