-- Problem 1: Median Employee Salary Without Built-in (LC #569)
-- already solved day 03 — replaced with:
-- Rank Scores (LC #178)
-- Difficulty: Medium-Hard
-- Approach: DENSE_RANK over all scores ordered desc
-- no gaps in ranking even when scores tie
-- Key insight: DENSE_RANK is the standard leaderboard pattern

SELECT score,
       DENSE_RANK() OVER (
           ORDER BY score DESC
       ) AS rank
FROM Scores
ORDER BY score DESC;

-- Problem 2: Department Top Three Salaries (LC #185)
-- already solved day 02 extension — replaced with:
-- The Latest Login in 2020 (LC #1890)
-- Difficulty: Medium-Hard
-- Approach: filter to 2020 only, MAX login per user
-- Key insight: simple aggregation but common in DE audit pipelines

SELECT user_id,
       MAX(time_stamp) AS last_stamp
FROM Logins
WHERE YEAR(time_stamp) = 2020
GROUP BY user_id
ORDER BY user_id;

-- Problem 3: Leetflex Banned Accounts (LC #2024)
-- Difficulty: Hard
-- Approach: self join LogInfo on account_id where two sessions overlap
-- one session from online = 1, another from online = 0
-- and their time ranges overlap at the same moment
-- Key insight: overlap condition is a.online <= b.offline AND b.online <= a.offline

SELECT DISTINCT a.account_id
FROM LogInfo a
INNER JOIN LogInfo b ON a.account_id = b.account_id
                    AND a.ip_address != b.ip_address
                    AND a.login <= b.logout
                    AND b.login <= a.logout
ORDER BY a.account_id;


-- Problem 4: Number of Unique Subjects Taught by Each Teacher (LC #2356)
-- Difficulty: Medium
-- Approach: COUNT DISTINCT subject_id per teacher
-- simple but foundational GROUP BY with DISTINCT count
-- Key insight: same teacher can teach same subject in different departments
-- DISTINCT prevents double counting

SELECT teacher_id,
       COUNT(DISTINCT subject_id) AS cnt
FROM Teacher
GROUP BY teacher_id
ORDER BY teacher_id;


-- Problem 5: Leetcode Stats (LC variant) /
--            The Number of Rich Customers (LC #2082)
-- Difficulty: Medium-Hard
-- Approach: count distinct customers who had at least one bill > 500
-- Key insight: COUNT DISTINCT inside HAVING would be wrong here
-- filter first then count unique customers

SELECT COUNT(DISTINCT customer_id) AS rich_count
FROM Store
WHERE amount > 500;


-- Problem 6: Find Customers With Positive Revenue This Year (LC #2013)
-- Difficulty: Medium-Hard
-- Approach: filter year = 2021, group by customer
-- HAVING ensures only positive net revenue customers returned
-- Key insight: SUM can be negative if expenses outweigh revenue

SELECT customer_id
FROM Customers
WHERE year = 2021
GROUP BY customer_id
HAVING SUM(revenue) > 0
ORDER BY customer_id;


-- Problem 7: Employee Bonus (LC #577)
-- Difficulty: Medium
-- Approach: LEFT JOIN bonus to employee
-- return employees with bonus < 1000 OR no bonus at all
-- Key insight: COALESCE or IS NULL handles missing bonus rows

SELECT e.name,
       b.bonus
FROM Employee e
LEFT JOIN Bonus b ON e.empId = b.empId
WHERE b.bonus < 1000
   OR b.bonus IS NULL
ORDER BY e.name;


-- Problem 8: Rising Temperature (LC #197)
-- Difficulty: Medium
-- Approach: self join weather to previous day using DATE_SUB
-- find rows where today's temp > yesterday's temp
-- Key insight: DATE_SUB in JOIN condition avoids correlated subquery

SELECT w1.id
FROM Weather w1
INNER JOIN Weather w2 ON w2.recordDate = DATE_SUB(w1.recordDate, INTERVAL 1 DAY)
WHERE w1.temperature > w2.temperature
ORDER BY w1.id;


-- Problem 9: Calculate Special Bonus (LC #1873)
-- already solved day 09 — replaced with:
-- Confirmation Rate (LC #1934)
-- Difficulty: Medium-Hard
-- Approach: LEFT JOIN confirmations to signups
-- rate = confirmed count / total count per user
-- COALESCE handles users with zero confirmations

SELECT s.user_id,
       ROUND(
           COALESCE(
               SUM(CASE WHEN c.action = 'confirmed' THEN 1 ELSE 0 END)
               / NULLIF(COUNT(c.action), 0),
           0), 2
       ) AS confirmation_rate
FROM Signups s
LEFT JOIN Confirmations c ON s.user_id = c.user_id
GROUP BY s.user_id
ORDER BY s.user_id;


-- Problem 10: Product Sales Analysis I (LC #1068)
-- Difficulty: Easy-Medium
-- Approach: INNER JOIN sales to product to get product name
-- return product name, year, price per sale row
-- Key insight: straightforward join but foundation for harder variants

SELECT p.product_name,
       s.year,
       s.price
FROM Sales s
INNER JOIN Product p ON s.product_id = p.product_id
ORDER BY s.product_id, s.year;


-- Problem 11: Monthly Transactions with Chargebacks (LC #1205)
-- already solved day 08 — replaced with:
-- Customer Who Visited but Did Not Make Any Transactions (LC #1581)
-- Difficulty: Medium-Hard
-- Approach: LEFT JOIN transactions to visits, filter no transaction rows
-- COUNT visits per customer with no matching transaction
-- Key insight: IS NULL after LEFT JOIN = no transaction visits only

SELECT v.customer_id,
       COUNT(*) AS count_no_trans
FROM Visits v
LEFT JOIN Transactions t ON v.visit_id = t.visit_id
WHERE t.transaction_id IS NULL
GROUP BY v.customer_id
ORDER BY v.customer_id;


-- Problem 12: Average Time of Process per Machine (LC #1661)
-- Difficulty: Medium-Hard
-- Approach: self join activity table on machine_id and process_id
-- one row type = start, other = end
-- subtract timestamps to get duration, average per machine
-- Key insight: self join with type filter on each side

SELECT a1.machine_id,
       ROUND(AVG(a2.timestamp - a1.timestamp), 3) AS processing_time
FROM Activity a1
INNER JOIN Activity a2 ON a1.machine_id = a2.machine_id
                      AND a1.process_id = a2.process_id
                      AND a1.activity_type = 'start'
                      AND a2.activity_type = 'end'
GROUP BY a1.machine_id
ORDER BY a1.machine_id;


-- Problem 13: Manager with at Least 5 Direct Reports (LC #570)
-- already solved day 01 — replaced with:
-- Count Salary Categories (LC #1907)
-- already solved day 07 — replaced with:
-- Students and Examinations (LC #1280)
-- Difficulty: Medium-Hard
-- Approach: CROSS JOIN students and subjects to generate full spine
-- LEFT JOIN examinations to count actual attendances
-- Key insight: CROSS JOIN spine guarantees every student x subject combo appears

SELECT st.student_id,
       st.student_name,
       su.subject_name,
       COUNT(e.student_id) AS attended_exams
FROM Students st
CROSS JOIN Subjects su
LEFT JOIN Examinations e ON st.student_id = e.student_id
                        AND su.subject_name = e.subject_name
GROUP BY st.student_id, st.student_name, su.subject_name
ORDER BY st.student_id, su.subject_name;


-- Problem 14: Biggest Window Between Visits (LC #1454 variant) /
--             Last Person to Fit in the Bus (LC #1204)
-- already solved day 03 — replaced with:
-- Immediate Food Delivery I (LC #1173)
-- Difficulty: Medium
-- Approach: immediate = order_date matches preferred delivery date
-- simple percentage calculation across all orders
-- Key insight: AVG of binary CASE WHEN gives percentage directly

SELECT ROUND(
    100 * AVG(
        CASE WHEN order_date = customer_pref_delivery_date
             THEN 1 ELSE 0
        END
    ), 2
) AS immediate_percentage
FROM Delivery;


-- Problem 15: Game Play Analysis III (LC #534)
-- Difficulty: Medium-Hard
-- Approach: running total of games played per player per date
-- window SUM partitioned by player ordered by event date
-- Key insight: cumulative sum per player tracks engagement over time

SELECT player_id,
       event_date,
       SUM(games_played) OVER (
           PARTITION BY player_id
           ORDER BY event_date
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS games_played_so_far
FROM Activity
ORDER BY player_id, event_date;