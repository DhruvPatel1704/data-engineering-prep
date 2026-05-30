-- Problem 1: Trips and Users (LC #262)
-- Difficulty: Hard
-- Approach: JOIN users twice to filter banned clients AND drivers
-- then conditional aggregation for cancellation rate in date range
-- Key insight: both client and driver must be unbanned — two separate joins to Users

SELECT t.request_at                                                        AS Day,
       ROUND(
           SUM(CASE WHEN t.status LIKE 'cancelled%' THEN 1 ELSE 0 END)
           * 1.0 / COUNT(*), 2
       )                                                                   AS 'Cancellation Rate'
FROM Trips t
INNER JOIN Users u1 ON t.client_id = u1.users_id AND u1.banned = 'No'
INNER JOIN Users u2 ON t.driver_id = u2.users_id AND u2.banned = 'No'
WHERE t.request_at BETWEEN '2013-10-01' AND '2013-10-03'
GROUP BY t.request_at
ORDER BY t.request_at;


-- Problem 2: Human Traffic of Stadium (LC #601)
-- Difficulty: Hard
-- Approach: id - ROW_NUMBER() trick to group consecutive rows into islands
-- filter islands where the group has 3 or more rows all with people >= 100
-- Key insight: consecutive IDs minus row_number = constant for each consecutive group

WITH filtered AS (
    SELECT id,
           visit_date,
           people,
           id - ROW_NUMBER() OVER (ORDER BY id) AS island
    FROM Stadium
    WHERE people >= 100
),
valid_islands AS (
    SELECT island
    FROM filtered
    GROUP BY island
    HAVING COUNT(*) >= 3
)
SELECT f.id,
       f.visit_date,
       f.people
FROM filtered f
INNER JOIN valid_islands v ON f.island = v.island
ORDER BY f.visit_date;


-- Problem 3: Average Salary: Departments VS Company (LC #615)
-- Difficulty: Hard
-- Approach: two CTEs — one for company monthly avg, one for dept monthly avg
-- join them and compare using CASE WHEN
-- Key insight: window function alternative would be AVG OVER() but CTE is more readable

WITH company_avg AS (
    SELECT DATE_FORMAT(pay_date, '%Y-%m') AS pay_month,
           AVG(amount)                    AS company_avg_salary
    FROM Salary
    GROUP BY DATE_FORMAT(pay_date, '%Y-%m')
),
dept_avg AS (
    SELECT DATE_FORMAT(s.pay_date, '%Y-%m') AS pay_month,
           e.department_id,
           AVG(s.amount)                    AS dept_avg_salary
    FROM Salary s
    INNER JOIN Employee e ON s.employee_id = e.employee_id
    GROUP BY DATE_FORMAT(s.pay_date, '%Y-%m'), e.department_id
)
SELECT d.pay_month,
       d.department_id,
       CASE WHEN d.dept_avg_salary > c.company_avg_salary THEN 'higher'
            WHEN d.dept_avg_salary < c.company_avg_salary THEN 'lower'
            ELSE 'same'
       END AS comparison
FROM dept_avg d
INNER JOIN company_avg c ON d.pay_month = c.pay_month
ORDER BY d.pay_month DESC, d.department_id;


-- Problem 4: Game Play Analysis V (LC #1097)
-- Difficulty: Hard
-- Approach: CTE to get install date per player (first login)
-- LEFT JOIN back to Activity to check if player logged in next day
-- Key insight: year filter goes in JOIN condition to preserve left join behavior

WITH first_login AS (
    SELECT player_id,
           MIN(event_date) AS install_date
    FROM Activity
    GROUP BY player_id
)
SELECT f.install_date,
       COUNT(f.player_id)                                      AS installs,
       ROUND(
           COUNT(a.player_id) * 1.0 / COUNT(f.player_id), 2
       )                                                       AS Day1_retention
FROM first_login f
LEFT JOIN Activity a ON f.player_id = a.player_id
                    AND a.event_date = DATE_ADD(f.install_date, INTERVAL 1 DAY)
GROUP BY f.install_date
ORDER BY f.install_date;


-- Problem 5: Median Employee Salary (LC #569)
-- Difficulty: Hard
-- Approach: ROW_NUMBER per company ordered by salary + total count per company
-- median position math: for n rows, median rows are where rn is between n/2 and n/2+1
-- Key insight: works for both odd and even counts without MEDIAN function
-- n=5: rn between 2.5 and 3.5 → picks rn=3 only
-- n=4: rn between 2.0 and 3.0 → picks rn=2 and rn=3 both

WITH ranked AS (
    SELECT id,
           company,
           salary,
           ROW_NUMBER() OVER (PARTITION BY company ORDER BY salary, id) AS rn,
           COUNT(*)     OVER (PARTITION BY company)                     AS cnt
    FROM Employee
)
SELECT id,
       company,
       salary
FROM ranked
WHERE rn >= cnt / 2.0
  AND rn <= cnt / 2.0 + 1
ORDER BY company, salary;