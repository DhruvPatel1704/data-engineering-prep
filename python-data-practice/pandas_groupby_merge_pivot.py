import pandas as pd
import numpy as np

df = pd.read_parquet("data/yellow_tripdata_2024-01.parquet")
df["hour"]=pd.to_datetime(df["tpep_pickup_datetime"]).dt.hour
df["date"]=pd.to_datetime(df["tpep_pickup_datetime"]).dt.date
df["day_of_week"]=pd.to_datetime(df["tpep_pickup_datetime"]).dt.day_name()

print(f"Loaded {len(df):,} rows\n")

#single kay groupby
result=df.groupby("payment_type")["fare_amount"].sum().round(2)
print(result)

#Multi-kay groupby
result=df.groupby(["payment_type","passenger_count"])["fare_amount"].mean().round(2)
print(result.head(4))

# "Find the top 3 payment types by revenue per hour
#  and flag any hour where revenue dropped more than 20%
#  compared to the previous hour"
# Skills: groupby, pivot, pct_change, conditional flagging

print("SCENARIO 1: Top payment types by hour + revenue drop flag")

hourly_payment = df.groupby(["hour", "payment_type"])["fare_amount"].sum().round(2)
hourly_total = df.groupby("hour")["fare_amount"].sum().round(2).reset_index()
hourly_total.columns = ["hour", "total_revenue"]
hourly_total["prev_hour_revenue"] = hourly_total["total_revenue"].shift(1)
hourly_total["pct_change"] = (
    (hourly_total["total_revenue"] - hourly_total["prev_hour_revenue"])
    / hourly_total["prev_hour_revenue"] * 100
).round(2)
hourly_total["revenue_drop_flag"] = hourly_total["pct_change"] < -20

print(hourly_total[["hour", "total_revenue", "pct_change", "revenue_drop_flag"]])
flagged = hourly_total[hourly_total["revenue_drop_flag"] == True]
print(f"\nHours with >20% revenue drop: {len(flagged)}")
print(flagged[["hour", "pct_change"]])

# "Find drivers (vendor) whose average fare is consistently
#  above the overall average. Flag trips that are outliers
#  (more than 2 standard deviations above mean fare per vendor)"
# Skills: transform, std, conditional flagging, merge

print("\nSCENARIO 2: Vendor performance vs overall average + outlier detection")

overall_avg = df["fare_amount"].mean()
print(f"Overall average fare: ${overall_avg:.2f}")

vendor_stats = df.groupby("VendorID")["fare_amount"].agg(
    vendor_avg  = "mean",
    vendor_std  = "std",
    trip_count  = "count"
).round(2).reset_index()

vendor_stats["above_overall_avg"] = vendor_stats["vendor_avg"] > overall_avg
print(vendor_stats)

df["vendor_avg"] = df.groupby("VendorID")["fare_amount"].transform("mean")
df["vendor_std"] = df.groupby("VendorID")["fare_amount"].transform("std")
df["is_outlier"] = df["fare_amount"] > (df["vendor_avg"] + 2 * df["vendor_std"])

print(f"\nTotal outlier trips: {df['is_outlier'].sum():,}")
print(f"Outlier rate: {df['is_outlier'].mean() * 100:.2f}%")

# "Build a cohort analysis — for each day of week,
#  find the busiest hour, average fare, and tip rate.
#  Rank days by total revenue"
# Skills: groupby multi-key, named agg, rank, pivot

print("\nSCENARIO 3: Day of week cohort analysis with rankings")

dow_hourly = df.groupby(["day_of_week", "hour"]).agg(
    trips       = ("fare_amount", "count"),
    avg_fare    = ("fare_amount", "mean"),
    total_rev   = ("fare_amount", "sum"),
    tip_rate    = ("tip_amount", "mean")
).round(2).reset_index()

busiest_hour_per_day = dow_hourly.loc[
    dow_hourly.groupby("day_of_week")["trips"].idxmax()
][["day_of_week", "hour", "trips"]].rename(columns={"hour": "busiest_hour"})

daily_summary = df.groupby("day_of_week").agg(
    total_revenue   = ("fare_amount", "sum"),
    total_trips     = ("fare_amount", "count"),
    avg_tip         = ("tip_amount", "mean")
).round(2).reset_index()

daily_summary["revenue_rank"] = daily_summary["total_revenue"].rank(
    ascending=False).astype(int)

daily_summary = daily_summary.merge(busiest_hour_per_day, on="day_of_week")
daily_summary = daily_summary.sort_values("revenue_rank")
print(daily_summary.to_string(index=False))

# "Identify data quality issues in the pipeline:
#  find trips with impossible values, calculate what % of
#  total revenue they represent, and produce a clean dataset"
# Skills: filtering, masking, merge, data quality reporting

print("\nSCENARIO 4: Data quality audit and pipeline cleaning")

total_trips = len(df)
total_revenue = df["fare_amount"].sum()

issues = {
    "negative_fare":        df["fare_amount"] < 0,
    "zero_distance":        df["trip_distance"] == 0,
    "fare_over_500":        df["fare_amount"] > 500,
    "negative_tip":         df["tip_amount"] < 0,
    "zero_passenger":       df["passenger_count"] == 0,
}

print(f"{'Issue':<25} {'Count':>10} {'% Trips':>10} {'Revenue Lost':>15}")
for issue, mask in issues.items():
    count = mask.sum()
    pct_trips = count / total_trips * 100
    rev_lost = df[mask]["fare_amount"].sum()
    print(f"{issue:<25} {count:>10,} {pct_trips:>9.2f}% {rev_lost:>15,.2f}")

any_issue = (
    (df["fare_amount"] < 0) |
    (df["trip_distance"] == 0) |
    (df["fare_amount"] > 500) |
    (df["tip_amount"] < 0) |
    (df["passenger_count"] == 0)
)

clean_df = df[~any_issue].copy()
print(f"\nOriginal dataset:  {total_trips:,} rows")
print(f"Clean dataset:     {len(clean_df):,} rows")
print(f"Removed:           {total_trips - len(clean_df):,} rows ({(total_trips - len(clean_df)) / total_trips * 100:.2f}%)")

# Pivot Table
# total revenue for each hour x payment type combination
# rows = hours, columns = payment types

print("\nPIVOT TABLE: Revenue by hour and payment type")

pivot = df.pivot_table(
    values  = "fare_amount",
    index   = "hour",
    columns = "payment_type",
    aggfunc = "sum"
).round(2)

print(pivot.head(10))
print(f"\nPivot shape: {pivot.shape} — {pivot.shape[0]} hours x {pivot.shape[1]} payment types")

# Apply + Lambda
# classify each trip into fare buckets
# then count trips and revenue per bucket

print("\nAPPLY + LAMBDA: Fare bucket classification")

df["fare_bucket"] = df["fare_amount"].apply(
    lambda x: "low"     if x < 10
    else "medium"       if x < 30
    else "high"         if x < 100
    else "premium"
)

bucket_summary = df.groupby("fare_bucket").agg(
    trips   = ("fare_amount", "count"),
    revenue = ("fare_amount", "sum"),
    avg_fare = ("fare_amount", "mean")
).round(2)

print(bucket_summary)

# Transform
# add column showing each trip's % of its payment type total revenue
# transform keeps all rows — same shape as original

print("\nTRANSFORM: Each trip as % of payment type total revenue")

df["payment_type_total"] = df.groupby("payment_type")["fare_amount"].transform("sum")
df["pct_of_payment_type"] = (df["fare_amount"] / df["payment_type_total"] * 100).round(4)

print(df[["fare_amount", "payment_type", "payment_type_total", "pct_of_payment_type"]].head(10))
print(f"\nSum of pct_of_payment_type for payment_type=1: "
      f"{df[df['payment_type']==1]['pct_of_payment_type'].sum():.2f}% (should be 100%)")