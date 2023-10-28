"""Module User Agents."""

from __future__ import annotations

import json
from logging import INFO, basicConfig, info
from pathlib import Path

import requests
from bs4 import BeautifulSoup, ResultSet, Tag

basicConfig(level=INFO)


class UserAgents:
    """Interface representing user agents utilities.

    MDN Web Docs:
    -
    The User-Agent request header is a characteristic string that lets servers and
    network peers identify the application, operating system, vendor, and/or version
    of the requesting user agent.

    Wikepedia:
    -
    The user agent plays the role of the client in a client-server system. The HTTP
    User-Agent header is intended to clearly identify the agent to the server. This
    header can be omitted/spoofed, so some websites use other agent detection methods.
    """

    def __init__(
        self: UserAgents,
        filename: str = "user-agents",
        folder: str = "datas",
        directory: Path = Path(__file__).parent,
    ) -> None:
        path = directory / folder
        self.path_html = path / f"{filename}.html"
        self.path_json = path / f"{filename}.json"
        self.endpoints = ["windows", "macos", "ios", "chrome-os", "android"]
        self.url = "https://www.whatismybrowser.com/guides/the-latest-user-agent/"

    def fetch_user_agents(
        self: UserAgents,
    ) -> None:
        """Fetch and save the user agents HTML tables."""
        data: str = ""

        for endpoint in self.endpoints:
            response = requests.get(url=f"{self.url}{endpoint}", timeout=10)
            info(response.ok, response.status_code)
            soup = BeautifulSoup(markup=response.content, features="html.parser")
            data += str(soup.find("table"))

        self.path_html.parent.mkdir(parents=True, exist_ok=True)
        self.path_html.write_text(data=data, encoding="utf-8")

    def format_user_agents(
        self: UserAgents,
    ) -> None:
        """Convert the user agents HTML tables to JSON format."""
        soup = BeautifulSoup(markup=self.path_html.read_text(), features="html.parser")
        tables: ResultSet[Tag] = soup.find_all("table")
        bodies: list[Tag] = [table.find("tbody") for table in tables]
        rows: list[Tag] = [row for body in bodies for row in body.find_all("tr")]
        lists = [row.select("td:last-child ul li span") for row in rows]
        data = [span.string for spans in lists for span in spans]
        self.save_user_agents(data=data)

    def save_user_agents(
        self: UserAgents,
        data: list[str],
        path: Path | None = None,
    ) -> None:
        """Save the user agents list as a JSON.

        Args:
        ----
            data (list[str]):
                The user agents list.
            path (Path | None, optional):
                The save path. Defaults to None.
        """
        (path or self.path_json).write_text(json.dumps(obj=data))

    def load_user_agents(
        self: UserAgents,
    ) -> list[str]:
        """Load the user agents JSON.

        Returns
        -------
            list[str]:
                The list of user agents.
        """
        return json.loads(s=self.path_json.read_text())
