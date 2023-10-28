"""Module Session."""

from __future__ import annotations

import random
from logging import INFO, basicConfig, info

import requests
from requests import exceptions

basicConfig(level=INFO)


class Session:
    """Interface representing a requests session."""

    def __init__(self: Session) -> None:
        self.session = requests.Session()

    def proxy_session(
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

    def request_session(
        self: Session,
        url: str,
        agent: str | None = None,
        timeout: float = 5,
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

    def requests_session(
        self: Session,
        url: str,
        proxies: list[str],
        agents: list[str],
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
            self.proxy_session(proxy=proxy)
            agent = random.choice(seq=agents)  # noqa: S311

            info(f"Session with proxy {proxy} and agent {agent}.")

            try:
                response = self.request_session(url=url)

                if response.ok:
                    info("Session SUCCESS")
                    return response

                info(f"Session FAILED with status code {response.status_code}.")
                continue
            except exceptions.RequestException as error:
                info(f"Session FAILE with error {error.errno}.")
                continue

        return None
