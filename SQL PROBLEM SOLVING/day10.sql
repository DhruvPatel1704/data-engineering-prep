-- Problem 1: Average Selling Price (LC #1251)
-- Difficulty: Medium-Hard
-- Approach: JOIN prices to units sold within valid date range
-- weighted average = total revenue / total units sold
-- Key insight: date range join condition inside ON clause not WHERE

SELECT p.product_id,
       ROUND(
           COALESCE(SUM(p.price * u.units) / NULLIF(SUM(u.units), 0), 0)
       , 2) AS average_price
FROM Prices p
LEFT JOIN UnitsSold u ON p.product_id = u.product_id
                     AND u.purchase_date BETWEEN p.start_date AND p.end_date
GROUP BY p.product_id
ORDER BY p.product_id;


-- Problem 2: Capital Gain Loss (LC #1393)
-- already solved day 08 — replaced with:
-- Reported Posts II (LC #1227 variant) /
-- Percentage of Users Attended a Contest (LC #1633)
-- Difficulty: Medium-Hard
-- Approach: count distinct users per contest, divide by total users
-- ORDER BY percentage DESC then contest_id ASC for tiebreak
-- Key insight: subquery for total user count avoids GROUP BY complication

SELECT contest_id,
       ROUND(
           COUNT(DISTINCT user_id) * 100.0
           / (SELECT COUNT(*) FROM Users), 2
       ) AS percentage
FROM Register
GROUP BY contest_id
ORDER BY percentage DESC, contest_id ASC;


-- Problem 3: Queries Quality and Percentage (LC #1211)
-- Difficulty: Medium-Hard
-- Approach: quality = avg(rating/position), poor = % where rating < 3
-- both metrics in one GROUP BY pass using AVG and conditional AVG
-- Key insight: AVG of CASE WHEN 1/0 gives percentage without COUNT

SELECT query_name,
       ROUND(AVG(rating / position), 2)                              AS quality,
       ROUND(AVG(CASE WHEN rating < 3 THEN 100.0 ELSE 0 END), 2)    AS poor_query_percentage
FROM Queries
WHERE query_name IS NOT NULL
GROUP BY query_name
ORDER BY query_name;


-- Problem 4: Users Who Have Visited Travel Destinations (LC variant) /
--            The Most Recent Orders for Each Product (LC #1549)
-- Difficulty: Hard
-- Approach: find max order date per product
-- then return all orders matching that date (handles ties)
-- Key insight: CTE for max date, join back for full row retrieval

WITH latest_orders AS (
    SELECT product_id,
           MAX(order_date) AS latest_date
    FROM Orders
    GROUP BY product_id
)
SELECT o.product_name,
       o.product_id,
       o.order_id,
       o.order_date
FROM Orders o
INNER JOIN Products p      ON o.product_id = p.product_id
INNER JOIN latest_orders l ON o.product_id = l.product_id
                           AND o.order_date = l.latest_date
ORDER BY o.product_name, o.product_id, o.order_id;


-- Problem 5: Determine if String Halves Are Alike (LC variant) /
--            The Most Frequently Ordered Products for Each Customer (LC #1596)
-- Difficulty: Hard
-- Approach: count orders per customer per product
-- rank by count desc, return all products tied for max per customer
-- Key insight: RANK not ROW_NUMBER to handle ties at top

WITH product_counts AS (
    SELECT customer_id,
           product_id,
           COUNT(*)                                          AS order_count,
           RANK() OVER (
               PARTITION BY customer_id
               ORDER BY COUNT(*) DESC
           )                                                AS rnk
    FROM Orders
    GROUP BY customer_id, product_id
)
SELECT pc.customer_id,
       pc.product_id,
       p.product_name
FROM product_counts pc
INNER JOIN Products p ON pc.product_id = p.product_id
WHERE rnk = 1
ORDER BY pc.customer_id, pc.product_id;


-- Problem 6: Find the Subtasks That Did Not Execute (LC #1767)
-- already solved day 06 — replaced with:
-- Npv Queries (LC #1571 variant) /
--  Bank Account Summary II (LC #1532)
-- Difficulty: Hard
-- Approach: SUM balance per user, filter where total > 10000
-- join to Users table for name, LEFT JOIN to keep all users

SELECT u.name,
       SUM(t.amount) AS balance
FROM Users u
INNER JOIN Transactions t ON u.account = t.account
GROUP BY u.account, u.name
HAVING SUM(t.amount) > 10000
ORDER BY u.name;


-- Problem 7: Find Cumulative Salary of an Employee (LC #579)
-- Difficulty: Hard
-- Approach: 3-month rolling sum per employee excluding current max month
-- window frame with LAG to exclude the most recent month
-- Key insight: filter out each employee's max month first, then rolling sum

WITH filtered AS (
    SELECT id,
           month,
           salary,
           MAX(month) OVER (PARTITION BY id) AS max_month
    FROM Employee
),
without_latest AS (
    SELECT id,
           month,
           salary
    FROM filtered
    WHERE month != max_month
)
SELECT id,
       month,
       SUM(salary) OVER (
           PARTITION BY id
           ORDER BY month
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
       ) AS Salary
FROM without_latest
ORDER BY id ASC, month DESC;


-- Problem 8: Trips and Users Follow-up Pattern /
--            Immediate Food Delivery III (LC variant) /
--            NPV for Each Query (LC #1445 variant) /
--            Reported Posts (LC #1132)
-- Difficulty: Hard
-- Approach: count extra reports per post per action removing duplicates
-- join to Actions table filtering report type only
-- Key insight: COUNT DISTINCT reporter_id per post per action_date

SELECT ROUND(
    SUM(daily_avg) / COUNT(*), 2
) AS average_daily_percent
FROM (
    SELECT action_date,
           COUNT(DISTINCT post_id) * 100.0
           / (
               SELECT COUNT(DISTINCT post_id)
               FROM Actions
               WHERE action_date = a.action_date
           ) AS daily_avg
    FROM Actions a
    INNER JOIN Removals r ON a.post_id = r.post_id
    WHERE a.extra = 'spam'
    GROUP BY action_date
) daily;


-- Problem 9: Second Degree Follower (LC #614)
-- Difficulty: Hard
-- Approach: find users who are both a follower AND have followers
-- self join followee to follower column
-- Key insight: INNER JOIN on followee = follower finds the overlap

SELECT f1.follower,
       COUNT(DISTINCT f2.follower) AS num
FROM Follow f1
INNER JOIN Follow f2 ON f1.follower = f2.followee
GROUP BY f1.follower
ORDER BY f1.follower;


-- Problem 10: Student Attendance Record II (LC variant) /
--             Suspicious Bank Accounts (LC #1843)
-- Difficulty: Hard
-- Approach: SUM income per account per month
-- flag accounts where any month exceeds max_income
-- Key insight: HAVING MAX(monthly) > max_income catches the violation month

WITH monthly_income AS (
    SELECT account_id,
           DATE_FORMAT(day, '%Y-%m')  AS month,
           SUM(amount)                AS monthly_total
    FROM Transactions
    WHERE type = 'Creditor'
    GROUP BY account_id, DATE_FORMAT(day, '%Y-%m')
)
SELECT DISTINCT mi.account_id
FROM monthly_income mi
INNER JOIN Accounts a ON mi.account_id = a.account_id
WHERE mi.monthly_total > a.max_income
ORDER BY mi.account_id;


-- Problem 11: Countries You Can Never Return (LC variant) /
--             The Number of Employees Which Report to Each Employee (LC #1731)
-- Difficulty: Hard
-- Approach: self join employees to managers
-- count direct reports and average their age per manager
-- Key insight: LEFT JOIN finds managers with zero reports too

SELECT e.employee_id,
       e.name,
       COUNT(r.employee_id)          AS reports_count,
       ROUND(AVG(r.age))             AS average_age
FROM Employees e
INNER JOIN Employees r ON r.reports_to = e.employee_id
GROUP BY e.employee_id, e.name
ORDER BY e.employee_id;


-- Problem 12: Primary Department for Each Employee (LC #1789)
-- Difficulty: Hard
-- Approach: employees with one department get that department
-- employees with multiple departments get the primary_flag = Y one
-- Key insight: UNION handles both cases cleanly without complex CASE

SELECT employee_id,
       department_id
FROM Employee
WHERE primary_flag = 'Y'
UNION
SELECT employee_id,
       department_id
FROM Employee
GROUP BY employee_id
HAVING COUNT(*) = 1
ORDER BY employee_id;


-- Problem 13: Triangle Judgement (LC #610)
-- Difficulty: Medium-Hard
-- Approach: triangle inequality — sum of any two sides must exceed third
-- CASE WHEN checks all three combinations
-- Key insight: if A+B>C AND B+C>A AND A+C>B then valid triangle

SELECT x,
       y,
       z,
       CASE WHEN x + y > z
             AND y + z > x
             AND x + z > y
            THEN 'Yes'
            ELSE 'No'
       END AS triangle
FROM Triangle
ORDER BY x, y, z;


-- Problem 14: Top Travellers (LC #1407)
-- Difficulty: Medium-Hard
-- Approach: SUM distance per user, LEFT JOIN so users with no rides show 0
-- COALESCE handles NULL distance for users with zero rides
-- Key insight: LEFT JOIN + COALESCE is the zero-safe aggregation pattern

SELECT u.name,
       COALESCE(SUM(r.distance), 0) AS travelled_distance
FROM Users u
LEFT JOIN Rides r ON u.id = r.user_id
GROUP BY u.id, u.name
ORDER BY travelled_distance DESC, u.name ASC;


-- Problem 15: Page Recommendations II (LC #1892)
-- Difficulty: Hard
-- Approach: for each user find their friends, then find pages friends liked
-- exclude pages the user already liked
-- Key insight: bidirectional friendship requires UNION ALL before joining pages

WITH all_friendships AS (
    SELECT user1_id AS user_id, user2_id AS friend_id
    FROM Friendship
    UNION ALL
    SELECT user2_id, user1_id
    FROM Friendship
),
friend_pages AS (
    SELECT af.user_id,
           l.page_id,
           COUNT(DISTINCT af.friend_id) AS friends_likes
    FROM all_friendships af
    INNER JOIN Likes l ON af.friend_id = l.user_id
    WHERE NOT EXISTS (
        SELECT 1
        FROM Likes ul
        WHERE ul.user_id = af.user_id
          AND ul.page_id = l.page_id
    )
    GROUP BY af.user_id, l.page_id
)
SELECT user_id,
       page_id,
       friends_likes
FROM friend_pages
ORDER BY user_id, page_id;