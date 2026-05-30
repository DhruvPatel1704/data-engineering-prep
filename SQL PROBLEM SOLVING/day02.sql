-- Problem 1: Department Highest Salary (LC #184)
-- Difficulty: Medium
-- Approach: CTE to get max salary per department, then join back to Employee
-- e is the employee side, dm holds the max salary benchmark per dept
-- Key insight: joining on both departmentId AND salary filters to top earners only

WITH dept_max AS (
    SELECT departmentId, MAX(salary) AS max_salary
    FROM Employee
    GROUP BY departmentId
)
SELECT d.name  AS Department, e.name  AS Employee, e.salary AS Salary
FROM Employee e
INNER JOIN Department d ON e.departmentId = d.id
INNER JOIN dept_max dm  ON e.departmentId = dm.departmentId AND e.salary = dm.max_salary;


-- Problem 2: Monthly Transactions I (LC #1193)
-- Difficulty: Medium
-- Approach: Group by month + country using DATE_FORMAT to strip the day
-- Use CASE WHEN inside SUM to split approved vs total in one pass
-- Key insight: no subquery needed, conditional aggregation handles both counts

SELECT DATE_FORMAT(trans_date, '%Y-%m') AS month, country, COUNT(*) AS trans_count, 
    SUM(CASE WHEN state = 'approved' THEN 1 ELSE 0 END) AS approved_count, 
    SUM(amount) AS trans_total_amount,
    SUM(CASE WHEN state = 'approved' THEN amount ELSE 0 END) AS approved_total_amount
FROM Transactions
GROUP BY DATE_FORMAT(trans_date, '%Y-%m'), country;


-- Problem 3: Immediate Food Delivery II (LC #1174)
-- Difficulty: Medium
-- Approach: CTE isolates each customer's first order date, then join back
-- immediate means order_date matches customer_pref_delivery_date
-- Key insight: year filter in JOIN condition, not WHERE, preserves the left join behavior

WITH first_orders AS (
    SELECT customer_id, MIN(order_date) AS first_order_date
    FROM Delivery
    GROUP BY customer_id
)
SELECT ROUND(100 * SUM(CASE WHEN d.order_date = d.customer_pref_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 2) AS immediate_percentage
FROM Delivery d
INNER JOIN first_orders fo ON d.customer_id = fo.customer_id AND d.order_date = fo.first_order_date;


-- Problem 4: Consecutive Numbers (LC #180)
-- Difficulty: Medium
-- Approach: Self join Logs table 3 times on consecutive id values
-- l1 is the anchor row, l2 and l3 follow immediately after
-- Key insight: DISTINCT handles cases where the same number repeats more than 3 times

SELECT DISTINCT l1.num AS ConsecutiveNums
FROM Logs l1
INNER JOIN Logs l2 ON l2.id = l1.id + 1 AND l2.num = l1.num
INNER JOIN Logs l3 ON l3.id = l1.id + 2 AND l3.num = l1.num;


-- Problem 5: Market Analysis I (LC #1158)
-- Difficulty: Medium
-- Approach: LEFT JOIN Orders onto Users so zero-order users still appear
-- Year filter goes in JOIN condition not WHERE to avoid turning left join into inner join
-- Key insight: COUNT(o.order_id) returns 0 for NULLs, COUNT(*) would not

SELECT u.user_id AS buyer_id, u.join_date, COUNT(o.order_id) AS orders_in_2019
FROM Users u
LEFT JOIN Orders o ON u.user_id = o.buyer_id AND YEAR(o.order_date) = 2019
GROUP BY u.user_id, u.join_date;

-- Problem 6: Department Top Three Salaries (LC #185)
-- Difficulty: Hard
-- Approach: DENSE_RANK within each department, filter rank <= 3
-- Key insight: DENSE_RANK handles ties correctly, RANK would skip numbers
-- upgrade of LC 184 — instead of top 1, get top 3 per group

WITH dept_ranked AS (
    SELECT d.name  AS Department,
           e.name  AS Employee,
           e.salary AS Salary,
           DENSE_RANK() OVER (
               PARTITION BY e.departmentId
               ORDER BY e.salary DESC
           ) AS rnk
    FROM Employee e
    INNER JOIN Department d ON e.departmentId = d.id
)
SELECT Department,
       Employee,
       Salary
FROM dept_ranked
WHERE rnk <= 3;


-- Problem 7: Restaurant Growth (LC #1321)
-- Difficulty: Medium
-- Approach: 7-day moving average using window frame
-- Key insight: ROWS BETWEEN 6 PRECEDING AND CURRENT ROW = 7 day window
-- real DE use case: rolling metrics in dashboards and pipeline outputs

WITH daily_totals AS (
    SELECT visited_on,
           SUM(amount) AS day_total
    FROM Customer
    GROUP BY visited_on
)
SELECT visited_on,
       SUM(day_total) OVER (
           ORDER BY visited_on
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS amount,
       ROUND(AVG(day_total) OVER (
           ORDER BY visited_on
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ), 2) AS average_amount
FROM daily_totals
ORDER BY visited_on
OFFSET 6;


-- Problem 8: Last Person to Fit in the Bus (LC #1204)
-- Difficulty: Medium
-- Approach: running sum of weight using window function, find last person under 1000
-- Key insight: cumulative SUM with ORDER BY gives running total per row

WITH boarding AS (
    SELECT person_name,
           weight,
           SUM(weight) OVER (
               ORDER BY turn
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
           ) AS cumulative_weight
    FROM Queue
)
SELECT person_name
FROM boarding
WHERE cumulative_weight <= 1000
ORDER BY cumulative_weight DESC
LIMIT 1;


-- Problem 9: Capital Gain/Loss (LC #1393)
-- Difficulty: Medium
-- Approach: CASE WHEN inside SUM to treat buy as negative, sell as positive
-- Key insight: conditional aggregation in one pass, no self join needed
-- common pattern in financial pipelines for P&L calculations

SELECT stock_name,
       SUM(CASE WHEN operation = 'Sell' THEN  price
                WHEN operation = 'Buy'  THEN -price
           END) AS capital_gain_loss
FROM Stocks
GROUP BY stock_name;


-- Problem 10: Movie Rating (LC #1341)
-- Difficulty: Medium
-- Approach: two separate CTEs, UNION ALL to combine results
-- CTE 1: most active reviewer by count, CTE 2: highest rated movie in Feb 2020
-- Key insight: UNION ALL works even when result columns mean different things

WITH most_active_user AS (
    SELECT u.name AS results
    FROM MovieRating mr
    INNER JOIN Users u ON mr.user_id = u.user_id
    GROUP BY u.name
    ORDER BY COUNT(*) DESC, u.name ASC
    LIMIT 1
),
highest_rated_feb AS (
    SELECT m.title AS results
    FROM MovieRating mr
    INNER JOIN Movies m ON mr.movie_id = m.movie_id
    WHERE DATE_FORMAT(mr.created_at, '%Y-%m') = '2020-02'
    GROUP BY m.title
    ORDER BY AVG(mr.rating) DESC, m.title ASC
    LIMIT 1
)
SELECT results FROM most_active_user
UNION ALL
SELECT results FROM highest_rated_feb;