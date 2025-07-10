from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/inventory")
def inventory():
    products = [
        {"name": "oranges", "quantity": "10"},
        {"name": "apples", "quantity": "20"},
    ]
    return jsonify(products)


if __name__ == "__main__":
    app.run(debug=True, port=5001)

# To run this python code with OpenTelemetry instrumentation, you can use the following command:
# $ OTEL_RESOURCE_ATTRIBUTES="service.name=legacy-inventory,
#                            service.version=0.9.1,
#                            net.host.name='hostname',
#                            net.host.ip='ipconfig getifaddr en0'" \
#   OTEL_TRACES_EXPORTER=console \
#   OTEL_PYTHON_TRACER_PROVIDER=sdk \
#   OTEL_METRICS_EXPORTER=console \
#   OTEL_PYTHON_METER_PROVIDER=sdk \
#   OTEL_LOGS_EXPORTER=console \
#   OTEL_PYTHON_LOGGER_PROVIDER=sdk \
#   OTEL_PROPAGATORS=b3 \
#   opentelemetry-instrument python legacy_inventory.py
