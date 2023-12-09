"""Module Utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, ResultSet, Tag

if TYPE_CHECKING:
    from web_scraping.session import Session


def extract_domain(url: str) -> str:
    """Extract the domain from a URL.

    Parameters
    ----------
    url : str
        The url to extract from.

    Returns
    -------
    str
        The URL domain.
    """
    return url[0 : url.index("/", url.index("/") + 2)]


def validate_href(
    href: str,
    domain: str,
) -> bool:
    """Validate the link "href" attribute.

    Parameters
    ----------
    href : str
        The link href attribute.
    domain : str
        The link domain.

    Returns
    -------
    bool
        True if from HTTPS and not from within its own domain.
    """
    return href.startswith("https") and not href.startswith(domain)


def fetch_links(
    url: str,
    agents: list[str],
    proxies: list[str],
    session: Session,
) -> list[str] | None:
    """Fetch a URL and extract its links "href" attributes.

    Parameters
    ----------
    url : str
        The URL to fetch.
    agents : list[str]
        The agents to use.
    proxies : list[str]
        The proxies to use.
    session : Session
        The requests session.

    Returns
    -------
    list[str] | None
        The list of links "href".
    """
    response = session.requests(
        agents=agents,
        proxies=proxies,
        url=url,
    )

    if response is None or not response.ok:
        return None

    soup = BeautifulSoup(markup=response.content, features="html5lib")
    links: ResultSet[Tag] = soup.find_all(name="a", attrs={"href": True})
    domain = extract_domain(url)
    hrefs: list[str] = [link.get(key="href") for link in links]
    valid_hrefs = filter(lambda href: validate_href(href=href, domain=domain), hrefs)
    unique_hrefs = set(valid_hrefs)

    return list(unique_hrefs)
