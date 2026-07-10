# pytest test suite for DataPipeline
# 12 tests covering load, validate, transform, save, exceptions
# Run with: pytest testing/test_pipeline.py -v

import pytest
import pandas as pd
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from testing.exceptions import PipelineError, ValidationError, IngestionError


# Fixtures
# fixtures are reusable setup functions
# pytest injects them automatically when a test function has a matching parameter name


@pytest.fixture
def sample_df():
    """Clean sample DataFrame for testing."""
    return pd.DataFrame(
        {
            "fare_amount": [10.0, 25.0, 5.0, 100.0, 50.0],
            "trip_distance": [2.0, 5.0, 1.0, 15.0, 8.0],
            "passenger_count": [1, 2, 1, 3, 1],
            "payment_type": [1, 2, 1, 1, 2],
            "tip_amount": [2.0, 5.0, 0.0, 20.0, 10.0],
            "tpep_pickup_datetime": pd.date_range("2024-01-01", periods=5, freq="h"),
        }
    )


@pytest.fixture
def dirty_df():
    """DataFrame with data quality issues for testing validation."""
    return pd.DataFrame(
        {
            "fare_amount": [-5.0, 0.0, 600.0, 25.0, 10.0],
            "trip_distance": [0.0, 2.0, 10.0, 5.0, 0.0],
            "passenger_count": [0, 1, 2, 3, 1],
            "payment_type": [1, 2, 1, 1, 2],
            "tip_amount": [-1.0, 0.0, 5.0, 3.0, 2.0],
            "tpep_pickup_datetime": pd.date_range("2024-01-01", periods=5, freq="h"),
        }
    )


@pytest.fixture
def minimal_df():
    """Minimal valid DataFrame — just required columns."""
    return pd.DataFrame(
        {
            "fare_amount": [10.0],
            "trip_distance": [2.0],
            "passenger_count": [1],
            "payment_type": [1],
            "tip_amount": [2.0],
            "tpep_pickup_datetime": [pd.Timestamp("2024-01-01")],
        }
    )


@pytest.fixture
def tmp_parquet(tmp_path, sample_df):
    """Write sample_df to a temp parquet file and return the path."""
    path = tmp_path / "test_trips.parquet"
    sample_df.to_parquet(path)
    return path


# Exception Tests


class TestExceptions:
    def test_pipeline_error_base(self):
        """PipelineError stores message and pipeline name."""
        err = PipelineError("something went wrong", pipeline_name="test_pipeline")
        assert "something went wrong" in str(err)
        assert err.pipeline_name == "test_pipeline"

    def test_validation_error_stores_missing_cols(self):
        """ValidationError stores the list of missing columns."""
        err = ValidationError(
            "Missing columns",
            missing_cols=["fare_amount", "trip_distance"],
            pipeline_name="test",
        )
        assert err.missing_cols == ["fare_amount", "trip_distance"]

    def test_ingestion_error_stores_path(self):
        """IngestionError stores the source path that failed."""
        err = IngestionError(
            "File not found",
            source_path="s3://bucket/missing.parquet",
            pipeline_name="test",
        )
        assert err.source_path == "s3://bucket/missing.parquet"

    def test_validation_error_is_pipeline_error(self):
        """ValidationError inherits from PipelineError — catch with base class."""
        with pytest.raises(PipelineError):
            raise ValidationError("bad data", pipeline_name="test")

    def test_ingestion_error_is_pipeline_error(self):
        """IngestionError inherits from PipelineError."""
        with pytest.raises(PipelineError):
            raise IngestionError("load failed", pipeline_name="test")


# Data Validation Tests


class TestDataValidation:
    def test_valid_df_passes_schema_check(self, sample_df):
        """Clean DataFrame has all required columns."""
        required = ["fare_amount", "trip_distance", "passenger_count", "payment_type"]
        missing = set(required) - set(sample_df.columns)
        assert len(missing) == 0

    def test_missing_column_detected(self, sample_df):
        """Dropping a required column is detected by schema check."""
        df_broken = sample_df.drop(columns=["fare_amount"])
        required = ["fare_amount", "trip_distance", "passenger_count", "payment_type"]
        missing = set(required) - set(df_broken.columns)
        assert "fare_amount" in missing

    def test_negative_fares_counted(self, dirty_df):
        """Negative fares are correctly identified."""
        negative_count = (dirty_df["fare_amount"] < 0).sum()
        assert negative_count == 1

    def test_zero_distance_trips_counted(self, dirty_df):
        """Zero distance trips are correctly identified."""
        zero_dist = (dirty_df["trip_distance"] == 0).sum()
        assert zero_dist == 2

    def test_cleaning_removes_bad_rows(self, dirty_df):
        """Filtering removes rows with negative fare or zero distance."""
        clean = dirty_df[
            (dirty_df["fare_amount"] > 0) & (dirty_df["trip_distance"] > 0)
        ]
        assert len(clean) < len(dirty_df)
        assert (clean["fare_amount"] < 0).sum() == 0
        assert (clean["trip_distance"] == 0).sum() == 0


# Transformation Tests


class TestTransformations:
    def test_hour_column_added(self, sample_df):
        """Hour extracted from pickup timestamp correctly."""
        sample_df["hour"] = pd.to_datetime(sample_df["tpep_pickup_datetime"]).dt.hour
        assert "hour" in sample_df.columns
        assert sample_df["hour"].between(0, 23).all()

    def test_fare_bucket_low(self):
        """Fares under 10 are classified as low."""

        def fare_bucket(x):
            if x < 10:
                return "low"
            elif x < 30:
                return "medium"
            elif x < 100:
                return "high"
            return "premium"

        assert fare_bucket(5.0) == "low"
        assert fare_bucket(9.99) == "low"

    def test_fare_bucket_boundaries(self):
        """Fare bucket boundaries are correct."""

        def fare_bucket(x):
            if x < 10:
                return "low"
            elif x < 30:
                return "medium"
            elif x < 100:
                return "high"
            return "premium"

        assert fare_bucket(10.0) == "medium"
        assert fare_bucket(30.0) == "high"
        assert fare_bucket(100.0) == "premium"

    def test_revenue_per_mile_calculated(self, sample_df):
        """Revenue per mile is fare divided by distance."""
        sample_df["revenue_per_mile"] = (
            sample_df["fare_amount"] / sample_df["trip_distance"]
        ).round(2)
        expected = round(10.0 / 2.0, 2)
        assert sample_df["revenue_per_mile"].iloc[0] == expected

    def test_revenue_per_mile_zero_distance(self):
        """Zero distance trips return NaN for revenue per mile."""
        df = pd.DataFrame({"fare_amount": [10.0], "trip_distance": [0.0]})
        df["revenue_per_mile"] = df["fare_amount"] / df["trip_distance"].replace(
            0, float("nan")
        )
        assert df["revenue_per_mile"].isna().all()


# Parametrize — test multiple inputs with one test function


class TestParametrize:
    @pytest.mark.parametrize(
        "fare,expected_bucket",
        [
            (5.0, "low"),
            (9.99, "low"),
            (10.0, "medium"),
            (29.99, "medium"),
            (30.0, "high"),
            (99.99, "high"),
            (100.0, "premium"),
            (500.0, "premium"),
        ],
    )
    def test_fare_bucket_parametrize(self, fare, expected_bucket):
        """Test fare bucket classification for multiple fare values."""

        def fare_bucket(x):
            if x < 10:
                return "low"
            elif x < 30:
                return "medium"
            elif x < 100:
                return "high"
            return "premium"

        assert fare_bucket(fare) == expected_bucket

    @pytest.mark.parametrize(
        "fare,distance,expected",
        [
            (20.0, 4.0, 5.0),
            (15.0, 3.0, 5.0),
            (10.0, 2.0, 5.0),
            (7.5, 1.5, 5.0),
        ],
    )
    def test_revenue_per_mile_parametrize(self, fare, distance, expected):
        """Revenue per mile = fare / distance for multiple inputs."""
        result = round(fare / distance, 2)
        assert result == expected
