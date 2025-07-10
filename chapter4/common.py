import logging
import resource

from flask import request
from opentelemetry import trace
from opentelemetry._logs import (
    set_logger_provider,
)
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.metrics import get_meter_provider, set_meter_provider, Observation
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.semconv.trace import SpanAttributes

from local_machine_resource_detector import LocalMachineResourceDetector


def configure_logger(name, version):
    local_resource = LocalMachineResourceDetector().detect()
    resource = local_resource.merge(
        Resource.create(
            {
                ResourceAttributes.SERVICE_NAME: name,
                ResourceAttributes.SERVICE_VERSION: version,
            }
        )
    )
    provider = LoggerProvider(resource=resource)
    set_logger_provider(provider)
    # exporter = ConsoleLogExporter()
    exporter = OTLPLogExporter()
    provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = LoggingHandler()
    logger.addHandler(handler)
    return logger


def record_max_rss_callback(result):
    yield Observation(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def start_recording_memory_metrics(meter):
    meter.create_observable_gauge(
        callbacks=[record_max_rss_callback],
        name="maxrss",
        unit="bytes",
        description="Max resident set size",
    )


def configure_meter(name, version):
    # exporter = ConsoleMetricExporter()
    exporter = OTLPMetricExporter()
    reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
    local_resource = LocalMachineResourceDetector().detect()
    resource = local_resource.merge(
        Resource.create(
            {
                ResourceAttributes.SERVICE_NAME: name,
                ResourceAttributes.SERVICE_VERSION: version,
            }
        )
    )
    provider = MeterProvider(metric_readers=[reader], resource=resource)
    set_meter_provider(provider)
    schema_url = "https://opentelemetry.io/schemas/1.9.0"
    return get_meter_provider().get_meter(
        name=name,
        version=version,
        schema_url=schema_url,
    )


def configure_tracer(name, version):
    # exporter = ConsoleSpanExporter()
    exporter = ConsoleSpanExporter()
    span_processor = BatchSpanProcessor(exporter)
    local_resource = LocalMachineResourceDetector().detect()
    resource = local_resource.merge(
        Resource.create(
            {
                ResourceAttributes.SERVICE_NAME: name,
                ResourceAttributes.SERVICE_VERSION: version,
            }
        )
    )
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(span_processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer(name, version)


def set_span_attributes_from_flask():
    span = trace.get_current_span()
    span.set_attributes(
        {
            SpanAttributes.HTTP_FLAVOR: request.environ.get("SERVER_PROTOCOL"),
            SpanAttributes.HTTP_METHOD: request.method,
            SpanAttributes.HTTP_USER_AGENT: str(request.user_agent),
            SpanAttributes.HTTP_HOST: request.host,
            SpanAttributes.HTTP_SCHEME: request.scheme,
            SpanAttributes.HTTP_TARGET: request.path,
            SpanAttributes.HTTP_CLIENT_IP: request.remote_addr,
        }
    )
