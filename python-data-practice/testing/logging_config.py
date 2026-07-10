# Structured JSON Logging for Data Pipelines
# JSON format allows log aggregation tools (Datadog, CloudWatch, Splunk)
# to parse, search, filter, and alert on specific fields

import logging
import json
import time
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """
    Formats log records as JSON.
    Each log line is a valid JSON object — one line per event.
    Log aggregation tools parse these automatically.
    """

    def __init__(self, pipeline_name: str = "default"):
        super().__init__()
        self.pipeline_name = pipeline_name

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "pipeline_name": self.pipeline_name,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # add extra fields if provided
        # logger.info("loaded data", extra={"record_count": 1000})
        for key, value in record.__dict__.items():
            if key not in {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "id",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
                "taskName",
            }:
                log_entry[key] = value

        # add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def get_pipeline_logger(
    pipeline_name: str, level: int = logging.INFO
) -> logging.Logger:
    """
    Create and return a structured JSON logger for a pipeline.

    Usage:
        logger = get_pipeline_logger("nyc_taxi_pipeline")
        logger.info("loaded data", extra={"record_count": 1_000_000})
    """
    logger = logging.getLogger(pipeline_name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter(pipeline_name=pipeline_name))
        logger.addHandler(handler)

    return logger


class PipelineLogger:
    """
    Context manager that logs pipeline stage start, end, duration,
    and record count in structured JSON format.
    """

    def __init__(self, logger: logging.Logger, stage: str, record_count: int = 0):
        self.logger = logger
        self.stage = stage
        self.record_count = record_count
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        self.logger.info(
            "stage started",
            extra={
                "stage": self.stage,
                "record_count": self.record_count,
                "status": "started",
            },
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = round((time.perf_counter() - self.start_time) * 1000, 2)
        if exc_type:
            self.logger.error(
                "stage failed",
                extra={
                    "stage": self.stage,
                    "duration_ms": duration_ms,
                    "status": "failed",
                    "error": str(exc_val),
                },
            )
        else:
            self.logger.info(
                "stage completed",
                extra={
                    "stage": self.stage,
                    "duration_ms": duration_ms,
                    "record_count": self.record_count,
                    "status": "completed",
                },
            )
        return False


# demo
if __name__ == "__main__":
    logger = get_pipeline_logger("nyc_taxi_pipeline")

    logger.info("pipeline started", extra={"source": "s3://bucket/taxi.parquet"})

    with PipelineLogger(logger, stage="load", record_count=2_964_624):
        time.sleep(0.1)  # simulate loading

    with PipelineLogger(logger, stage="validate", record_count=2_964_624):
        time.sleep(0.05)

    logger.warning(
        "data quality issue",
        extra={"stage": "validate", "negative_fares": 123, "zero_distance": 4521},
    )

    with PipelineLogger(logger, stage="transform", record_count=2_910_000):
        time.sleep(0.2)

    logger.info(
        "pipeline completed",
        extra={
            "input_rows": 2_964_624,
            "output_rows": 2_910_000,
            "dropped_rows": 54_624,
        },
    )
