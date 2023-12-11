"""Module Server."""

from __future__ import annotations

# ruff: noqa: F401, ERA001
import asyncio
import contextlib

import requests
from flask import Flask, jsonify, render_template, request
from utilities import logger
from web_scraping.agents import UserAgents
from web_scraping.proxies import Proxies
from web_scraping.session import Session
from web_spider.utilities import (
    extract_domain,
    extract_hrefs,
)

"""agents = UserAgents()
proxies = Proxies()
session = Session()


agents.refresh(refresh_time=60 * 60)
proxies_refresh = proxies.refresh(refresh_time=60 * 1)

list_agents = agents.extract(limit=10)


if proxies_refresh:
    active_proxies = asyncio.run(
        session.check_proxies(proxies=proxies.extract()),
    )
    proxies.save_active(proxies=active_proxies)"""


app = Flask(
    import_name=__name__,
    static_folder="statics",
    template_folder="templates",
)

logger.info_(msg="Server Listening...")


@app.route("/")
def route_home() -> str:
    """Render route home."""
    return render_template("index.html")


@app.route("/api/spider", methods=["POST"])
def api_spider() -> str:
    """Trace a URL."""
    form = request.form
    url = form.get("url")

    url = "https://www.webscraper.io/test-sites"

    hrefs = extract_hrefs(url=url)

    return jsonify({"domain": extract_domain(url=url), "hrefs": hrefs})


# @app.route("/api/spider", methods=["POST"])
# def api_spider() -> str:
#     """Trace a URL."""
#     form = request.form
#     url = form.get("url")

#     list_agents = agents.extract(limit=10)
#     list_proxies = proxies.load_active()

#     domain = extract_domain(url)
#     domain_urls = fetch_links(
#         agents=list_agents,
#         proxies=list_proxies,
#         session=session,
#         url=url,
#     )

#     if domain_urls is None:
#         return jsonify("Could not fetch the url...")

#     domains = {}

#     for domain_url in domain_urls:
#         urls = fetch_links(
#             agents=list_agents,
#             proxies=list_proxies,
#             session=session,
#             url=url,
#         )
#         urls_domain = extract_domain(url=domain_url)
#         domains[urls_domain] = urls

#     return jsonify({"domain": domain, "domains": domains})


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        app.run(host="127.0.0.1", port="8080", debug=True)
