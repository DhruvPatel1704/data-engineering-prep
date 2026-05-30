-- Problem 1: Investments in 2016 (LC #585)
-- Difficulty: Hard
-- Approach: find policyholders where tiv_2015 matches at least one other
-- AND their lat/lon is unique across all policyholders
-- Key insight: two separate EXISTS/IN conditions combined with AND

SELECT ROUND(SUM(tiv_2016), 2) AS tiv_2016
FROM Insurance
WHERE tiv_2015 IN (
    SELECT tiv_2015
    FROM Insurance
    GROUP BY tiv_2015
    HAVING COUNT(*) > 1
)
AND (lat, lon) IN (
    SELECT lat, lon
    FROM Insurance
    GROUP BY lat, lon
    HAVING COUNT(*) = 1
);


-- Problem 2: Friend Requests II: Who Has the Most Friends (LC #602)
-- Difficulty: Hard
-- Approach: UNION ALL both requester and accepter into one column
-- count all appearances, pick the top one
-- Key insight: each accepted friendship adds to both people's friend count

WITH all_friends AS (
    SELECT requester_id AS id
    FROM RequestAccepted
    UNION ALL
    SELECT accepter_id
    FROM RequestAccepted
)
SELECT id,
       COUNT(*) AS num
FROM all_friends
GROUP BY id
ORDER BY num DESC
LIMIT 1;


-- Problem 3: Biggest Single Number (LC #619)
-- Difficulty: Hard
-- Approach: find numbers that appear exactly once, return the max
-- handle edge case where no single number exists — return NULL
-- Key insight: subquery with HAVING COUNT = 1, outer MAX handles empty set

SELECT MAX(num) AS num
FROM (
    SELECT num
    FROM MyNumbers
    GROUP BY num
    HAVING COUNT(*) = 1
) singles;


-- Problem 4: Reformat Department Table (LC #1179)
-- Difficulty: Hard
-- Approach: pivot month column into separate columns using MAX CASE WHEN
-- one row per department with revenue per month as separate columns
-- Key insight: standard pivot pattern — MAX absorbs the single non-null per group

SELECT id,
       MAX(CASE WHEN month = 'Jan' THEN revenue END) AS Jan_Revenue,
       MAX(CASE WHEN month = 'Feb' THEN revenue END) AS Feb_Revenue,
       MAX(CASE WHEN month = 'Mar' THEN revenue END) AS Mar_Revenue,
       MAX(CASE WHEN month = 'Apr' THEN revenue END) AS Apr_Revenue,
       MAX(CASE WHEN month = 'May' THEN revenue END) AS May_Revenue,
       MAX(CASE WHEN month = 'Jun' THEN revenue END) AS Jun_Revenue,
       MAX(CASE WHEN month = 'Jul' THEN revenue END) AS Jul_Revenue,
       MAX(CASE WHEN month = 'Aug' THEN revenue END) AS Aug_Revenue,
       MAX(CASE WHEN month = 'Sep' THEN revenue END) AS Sep_Revenue,
       MAX(CASE WHEN month = 'Oct' THEN revenue END) AS Oct_Revenue,
       MAX(CASE WHEN month = 'Nov' THEN revenue END) AS Nov_Revenue,
       MAX(CASE WHEN month = 'Dec' THEN revenue END) AS Dec_Revenue
FROM Department
GROUP BY id
ORDER BY id;


-- Problem 5: Consecutive Seat Friends (LC #603)
-- Difficulty: Hard
-- Approach: self join cinema table on seat_id + 1
-- both seats must be free for them to be consecutive free seats
-- Key insight: self join on adjacent id is cleaner than LAG for this pattern

SELECT DISTINCT c1.seat_id
FROM Cinema c1
INNER JOIN Cinema c2 ON ABS(c1.seat_id - c2.seat_id) = 1
WHERE c1.free = 1
  AND c2.free = 1
ORDER BY c1.seat_id;


-- Problem 6: Product Price at a Given Date (LC #1164)
-- Difficulty: Hard
-- Approach: for each product find the latest price change on or before 2019-08-16
-- products with no price change before that date default to 10
-- Key insight: correlated subquery finds max date per product before cutoff

WITH latest_price AS (
    SELECT product_id,
           new_price AS price
    FROM Products
    WHERE (product_id, change_date) IN (
        SELECT product_id,
               MAX(change_date)
        FROM Products
        WHERE change_date <= '2019-08-16'
        GROUP BY product_id
    )
),
all_products AS (
    SELECT DISTINCT product_id
    FROM Products
)
SELECT ap.product_id,
       COALESCE(lp.price, 10) AS price
FROM all_products ap
LEFT JOIN latest_price lp ON ap.product_id = lp.product_id
ORDER BY ap.product_id;


-- Problem 7: Last Person to Fit in the Elevator (LC #1204)
-- already solved day 03 — replaced with:
-- Exchange Seats (LC #626)
-- Difficulty: Hard
-- Approach: swap adjacent seat ids using CASE WHEN on odd/even
-- last seat stays if total count is odd
-- Key insight: MOD(id, 2) = 1 is odd seat, swap with id+1
-- but only if id+1 exists, otherwise keep same id

SELECT CASE WHEN MOD(id, 2) = 1 AND id + 1 <= (SELECT COUNT(*) FROM Seat)
                 THEN id + 1
            WHEN MOD(id, 2) = 0
                 THEN id - 1
            ELSE id
       END  AS id,
       student
FROM Seat
ORDER BY id;


-- Problem 8: Sales Analysis III (LC #1084)
-- Difficulty: Hard
-- Approach: find products sold ONLY in spring 2019
-- exclude any product that has a sale outside that window
-- Key insight: NOT EXISTS or HAVING with conditional count
-- products with any sale outside range must be excluded entirely

SELECT DISTINCT s.product_id,
       p.product_name
FROM Sales s
INNER JOIN Product p ON s.product_id = p.product_id
WHERE s.product_id NOT IN (
    SELECT product_id
    FROM Sales
    WHERE sale_date < '2019-01-01'
       OR sale_date > '2019-03-31'
)
ORDER BY s.product_id;


-- Problem 9: Evaluate Boolean Expression (LC #1945 variant) /
--            Calculate Special Bonus (LC #1873)
-- Difficulty: Hard
-- Approach: CASE WHEN on employee_id and name conditions
-- bonus = 100% salary if id is odd AND name does not start with M
-- Key insight: MOD and LEFT string check combined in CASE

SELECT employee_id,
       CASE WHEN MOD(employee_id, 2) = 1
             AND LEFT(name, 1) != 'M'
            THEN salary
            ELSE 0
       END AS bonus
FROM Employees
ORDER BY employee_id;


-- Problem 10: Count Apples and Oranges (LC #1965)
-- already solved day 07 — replaced with:
-- Team Scores in Football Tournament (LC #1212)
-- Difficulty: Hard
-- Approach: UNION ALL host and guest goals for each team
-- calculate points: 3 for win, 1 for draw, 0 for loss per match
-- Key insight: each match generates two rows after UNION ALL
-- one for host team, one for guest team with mirrored logic

WITH all_matches AS (
    SELECT host_team                             AS team_id,
           CASE WHEN host_goals > guest_goals    THEN 3
                WHEN host_goals = guest_goals    THEN 1
                ELSE 0
           END                                   AS points,
           host_goals                            AS goals_scored,
           guest_goals                           AS goals_against
    FROM Matches
    UNION ALL
    SELECT guest_team,
           CASE WHEN guest_goals > host_goals    THEN 3
                WHEN guest_goals = host_goals    THEN 1
                ELSE 0
           END,
           guest_goals,
           host_goals
    FROM Matches
)
SELECT t.team_id,
       t.team_name,
       COUNT(*)                                  AS matches_played,
       SUM(am.points)                            AS points,
       SUM(am.goals_scored)                      AS goal_for,
       SUM(am.goals_against)                     AS goal_against,
       SUM(am.goals_scored) - SUM(am.goals_against) AS goal_diff
FROM Teams t
INNER JOIN all_matches am ON t.team_id = am.team_id
GROUP BY t.team_id, t.team_name
ORDER BY points DESC,
         goal_diff DESC,
         t.team_name ASC;