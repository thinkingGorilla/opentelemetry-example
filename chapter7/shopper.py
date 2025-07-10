#!/usr/bin/env python3
import logging

import requests
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler

logger_provider = LoggerProvider()
set_logger_provider(logger_provider)

tracer = trace.get_tracer("shopper", "0.1.2")
logger = logging.getLogger("shopper")
logger.setLevel(logging.DEBUG)
logger.addHandler(LoggingHandler())


@tracer.start_as_current_span("add item to cart")
def add_item_to_cart(item, quantity):
    span = trace.get_current_span()
    span.set_attributes(
        {
            "item": item,
            "quantity": quantity,
        }
    )
    logger.info("add {} to cart".format(item))


@tracer.start_as_current_span("browse")
def browse():
    resp = requests.get("http://localhost:5000/products")
    add_item_to_cart("orange", 5)


@tracer.start_as_current_span("visit store")
def visit_store():
    browse()


if __name__ == "__main__":
    visit_store()


# To run this python code with OpenTelemetry instrumentation, you can use the following command:
# $ OTEL_RESOURCE_ATTRIBUTES="service.name=shopper,
#                             service.version=0.1.3,
#                             net.host.name='hostname',
#                             net.host.ip='ipconfig getifaddr en0'" \
#   OTEL_TRACES_EXPORTER=console \
#   OTEL_PYTHON_TRACER_PROVIDER=sdk \
#   OTEL_METRICS_EXPORTER=console \
#   OTEL_PYTHON_METER_PROVIDER=sdk \
#   OTEL_LOGS_EXPORTER=console \
#   OTEL_PYTHON_LOGGER_PROVIDER=sdk \
#   opentelemetry-instrument python shopper.py
