import time

from opentelemetry._logs import (
    set_logger_provider,
    get_logger_provider
)
from opentelemetry._logs.severity import SeverityNumber
from opentelemetry.sdk._logs import LoggerProvider, LogRecord
from opentelemetry.sdk._logs.export import ConsoleLogExporter, BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource


def configure_logger_provider():
    provider = LoggerProvider(resource=Resource.create())
    set_logger_provider(provider)
    exporter = ConsoleLogExporter()
    provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

if __name__ == '__main__':
    configure_logger_provider()
    logger = get_logger_provider().get_logger(
        "shopper",
        "0.1.2",
    )
    logger.emit(
        LogRecord(
            timestamp=time.time_ns(),
            body="first log line",
            severity_number=SeverityNumber.INFO,
        )
    )