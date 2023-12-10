"""Module User Agents."""

from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any

import pytz
import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from utilities import logger


class UserAgents:
    """Interface representing user agents utilities.

    MDN Web Docs:
    -
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent

    Wikepedia:
    -
    https://en.wikipedia.org/wiki/User_agent
    """

    def __init__(
        self: UserAgents,
        filename: str = "user-agents",
        folder: str = "datas",
        directory: Path = Path(__file__).parent,
        refresh_time: float = 60 * 60 * 24,
    ) -> None:
        """Interface representing user agents utilities.

        Args:
            filename (str, optional):
                The filename to save the list of user agents.
                Defaults to "user-agents".
            folder (str, optional):
                The folder to save the list of user agents.
                Defaults to "datas".
            directory (Path, optional):
                The directory to save the list of user agents.
                Defaults to Path(__file__).parent.
        """
        path = directory / folder
        self.path = path
        self.path_time = path / f"{filename}-time.json"
        self.path_html = path / f"{filename}.html"
        self.path_json = path / f"{filename}.json"
        self.endpoints = ["windows", "macos", "ios", "chrome-os", "android"]
        self.url = "https://www.whatismybrowser.com/guides/the-latest-user-agent/"
        self.refresh_time = refresh_time

    def fetch(
        self: UserAgents,
    ) -> None:
        """Fetch and save the user agents HTML tables."""
        data: str = ""

        for endpoint in self.endpoints:
            response = requests.get(url=f"{self.url}{endpoint}", timeout=10)
            soup = BeautifulSoup(markup=response.content, features="html.parser")
            data += str(soup.find("table"))

        self.path_html.parent.mkdir(parents=True, exist_ok=True)
        self.path_html.write_text(data=data, encoding="utf-8")

    def convert(
        self: UserAgents,
    ) -> list[str | None]:
        """Convert the user agents HTML tables to JSON format."""
        soup = BeautifulSoup(markup=self.path_html.read_text(), features="html.parser")
        tables: ResultSet[Tag] = soup.find_all("table")
        bodies: list[Tag] = [table.find("tbody") for table in tables]
        rows: list[Tag] = [row for body in bodies for row in body.find_all("tr")]
        lists = [row.select("td:last-child ul li span") for row in rows]
        return [span.string for spans in lists for span in spans]

    def refresh(
        self: UserAgents,
        refresh_time: float | None = None,
    ) -> bool:
        """Refresh the list of user agents.

        Parameters
        ----------
        refresh_time : float | None, optional
            The time (seconds) needed for a refresh, by default None

        Returns
        -------
        bool
            True if a refresh was done.
        """
        datetime_info = pytz.timezone(zone=("America/Montreal"))
        datetime_next = datetime.now(tz=datetime_info)

        if self.path_time.exists():
            datetime_data = json.loads(s=self.path_time.read_text())
            datetime_prev = datetime.strptime(
                datetime_data,
                "%d/%m/%Y, %H:%M:%S",
            ).astimezone(tz=datetime_info)
            datetime_diff = datetime_next - datetime_prev
            datetime_secs = datetime_diff.total_seconds()

            if datetime_secs < (refresh_time or self.refresh_time):
                return False

        logger.trace_(msg="Refresh User Agents!")

        self.fetch()
        data = self.convert()
        self.save(data=data, datetime=datetime_next)

        return True

    def save(
        self: UserAgents,
        data: list[str],
        datetime: datetime,
        path: Path | None = None,
    ) -> None:
        """Save the user agents list.

        Args:
        ----
            data (list[str]):
                The user agents list.
            path (Path | None, optional):
                The save path. Defaults to None.
        """
        (path or self.path_json).write_text(json.dumps(obj=data))
        self.path_time.write_text(
            json.dumps(obj=datetime.strftime(format="%d/%m/%Y, %H:%M:%S")),
        )

    def load(
        self: UserAgents,
    ) -> dict[str, Any]:
        """Load the user agents list.

        Returns
        -------
            list[str]:
                The list of user agents.
        """
        return json.loads(s=self.path_json.read_text())

    def extract(
        self: UserAgents,
        limit: int | None = None,
    ) -> list[str]:
        """Extract a list of random user agents.

        Args:
        ----
            limit (int | None, optional):
                The maximum number of user agents. Defaults to None.

        Returns
        -------
            list[str]:
                The list of user agents.
        """
        agents = self.load()

        return random.sample(
            population=agents,
            k=len(agents) if limit is None else limit,
        )
