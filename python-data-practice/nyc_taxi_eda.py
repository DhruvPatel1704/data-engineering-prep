# NYC Yellow Taxi Trip Data — January 2024
# Exploratory Data Analysis
# Dataset: 2.9M rows, Parquet format from NYC TLC

import pandas as pd
import numpy as np

# Load data
df = pd.read_parquet("data/yellow_tripdata_2024-01.parquet")


# Function 1: Basic dataset overview
def dataset_overview(df):
    print("DATASET OVERVIEW")
    print(f"Shape:   {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"Memory:  {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    print(f"\nColumns:\n{df.dtypes}")
    print(f"\nNull counts:\n{df.isnull().sum()}")


# Function 2: Fare statistics
def fare_statistics(df):
    print("\nFARE STATISTICS")
    stats = df["fare_amount"].describe()
    print(stats.round(2))
    print(f"\nNegative fares:  {(df['fare_amount'] < 0).sum():,}")
    print(f"Zero fares:      {(df['fare_amount'] == 0).sum():,}")
    print(f"Fares over $200: {(df['fare_amount'] > 200).sum():,}")


# Function 3: Trip distance analysis
def trip_distance_analysis(df):
    print("\nTRIP DISTANCE ANALYSIS")
    print(f"Average distance:  {df['trip_distance'].mean():.2f} miles")
    print(f"Median distance:   {df['trip_distance'].median():.2f} miles")
    print(f"Max distance:      {df['trip_distance'].max():.2f} miles")
    print(f"Zero distance trips: {(df['trip_distance'] == 0).sum():,}")
    print(f"Trips over 50 miles: {(df['trip_distance'] > 50).sum():,}")


# Function 4: Passenger count breakdown
def passenger_breakdown(df):
    print("\nPASSENGER COUNT BREAKDOWN")
    counts = df["passenger_count"].value_counts().sort_index()
    total = len(df)
    for passengers, count in counts.items():
        pct = count / total * 100
        print(f"  {int(passengers)} passenger(s): {count:>10,}  ({pct:.1f}%)")


# Function 5: Payment type distribution
def payment_distribution(df):
    print("\nPAYMENT TYPE DISTRIBUTION")
    payment_map = {1: "Credit card", 2: "Cash", 3: "No charge", 4: "Dispute", 5: "Unknown"}
    counts = df["payment_type"].value_counts()
    total = len(df)
    for ptype, count in counts.items():
        label = payment_map.get(ptype, f"Type {ptype}")
        pct = count / total * 100
        print(f"  {label:<15}: {count:>10,}  ({pct:.1f}%)")


# Function 6: Hourly demand pattern
def hourly_demand(df):
    print("\nHOURLY DEMAND (top 5 and bottom 5 hours)")
    df["hour"] = pd.to_datetime(df["tpep_pickup_datetime"]).dt.hour
    hourly = df.groupby("hour").size().rename("trips")
    print("Busiest hours:")
    print(hourly.nlargest(5).to_string())
    print("\nQuietest hours:")
    print(hourly.nsmallest(5).to_string())


# Function 7: Revenue per mile efficiency
def revenue_per_mile(df):
    print("\nREVENUE PER MILE")
    clean = df[(df["trip_distance"] > 0) & (df["fare_amount"] > 0)].copy()
    clean["revenue_per_mile"] = clean["fare_amount"] / clean["trip_distance"]
    print(f"Average revenue per mile: ${clean['revenue_per_mile'].mean():.2f}")
    print(f"Median revenue per mile:  ${clean['revenue_per_mile'].median():.2f}")
    print(f"p95 revenue per mile:     ${clean['revenue_per_mile'].quantile(0.95):.2f}")


# Function 8: Tip analysis by payment type
def tip_analysis(df):
    print("\nTIP ANALYSIS BY PAYMENT TYPE")
    payment_map = {1: "Credit card", 2: "Cash"}
    for ptype, label in payment_map.items():
        subset = df[df["payment_type"] == ptype]["tip_amount"]
        print(f"\n  {label}:")
        print(f"    Average tip:  ${subset.mean():.2f}")
        print(f"    Median tip:   ${subset.median():.2f}")
        print(f"    Zero tips:    {(subset == 0).sum():,}")


# Function 9: Trip duration analysis
def trip_duration(df):
    print("\nTRIP DURATION ANALYSIS")
    df["duration_min"] = (
        pd.to_datetime(df["tpep_dropoff_datetime"]) -
        pd.to_datetime(df["tpep_pickup_datetime"])
    ).dt.total_seconds() / 60
    valid = df[(df["duration_min"] > 0) & (df["duration_min"] < 180)]
    print(f"Average duration:  {valid['duration_min'].mean():.1f} minutes")
    print(f"Median duration:   {valid['duration_min'].median():.1f} minutes")
    print(f"Trips under 2 min: {(df['duration_min'] < 2).sum():,}")
    print(f"Trips over 2 hrs:  {(df['duration_min'] > 120).sum():,}")


# Function 10: Data quality report
def data_quality_report(df):
    print("\nDATA QUALITY REPORT")
    total = len(df)
    issues = {
        "Negative fares":       (df["fare_amount"] < 0).sum(),
        "Zero distance trips":  (df["trip_distance"] == 0).sum(),
        "Missing passengers":   df["passenger_count"].isnull().sum(),
        "Future pickup dates":  (pd.to_datetime(df["tpep_pickup_datetime"]) > pd.Timestamp("2024-02-01")).sum(),
        "Fare over $500":       (df["fare_amount"] > 500).sum(),
    }
    for issue, count in issues.items():
        pct = count / total * 100
        print(f"  {issue:<25}: {count:>8,}  ({pct:.2f}%)")


if __name__ == "__main__":
    print(f"Loaded {len(df):,} rows\n")
    dataset_overview(df)
    fare_statistics(df)
    trip_distance_analysis(df)
    passenger_breakdown(df)
    payment_distribution(df)
    hourly_demand(df)
    revenue_per_mile(df)
    tip_analysis(df)
    trip_duration(df)
    data_quality_report(df)
    print("\nEDA complete")