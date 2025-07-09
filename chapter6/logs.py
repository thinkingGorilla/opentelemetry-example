from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import ConsoleLogExporter, BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource


def configure_logger_provider():
    provider = LoggerProvider(resource=Resource.create())
    set_logger_provider(provider)
    exporter = ConsoleLogExporter()
    provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
