"""Module Session."""

from __future__ import annotations

import asyncio
import random
import time

import aiohttp
import requests
import urllib3
from requests import exceptions
from utilities import logger

urllib3.disable_warnings()


class Session:
    """Interface representing a requests session.

    MDN Web Docs:
    -
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Session

    Wikipedia
    -
    https://en.wikipedia.org/wiki/Session_(computer_science)
    """

    def __init__(
        self: Session,
        delay: float = 2,
        timeout: float = 10,
        validate: bool = False,
    ) -> None:
        """Initiate a requests session.

        Parameters
        ----------
        self : Session
            _description_
        delay : float, optional
            The time (seconds) to wait between requests, by default 2
        timeout : float, optional
            The time (seconds) to wait before giving up, by default 5
        validate : bool, optional
            The request mode, either get if False or head if True, by default False.
        """
        self.delay = delay
        self.timeout = timeout
        self.validate = validate
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
    ) -> requests.Response:
        """Request a URL with a session.

        Args:
        ----
            url (str):
                The URL to request.

        Returns
        -------
            requests.Response:
                The HTTP request reponse.
        """
        time.sleep(self.delay)
        timeout = (self.timeout, self.timeout)

        return (
            self.session.head(url=url, timeout=timeout)
            if self.validate
            else self.session.get(url=url, timeout=timeout, verify=False)
        )

    def requests(
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
        self.session.trust_env = False

        for proxy in proxies:
            self.proxy(proxy=proxy)
            agent = random.choice(seq=agents)  # noqa: S311
            self.session.headers.update({"User-Agent": agent})

            logger.info_(f"Session with proxy {proxy} and agent {agent}.")

            try:
                response = self.request(url=url)

                if response.ok:
                    logger.info_("Session SUCCESS")
                    return response

                logger.warn_(f"Session FAILED with code {response.status_code}.")
                continue
            except exceptions.RequestException as error:
                logger.error_(f"Session FAILED with error {error}.")
                continue

        return None

    async def check_proxy(
        self: Session,
        session: aiohttp.ClientSession,
        proxy: str,
    ) -> str | None:
        """Check if a proxy server is available.

        Parameters
        ----------
        session : aiohttp.ClientSession
            The request client session.
        proxy : str
            The proxy server.

        Returns
        -------
        str | None
            The proxy server if available.
        """
        status = 200

        try:
            response = await session.head(timeout=10, url=proxy)
        except Exception:  # noqa: BLE001
            return None
        else:
            valid = response.ok and response.status == status
            return proxy if valid else None

    async def check_proxies(
        self: Session,
        proxies: list[str],
    ) -> list[str]:
        """Check a list of proxies for their availibilty.

        Parameters
        ----------
        proxies : list[str]
            The list of proxies.

        Returns
        -------
        list[str]
            The list of proxies available.
        """
        async with aiohttp.ClientSession() as session:
            results: list[str | None] = await asyncio.gather(
                *[self.judge_proxy(proxy=proxy, session=session) for proxy in proxies],
            )
            return list(filter(lambda result: result is not None, results))
