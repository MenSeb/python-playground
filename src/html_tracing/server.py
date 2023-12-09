"""Module Server."""

from __future__ import annotations

import contextlib

from flask import Flask, jsonify, render_template, request
from web_scraping.agents import UserAgents
from web_scraping.proxies import Proxies, Query
from web_scraping.session import Session
from web_spider.utilities import extract_domain, fetch_links

agents = UserAgents()
proxies = Proxies()
session = Session()

agents.refresh(refresh_time=60 * 60)
proxies.refresh(refresh_time=60 * 60)


app = Flask(
    import_name=__name__,
    static_folder="statics",
    template_folder="templates",
)


@app.route("/")
def route_home() -> str:
    """Render route home."""
    return render_template("index.html")


@app.route("/api/spider", methods=["POST"])
def api_spider() -> str:
    """Trace a URL."""
    form = request.form
    url = form.get("url")

    list_agents = agents.extract(limit=10)
    list_proxies = proxies.extract(
        limit=10,
        dataframe=proxies.query(
            queries=[
                Query(
                    data="US",
                    key=proxies.headers.code,
                    operator=proxies.operators.eq,
                ),
                Query(
                    data="elite proxy",
                    key=proxies.headers.anonymity,
                    operator=proxies.operators.eq,
                ),
            ],
            dataframe=proxies.load(),
        ),
    )

    domain = extract_domain(url)
    domain_urls = fetch_links(
        agents=list_agents,
        proxies=list_proxies,
        session=session,
        url=url,
    )

    if domain_urls is None:
        return jsonify("Could not fetch the url...")

    domains = {}

    for domain_url in domain_urls:
        urls = fetch_links(
            agents=list_agents,
            proxies=list_proxies,
            session=session,
            url=url,
        )
        urls_domain = extract_domain(url=domain_url)
        domains[urls_domain] = urls

    return jsonify({"domain": domain, "domains": domains})


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        app.run(host="127.0.0.1", port="8080", debug=True)
