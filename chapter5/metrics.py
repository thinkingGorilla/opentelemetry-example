import resource
import time

from opentelemetry.metrics import Observation
from opentelemetry.metrics import get_meter_provider, set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader
)
from opentelemetry.sdk.metrics.view import View, DropAggregation
from opentelemetry.sdk.resources import Resource


# from opentelemetry.exporter.prometheus import PrometheusMetricReader
# from prometheus_client import start_http_server


def configure_meter_provider():
    # start_http_server(port=8080, addr="localhost")
    # reader = PrometheusMetricReader()
    # provider = MeterProvider(metric_readers=[reader], resource=Resource.create())

    exporter = ConsoleMetricExporter()
    reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
    view_all = View(instrument_name="*", aggregation=DropAggregation())
    view = View(instrument_name="inventory")
    provider = MeterProvider(
        metric_readers=[reader],
        resource=Resource.create(),
        views=[view_all, view],
    )

    set_meter_provider(provider)


def async_counter_callback(result):
    yield Observation(10)


def async_updowncounter_callback(result):
    yield Observation(20, {"locale": "en-US"})
    yield Observation(10, {"locale": "fr-CA"})


def async_gauge_callback(result):
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    yield Observation(rss, {})


if __name__ == '__main__':
    configure_meter_provider()
    meter = get_meter_provider().get_meter(
        name="metric-example",
        version="0.1.2",
        schema_url="https://opentelemetry.io/schemas/1.9.0",
    )

    input("Press any key to exit...")

    counter = meter.create_counter(
        "major_page_faults",
        unit="items",
        description="Total item sold"
    )
    counter.add(6, {"local": "fr-FR", "country": "CA"})
    counter.add(1, {"local": "es-ES"})

    meter.create_observable_counter(
        name="major_page_faults",
        callbacks=[async_counter_callback],
        description="page faults requiring I/O",
        unit="faults",
    )
    time.sleep(10)

    inventory_counter = meter.create_up_down_counter(
        name="inventory",
        unit="items",
        description="Number of items in inventory",
    )
    inventory_counter.add(20)
    inventory_counter.add(-5)

    upcounter_counter = meter.create_observable_up_down_counter(
        name="customer_in_store",
        callbacks=[async_updowncounter_callback],
        unit="persons",
        description="Keeps a count of customers in the store",
    )

    histogram = meter.create_histogram(
        "response_times",
        unit="ms",
        description="Response times for all requests",
    )
    histogram.record(96)
    histogram.record(9)

    meter.create_observable_gauge(
        name="maxrss",
        unit="bytes",
        callbacks=[async_gauge_callback],
        description="Max resident set size",
    )
    time.sleep(10)
