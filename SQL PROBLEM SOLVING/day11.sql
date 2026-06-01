-- Problem 16: Find the Missing IDs (LC #1613)
-- Difficulty: Hard
-- Approach: recursive CTE generates sequence 1 to max customer_id
-- LEFT JOIN to Customers, return IDs that have no match
-- Key insight: recursive sequence generation is core DE pattern
-- used for filling gaps in ID sequences or date spines

WITH RECURSIVE sequence AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM sequence
    WHERE n < (SELECT MAX(customer_id) FROM Customers)
)
SELECT n AS ids
FROM sequence
WHERE n NOT IN (
    SELECT customer_id
    FROM Customers
)
ORDER BY ids;


-- Problem 17: Count Vowel Substrings of a String (LC variant) /
--             Find Interview Candidates (LC #2083)
-- Difficulty: Hard
-- Approach: find users with gold medal (rank 1) in 3+ contests
-- OR gold medal in at least 3 consecutive contests
-- Key insight: two separate CTEs with UNION, gold = rank 1

WITH gold_counts AS (
    SELECT user_id,
           COUNT(*) AS gold_medals
    FROM Contest
    WHERE gold_medal = user_id
    GROUP BY user_id
    HAVING COUNT(*) >= 3
),
consecutive_golds AS (
    SELECT user_id
    FROM (
        SELECT user_id,
               contest_id,
               contest_id - ROW_NUMBER() OVER (
                   PARTITION BY user_id
                   ORDER BY contest_id
               ) AS grp
        FROM Contest
        WHERE gold_medal = user_id
    ) ranked
    GROUP BY user_id, grp
    HAVING COUNT(*) >= 3
)
SELECT DISTINCT user_id
FROM (
    SELECT user_id FROM gold_counts
    UNION
    SELECT user_id FROM consecutive_golds
) combined
ORDER BY user_id;


-- Problem 18: Minimum Number of Days to Eat N Oranges (LC variant) /
--             Biggest Window Between Visits (LC #1454 variant) /
--             User Activity for the Past 30 Days I (LC #1141)
-- Difficulty: Hard
-- Approach: count distinct sessions per day in 30 day window
-- session = activity within 30 days before 2019-07-27
-- Key insight: date range filter in WHERE, COUNT DISTINCT session_id

SELECT activity_date            AS day,
       COUNT(DISTINCT session_id) AS active_sessions
FROM Activity
WHERE activity_date > DATE_SUB('2019-07-27', INTERVAL 30 DAY)
  AND activity_date <= '2019-07-27'
GROUP BY activity_date
ORDER BY activity_date;


-- Problem 19: Product Sales Analysis III (LC #1070)
-- Difficulty: Hard
-- Approach: find first year each product was sold
-- return all sales records matching that product + year combination
-- Key insight: CTE for first year, join back to get full row details

WITH first_year AS (
    SELECT product_id,
           MIN(year) AS first_sale_year
    FROM Sales
    GROUP BY product_id
)
SELECT s.product_id,
       s.year        AS first_year,
       s.quantity,
       s.price
FROM Sales s
INNER JOIN first_year fy ON s.product_id = fy.product_id
                        AND s.year = fy.first_sale_year
ORDER BY s.product_id;


-- Problem 20: Group Sold Products By The Date (LC #1484)
-- Difficulty: Medium-Hard
-- Approach: GROUP_CONCAT aggregates multiple product names per date
-- ORDER BY inside GROUP_CONCAT ensures alphabetical order
-- Key insight: GROUP_CONCAT with DISTINCT and ORDER BY is MySQL specific
-- Snowflake equivalent is LISTAGG, BigQuery is STRING_AGG

SELECT sell_date,
       COUNT(DISTINCT product)                                      AS num_sold,
       GROUP_CONCAT(DISTINCT product ORDER BY product SEPARATOR ',') AS products
FROM Activities
GROUP BY sell_date
ORDER BY sell_date;


-- Problem 21: List the Products Ordered in a Period (LC #1517 variant) /
--             Countries You Can Never Return variant /
--             Find the Quiet Students variant /
--             Sellers With No Sales (LC #1607)
-- Difficulty: Hard
-- Approach: find sellers who made zero sales in 2020
-- LEFT JOIN + IS NULL exclusion pattern
-- Key insight: year filter in JOIN condition preserves all sellers in left table

SELECT s.seller_name
FROM Seller s
LEFT JOIN Orders o ON s.seller_id = o.seller_id
                  AND YEAR(o.sale_date) = 2020
WHERE o.order_id IS NULL
ORDER BY s.seller_name;


-- Problem 22: Unique Substrings (LC variant) /
--             Count the Number of Experiments (LC #2388)
-- Difficulty: Hard
-- Approach: CROSS JOIN platforms and experiments spine
-- LEFT JOIN to actual Experiments table
-- count actual experiments or 0 for missing combinations
-- Key insight: full spine generation ensures all platform x experiment combos appear

WITH platforms AS (
    SELECT 'Android'  AS platform
    UNION ALL SELECT 'IOS'
    UNION ALL SELECT 'Web'
),
experiment_names AS (
    SELECT 'Reading'  AS experiment_name
    UNION ALL SELECT 'Sports'
    UNION ALL SELECT 'Programming'
),
spine AS (
    SELECT platform, experiment_name
    FROM platforms
    CROSS JOIN experiment_names
)
SELECT s.platform,
       s.experiment_name,
       COUNT(e.experiment_id) AS num_experiments
FROM spine s
LEFT JOIN Experiments e ON s.platform = e.platform
                       AND s.experiment_name = e.experiment_name
GROUP BY s.platform, s.experiment_name
ORDER BY s.platform, s.experiment_name;


-- Problem 23: Stocks Price Fluctuation (LC variant) /
--             Maximum Transaction Each Day (LC #2205)
-- Difficulty: Hard
-- Approach: rank transactions by amount desc per day
-- return the transaction with highest amount each day
-- handle ties by returning smaller transaction_id

WITH daily_ranked AS (
    SELECT transaction_id,
           DATE(day)  AS transaction_day,
           amount,
           RANK() OVER (
               PARTITION BY DATE(day)
               ORDER BY amount DESC
           ) AS rnk
    FROM Transactions
    WHERE type = 'Creditor'
)
SELECT transaction_id
FROM daily_ranked
WHERE rnk = 1
ORDER BY transaction_id;


-- Problem 24: Find Users With Valid E-Mails (LC #1517)
-- Difficulty: Hard
-- Approach: REGEXP to validate email format
-- prefix must start with letter, contain only letters/digits/underscore/period/dash
-- domain must be @leetcode.com exactly
-- Key insight: anchored regex pattern ^ and $ prevent partial matches

SELECT user_id,
       name,
       mail
FROM Users
WHERE mail REGEXP '^[a-zA-Z][a-zA-Z0-9_.-]*@leetcode\\.com$'
ORDER BY user_id;


-- Problem 25: Customers With Strictly Increasing Purchases (LC #2monotone variant) /
--             Determine if a Cell Is Reachable at a Given Time variant /
--             Consecutive Transactions with Increasing Amounts (LC #2837)
-- Difficulty: Hard
-- Approach: get annual total per customer, compare each year to previous
-- using LAG to get prior year total
-- exclude customers where any year's total is not strictly greater

WITH annual_totals AS (
    SELECT customer_id,
           YEAR(transaction_date)    AS yr,
           SUM(amount)               AS yearly_total
    FROM Transactions
    GROUP BY customer_id, YEAR(transaction_date)
),
with_prev AS (
    SELECT customer_id,
           yr,
           yearly_total,
           LAG(yearly_total) OVER (
               PARTITION BY customer_id
               ORDER BY yr
           ) AS prev_total,
           LAG(yr) OVER (
               PARTITION BY customer_id
               ORDER BY yr
           ) AS prev_yr
    FROM annual_totals
),
violations AS (
    SELECT DISTINCT customer_id
    FROM with_prev
    WHERE prev_total IS NOT NULL
      AND (yearly_total <= prev_total
       OR yr != prev_yr + 1)
)
SELECT customer_id
FROM (
    SELECT DISTINCT customer_id FROM Transactions
) all_customers
WHERE customer_id NOT IN (SELECT customer_id FROM violations)
ORDER BY customer_id;