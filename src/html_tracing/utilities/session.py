"""Module Session."""

from __future__ import annotations

import random
from logging import INFO, basicConfig, info, warning

import requests
from requests import exceptions

basicConfig(level=INFO)


class Session:
    """Interface representing a requests session.

    MDN Web Docs:
    -
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Session

    Wikipedia
    -
    https://en.wikipedia.org/wiki/Session_(computer_science)
    """

    def __init__(self: Session) -> None:
        """Interface representing a requests session."""
        self.session = requests.Session()

    def proxy(
        self: Session,
        proxy: str,
    ) -> None:
        """Assign a proxy to a requests session.

        Args:
        ----
            proxy (str):
                The session proxy.
        """
        self.session.proxies = {"http": proxy, "https": proxy}

    def request(
        self: Session,
        url: str,
        agent: str | None = None,
        timeout: float = 10,
    ) -> requests.Response:
        """Request a URL using a session proxy.

        Args:
        ----
            url (str):
                The URL to request.
            agent (str):
                The user agent for the headers.
            timeout (float, optional):
                The time (seconds) to wait before giving up. Defaults to 5.

        Returns
        -------
            requests.Response:
                The HTTP request reponse.
        """
        return self.session.get(
            url=url,
            timeout=timeout,
            headers=None if agent is None else {"User-Agent": agent},
        )

    def requests(
        self: Session,
        url: str,
        proxies: list[str],
        agents: list[str],
        timeout: float | None = None,
    ) -> requests.Response | None:
        """Request a URL with a session using different proxies and user agents.

        Args:
        ----
            url (str):
                The URL to request.
            proxies (list[str]):
                The list of proxies.
            agents (list[str]):
                The list of user agents.

        Returns
        -------
            requests.Response | None:
                The HTTP request reponse.
        """
        for proxy in proxies:
            self.proxy(proxy=proxy)
            agent = random.choice(seq=agents)  # noqa: S311

            info(f"Session with proxy {proxy} and agent {agent}.\n")

            try:
                response = self.request(url=url, timeout=timeout)

                if response.ok:
                    info("Session SUCCESS\n")
                    return response

                warning(f"Session FAILED with status code {response.status_code}.\n")
                continue
            except exceptions.RequestException as error:
                warning(f"Session FAILED with error {error}.\n")
                continue

        return None
