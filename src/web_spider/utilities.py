"""Module Utilities."""

from __future__ import annotations

import requests
from bs4 import BeautifulSoup, ResultSet, Tag


def extract_domain(url: str) -> str:
    """Extract the domain from a website URL.

    Parameters
    ----------
    url : str
        The website URL.

    Returns
    -------
    str
        The website domain.
    """
    return url[0 : url.index("/", url.index("/") + 2)]


def extract_hrefs(
    url: str,
    timeout: float = 5,
) -> list[str] | None:
    """Extract all href attributes from links found in a website's URL.

    Parameters
    ----------
    url : str
        The website URL.
    timeout : float, optional
        The time (seconds) to wait before giving up, by default 5

    Returns
    -------
    list[str] | None
        The list of href attributes.
    """
    response = requests.get(url=url, timeout=(timeout, timeout))

    if not response.ok:
        return None

    soup = BeautifulSoup(markup=response.content, features="html5lib")
    links: ResultSet[Tag] = soup.find_all(name="a", attrs={"href": True})
    hrefs: list[str] = [link.get(key="href") for link in links]

    domain = extract_domain(url=url)

    result = set()
    for href in hrefs:
        if href.startswith("https") and not href.startswith(domain):
            result.add(href)

    return list(result)
