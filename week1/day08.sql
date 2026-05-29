-- Problem 1: Monthly Transactions II (LC #1205)
-- Difficulty: Hard
-- Approach: UNION ALL approved transactions with chargebacks
-- tag each with its type and month, then pivot into columns
-- Key insight: chargebacks use chargeback_date not transaction_date
-- two separate date sources unified before aggregation

WITH transaction_data AS (
    SELECT DATE_FORMAT(t.trans_date, '%Y-%m')  AS month,
           t.country,
           'approved'                          AS type,
           t.amount
    FROM Transactions t
    WHERE t.state = 'approved'
    UNION ALL
    SELECT DATE_FORMAT(c.trans_date, '%Y-%m'),
           t.country,
           'chargeback',
           t.amount
    FROM Chargebacks c
    INNER JOIN Transactions t ON c.trans_id = t.id
)
SELECT month,
       country,
       SUM(CASE WHEN type = 'approved'   THEN 1 ELSE 0 END)      AS approved_count,
       SUM(CASE WHEN type = 'approved'   THEN amount ELSE 0 END)  AS approved_amount,
       SUM(CASE WHEN type = 'chargeback' THEN 1 ELSE 0 END)       AS chargeback_count,
       SUM(CASE WHEN type = 'chargeback' THEN amount ELSE 0 END)  AS chargeback_amount
FROM transaction_data
GROUP BY month, country
ORDER BY month, country;


-- Problem 2: Consecutive Numbers III (LC #2701 variant) /
--            Longest Subsequence With Limited Sum variant /
--            Warehouse Manager (LC #1571)
-- Difficulty: Hard
-- Approach: join warehouses to products to get cubic feet per unit
-- multiply by units stored to get total volume per warehouse
-- Key insight: multi-table join with arithmetic in SELECT is standard
-- DE pattern for denormalizing product dimensions into inventory facts

SELECT w.name                                       AS warehouse_name,
       SUM(p.Width * p.Length * p.Height * w.units) AS volume
FROM Warehouse w
INNER JOIN Products p ON w.product_id = p.product_id
GROUP BY w.name
ORDER BY w.name;


-- Problem 3: Game Play Analysis IV (LC #550)
-- Difficulty: Hard
-- Approach: CTE gets first login per player
-- LEFT JOIN back to check login on exactly day after first login
-- fraction = players who logged in next day / total distinct players
-- Key insight: DATE_ADD on first login date as join condition

WITH first_login AS (
    SELECT player_id,
           MIN(event_date) AS first_date
    FROM Activity
    GROUP BY player_id
)
SELECT ROUND(
    COUNT(DISTINCT a.player_id) /
    COUNT(DISTINCT f.player_id), 2
) AS fraction
FROM first_login f
LEFT JOIN Activity a ON f.player_id = a.player_id
                    AND a.event_date = DATE_ADD(f.first_date, INTERVAL 1 DAY);


-- Problem 4: Customers Who Bought All Products (LC #1045)
-- Difficulty: Hard
-- Approach: count distinct products per customer
-- compare to total products in Product table
-- Key insight: HAVING COUNT(DISTINCT) = subquery total is cleaner
-- than NOT EXISTS or multiple joins for this pattern

SELECT customer_id
FROM Customer
GROUP BY customer_id
HAVING COUNT(DISTINCT product_key) = (
    SELECT COUNT(DISTINCT product_key)
    FROM Product
)
ORDER BY customer_id;


-- Problem 5: All People Report to the Given Manager (LC #1544 variant) /
--            Find the Team Size (LC #1377)
-- Difficulty: Hard
-- Approach: window COUNT over partition by team_id gives team size per row
-- no subquery or self join needed
-- Key insight: COUNT(*) OVER PARTITION is cleaner than a correlated subquery

SELECT employee_id,
       COUNT(*) OVER (
           PARTITION BY team_id
       ) AS team_size
FROM Employee
ORDER BY employee_id;


-- Problem 6: Running Total for Different Genders (LC #1308)
-- Difficulty: Hard
-- Approach: window SUM partitioned by gender ordered by day
-- gives running score total per gender per day
-- Key insight: PARTITION BY gender ORDER BY day_number
-- gives separate running totals per group

SELECT gender,
       day,
       SUM(score_points) OVER (
           PARTITION BY gender
           ORDER BY day
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS total
FROM Scores
ORDER BY gender, day;


-- Problem 7: Number of Calls Between Two Persons (LC #1699)
-- Difficulty: Hard
-- Approach: normalize caller/recipient so smaller id is always first
-- prevents (A→B) and (B→A) being counted as different pairs
-- Key insight: LEAST and GREATEST functions normalize direction

SELECT LEAST(from_id, to_id)       AS person1,
       GREATEST(from_id, to_id)    AS person2,
       COUNT(*)                    AS call_count,
       SUM(duration)               AS total_duration
FROM Calls
GROUP BY LEAST(from_id, to_id),
         GREATEST(from_id, to_id)
ORDER BY person1, person2;


-- Problem 8: Patients With a Condition (LC #1527)
-- Difficulty: Hard
-- Approach: LIKE pattern match for DIAB1 prefix
-- must handle condition appearing at start or after a space
-- Key insight: two LIKE conditions cover both edge cases
-- DIAB1 at start of string OR after a space separator

SELECT patient_id,
       patient_name,
       conditions
FROM Patients
WHERE conditions LIKE 'DIAB1%'
   OR conditions LIKE '% DIAB1%'
ORDER BY patient_id;


-- Problem 9: Fix Names in a Table (LC #1667)
-- Difficulty: Hard
-- Approach: UPPER on first character + LOWER on rest
-- SUBSTRING handles character extraction and slicing
-- Key insight: CONCAT(UPPER(LEFT), LOWER(SUBSTRING from 2)) pattern
-- used in DE pipelines for name normalization before loading to gold layer

SELECT user_id,
       CONCAT(
           UPPER(LEFT(name, 1)),
           LOWER(SUBSTRING(name, 2))
       ) AS name
FROM Users
ORDER BY user_id;


-- Problem 10: Find Followers Count (LC #1729)
-- Difficulty: Hard
-- Approach: simple GROUP BY with COUNT, but ordered by user_id
-- foundation problem for social graph analytics in DE pipelines
-- real use case: follower counts denormalized into user profile gold table

SELECT user_id,
       COUNT(follower_id) AS followers_count
FROM Followers
GROUP BY user_id
ORDER BY user_id;