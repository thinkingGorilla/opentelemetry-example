#!/usr/bin/env python3
import requests
from opentelemetry import trace
from opentelemetry.propagate import inject
from opentelemetry.semconv.trace import HttpFlavorValues, SpanAttributes
from opentelemetry.trace import StatusCode, Status

from common import configure_tracer

tracer = configure_tracer("shopper", "0.1.2")


@tracer.start_as_current_span("browse")
def browse():
    print("visiting the grocery store")
    with tracer.start_as_current_span(
            "web request", kind=trace.SpanKind.CLIENT, record_exception=False, set_status_on_exception=True
    ) as span:
        url = "http://localhost:5000/products/invalid"
        span.set_attributes(
            {
                SpanAttributes.HTTP_REQUEST_METHOD: "GET",
                SpanAttributes.HTTP_FLAVOR: str(HttpFlavorValues.HTTP_1_1),
                SpanAttributes.HTTP_URL: url,
                SpanAttributes.NET_PEER_IP: "127.0.0.1",
            }
        )
        headers = {}
        inject(headers)
        span.add_event("about to send a request")
        resp = requests.get(url, headers=headers)
        if resp:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(Status(StatusCode.ERROR, "status code: {}".format(resp.status_code)))
        span.add_event("request sent", attributes={"rul": url}, timestamp=0)
        # try:
        #     url = "invalid_url"
        #     resp = requests.get(url, headers=headers)
        #     span.add_event("request sent", attributes={"rul": url}, timestamp=0)
        # except Exception as err:
        #     span.record_exception(err)
        span.set_attribute(SpanAttributes.HTTP_STATUS_CODE, resp.status_code)
        add_item_to_cart("orange", 5)


@tracer.start_as_current_span("add item to cart")
def add_item_to_cart(item, quantity):
    print("add {} to cart".format(item))
    span = trace.get_current_span()
    span.set_attributes({
        "item": item,
        "quantity": quantity,
    })
    print("add {} to cart".format(item))


@tracer.start_as_current_span("visit store")
def visit_store():
    browse()


if __name__ == "__main__":
    visit_store()
