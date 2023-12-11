"""Main HTML Tracing."""
from __future__ import annotations

import requests
from utilities import logger
from web_spider.utilities import extract_links

if __name__ == "__main__":
    session = requests.Session()

    url = "https://www.webscraper.io/test-sites"

    uniques = extract_links(
        url=url,
        session=session,
    )

    logger.info_(uniques)

    # for href in uniques:
