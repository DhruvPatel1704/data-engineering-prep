-- Problem 1: Find the Start and End Number of Continuous Ranges (LC #1285)
-- Difficulty: Hard
-- Approach: id - ROW_NUMBER() trick groups consecutive IDs into islands
-- then MIN and MAX of each island gives start and end of the range
-- Key insight: same island trick from day 3 LC 601 — core DE pattern for gap detection

WITH grouped AS (
    SELECT log_id,
           log_id - ROW_NUMBER() OVER (ORDER BY log_id) AS grp
    FROM Logs
)
SELECT MIN(log_id) AS start_id,
       MAX(log_id) AS end_id
FROM grouped
GROUP BY grp
ORDER BY start_id;


-- Problem 2: Sales by Day of the Week (LC #1479)
-- Difficulty: Hard
-- Approach: LEFT JOIN items to orders, pivot with CASE WHEN per day of week
-- DAYOFWEEK returns 1=Sunday, 2=Monday ... 7=Saturday in MySQL
-- Key insight: this is manual pivot — standard DE pattern when PIVOT keyword unavailable

SELECT i.item_category                                                          AS Category,
       SUM(CASE WHEN DAYOFWEEK(o.order_date) = 2 THEN o.quantity ELSE 0 END)   AS Monday,
       SUM(CASE WHEN DAYOFWEEK(o.order_date) = 3 THEN o.quantity ELSE 0 END)   AS Tuesday,
       SUM(CASE WHEN DAYOFWEEK(o.order_date) = 4 THEN o.quantity ELSE 0 END)   AS Wednesday,
       SUM(CASE WHEN DAYOFWEEK(o.order_date) = 5 THEN o.quantity ELSE 0 END)   AS Thursday,
       SUM(CASE WHEN DAYOFWEEK(o.order_date) = 6 THEN o.quantity ELSE 0 END)   AS Friday,
       SUM(CASE WHEN DAYOFWEEK(o.order_date) = 7 THEN o.quantity ELSE 0 END)   AS Saturday,
       SUM(CASE WHEN DAYOFWEEK(o.order_date) = 1 THEN o.quantity ELSE 0 END)   AS Sunday
FROM Items i
LEFT JOIN Orders o ON i.item_id = o.item_id
GROUP BY i.item_category
ORDER BY i.item_category;


-- Problem 3: Find the Quiet Students in All Exams (LC #1412)
-- Difficulty: Hard
-- Approach: three CTEs — exam min/max scores, students who hit either extreme,
-- students who took at least one exam — then exclude the noisy ones
-- Key insight: NOT IN exclusion pattern is cleaner than a LEFT JOIN IS NULL here

WITH exam_stats AS (
    SELECT exam_id,
           MAX(score) AS max_score,
           MIN(score) AS min_score
    FROM Exam
    GROUP BY exam_id
),
noisy_students AS (
    SELECT DISTINCT e.student_id
    FROM Exam e
    INNER JOIN exam_stats es ON e.exam_id = es.exam_id
    WHERE e.score = es.max_score
       OR e.score = es.min_score
),
took_exam AS (
    SELECT DISTINCT student_id
    FROM Exam
)
SELECT s.student_id,
       s.student_name
FROM Student s
INNER JOIN took_exam te ON s.student_id = te.student_id
WHERE s.student_id NOT IN (SELECT student_id FROM noisy_students)
ORDER BY s.student_id;


-- Problem 4: Hopper Company Queries I (LC #1635)
-- Difficulty: Hard
-- Approach: recursive CTE generates months 1-12 as a calendar spine
-- LEFT JOIN drivers and accepted rides onto the calendar
-- Key insight: recursive CTE for calendar generation is a core DE pattern
-- used in every pipeline that needs to report on months with zero activity

WITH RECURSIVE months AS (
    SELECT 1 AS month
    UNION ALL
    SELECT month + 1
    FROM months
    WHERE month < 12
),
active_drivers AS (
    SELECT m.month,
           COUNT(d.driver_id) AS active_count
    FROM months m
    LEFT JOIN Drivers d ON YEAR(d.join_date) < 2020
                        OR (YEAR(d.join_date) = 2020
                            AND MONTH(d.join_date) <= m.month)
    GROUP BY m.month
),
monthly_rides AS (
    SELECT MONTH(r.requested_at)  AS month,
           COUNT(ar.ride_id)      AS accepted_count
    FROM Rides r
    INNER JOIN AcceptedRides ar ON r.ride_id = ar.ride_id
    WHERE YEAR(r.requested_at) = 2020
    GROUP BY MONTH(r.requested_at)
)
SELECT m.month,
       COALESCE(ad.active_count, 0)   AS active_drivers,
       COALESCE(mr.accepted_count, 0) AS accepted_rides
FROM months m
LEFT JOIN active_drivers ad ON m.month = ad.month
LEFT JOIN monthly_rides  mr ON m.month = mr.month
ORDER BY m.month;


-- Problem 5: Students Report By Geography (LC #618)
-- Difficulty: Hard
-- Approach: ROW_NUMBER per continent to create a row spine
-- then pivot using MAX + CASE WHEN grouped by that row number
-- Key insight: ROW_NUMBER creates the alignment between continents
-- without it MAX CASE would collapse all names into one row per continent

WITH ranked AS (
    SELECT name,
           continent,
           ROW_NUMBER() OVER (
               PARTITION BY continent
               ORDER BY name
           ) AS rn
    FROM Student
)
SELECT MAX(CASE WHEN continent = 'America' THEN name END) AS America,
       MAX(CASE WHEN continent = 'Asia'    THEN name END) AS Asia,
       MAX(CASE WHEN continent = 'Europe'  THEN name END) AS Europe
FROM ranked
GROUP BY rn
ORDER BY rn;