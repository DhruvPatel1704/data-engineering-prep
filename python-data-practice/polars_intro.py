# Polars Introduction — Rewrite NYC Taxi EDA in Polars
# Compare speed with pandas on same operations
# Key patterns: lazy execution, expression API, scan_parquet

import time
import polars as pl
import pandas as pd

SOURCE = "data/yellow_tripdata_2024-01.parquet"


def benchmark(name: str, func):
    """Run a function and return result + elapsed time."""
    start = time.perf_counter()
    result = func()
    elapsed = round(time.perf_counter() - start, 4)
    print(f"  {name:<35} {elapsed:.4f}s")
    return result, elapsed


print("=" * 60)
print("POLARS vs PANDAS BENCHMARK")
print("=" * 60)


# ── 1. Load data ────────────────────────────────────────────

print("\n1. LOADING DATA")

_, pandas_load = benchmark("pandas read_parquet", lambda: pd.read_parquet(SOURCE))

_, polars_load = benchmark("polars read_parquet", lambda: pl.read_parquet(SOURCE))

df_pd = pd.read_parquet(SOURCE)
df_pl = pl.read_parquet(SOURCE)

print(f"\n  Polars speedup: {pandas_load / polars_load:.1f}x faster")
print(f"  Pandas shape:  {df_pd.shape}")
print(f"  Polars shape:  {df_pl.shape}")


# ── 2. Expression API — how Polars thinks ───────────────────

print("\n2. EXPRESSION API")
print("Polars uses expressions — lazy operations chained together")
print("No index — all operations are columnar by default")

# pandas style
df_pd_result = df_pd.groupby("payment_type")["fare_amount"].agg(
    ["sum", "mean", "count"]
)

# polars style — expression API
df_pl_result = (
    df_pl.group_by("payment_type")
    .agg(
        [
            pl.col("fare_amount").sum().alias("total_revenue"),
            pl.col("fare_amount").mean().alias("avg_fare"),
            pl.col("fare_amount").count().alias("trip_count"),
        ]
    )
    .sort("payment_type")
)

print("\nPolars result:")
print(df_pl_result)


# ── 3. Lazy execution — the key Polars advantage ────────────

print("\n3. LAZY EXECUTION")
print("lazy() builds a query plan — nothing runs until collect()")
print("Polars optimizes the entire plan before executing")

# eager (pandas style) — runs immediately
eager_result = (
    df_pl.filter(pl.col("fare_amount") > 0)
    .select(["fare_amount", "trip_distance", "payment_type"])
    .head(5)
)

# lazy (polars optimized) — builds plan first
lazy_query = (
    pl.scan_parquet(SOURCE)  # scan = lazy read, doesn't load file yet
    .filter(pl.col("fare_amount") > 0)
    .filter(pl.col("trip_distance") > 0)
    .select(["fare_amount", "trip_distance", "payment_type", "passenger_count"])
    .with_columns(
        [(pl.col("fare_amount") / pl.col("trip_distance")).alias("revenue_per_mile")]
    )
    .group_by("payment_type")
    .agg(
        [
            pl.col("fare_amount").sum().alias("total_revenue"),
            pl.col("revenue_per_mile").mean().alias("avg_revenue_per_mile"),
            pl.col("fare_amount").count().alias("trips"),
        ]
    )
    .sort("total_revenue", descending=True)
)

print("\nLazy query plan (before collect):")
print(lazy_query.explain())

result = lazy_query.collect()
print("\nResult after collect():")
print(result)


# ── 4. scan_parquet — never loads full file ─────────────────

print("\n4. SCAN_PARQUET vs READ_PARQUET")
print("scan_parquet reads only needed columns and rows")
print("critical for large files — 10GB file, only need 2 columns")

_, scan_time = benchmark(
    "polars scan_parquet (lazy)",
    lambda: (
        pl.scan_parquet(SOURCE)
        .select(["fare_amount", "trip_distance"])
        .filter(pl.col("fare_amount") > 10)
        .collect()
    ),
)

_, read_time = benchmark(
    "polars read_parquet (eager)",
    lambda: (
        pl.read_parquet(SOURCE)[["fare_amount", "trip_distance"]].filter(
            pl.col("fare_amount") > 10
        )
    ),
)

print(f"\n  scan_parquet speedup: {read_time / scan_time:.1f}x faster")


# ── 5. Benchmark common operations ──────────────────────────

print("\n5. OPERATION BENCHMARKS — Polars vs Pandas")

operations = [
    (
        "groupby + agg",
        lambda: df_pd.groupby("payment_type")["fare_amount"].agg(["sum", "mean"]),
        lambda: df_pl.group_by("payment_type").agg(
            [pl.col("fare_amount").sum(), pl.col("fare_amount").mean()]
        ),
    ),
    (
        "filter rows",
        lambda: df_pd[df_pd["fare_amount"] > 10],
        lambda: df_pl.filter(pl.col("fare_amount") > 10),
    ),
    (
        "add computed column",
        lambda: df_pd.assign(
            rev_per_mile=df_pd["fare_amount"]
            / df_pd["trip_distance"].replace(0, float("nan"))
        ),
        lambda: df_pl.with_columns(
            (pl.col("fare_amount") / pl.col("trip_distance").replace(0, None)).alias(
                "rev_per_mile"
            )
        ),
    ),
    (
        "sort by fare desc",
        lambda: df_pd.sort_values("fare_amount", ascending=False),
        lambda: df_pl.sort("fare_amount", descending=True),
    ),
]

pandas_times = []
polars_times = []

for name, pd_op, pl_op in operations:
    _, pd_time = benchmark(f"pandas {name}", pd_op)
    _, pl_time = benchmark(f"polars {name}", pl_op)
    pandas_times.append(pd_time)
    polars_times.append(pl_time)
    speedup = pd_time / pl_time
    print(f"  → Polars {speedup:.1f}x faster\n")

avg_speedup = sum(pandas_times) / sum(polars_times)
print(f"Average speedup across all operations: {avg_speedup:.1f}x")


# ── 6. Key Polars patterns summary ──────────────────────────

print("\n6. KEY POLARS PATTERNS")

# with_columns — add multiple columns at once
result = (
    df_pl.with_columns(
        [
            pl.col("fare_amount").alias("fare"),
            (pl.col("fare_amount") / pl.col("trip_distance").replace(0, None))
            .round(2)
            .alias("revenue_per_mile"),
            pl.col("fare_amount")
            .map_elements(
                lambda x: "low" if x < 10 else "medium" if x < 30 else "high",
                return_dtype=pl.String,
            )
            .alias("fare_bucket"),
        ]
    )
    .select(["fare", "revenue_per_mile", "fare_bucket"])
    .head(5)
)

print("\nwith_columns result:")
print(result)

# when/then/otherwise — polars equivalent of CASE WHEN
result = (
    df_pl.with_columns(
        pl.when(pl.col("fare_amount") < 10)
        .then(pl.lit("low"))
        .when(pl.col("fare_amount") < 30)
        .then(pl.lit("medium"))
        .when(pl.col("fare_amount") < 100)
        .then(pl.lit("high"))
        .otherwise(pl.lit("premium"))
        .alias("fare_bucket")
    )
    .select(["fare_amount", "fare_bucket"])
    .head(5)
)

print("\nwhen/then/otherwise (CASE WHEN equivalent):")
print(result)

print("\nPolars intro complete")
print(f"Key takeaway: Polars is {avg_speedup:.1f}x faster on average")
print("Use Polars for large files, pandas for small files and ML integration")
