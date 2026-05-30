-- Problem 1: Hopper Company Queries II (LC #1645)
-- Difficulty: Hard
-- Approach: recursive CTE for month spine, calculate working drivers
-- working = accepted at least one ride that month
-- Key insight: driver must have joined before or during month AND accepted a ride

WITH RECURSIVE months AS (
    SELECT 1 AS month
    UNION ALL
    SELECT month + 1
    FROM months
    WHERE month < 12
),
active_drivers AS (
    SELECT m.month,
           d.driver_id
    FROM months m
    INNER JOIN Drivers d ON YEAR(d.join_date) < 2020
                         OR (YEAR(d.join_date) = 2020
                             AND MONTH(d.join_date) <= m.month)
),
working_drivers AS (
    SELECT MONTH(r.requested_at) AS month,
           ar.driver_id
    FROM Rides r
    INNER JOIN AcceptedRides ar ON r.ride_id = ar.ride_id
    WHERE YEAR(r.requested_at) = 2020
)
SELECT m.month,
       CASE WHEN COUNT(ad.driver_id) = 0 THEN 0
            ELSE ROUND(
                COUNT(DISTINCT wd.driver_id) * 100.0
                / COUNT(DISTINCT ad.driver_id), 2
            )
       END AS working_percentage
FROM months m
LEFT JOIN active_drivers ad ON m.month = ad.month
LEFT JOIN working_drivers wd ON m.month = wd.month
                             AND ad.driver_id = wd.driver_id
GROUP BY m.month
ORDER BY m.month;


-- Problem 2: Hopper Company Queries III (LC #1651)
-- Difficulty: Hard
-- Approach: 3-month rolling average of ride distance and duration
-- window frame of 3 months using LAG or ROWS BETWEEN
-- Key insight: rolling average with explicit frame is standard pipeline metric

WITH monthly_stats AS (
    SELECT MONTH(r.requested_at)              AS month,
           SUM(ar.ride_distance)              AS total_distance,
           SUM(ar.ride_duration)              AS total_duration
    FROM Rides r
    INNER JOIN AcceptedRides ar ON r.ride_id = ar.ride_id
    WHERE YEAR(r.requested_at) = 2020
    GROUP BY MONTH(r.requested_at)
),
all_months AS (
    SELECT m.month,
           COALESCE(ms.total_distance, 0) AS total_distance,
           COALESCE(ms.total_duration, 0) AS total_duration
    FROM (
        SELECT 1 AS month UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
        UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8
        UNION SELECT 9 UNION SELECT 10 UNION SELECT 11 UNION SELECT 12
    ) m
    LEFT JOIN monthly_stats ms ON m.month = ms.month
)
SELECT month,
       ROUND(AVG(total_distance) OVER (
           ORDER BY month
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
       ), 2) AS average_ride_distance,
       ROUND(AVG(total_duration) OVER (
           ORDER BY month
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
       ), 2) AS average_ride_duration
FROM all_months
ORDER BY month;


-- Problem 3: User Purchase Platform (LC #1127)
-- Difficulty: Hard
-- Approach: generate all date + platform combinations using CROSS JOIN
-- then LEFT JOIN actual spend data onto that spine
-- Key insight: spine generation with CROSS JOIN ensures zero rows appear
-- same pattern used in DE pipelines for complete date x dimension reporting

WITH platforms AS (
    SELECT 'desktop' AS platform
    UNION ALL
    SELECT 'mobile'
),
dates AS (
    SELECT DISTINCT spend_date FROM Spending
),
spine AS (
    SELECT d.spend_date, p.platform
    FROM dates d
    CROSS JOIN platforms p
),
user_platform AS (
    SELECT spend_date,
           user_id,
           CASE WHEN COUNT(DISTINCT platform) = 2 THEN 'both'
                ELSE MAX(platform)
           END                AS platform,
           SUM(amount)        AS total_amount
    FROM Spending
    GROUP BY spend_date, user_id
)
SELECT s.spend_date,
       s.platform,
       COALESCE(SUM(up.total_amount), 0) AS total_amount,
       COUNT(DISTINCT up.user_id)        AS total_users
FROM spine s
LEFT JOIN user_platform up ON s.spend_date = up.spend_date
                           AND s.platform = up.platform
GROUP BY s.spend_date, s.platform
ORDER BY s.spend_date, s.platform;


-- Problem 4: Report Contiguous Dates (LC #1225)
-- Difficulty: Hard
-- Approach: UNION both tables with a status label, then apply island detection
-- date - ROW_NUMBER() as date difference groups consecutive dates
-- Key insight: island trick works on dates too, not just integers

WITH all_dates AS (
    SELECT fail_date  AS dt, 'failed'    AS period_state
    FROM Failed
    WHERE fail_date BETWEEN '2019-01-01' AND '2019-12-31'
    UNION ALL
    SELECT success_date, 'succeeded'
    FROM Succeeded
    WHERE success_date BETWEEN '2019-01-01' AND '2019-12-31'
),
grouped AS (
    SELECT dt,
           period_state,
           dt - INTERVAL (ROW_NUMBER() OVER (
               PARTITION BY period_state
               ORDER BY dt
           ) - 1) DAY AS grp
    FROM all_dates
)
SELECT period_state,
       MIN(dt) AS start_date,
       MAX(dt) AS end_date
FROM grouped
GROUP BY period_state, grp
ORDER BY start_date;


-- Problem 5: Number of Transactions per Visit (LC #1336)
-- Difficulty: Hard
-- Approach: recursive CTE generates transaction count spine 0 to max
-- LEFT JOIN actual visit/transaction data onto spine to include zero rows
-- Key insight: users who visited but made 0 transactions must still appear
-- two-level aggregation: first count per user per day, then count users per bucket

WITH visits_with_count AS (
    SELECT v.user_id,
           v.visit_date,
           COUNT(t.transaction_date) AS transaction_count
    FROM Visits v
    LEFT JOIN Transactions t ON v.user_id = t.user_id
                             AND v.visit_date = t.transaction_date
    GROUP BY v.user_id, v.visit_date
),
max_count AS (
    SELECT MAX(transaction_count) AS max_txn
    FROM visits_with_count
),
RECURSIVE count_spine AS (
    SELECT 0 AS transactions_count
    UNION ALL
    SELECT transactions_count + 1
    FROM count_spine, max_count
    WHERE transactions_count < max_txn
)
SELECT cs.transactions_count,
       COUNT(vc.user_id) AS visits_count
FROM count_spine cs
LEFT JOIN visits_with_count vc ON cs.transactions_count = vc.transaction_count
GROUP BY cs.transactions_count
ORDER BY cs.transactions_count