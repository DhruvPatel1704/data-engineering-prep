# Custom Exception Hierarchy for Data Pipeline
# PipelineError is the base — catch this to handle any pipeline error
# Specific exceptions let you handle different failure types separately


class PipelineError(Exception):
    """Base exception for all pipeline errors."""

    def __init__(
        self, message: str, pipeline_name: str = "unknown", details: dict = None
    ):
        self.pipeline_name = pipeline_name
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        base = super().__str__()
        if self.details:
            return f"{base} | pipeline={self.pipeline_name} | details={self.details}"
        return f"{base} | pipeline={self.pipeline_name}"


class ValidationError(PipelineError):
    """Raised when data fails schema or quality validation."""

    def __init__(self, message: str, missing_cols: list = None, **kwargs):
        self.missing_cols = missing_cols or []
        super().__init__(message, **kwargs)


class IngestionError(PipelineError):
    """Raised when data cannot be loaded from source."""

    def __init__(self, message: str, source_path: str = "", **kwargs):
        self.source_path = source_path
        super().__init__(message, **kwargs)


class TransformError(PipelineError):
    """Raised when data transformation fails."""

    def __init__(self, message: str, transform_step: str = "", **kwargs):
        self.transform_step = transform_step
        super().__init__(message, **kwargs)


class SaveError(PipelineError):
    """Raised when data cannot be saved to destination."""

    def __init__(self, message: str, output_path: str = "", **kwargs):
        self.output_path = output_path
        super().__init__(message, **kwargs)


# usage examples
if __name__ == "__main__":
    # catch specific exception
    try:
        raise ValidationError(
            "Missing required columns",
            missing_cols=["fare_amount", "trip_distance"],
            pipeline_name="nyc_taxi_pipeline",
        )
    except ValidationError as e:
        print(f"Validation failed: {e}")
        print(f"Missing: {e.missing_cols}")

    # catch any pipeline error with base class
    try:
        raise IngestionError(
            "File not found",
            source_path="data/missing.parquet",
            pipeline_name="nyc_taxi_pipeline",
        )
    except PipelineError as e:
        print(f"Pipeline error: {e}")
