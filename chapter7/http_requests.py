import requests
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter
)


def configure_tracer():
    exporter = ConsoleSpanExporter()
    span_processor = BatchSpanProcessor(exporter)
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)


def rename_span(span, request):
    span.update_name(f"Web Request {request.method}")


def add_response_attribute(span, request, response):
    span.set_attribute("http.response.headers", str(response.headers))


configure_tracer()
# RequestsInstrumentor().uninstrument()
RequestsInstrumentor().instrument(
    request_hook=rename_span,
    response_hook=add_response_attribute,
)

url = "https://www.cloudnativeobservability.com"
resp = requests.get(url, verify=False)
print(resp.status_code)

# This script demonstrates how to instrument HTTP requests using OpenTelemetry.
# $ opentelemetry-instrument --traces_exporter console \
#                            --metrics_exporter console \
#                            --logs_exporter console \
#                            python http_requests.py
