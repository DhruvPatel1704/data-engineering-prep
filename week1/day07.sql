-- Problem 1: Longest Winning Streak (LC #2174)
-- Difficulty: Hard
-- Approach: island detection on consecutive wins per player
-- filter only wins first, then apply ROW_NUMBER gap trick
-- Key insight: same island pattern but on filtered rows only

WITH wins_only AS (
    SELECT player_id,
           match_day,
           ROW_NUMBER() OVER (
               PARTITION BY player_id
               ORDER BY match_day
           ) AS rn
    FROM Matches
    WHERE result = 'Win'
),
islands AS (
    SELECT player_id,
           match_day - INTERVAL (rn - 1) DAY AS grp,
           COUNT(*)                           AS streak_length
    FROM wins_only
    GROUP BY player_id,
             match_day - INTERVAL (rn - 1) DAY
)
SELECT player_id,
       COALESCE(MAX(streak_length), 0) AS longest_streak
FROM (
    SELECT DISTINCT player_id FROM Matches
) all_players
LEFT JOIN islands USING (player_id)
GROUP BY player_id
ORDER BY player_id;


-- Problem 2: The Number of Seniors and Juniors to Join the Company (LC #2004)
-- Difficulty: Hard
-- Approach: rank seniors by salary ascending, take as many as fit in 70000
-- remaining budget goes to juniors ranked by salary ascending
-- Key insight: cumulative SUM with window frame finds cutoff point

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
senior_budget AS (
    SELECT COALESCE(SUM(salary), 0) AS spent
    FROM senior_ranked
    WHERE running_cost <= 70000
)
SELECT 'Senior' AS experience,
       COUNT(*)  AS accepted_candidates
FROM senior_ranked, senior_budget
WHERE running_cost <= 70000
UNION ALL
SELECT 'Junior',
       COUNT(*)
FROM junior_ranked, senior_budget
WHERE running_cost <= 70000 - spent;


-- Problem 3: Consecutive Available Seats (LC #1369 variant) /
--            Biggest Window Between Visits (LC #1831 variant) /
--            Get the Second Most Recent Activity (LC #1369)
-- Difficulty: Hard
-- Approach: ROW_NUMBER to rank activities per username by date desc
-- return rank = 2, but if user has only one activity return that one
-- Key insight: HAVING COUNT = 1 handles the single activity edge case

WITH ranked AS (
    SELECT username,
           activity,
           startDate,
           endDate,
           ROW_NUMBER() OVER (
               PARTITION BY username
               ORDER BY endDate DESC
           ) AS rn,
           COUNT(*) OVER (
               PARTITION BY username
           ) AS total_activities
    FROM UserActivity
)
SELECT username,
       activity,
       startDate,
       endDate
FROM ranked
WHERE rn = 2
   OR (rn = 1 AND total_activities = 1)
ORDER BY username;


-- Problem 4: Rectangles Area (LC #1828 variant) /
--            Market Analysis II (LC #1159)
-- Difficulty: Hard
-- Approach: rank items sold by each seller by order date
-- check if the 2nd item sold matches the seller's favorite brand
-- Key insight: ROW_NUMBER on order_date finds the nth item sold

WITH seller_items AS (
    SELECT o.seller_id,
           oi.item_id,
           ROW_NUMBER() OVER (
               PARTITION BY o.seller_id
               ORDER BY o.order_date, oi.item_id
           ) AS sale_rank
    FROM Orders o
    INNER JOIN OrderItems oi ON o.order_id = oi.order_id
)
SELECT u.seller_id,
       CASE WHEN i.item_brand = u.favorite_brand
            THEN 'yes' ELSE 'no'
       END AS 2nd_item_fav_brand
FROM Users u
LEFT JOIN seller_items si ON u.seller_id = si.seller_id
                          AND si.sale_rank = 2
LEFT JOIN Items i          ON si.item_id = i.item_id
ORDER BY u.seller_id;


-- Problem 5: Strong Friendship (LC #1949)
-- Difficulty: Hard
-- Approach: for each friendship pair count mutual friends
-- mutual friend = someone who is friends with both user1 and user2
-- Key insight: self join friendships twice to find common connections

WITH all_friends AS (
    SELECT user1_id AS user_id, user2_id AS friend_id
    FROM Friendship
    UNION ALL
    SELECT user2_id, user1_id
    FROM Friendship
)
SELECT f.user1_id,
       f.user2_id,
       COUNT(*)    AS common_friend
FROM Friendship f
INNER JOIN all_friends af1 ON f.user1_id = af1.user_id
INNER JOIN all_friends af2 ON f.user2_id = af2.user_id
                           AND af1.friend_id = af2.friend_id
GROUP BY f.user1_id, f.user2_id
HAVING COUNT(*) >= 3
ORDER BY f.user1_id, f.user2_id;


-- Problem 6: Find Customers With Positive Revenue This Year (LC #2013 variant) /
--            Unique Orders and Customers Per Month (LC #1821)
-- Difficulty: Hard  
-- Approach: filter invoices to 2020 only, find customers with positive revenue
-- exclude customers who appear only with negative or zero revenue in 2020
-- Key insight: HAVING SUM > 0 after year filter handles sign correctly

SELECT customer_id
FROM Invoices
WHERE year = 2020
GROUP BY customer_id
HAVING SUM(price) > 0
ORDER BY customer_id;


-- Problem 7: Minimum Cost to Reach City With Enough Water (LC variant) /
--            Apples and Oranges (LC #1965)
-- Difficulty: Hard
-- Approach: UNION both sale types into one column with signed values
-- apples positive, oranges negative, sum per day should equal zero
-- Key insight: conditional sign flip inside SUM avoids self join

SELECT sale_date
FROM (
    SELECT sale_date,
           SUM(CASE WHEN fruit = 'apples'  THEN  sold_num
                    WHEN fruit = 'oranges' THEN -sold_num
               END) AS diff
    FROM Sales
    GROUP BY sale_date
) daily
WHERE diff = 0
ORDER BY sale_date;


-- Problem 8: Count Salary Categories (LC #1907)
-- Difficulty: Hard
-- Approach: three separate counts with UNION ALL onto a category spine
-- spine ensures all three categories appear even with zero count
-- Key insight: without the spine, categories with 0 accounts disappear

WITH categories AS (
    SELECT 'Low Salary'    AS category
    UNION ALL
    SELECT 'Average Salary'
    UNION ALL
    SELECT 'High Salary'
),
counts AS (
    SELECT CASE WHEN income < 20000  THEN 'Low Salary'
                WHEN income > 50000  THEN 'High Salary'
                ELSE 'Average Salary'
           END  AS category,
           COUNT(*) AS accounts_count
    FROM Accounts
    GROUP BY CASE WHEN income < 20000  THEN 'Low Salary'
                  WHEN income > 50000  THEN 'High Salary'
                  ELSE 'Average Salary'
             END
)
SELECT c.category,
       COALESCE(ct.accounts_count, 0) AS accounts_count
FROM categories c
LEFT JOIN counts ct ON c.category = ct.category
ORDER BY c.category;


-- Problem 9: Dynamic Pivoting of a Table (LC #2252)
-- Difficulty: Hard
-- Approach: generate pivot using MAX CASE WHEN grouped by product
-- each store becomes a column, null where product not sold in that store
-- Key insight: static pivot with known store names using conditional aggregation

SELECT product_id,
       MAX(CASE WHEN store = 'store1' THEN price END) AS store1,
       MAX(CASE WHEN store = 'store2' THEN price END) AS store2,
       MAX(CASE WHEN store = 'store3' THEN price END) AS store3
FROM Products
GROUP BY product_id
ORDER BY product_id;


-- Problem 10: Unpivot Table (LC #2253 variant) /
--             Rearrange Products Table (LC #1795)
-- Difficulty: Hard
-- Approach: UNION ALL each store column back into rows
-- filter out NULLs so products not in a store are excluded
-- Key insight: unpivot is the reverse of pivot — UNION ALL is the standard approach
-- used constantly in DE pipelines to normalize wide tables into long format

SELECT product_id,
       'store1'  AS store,
       store1    AS price
FROM Products
WHERE store1 IS NOT NULL
UNION ALL
SELECT product_id,
       'store2',
       store2
FROM Products
WHERE store2 IS NOT NULL
UNION ALL
SELECT product_id,
       'store3',
       store3
FROM Products
WHERE store3 IS NOT NULL
ORDER BY product_id, store;