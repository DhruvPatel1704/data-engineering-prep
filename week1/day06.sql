-- Problem 1: Tournament Winners (LC #1194)
-- Difficulty: Hard
-- Approach: UNION ALL both player columns into one column with points
-- then sum points per group, rank within group, filter rank = 1
-- Key insight: unpivoting two columns into one with UNION ALL before aggregating

WITH all_results AS (
    SELECT first_player  AS player_id,
           first_score   AS score,
           group_id
    FROM Players p
    INNER JOIN Matches m ON p.player_id = m.first_player
    UNION ALL
    SELECT second_player AS player_id,
           second_score  AS score,
           group_id
    FROM Players p
    INNER JOIN Matches m ON p.player_id = m.second_player
),
player_totals AS (
    SELECT group_id,
           player_id,
           SUM(score) AS total_score
    FROM all_results
    GROUP BY group_id, player_id
),
ranked AS (
    SELECT group_id,
           player_id,
           total_score,
           RANK() OVER (
               PARTITION BY group_id
               ORDER BY total_score DESC, player_id ASC
           ) AS rnk
    FROM player_totals
)
SELECT group_id,
       player_id
FROM ranked
WHERE rnk = 1
ORDER BY group_id;


-- Problem 2: Find the Subtasks That Did Not Execute (LC #1767)
-- Difficulty: Hard
-- Approach: recursive CTE generates all expected subtask ids per task
-- LEFT JOIN to Executed table to find missing ones
-- Key insight: recursive CTE counting down from subtasks_count to 1
-- generates the complete expected set to diff against actual

WITH RECURSIVE all_subtasks AS (
    SELECT task_id,
           subtasks_count AS subtask_id
    FROM Tasks
    UNION ALL
    SELECT task_id,
           subtask_id - 1
    FROM all_subtasks
    WHERE subtask_id > 1
)
SELECT a.task_id,
       a.subtask_id
FROM all_subtasks a
LEFT JOIN Executed e ON a.task_id = e.task_id
                    AND a.subtask_id = e.subtask_id
WHERE e.task_id IS NULL
ORDER BY a.task_id, a.subtask_id;


-- Problem 3: Build the Equation (LC #1656 variant) /
--            Active Businesses (LC #1454)
-- Difficulty: Hard
-- Approach: calculate average per event type across all businesses
-- then find businesses where more than one event type exceeds its average
-- Key insight: window AVG over entire partition gives global avg per event type
-- compare each row against its event type global average in one pass

WITH event_avgs AS (
    SELECT business_id,
           event_type,
           occurences,
           AVG(occurences) OVER (
               PARTITION BY event_type
           ) AS avg_occurences
    FROM Events
)
SELECT business_id
FROM event_avgs
WHERE occurences > avg_occurences
GROUP BY business_id
HAVING COUNT(*) > 1;


-- Problem 4: Merge Overlapping Events in the Same Hall (LC #2494)
-- Difficulty: Hard
-- Approach: detect where a new event starts (no overlap with previous end)
-- use cumulative MAX of end_day to check if current start overlaps
-- then group overlapping events and take MIN start MAX end
-- Key insight: LAG on MAX end_day detects event group boundaries

WITH ordered AS (
    SELECT hall_id,
           start_day,
           end_day,
           MAX(end_day) OVER (
               PARTITION BY hall_id
               ORDER BY start_day
               ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
           ) AS prev_max_end
    FROM HallOfFame
),
grouped AS (
    SELECT hall_id,
           start_day,
           end_day,
           SUM(CASE WHEN start_day > prev_max_end
                     OR prev_max_end IS NULL
                    THEN 1 ELSE 0 END
           ) OVER (
               PARTITION BY hall_id
               ORDER BY start_day
           ) AS grp
    FROM ordered
)
SELECT hall_id,
       MIN(start_day) AS start_day,
       MAX(end_day)   AS end_day
FROM grouped
GROUP BY hall_id, grp
ORDER BY hall_id, start_day;


-- Problem 5: Median of a Column Without Median Function (LC #571)
-- Difficulty: Hard
-- Approach: for each number count how many are <= it and >= it
-- median condition: both counts must be >= half the total frequency sum
-- Key insight: avoids ROW_NUMBER by using frequency column directly
-- handles duplicate values correctly unlike the ROW_NUMBER approach

WITH total AS (
    SELECT SUM(frequency) AS total_freq
    FROM Numbers
),
cumulative AS (
    SELECT num,
           frequency,
           SUM(frequency) OVER (ORDER BY num)                          AS cum_asc,
           SUM(frequency) OVER (ORDER BY num DESC)                     AS cum_desc,
           SUM(frequency) OVER ()                                      AS total
    FROM Numbers
)
SELECT ROUND(AVG(num), 1) AS median
FROM cumulative
WHERE cum_asc  >= total / 2.0
  AND cum_desc >= total / 2.0;