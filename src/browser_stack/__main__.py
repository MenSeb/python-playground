"""Main Browser Stack."""


import contextlib

from flask import Flask, jsonify, render_template, request
from web_driver import BrowserBreakpoints, BrowserDevices, BrowserStack, aslist

from src.utilities import logger

browser_breakpoints = BrowserBreakpoints()
browser_devices = BrowserDevices()
browser_stack = BrowserStack()

app = Flask(import_name=__name__)


@app.route("/")
def route_index() -> str:
    """Render the application index page."""
    return render_template(
        "index.jinja",
        context={
            "breakpoints": aslist(browser_breakpoints),
            "browsers": browser_stack.browsers,
            "devices": aslist(browser_devices),
        },
    )


@app.route("/api/browser/start", methods=["POST"])
def start_browser() -> str:
    """Start the web browser."""
    options = request.form.to_dict()

    logger.info_(msg=f"OPTIONS {options}")

    browser_stack.start(**options)

    return jsonify("api_driver_start!")


@app.route("/api/browser/stop")
def stop_browser() -> str:
    """Stop the web browser."""
    browser_stack.stop()

    logger.info_(msg=f"DRIVER {browser_stack.driver}")

    return jsonify("api_driver_stop!")


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        app.run(
            debug=True,
            host="127.0.0.1",
            port="8080",
        )
