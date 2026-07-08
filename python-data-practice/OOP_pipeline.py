# OOP for Data Engineering
# Classes, Decorators, Context Managers, Generators, DataPipeline
# These patterns appear in every production DE codebase

from __future__ import annotations

import time
import functools
import logging
import contextlib
from dataclasses import dataclass, field
from typing import Iterator, Any, Callable
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)


# SECTION 1 — CLASSES
# __init__, methods, @property, @staticmethod, @classmethod

class TaxiTrip:
    """Represents a single taxi trip with validation and computed properties."""

    # class variable — shared across ALL instances
    total_trips_created = 0

    def __init__(self, trip_id: str, fare: float, distance: float, passengers: int):
        # instance variables — unique to each instance
        self.trip_id   = trip_id
        self.fare      = fare
        self.distance  = distance
        self.passengers = passengers
        TaxiTrip.total_trips_created += 1

    # @property — computed attribute, accessed like a variable not a method
    # no () needed when calling: trip.revenue_per_mile not trip.revenue_per_mile()
    @property
    def revenue_per_mile(self) -> float:
        if self.distance == 0:
            return 0.0
        return round(self.fare / self.distance, 2)

    @property
    def is_valid(self) -> bool:
        return self.fare > 0 and self.distance >= 0 and self.passengers > 0

    # @staticmethod — belongs to class but needs no class or instance
    # use when logic is related to class but doesn't need self or cls
    @staticmethod
    def fare_bucket(fare: float) -> str:
        if fare < 10:
            return "low"
        elif fare < 30:
            return "medium"
        elif fare < 100:
            return "high"
        return "premium"

    # @classmethod — receives class itself as first arg (cls not self)
    # use for alternative constructors — create instance from different input
    @classmethod
    def from_dict(cls, data: dict) -> TaxiTrip:
        return cls(
            trip_id    = data.get("trip_id", "unknown"),
            fare       = float(data.get("fare_amount", 0)),
            distance   = float(data.get("trip_distance", 0)),
            passengers = int(data.get("passenger_count", 1))
        )

    @classmethod
    def from_dataframe_row(cls, row: pd.Series) -> TaxiTrip:
        return cls(
            trip_id    = str(row.name),
            fare       = float(row["fare_amount"]),
            distance   = float(row["trip_distance"]),
            passengers = int(row.get("passenger_count", 1))
        )

    def __repr__(self) -> str:
        return f"TaxiTrip(id={self.trip_id}, fare=${self.fare}, dist={self.distance}mi)"


# test the class
print("=" * 60)
print("SECTION 1 — CLASSES")
print("=" * 60)

trip1 = TaxiTrip("T001", fare=25.50, distance=3.2, passengers=2)
trip2 = TaxiTrip.from_dict({"fare_amount": 15.0, "trip_distance": 2.1, "passenger_count": 1})

print(f"Trip 1: {trip1}")
print(f"Revenue per mile: ${trip1.revenue_per_mile}")
print(f"Is valid: {trip1.is_valid}")
print(f"Fare bucket: {TaxiTrip.fare_bucket(trip1.fare)}")
print(f"Total trips created: {TaxiTrip.total_trips_created}")


# DATACLASSES — cleaner way to write data classes
# auto-generates __init__, __repr__, __eq__

@dataclass
class PipelineConfig:
    """Configuration for a data pipeline run."""
    source_path:     str
    output_path:     str
    batch_size:      int   = 10_000
    max_fare:        float = 500.0
    min_distance:    float = 0.0
    remove_nulls:    bool  = True
    tags:            list  = field(default_factory=list)

    def __post_init__(self):
        # runs after __init__ — use for validation
        if self.batch_size <= 0:
            raise ValueError(f"batch_size must be positive, got {self.batch_size}")
        if self.max_fare <= 0:
            raise ValueError(f"max_fare must be positive, got {self.max_fare}")

print("\nDATACLASS:")
config = PipelineConfig(
    source_path  = "data/yellow_tripdata_2024-01.parquet",
    output_path  = "data/clean_trips.parquet",
    batch_size   = 50_000,
    tags         = ["nyc", "taxi", "2024"]
)
print(config)


# SECTION 2 — DECORATORS
# @timer, @retry, @validate_schema

print("\n" + "=" * 60)
print("SECTION 2 — DECORATORS")
print("=" * 60)


# @timer — measures how long a function takes to run
def timer(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info(f"{func.__name__} completed in {elapsed:.4f}s")
        return result
    return wrapper


# @retry — retries a function up to max_attempts times on failure
def retry(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {attempt}/{max_attempts} failed: {e}")
                    if attempt == max_attempts:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator


# @validate_schema — checks DataFrame has required columns before processing
def validate_schema(required_cols: list[str]):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(df: pd.DataFrame, *args, **kwargs):
            missing = set(required_cols) - set(df.columns)
            if missing:
                raise ValueError(f"Missing required columns: {missing}")
            return func(df, *args, **kwargs)
        return wrapper
    return decorator


# using the decorators
@timer
@validate_schema(["fare_amount", "trip_distance", "passenger_count"])
def calculate_metrics(df: pd.DataFrame) -> dict:
    return {
        "total_trips":   len(df),
        "avg_fare":      round(df["fare_amount"].mean(), 2),
        "avg_distance":  round(df["trip_distance"].mean(), 2),
        "total_revenue": round(df["fare_amount"].sum(), 2),
    }


@retry(max_attempts=3, delay=0.1)
@timer
def load_parquet(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)


print("Loading data with @retry and @timer decorators...")
df = load_parquet("data/yellow_tripdata_2024-01.parquet")
metrics = calculate_metrics(df)
print(f"Metrics: {metrics}")


# ============================================================
# SECTION 3 — CONTEXT MANAGERS
# __enter__ / __exit__ and contextlib.contextmanager
# ============================================================

print("\n" + "=" * 60)
print("SECTION 3 — CONTEXT MANAGERS")
print("=" * 60)


# Class-based context manager
class PipelineTimer:
    """Times a pipeline stage and logs start/end."""

    def __init__(self, stage_name: str):
        self.stage_name = stage_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        logger.info(f"Starting stage: {self.stage_name}")
        return self   # returned as the 'as' variable

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.perf_counter() - self.start_time
        if exc_type:
            logger.error(f"Stage {self.stage_name} failed after {elapsed:.4f}s — {exc_val}")
        else:
            logger.info(f"Stage {self.stage_name} completed in {elapsed:.4f}s")
        return False  # False = don't suppress exceptions


# Generator-based context manager using contextlib
@contextlib.contextmanager
def managed_dataframe(path: str):
    """Load a dataframe, yield it, then clean up memory."""
    logger.info(f"Loading {path}")
    df = pd.read_parquet(path)
    try:
        yield df
    finally:
        del df
        logger.info("DataFrame released from memory")


# using both context managers
with PipelineTimer("data validation"):
    valid_df = df[(df["fare_amount"] > 0) & (df["trip_distance"] > 0)]
    print(f"Valid trips: {len(valid_df):,}")

with managed_dataframe("data/yellow_tripdata_2024-01.parquet") as data:
    print(f"Managed load: {len(data):,} rows")


# SECTION 4 — GENERATORS
# process 10M rows without loading all to RAM

print("\n" + "=" * 60)
print("SECTION 4 — GENERATORS")
print("=" * 60)


def row_processor(df: pd.DataFrame, batch_size: int = 10_000) -> Iterator[pd.DataFrame]:
    """
    Yield DataFrame in batches.
    Memory efficient — only batch_size rows in memory at a time.
    Use for processing files too large to fit in RAM.
    """
    total_rows = len(df)
    for start in range(0, total_rows, batch_size):
        end = min(start + batch_size, total_rows)
        yield df.iloc[start:end]


def fare_stream(df: pd.DataFrame) -> Iterator[float]:
    """Yield one fare at a time — never loads all fares to memory."""
    for fare in df["fare_amount"]:
        if fare > 0:
            yield fare


# process in batches
total_processed = 0
batch_count = 0

with PipelineTimer("batch processing"):
    for batch in row_processor(df, batch_size=100_000):
        batch_count += 1
        total_processed += len(batch)

print(f"Processed {total_processed:,} rows in {batch_count} batches")

# running sum using generator — never loads all to memory
running_total = 0
count = 0
for fare in fare_stream(df):
    running_total += fare
    count += 1

print(f"Streamed {count:,} fares, total: ${running_total:,.2f}")


# SECTION 5 — DataPipeline CLASS
# full pipeline with load, validate, transform, save

print("\n" + "=" * 60)
print("SECTION 5 — DataPipeline CLASS")
print("=" * 60)


class DataPipeline:
    """
    Production-grade data pipeline class.
    Encapsulates load, validate, transform, save with logging.
    """

    def __init__(self, config: PipelineConfig):
        self.config   = config
        self.df       = None
        self.errors   = []
        self._is_loaded    = False
        self._is_validated = False

    @timer
    def load(self) -> DataPipeline:
        """Load data from source path."""
        logger.info(f"Loading from {self.config.source_path}")
        self.df = pd.read_parquet(self.config.source_path)
        self._is_loaded = True
        logger.info(f"Loaded {len(self.df):,} rows")
        return self   # return self enables method chaining

    @timer
    def validate(self) -> DataPipeline:
        """Validate schema and data quality."""
        if not self._is_loaded:
            raise RuntimeError("Must call load() before validate()")

        required = ["fare_amount", "trip_distance", "passenger_count", "payment_type"]
        missing = set(required) - set(self.df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        # flag issues but don't fail
        negative_fares = (self.df["fare_amount"] < 0).sum()
        zero_distance  = (self.df["trip_distance"] == 0).sum()

        if negative_fares > 0:
            self.errors.append(f"{negative_fares:,} negative fares found")
        if zero_distance > 0:
            self.errors.append(f"{zero_distance:,} zero distance trips found")

        self._is_validated = True
        logger.info(f"Validation complete. Issues found: {len(self.errors)}")
        for err in self.errors:
            logger.warning(err)
        return self

    @timer
    def transform(self) -> DataPipeline:
        """Clean and enrich the dataset."""
        if not self._is_validated:
            raise RuntimeError("Must call validate() before transform()")

        # remove bad rows
        self.df = self.df[
            (self.df["fare_amount"] > 0) &
            (self.df["fare_amount"] <= self.config.max_fare) &
            (self.df["trip_distance"] >= self.config.min_distance)
        ].copy()

        # add enriched columns
        self.df["hour"] = pd.to_datetime(self.df["tpep_pickup_datetime"]).dt.hour
        self.df["day_of_week"] = pd.to_datetime(self.df["tpep_pickup_datetime"]).dt.day_name()
        self.df["revenue_per_mile"] = (
            self.df["fare_amount"] / self.df["trip_distance"].replace(0, float("nan"))
        ).round(2)
        self.df["fare_bucket"] = self.df["fare_amount"].apply(
            lambda x: "low" if x < 10 else "medium" if x < 30
            else "high" if x < 100 else "premium"
        )

        logger.info(f"Transform complete. {len(self.df):,} rows remaining")
        return self

    @timer
    def save(self, path: str | None = None) -> DataPipeline:
        """Save transformed data to output path."""
        output = path or self.config.output_path
        self.df.to_parquet(output, index=False)
        logger.info(f"Saved {len(self.df):,} rows to {output}")
        return self

    @property
    def summary(self) -> dict:
        """Return pipeline run summary."""
        if self.df is None:
            return {}
        return {
            "rows":          len(self.df),
            "columns":       len(self.df.columns),
            "total_revenue": round(self.df["fare_amount"].sum(), 2),
            "avg_fare":      round(self.df["fare_amount"].mean(), 2),
            "errors":        self.errors,
        }

    def __repr__(self) -> str:
        return f"DataPipeline(source={self.config.source_path}, loaded={self._is_loaded})"


# run the full pipeline using method chaining
pipeline = (
    DataPipeline(config)
    .load()
    .validate()
    .transform()
    .save("data/clean_trips.parquet")
)

print(f"\nPipeline summary: {pipeline.summary}")