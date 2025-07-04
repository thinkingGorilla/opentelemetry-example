from opentelemetry.metrics import get_meter_provider, set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader
)
from opentelemetry.sdk.resources import Resource


# from opentelemetry.exporter.prometheus import PrometheusMetricReader
# from prometheus_client import start_http_server


def configure_meter_provider():
    # start_http_server(port=8080, addr="localhost")
    # reader = PrometheusMetricReader()
    # provider = MeterProvider(metric_readers=[reader], resource=Resource.create())

    exporter = ConsoleMetricExporter()
    reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
    provider = MeterProvider(metric_readers=[reader], resource=Resource.create())

    set_meter_provider(provider)


if __name__ == '__main__':
    configure_meter_provider()
    meter = get_meter_provider().get_meter(
        name="metric-example",
        version="0.1.2",
        schema_url="https://opentelemetry.io/schemas/1.9.0",
    )
    input("Press any key to exit...")
    counter = meter.create_counter(
        "item_sold",
        unit="items",
        description="Total item sold"
    )
    counter.add(6, {"local": "fr-FR", "country": "CA"})
    counter.add(1, {"local": "es-ES"})
