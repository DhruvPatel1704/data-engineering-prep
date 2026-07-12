# End-to-End Data Pipeline
# ingest CSV/Parquet → clean → transform → output Parquet + JSON summary
# production patterns: structured logging, custom exceptions, type hints, tests

from __future__ import annotations

import json
import time
import functools
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, field
from typing import Callable

import pandas as pd
import numpy as np

from testing.exceptions import (
    ValidationError,
    IngestionError,
    TransformError,
    SaveError,
)
from testing.logging_config import get_pipeline_logger, PipelineLogger


# ── Config ─────────────────────────────────────────────────


@dataclass
class PipelineConfig:
    source_path: str
    output_dir: str
    pipeline_name: str = "nyc_taxi_pipeline"
    batch_size: int = 100_000
    max_fare: float = 500.0
    min_distance: float = 0.0
    required_cols: list = field(
        default_factory=lambda: [
            "fare_amount",
            "trip_distance",
            "passenger_count",
            "payment_type",
            "tpep_pickup_datetime",
            "tpep_dropoff_datetime",
            "tip_amount",
        ]
    )

    def __post_init__(self):
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        if self.batch_size <= 0:
            raise ValueError(f"batch_size must be positive, got {self.batch_size}")


# ── Decorators ─────────────────────────────────────────────


def timer(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        return result, elapsed

    return wrapper


# ── Pipeline ───────────────────────────────────────────────


class TaxiDataPipeline:
    """
    End-to-end taxi data pipeline.
    ingest → validate → clean → transform → save → report
    """

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.df = None
        self.metrics = {
            "pipeline_name": config.pipeline_name,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "stages": {},
            "input_rows": 0,
            "output_rows": 0,
            "dropped_rows": 0,
            "errors": [],
        }
        self.logger = get_pipeline_logger(config.pipeline_name)

    def ingest(self) -> TaxiDataPipeline:
        """Load data from source — supports parquet and csv."""
        with PipelineLogger(self.logger, "ingest"):
            try:
                path = Path(self.config.source_path)
                if not path.exists():
                    raise IngestionError(
                        "Source file not found",
                        source_path=str(path),
                        pipeline_name=self.config.pipeline_name,
                    )
                if path.suffix == ".parquet":
                    self.df = pd.read_parquet(path)
                elif path.suffix == ".csv":
                    self.df = pd.read_csv(path)
                else:
                    raise IngestionError(
                        f"Unsupported format: {path.suffix}",
                        source_path=str(path),
                        pipeline_name=self.config.pipeline_name,
                    )

                self.metrics["input_rows"] = len(self.df)
                self.metrics["stages"]["ingest"] = {
                    "rows_loaded": len(self.df),
                    "columns": len(self.df.columns),
                    "source": str(path),
                    "status": "success",
                }
                self.logger.info(
                    "ingest complete", extra={"rows": len(self.df), "source": str(path)}
                )

            except IngestionError:
                raise
            except Exception as e:
                raise IngestionError(
                    str(e),
                    source_path=self.config.source_path,
                    pipeline_name=self.config.pipeline_name,
                ) from e

        return self

    def validate(self) -> TaxiDataPipeline:
        """Validate schema and data quality."""
        with PipelineLogger(self.logger, "validate", record_count=len(self.df)):
            missing_cols = set(self.config.required_cols) - set(self.df.columns)
            if missing_cols:
                raise ValidationError(
                    "Schema validation failed",
                    missing_cols=list(missing_cols),
                    pipeline_name=self.config.pipeline_name,
                )

            issues = {}
            issues["negative_fares"] = int((self.df["fare_amount"] < 0).sum())
            issues["zero_distance"] = int((self.df["trip_distance"] == 0).sum())
            issues["null_fare"] = int(self.df["fare_amount"].isnull().sum())
            issues["fare_over_max"] = int(
                (self.df["fare_amount"] > self.config.max_fare).sum()
            )
            issues["zero_passenger"] = int((self.df["passenger_count"] == 0).sum())

            total_issues = sum(issues.values())
            issue_rate = total_issues / len(self.df) * 100

            self.metrics["stages"]["validate"] = {
                "issues": issues,
                "total_issues": total_issues,
                "issue_rate_pct": round(issue_rate, 2),
                "status": "success",
            }

            for issue, count in issues.items():
                if count > 0:
                    self.metrics["errors"].append(f"{issue}: {count:,} rows")
                    self.logger.warning(
                        "data quality issue", extra={"issue": issue, "count": count}
                    )

        return self

    def clean(self) -> TaxiDataPipeline:
        """Remove invalid rows and handle nulls."""
        with PipelineLogger(self.logger, "clean", record_count=len(self.df)):
            before = len(self.df)

            # flag nulls before filling
            for col in ["passenger_count", "congestion_surcharge", "airport_fee"]:
                if col in self.df.columns:
                    self.df[f"{col}_was_null"] = self.df[col].isnull()

            # fill nulls with safe defaults
            fill_map = {
                "passenger_count": 1,
                "congestion_surcharge": 0.0,
                "airport_fee": 0.0,
                "tip_amount": 0.0,
            }
            for col, val in fill_map.items():
                if col in self.df.columns:
                    self.df[col] = self.df[col].fillna(val)

            # remove invalid rows
            self.df = self.df[
                (self.df["fare_amount"] > 0)
                & (self.df["fare_amount"] <= self.config.max_fare)
                & (self.df["trip_distance"] >= self.config.min_distance)
                & (self.df["passenger_count"] > 0)
            ].copy()

            # remove duplicates
            subset = ["tpep_pickup_datetime", "fare_amount", "trip_distance"]
            self.df = self.df.drop_duplicates(subset=subset, keep="first")

            after = len(self.df)
            self.metrics["stages"]["clean"] = {
                "rows_before": before,
                "rows_after": after,
                "rows_removed": before - after,
                "removal_pct": round((before - after) / before * 100, 2),
                "status": "success",
            }

        return self

    def transform(self) -> TaxiDataPipeline:
        """Enrich dataset with computed columns."""
        with PipelineLogger(self.logger, "transform", record_count=len(self.df)):
            try:
                # time features
                pickup = pd.to_datetime(
                    self.df["tpep_pickup_datetime"], errors="coerce"
                )
                dropoff = pd.to_datetime(
                    self.df["tpep_dropoff_datetime"], errors="coerce"
                )

                self.df["hour"] = pickup.dt.hour
                self.df["day_of_week"] = pickup.dt.day_name()
                self.df["month"] = pickup.dt.month
                self.df["is_weekend"] = pickup.dt.dayofweek >= 5
                self.df["is_rush_hour"] = self.df["hour"].isin([7, 8, 9, 17, 18, 19])
                self.df["duration_min"] = (
                    (dropoff - pickup).dt.total_seconds() / 60
                ).round(2)

                # fare features
                self.df["revenue_per_mile"] = (
                    self.df["fare_amount"] / self.df["trip_distance"].replace(0, np.nan)
                ).round(2)

                self.df["total_amount_calc"] = (
                    self.df["fare_amount"]
                    + self.df["tip_amount"]
                    + self.df.get(
                        "congestion_surcharge", pd.Series(0, index=self.df.index)
                    ).fillna(0)
                ).round(2)

                self.df["fare_bucket"] = pd.cut(
                    self.df["fare_amount"],
                    bins=[0, 10, 30, 100, float("inf")],
                    labels=["low", "medium", "high", "premium"],
                    right=False,
                )

                # outlier flags
                q1 = self.df["fare_amount"].quantile(0.25)
                q3 = self.df["fare_amount"].quantile(0.75)
                iqr = q3 - q1
                self.df["is_fare_outlier"] = (
                    self.df["fare_amount"] < q1 - 1.5 * iqr
                ) | (self.df["fare_amount"] > q3 + 1.5 * iqr)

                self.metrics["output_rows"] = len(self.df)
                self.metrics["dropped_rows"] = (
                    self.metrics["input_rows"] - self.metrics["output_rows"]
                )
                self.metrics["stages"]["transform"] = {
                    "columns_added": [
                        "hour",
                        "day_of_week",
                        "month",
                        "is_weekend",
                        "is_rush_hour",
                        "duration_min",
                        "revenue_per_mile",
                        "total_amount_calc",
                        "fare_bucket",
                        "is_fare_outlier",
                    ],
                    "output_rows": len(self.df),
                    "status": "success",
                }

            except Exception as e:
                raise TransformError(
                    str(e),
                    transform_step="feature_engineering",
                    pipeline_name=self.config.pipeline_name,
                ) from e

        return self

    def save(self) -> TaxiDataPipeline:
        """Save transformed data as Parquet and JSON summary report."""
        with PipelineLogger(self.logger, "save", record_count=len(self.df)):
            try:
                output_dir = Path(self.config.output_dir)

                # save parquet
                parquet_path = output_dir / "clean_taxi_trips.parquet"
                self.df.to_parquet(parquet_path, index=False)
                self.logger.info(
                    "parquet saved",
                    extra={"path": str(parquet_path), "rows": len(self.df)},
                )

                # build summary report
                summary = {
                    **self.metrics,
                    "fare_stats": {
                        "mean": round(float(self.df["fare_amount"].mean()), 2),
                        "median": round(float(self.df["fare_amount"].median()), 2),
                        "max": round(float(self.df["fare_amount"].max()), 2),
                        "min": round(float(self.df["fare_amount"].min()), 2),
                    },
                    "trip_stats": {
                        "avg_distance_miles": round(
                            float(self.df["trip_distance"].mean()), 2
                        ),
                        "avg_duration_min": round(
                            float(self.df["duration_min"].mean()), 2
                        ),
                        "total_revenue": round(float(self.df["fare_amount"].sum()), 2),
                        "weekend_pct": round(
                            float(self.df["is_weekend"].mean() * 100), 2
                        ),
                        "rush_hour_pct": round(
                            float(self.df["is_rush_hour"].mean() * 100), 2
                        ),
                        "outlier_pct": round(
                            float(self.df["is_fare_outlier"].mean() * 100), 2
                        ),
                    },
                    "payment_breakdown": (
                        self.df.groupby("payment_type")["fare_amount"]
                        .agg(["count", "sum", "mean"])
                        .round(2)
                        .to_dict()
                    ),
                    "fare_bucket_counts": (
                        self.df["fare_bucket"].value_counts().to_dict()
                    ),
                }

                # save JSON report
                report_path = output_dir / "pipeline_summary.json"
                with open(report_path, "w") as f:
                    json.dump(summary, f, indent=2, default=str)

                self.logger.info("report saved", extra={"path": str(report_path)})

                self.metrics["stages"]["save"] = {
                    "parquet_path": str(parquet_path),
                    "report_path": str(report_path),
                    "status": "success",
                }

            except Exception as e:
                raise SaveError(
                    str(e),
                    output_path=self.config.output_dir,
                    pipeline_name=self.config.pipeline_name,
                ) from e

        return self

    @property
    def summary(self) -> dict:
        return self.metrics


# ── Run Pipeline ────────────────────────────────────────────

if __name__ == "__main__":
    config = PipelineConfig(
        source_path="data/yellow_tripdata_2024-01.parquet",
        output_dir="data/output",
    )

    pipeline = TaxiDataPipeline(config).ingest().validate().clean().transform().save()

    print("\nPipeline complete")
    print(f"Input rows:  {pipeline.summary['input_rows']:,}")
    print(f"Output rows: {pipeline.summary['output_rows']:,}")
    print(f"Dropped:     {pipeline.summary['dropped_rows']:,}")
    print(f"Errors:      {pipeline.summary['errors']}")
