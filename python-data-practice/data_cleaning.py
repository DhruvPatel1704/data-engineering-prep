# Data Cleaning Pipeline
# Production patterns for handling nulls, duplicates, outliers, strings, dates
# Dataset: NYC Yellow Taxi January 2024

import re
import pandas as pd
import numpy as np

df = pd.read_parquet("data/yellow_tripdata_2024-01.parquet")
print(f"Loaded {len(df):,} rows\n")

# SECTION 1 — NULL STRATEGIES

print("=" * 60)
print("SECTION 1 — NULL STRATEGIES")
print("=" * 60)

# first always understand your nulls before touching them
print("\nNull counts per column:")
print(df.isnull().sum()[df.isnull().sum() > 0])
print("\nNull percentage:")
print((df.isnull().sum() / len(df) * 100).round(2)[df.isnull().sum() > 0])


# strategy 1: dropna — only when safe
# safe = the column is REQUIRED and cannot be inferred
# unsafe = dropping removes too many rows or the column can be filled

print("\n1a. dropna — safe when column is required and null means bad row")
before = len(df)
df_dropped = df.dropna(subset=["fare_amount", "trip_distance"])
after = len(df_dropped)
print(f"Rows before: {before:,}")
print(f"Rows after:  {after:,}")
print(f"Dropped:     {before - after:,} ({(before - after) / before * 100:.2f}%)")
# rule: if dropping removes more than 5% of data — reconsider


# strategy 2: fillna with strategy dict
# different columns need different fill strategies

print("\n1b. fillna with strategy dict")
fill_strategies = {
    "passenger_count": 1,  # assume solo rider
    "congestion_surcharge": 0.0,  # assume no surcharge
    "airport_fee": 0.0,  # assume no airport fee
    "tip_amount": 0.0,  # assume no tip
}

df_filled = df.copy()
for col, fill_value in fill_strategies.items():
    if col in df_filled.columns:
        null_count = df_filled[col].isnull().sum()
        df_filled[col] = df_filled[col].fillna(fill_value)
        print(f"  {col:<30} filled {null_count:>8,} nulls with {fill_value}")


# strategy 3: flag-and-fill pattern
# fill nulls BUT add a flag column so downstream knows which were filled
# critical in DE — never silently impute without tracking it

print("\n1c. flag-and-fill pattern")
df_flagged = df.copy()

if "passenger_count" in df_flagged.columns:
    df_flagged["passenger_count_was_null"] = df_flagged["passenger_count"].isnull()
    df_flagged["passenger_count"] = df_flagged["passenger_count"].fillna(1)
    flagged_count = df_flagged["passenger_count_was_null"].sum()
    print(f"  Flagged and filled {flagged_count:,} null passenger counts")
    print("  New column 'passenger_count_was_null' tracks imputed rows")


# strategy 4: fill with group statistics
# fill nulls using the median of a related group
# better than global median for skewed data

print("\n1d. fill with group median (payment_type group)")
df_group_fill = df.copy()
if "tip_amount" in df_group_fill.columns:
    df_group_fill["tip_amount"] = df_group_fill.groupby("payment_type")[
        "tip_amount"
    ].transform(lambda x: x.fillna(x.median()))
    print("  tip_amount nulls filled with median per payment_type group")


# SECTION 2 — DUPLICATE DETECTION

print("\n" + "=" * 60)
print("SECTION 2 — DUPLICATE DETECTION")
print("=" * 60)


# strategy 1: exact duplicates on all columns
print("\n2a. exact full-row duplicates")
exact_dupes = df.duplicated().sum()
print(f"Exact duplicate rows: {exact_dupes:,}")


# strategy 2: subset key duplicates
# in a trips dataset, same pickup time + location = likely duplicate
print("\n2b. subset key duplicates")
subset_cols = ["tpep_pickup_datetime", "fare_amount", "trip_distance"]
subset_dupes = df.duplicated(subset=subset_cols).sum()
print(f"Duplicate on {subset_cols}: {subset_dupes:,}")


# strategy 3: keep logic
# keep='first' → keep earliest occurrence
# keep='last'  → keep most recent occurrence
# keep=False   → mark ALL duplicates (useful for investigation)

print("\n2c. keep logic")
df_deduped_first = df.drop_duplicates(subset=subset_cols, keep="first")
df_deduped_last = df.drop_duplicates(subset=subset_cols, keep="last")
all_dupes = df[df.duplicated(subset=subset_cols, keep=False)]

print(f"  keep='first': {len(df_deduped_first):,} rows")
print(f"  keep='last':  {len(df_deduped_last):,} rows")
print(f"  all duplicates flagged: {len(all_dupes):,} rows")


# strategy 4: ROW_NUMBER equivalent in pandas
# keep only the most recent record per group — same as SQL dedup pattern

print("\n2d. ROW_NUMBER dedup — keep latest per pickup time + fare")
df["row_num"] = df.groupby(subset_cols).cumcount() + 1
df_deduped_rownum = df[df["row_num"] == 1].drop(columns=["row_num"])
print(f"  After ROW_NUMBER dedup: {len(df_deduped_rownum):,} rows")


# strategy 5: fuzzy deduplication concept
# exact match misses near-duplicates
# fuzzy: two trips within 1 minute and same fare = likely duplicate

print("\n2e. fuzzy dedup concept — trips within same minute with same fare")
df_sample = df.head(10_000).copy()
df_sample["pickup_minute"] = pd.to_datetime(df_sample["tpep_pickup_datetime"]).dt.floor(
    "min"
)

fuzzy_dupes = df_sample.duplicated(
    subset=["pickup_minute", "fare_amount", "passenger_count"], keep="first"
).sum()
print(f"  Fuzzy duplicates in sample 10k rows: {fuzzy_dupes:,}")
print("  Full fuzzy dedup would use record linkage or Levenshtein distance")


# SECTION 3 — OUTLIER DETECTION

print("\n" + "=" * 60)
print("SECTION 3 — OUTLIER DETECTION")
print("=" * 60)


# strategy 1: IQR fence method
# IQR = interquartile range = Q3 - Q1
# lower fence = Q1 - 1.5 * IQR
# upper fence = Q3 + 1.5 * IQR
# anything outside these fences = outlier

print("\n3a. IQR fence method on fare_amount")
Q1 = df["fare_amount"].quantile(0.25)
Q3 = df["fare_amount"].quantile(0.75)
IQR = Q3 - Q1

lower_fence = Q1 - 1.5 * IQR
upper_fence = Q3 + 1.5 * IQR

outliers_iqr = df[(df["fare_amount"] < lower_fence) | (df["fare_amount"] > upper_fence)]

print(f"  Q1:          ${Q1:.2f}")
print(f"  Q3:          ${Q3:.2f}")
print(f"  IQR:         ${IQR:.2f}")
print(f"  Lower fence: ${lower_fence:.2f}")
print(f"  Upper fence: ${upper_fence:.2f}")
print(f"  Outliers:    {len(outliers_iqr):,} ({len(outliers_iqr)/len(df)*100:.2f}%)")


# strategy 2: z-score method
# z-score = (value - mean) / std
# z > 3 or z < -3 = more than 3 standard deviations from mean = outlier
# best for normally distributed data

print("\n3b. z-score method on fare_amount")
mean = df["fare_amount"].mean()
std = df["fare_amount"].std()

df["fare_zscore"] = (df["fare_amount"] - mean) / std
outliers_zscore = df[df["fare_zscore"].abs() > 3]

print(f"  Mean:     ${mean:.2f}")
print(f"  Std:      ${std:.2f}")
print(f"  Outliers: {len(outliers_zscore):,} ({len(outliers_zscore)/len(df)*100:.2f}%)")


# strategy 3: log transform for skewed data
# fare data is right-skewed — most fares are low, few are very high
# log transform compresses the range, makes outlier detection more accurate

print("\n3c. log transform for skewed fare data")
print(f"  Original skewness: {df['fare_amount'][df['fare_amount'] > 0].skew():.2f}")

df["fare_log"] = np.log1p(df["fare_amount"].clip(lower=0))
print(f"  Log-transformed skewness: {df['fare_log'].skew():.2f}")
print("  Skewness closer to 0 = more normal distribution")
print("  np.log1p(x) = log(1+x) — handles zero values safely")


# strategy 4: percentile capping (winsorization)
# instead of removing outliers, cap them at a threshold
# safer than dropping — preserves row count

print("\n3d. percentile capping (winsorization)")
p01 = df["fare_amount"].quantile(0.01)
p99 = df["fare_amount"].quantile(0.99)

df["fare_capped"] = df["fare_amount"].clip(lower=p01, upper=p99)
print(f"  1st percentile:  ${p01:.2f}")
print(f"  99th percentile: ${p99:.2f}")
print(
    f"  Values capped:   {((df['fare_amount'] < p01) | (df['fare_amount'] > p99)).sum():,}"
)
print(f"  Max after cap:   ${df['fare_capped'].max():.2f}")


# SECTION 4 — STRING CLEANING

print("\n" + "=" * 60)
print("SECTION 4 — STRING CLEANING")
print("=" * 60)

# create a sample string column to demonstrate cleaning
# taxi dataset doesn't have many strings so we simulate realistic DE scenarios

sample_strings = pd.DataFrame(
    {
        "store_name": [
            "  Starbucks ",
            "MCDONALD'S",
            "subway",
            "Dunkin Donuts  ",
            "7-ELEVEN",
        ],
        "phone": [
            "(212) 555-1234",
            "212.555.5678",
            "2125559012",
            "212-555-3456",
            "+1 212 555 7890",
        ],
        "zip_code": ["10001", "10001-1234", "10 001", "NY10001", "10001"],
        "category": [
            "Coffee Shop",
            "fast_food",
            "FAST FOOD",
            "coffee-shop",
            "Convenience",
        ],
        "email": [
            "user@example.com",
            "ADMIN@COMPANY.COM",
            "  test@test.org  ",
            "bad-email",
            "valid@email.co",
        ],
    }
)

print("\nOriginal strings:")
print(sample_strings)


# .str accessor — apply string methods to entire column
print("\n4a. normalize + strip + lower")
sample_strings["store_name_clean"] = (
    sample_strings["store_name"]
    .str.strip()  # remove leading and trailing whitespace
    .str.lower()  # convert to lowercase
    .str.replace(r"['\-]", "", regex=True)  # remove apostrophes and hyphens
    .str.replace(r"\s+", " ", regex=True)  # collapse multiple spaces
)
print(sample_strings[["store_name", "store_name_clean"]])


# compiled regex patterns — compile once, reuse many times
# faster than re-compiling pattern on every row

print("\n4b. regex compile patterns for phone cleaning")
phone_pattern = re.compile(r"[\s\(\)\-\.\+]")  # characters to remove

sample_strings["phone_clean"] = (
    sample_strings["phone"]
    .str.replace(phone_pattern, "", regex=True)
    .str.replace(r"^1", "", regex=True)  # remove leading country code
)
print(sample_strings[["phone", "phone_clean"]])


# email validation with regex
print("\n4c. email validation with regex")
email_pattern = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

sample_strings["email_clean"] = sample_strings["email"].str.strip().str.lower()
sample_strings["email_valid"] = sample_strings["email_clean"].str.match(email_pattern)
print(sample_strings[["email", "email_clean", "email_valid"]])


# category normalization
print("\n4d. category normalization")
sample_strings["category_normalized"] = (
    sample_strings["category"]
    .str.lower()
    .str.strip()
    .str.replace(
        r"[\-_]", " ", regex=True
    )  # replace hyphens and underscores with space
    .str.replace(r"\s+", " ", regex=True)
)
print(sample_strings[["category", "category_normalized"]])


# zip code extraction with regex
print("\n4e. zip code extraction")
zip_pattern = re.compile(r"(\d{5})")
sample_strings["zip_clean"] = (
    sample_strings["zip_code"]
    .str.replace(r"\s", "", regex=True)  # remove spaces
    .str.extract(zip_pattern, expand=False)  # extract 5-digit zip
)
print(sample_strings[["zip_code", "zip_clean"]])


# SECTION 5 — DATE HANDLING

print("\n" + "=" * 60)
print("SECTION 5 — DATE HANDLING")
print("=" * 60)


# strategy 1: basic pd.to_datetime with format
print("\n5a. pd.to_datetime with explicit format")
date_strings = pd.Series(
    [
        "2024-01-15 14:32:05",
        "2024-01-16 09:15:00",
        "not-a-date",  # bad value
        "2024-01-17 23:59:59",
        "",  # empty string
    ]
)

# errors='coerce' converts bad values to NaT instead of raising exception
# critical for production — bad dates should not crash your pipeline
parsed_dates = pd.to_datetime(date_strings, format="%Y-%m-%d %H:%M:%S", errors="coerce")
print(parsed_dates)
print(f"\nNaT count (bad dates): {parsed_dates.isna().sum()}")


# strategy 2: handle multiple date formats
print("\n5b. handle multiple date formats with errors='coerce'")
mixed_dates = pd.Series(
    ["2024-01-15", "01/15/2024", "January 15, 2024", "20240115", "bad-date"]
)

parsed_mixed = pd.to_datetime(mixed_dates, errors="coerce")
print(parsed_mixed)


# strategy 3: timezone-aware parsing
print("\n5c. timezone-aware parsing")
df_taxi = df.copy()
df_taxi["pickup_utc"] = pd.to_datetime(df_taxi["tpep_pickup_datetime"]).dt.tz_localize(
    "America/New_York"
)  # localize to NYC timezone

df_taxi["pickup_utc_converted"] = df_taxi["pickup_utc"].dt.tz_convert("UTC")

print(df_taxi[["tpep_pickup_datetime", "pickup_utc", "pickup_utc_converted"]].head(3))


# strategy 4: extract date components for analysis
print("\n5d. extract date components")
df_taxi["hour"] = df_taxi["pickup_utc"].dt.hour
df_taxi["day_of_week"] = df_taxi["pickup_utc"].dt.day_name()
df_taxi["month"] = df_taxi["pickup_utc"].dt.month
df_taxi["is_weekend"] = df_taxi["pickup_utc"].dt.dayofweek >= 5
df_taxi["is_rush_hour"] = df_taxi["hour"].isin([7, 8, 9, 17, 18, 19])

weekend_trips = df_taxi["is_weekend"].sum()
rush_trips = df_taxi["is_rush_hour"].sum()
print(f"  Weekend trips:   {weekend_trips:,} ({weekend_trips/len(df_taxi)*100:.1f}%)")
print(f"  Rush hour trips: {rush_trips:,} ({rush_trips/len(df_taxi)*100:.1f}%)")


# strategy 5: date arithmetic and duration
print("\n5e. date arithmetic — delivery time calculation")
df_taxi["duration_minutes"] = (
    pd.to_datetime(df_taxi["tpep_dropoff_datetime"])
    - pd.to_datetime(df_taxi["tpep_pickup_datetime"])
).dt.total_seconds() / 60

valid_durations = df_taxi[
    (df_taxi["duration_minutes"] > 0) & (df_taxi["duration_minutes"] < 180)
]
print(
    f"  Average trip duration: {valid_durations['duration_minutes'].mean():.1f} minutes"
)
print(
    f"  Median trip duration:  {valid_durations['duration_minutes'].median():.1f} minutes"
)
print(f"  Trips under 2 min:     {(df_taxi['duration_minutes'] < 2).sum():,}")
print(f"  Trips over 2 hours:    {(df_taxi['duration_minutes'] > 120).sum():,}")


print("\nData cleaning pipeline complete")
