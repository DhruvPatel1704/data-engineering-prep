#!/bin/bash
# Bash Essentials for Data Engineers
# grep, awk, sed, cut, sort, uniq, xargs, pipes, cron
# Practice on simulated pipeline logs and CSV data

# create sample data to practice on
cat > /tmp/sample_logs.txt << 'EOF'
2024-01-15 08:32:05 INFO  pipeline=taxi_pipeline stage=ingest rows=2964624
2024-01-15 08:32:45 INFO  pipeline=taxi_pipeline stage=validate rows=2964624
2024-01-15 08:33:10 WARN  pipeline=taxi_pipeline stage=validate issue=negative_fares count=123
2024-01-15 08:34:02 INFO  pipeline=taxi_pipeline stage=transform rows=2910000
2024-01-15 08:34:55 INFO  pipeline=taxi_pipeline stage=save rows=2910000
2024-01-15 09:15:00 ERROR pipeline=weather_pipeline stage=ingest error=file_not_found
2024-01-15 09:16:00 INFO  pipeline=weather_pipeline stage=ingest rows=50000
2024-01-15 10:00:00 INFO  pipeline=taxi_pipeline stage=ingest rows=3100000
2024-01-15 10:01:30 ERROR pipeline=taxi_pipeline stage=validate error=schema_mismatch
2024-01-15 10:02:00 INFO  pipeline=sales_pipeline stage=ingest rows=150000
EOF

cat > /tmp/sample_data.csv << 'EOF'
date,pipeline,rows_processed,duration_sec,status
2024-01-15,taxi_pipeline,2964624,120,success
2024-01-15,weather_pipeline,50000,15,success
2024-01-15,sales_pipeline,150000,45,success
2024-01-16,taxi_pipeline,3100000,135,failed
2024-01-16,weather_pipeline,48000,14,success
2024-01-16,sales_pipeline,155000,47,success
2024-01-17,taxi_pipeline,2900000,118,success
2024-01-17,weather_pipeline,0,0,failed
2024-01-17,sales_pipeline,160000,50,success
EOF

echo "sample files created"
echo ""


# 1. grep — find all ERROR lines in logs
# -n shows line numbers, -c counts matches, -v inverts match
echo "1. grep — find ERROR lines"
grep "ERROR" /tmp/sample_logs.txt

echo ""
echo "   with line numbers:"
grep -n "ERROR" /tmp/sample_logs.txt

echo ""
echo "   count of errors:"
grep -c "ERROR" /tmp/sample_logs.txt

echo ""
echo "   lines that are not INFO:"
grep -v "INFO" /tmp/sample_logs.txt


# 2. grep with regex — find errors for a specific pipeline
echo ""
echo "2. grep regex — taxi_pipeline errors only"
grep -E "ERROR.*taxi_pipeline|taxi_pipeline.*ERROR" /tmp/sample_logs.txt


# 3. awk — extract and process columns from structured text
# $1 $2 $3 = first second third field, NF = last field, NR = row number
echo ""
echo "3. awk — extract date, level, pipeline"
awk '{print $1, $3, $4}' /tmp/sample_logs.txt

echo ""
echo "   awk on CSV — pipeline and status"
awk -F',' '{print $2, $5}' /tmp/sample_data.csv

echo ""
echo "   awk — sum total rows across all runs"
awk -F',' 'NR>1 {sum += $3} END {print "total rows:", sum}' /tmp/sample_data.csv


# 4. awk with condition — filter rows meeting a threshold
echo ""
echo "4. awk condition — runs processing over 1M rows"
awk -F',' 'NR>1 && $3 > 1000000 {print $1, $2, $3}' /tmp/sample_data.csv


# 5. sed — find and replace, delete lines
# s/find/replace/g = global substitute, /pattern/d = delete matching lines
echo ""
echo "5. sed — replace ERROR with CRITICAL"
sed 's/ERROR/CRITICAL/g' /tmp/sample_logs.txt

echo ""
echo "   sed — remove WARN lines"
sed '/WARN/d' /tmp/sample_logs.txt


# 6. cut — extract specific columns by delimiter
# -d sets delimiter, -f sets field numbers
echo ""
echo "6. cut — pipeline name and status"
cut -d',' -f2,5 /tmp/sample_data.csv

echo ""
echo "   cut — date column only"
cut -d',' -f1 /tmp/sample_data.csv


# 7. sort + uniq — count frequency of values
# uniq needs sorted input, -c adds count, sort -rn sorts by count descending
echo ""
echo "7. sort + uniq — runs per pipeline"
cut -d',' -f2 /tmp/sample_data.csv | tail -n +2 | sort | uniq -c | sort -rn

echo ""
echo "   unique pipeline names:"
cut -d',' -f2 /tmp/sample_data.csv | tail -n +2 | sort -u


# 8. pipes — chain commands for log analysis
echo ""
echo "8. pipes — most common error types"
grep "ERROR" /tmp/sample_logs.txt \
    | awk '{print $NF}' \
    | sort \
    | uniq -c \
    | sort -rn

echo ""
echo "   failed pipelines with dates"
grep -v "^date" /tmp/sample_data.csv \
    | awk -F',' '$5 == "failed" {print $1, $2}' \
    | sort


# 9. xargs — pass output as arguments to another command
echo ""
echo "9. xargs — line count of all sample files"
find /tmp -name "sample*" | xargs wc -l

echo ""
echo "   xargs — search ERROR across multiple files"
find /tmp -name "sample*" | xargs grep "ERROR"


# 10. full pipeline health check combining everything
echo ""
echo "10. pipeline health report"
echo "total runs:        $(tail -n +2 /tmp/sample_data.csv | wc -l)"
echo "successful runs:   $(grep -c "success" /tmp/sample_data.csv)"
echo "failed runs:       $(grep -c "failed" /tmp/sample_data.csv)"
echo "failed pipelines:"
awk -F',' '$5 == "failed" {print "  " $1, $2}' /tmp/sample_data.csv
echo "total rows processed:"
awk -F',' 'NR>1 {sum += $3} END {print "  " sum}' /tmp/sample_data.csv
echo "average duration (sec):"
awk -F',' 'NR>1 && $4 > 0 {sum += $4; count++} END {printf "  %.1f\n", sum/count}' /tmp/sample_data.csv


# cron syntax reference
# * * * * * command
# | | | | |
# | | | | day of week (0-7)
# | | | month (1-12)
# | | day of month (1-31)
# | hour (0-23)
# minute (0-59)
#
# common schedules:
# 0 6 * * *       every day at 6am
# 0 6 * * 1-5     weekdays at 6am
# */15 * * * *    every 15 minutes
# 0 6 1 * *       first of every month at 6am
#
# schedule pipeline to run at 6am daily:
# crontab -e
# 0 6 * * * /usr/bin/python3 /path/to/end_to_end_pipeline.py >> /var/log/pipeline.log 2>&1
#
# >> appends stdout to log file
# 2>&1 redirects stderr to same place as stdout
# crontab -l to view current crontab
# crontab -e to edit

echo ""
echo "bash practice complete"
