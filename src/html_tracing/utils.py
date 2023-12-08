"""Module Utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, ResultSet, Tag

if TYPE_CHECKING:
    from web_scraping.session import Session


def valid_href(href: str, domain: str) -> bool:
    return href.startswith("https") and not href.startswith(domain)


def extract_favicon(soup: BeautifulSoup) -> str:
    favicon = soup.find(name="link", attrs={"rel": "icon"})
    return favicon.get(key="href")


def fetch_urls(
    url: str,
    agents: list[str],
    proxies: list[str],
    session: Session,
    **kwargs,
) -> list[str]:
    domain = url[0 : url.index("/", url.index("/") + 2)]
    response = session.requests(
        **kwargs,
        agents=agents,
        proxies=proxies,
        url=url,
    )

    if response is None or not response.ok:
        return None

    if "validate" in kwargs and kwargs.get("validate") is True:
        return response

    soup = BeautifulSoup(markup=response.content, features="html5lib")
    links: ResultSet[Tag] = soup.find_all(name="a", attrs={"href": True})
    hrefs = [link.get(key="href") for link in links]

    return set(filter(lambda href: valid_href(href=href, domain=domain), hrefs))
