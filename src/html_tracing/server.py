"""Module Server."""

from __future__ import annotations

import contextlib
from os import environ

from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, render_template
from utils import fetch_urls

load_dotenv(find_dotenv())

app = Flask(
    import_name=__name__,
    static_folder="statics",
    template_folder="templates",
)


@app.route("/")
def route_home() -> str:
    """Render route home."""
    return render_template("index.html")


@app.route("/api/tracing/<url>")
def api_tracing(url: str) -> str:
    """Trace a URL."""
    return jsonify(urls=fetch_urls(url=url))


if __name__ == "__main__":
    host = environ.get("HOST")
    port = int(environ.get("PORT"))
    debug = bool(environ.get("DEBUG"))

    with contextlib.suppress(KeyboardInterrupt):
        app.run(host=host, port=port, debug=debug)
