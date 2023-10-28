"""Module Server."""

from __future__ import annotations

import contextlib
from logging import INFO, basicConfig
from os import environ

from dotenv import find_dotenv, load_dotenv
from flask import Flask, render_template

basicConfig(level=INFO)
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


if __name__ == "__main__":
    host = environ.get("HOST")
    port = int(environ.get("PORT"))
    debug = bool(environ.get("DEBUG"))

    with contextlib.suppress(KeyboardInterrupt):
        app.run(host=host, port=port, debug=debug)
