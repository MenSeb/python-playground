"""Main HTML Tracing."""
from __future__ import annotations

from utilities import logger
from utils import fetch_urls
from web_scraping.agents import UserAgents
from web_scraping.proxies import Proxies, Query
from web_scraping.session import Session

if __name__ == "__main__":
    agents = UserAgents()
    proxies = Proxies()
    session = Session()

    agents.refresh()
    list_agents = agents.extract(limit=10)

    proxies.refresh()
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

    logger.info_(list_proxies)

    url = "https://www.webscraper.io/test-sites"

    uniques = fetch_urls(
        url=url,
        agents=list_agents,
        proxies=list_proxies,
        session=session,
        timeout=10,
        validate=True,
    )

    logger.info_(uniques)

    # for href in uniques:
