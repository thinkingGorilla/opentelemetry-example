from logging.config import dictConfig

import requests
from flask import Flask
from opentelemetry._logs import set_logger_provider
from opentelemetry.instrumentation.wsgi import OpenTelemetryMiddleware
from opentelemetry.sdk._logs import LoggerProvider

logger_provider = LoggerProvider()
set_logger_provider(logger_provider)

dictConfig(
    {
        "version": 1,
        "handlers": {
            "otlp": {
                "class": "opentelemetry.sdk._logs.LoggingHandler",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["otlp"]},
    }
)

app = Flask(__name__)
app.wsgi_app = OpenTelemetryMiddleware(app.wsgi_app)


@app.route("/")
def welcome():
    return "Welcome to the grocery store!"


@app.route("/products")
def products():
    url = "http://localhost:5001/inventory"
    resp = requests.get(url)
    return resp.text


if __name__ == "__main__":
    app.run(port=5000)

# To run this python code with OpenTelemetry instrumentation, you can use the following command:
# $ OTEL_RESOURCE_ATTRIBUTES="service.name=grocery-store,
#                             service.version=0.1.2,
#                             net.host.name='hostname',
#                             net.host.ip='ipconfig getifaddr en0'" \
#   OTEL_TRACES_EXPORTER=console \
#   OTEL_PYTHON_TRACER_PROVIDER=sdk \
#   OTEL_METRICS_EXPORTER=console \
#   OTEL_PYTHON_METER_PROVIDER=sdk \
#   OTEL_LOGS_EXPORTER=console \
#   OTEL_PYTHON_LOGGER_PROVIDER=sdk \
#   OTEL_PROPAGATORS=b3,tracecontext \
#   opentelemetry-instrument python grocery_store.py
