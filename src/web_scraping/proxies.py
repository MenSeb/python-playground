"""Module Proxies."""

from __future__ import annotations

import functools
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, NamedTuple

import numpy as np
import pandas as pd
import pytz
import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from pandas import DataFrame
from utilities import logger


@dataclass
class Operators:
    """Interface representing dataframe comparison operators."""

    def eq(
        self: Operators,
        data: str,
        dataframe: DataFrame,
    ) -> DataFrame:
        """Compare DataFrames for equality elementwise."""
        return dataframe.eq(data)

    def ne(
        self: Operators,
        data: str,
        dataframe: DataFrame,
    ) -> DataFrame:
        """Compare DataFrames for inequality elementwise."""
        return dataframe.ne(data)

    def le(
        self: Operators,
        data: str,
        dataframe: DataFrame,
    ) -> DataFrame:
        """Compare DataFrames for less than inequality or equality elementwise."""
        return dataframe.le(data)

    def lt(
        self: Operators,
        data: str,
        dataframe: DataFrame,
    ) -> DataFrame:
        """Compare DataFrames for strictly less than inequality elementwise."""
        return dataframe.lt(data)

    def ge(
        self: Operators,
        data: str,
        dataframe: DataFrame,
    ) -> DataFrame:
        """Compare DataFrames for greater than inequality or equality elementwise."""
        return dataframe.ge(data)

    def gt(
        self: Operators,
        data: str,
        dataframe: DataFrame,
    ) -> DataFrame:
        """Compare DataFrames for strictly greater than inequality elementwise."""
        return dataframe.gt(data)


@dataclass
class Headers:
    """Interface representing the proxy list headers."""

    host: str = "host"
    port: str = "port"
    code: str = "code"
    country: str = "country"
    anonymity: str = "anonymity"
    google: str = "google"
    https: str = "https"
    time: str = "time"


class Query(NamedTuple):
    """Interface representing a proxy query."""

    data: Any
    key: str
    operator: Callable[[str, DataFrame], DataFrame]


class Proxies:
    """Interface representating proxy utilities.

    MDN Web Docs:
    -
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Proxy_servers_and_tunneling

    Wikipedia:
    -
    https://en.wikipedia.org/wiki/Proxy_server
    """

    def __init__(
        self: Proxies,
        filename: str = "proxies",
        folder: str = "datas",
        directory: Path = Path(__file__).parent,
        refresh_time: float = 60 * 60 * 24,
    ) -> None:
        """Interface representating proxy utilities.

        Args:
            filename (str, optional):
                The filename to save the list of user agents.
                Defaults to "proxies".
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
        self.path_active = path / f"{filename}-active.json"
        self.path_html = path / f"{filename}.html"
        self.path_csv = path / f"{filename}.csv"
        self.url = "https://free-proxy-list.net/"
        self.headers = Headers()
        self.operators = Operators()
        self.session = requests.Session()
        self.keys = list(asdict(self.headers).keys())
        self.refresh_time = refresh_time

    def fetch(
        self: Proxies,
    ) -> None:
        """Fetch and save the proxy HTML table."""
        response = requests.get(url=self.url, timeout=10)
        soup = BeautifulSoup(markup=response.content, features="html.parser")
        self.path_html.parent.mkdir(parents=True, exist_ok=True)
        self.path_html.write_text(data=str(soup.find("table")), encoding="utf-8")

    def convert(
        self: Proxies,
    ) -> list[str]:
        """Convert the proxy HTML table to CSV format."""
        table = BeautifulSoup(markup=self.path_html.read_text(), features="html.parser")
        rows: ResultSet[Tag] = table.find("tbody").find_all("tr")
        rows_cells: list[ResultSet[Tag]] = [row.find_all("td") for row in rows]
        data: list[str] = [(cell.string for cell in cells) for cells in rows_cells]
        return data

    def refresh(
        self: Proxies,
        refresh_time: float | None = None,
    ) -> None:
        """Refresh the list of proxies.

        Parameters
        ----------
        refresh_time : float | None, optional
            The time (seconds) needed for a refresh, by default None

        Returns
        -------
        bool
            True if a refresh was done.
        """
        logger.trace_()

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

        logger.info_(msg="Refresh Proxies!")

        self.fetch()
        data = self.convert()
        self.save(data=data, datetime=datetime_next)

        return True

    def query(
        self: Proxies,
        queries: list[Query],
        dataframe: DataFrame | None = None,
        logical_operator: str = "and",
    ) -> DataFrame:
        """Find specific proxies using query conditions.

        Usage:
        -----

        dataframe = self.query(
            queries=[
                Query(data="US", key=keys.code, operator=operators.eq),

                Query(data=80, key=keys.port, operator=operators.eq),
            ],
        )

        Args:
        ----
            queries (list[Query]):
                The list of query conditions.

        Returns
        -------
            DataFrame:
                The filtered dataframe.
        """
        dataframe = self.load() if dataframe is None else dataframe
        conditions = [
            operator(data, dataframe.get(key)) for data, key, operator in queries
        ]
        logic_operator = np.logical_and if logical_operator == "and" else np.logical_or
        reducer = functools.reduce(logic_operator, conditions)
        return dataframe[reducer]

    def extract(
        self: Proxies,
        limit: int | None = None,
        dataframe: DataFrame | None = None,
        protocol: bool = True,
    ) -> list[str]:
        """Extract a list of proxies.

        Default format: {protocol}://{host}:{port}

        Args:
        ----
            limit (int | None, optional):
                The maximum number of proxies. Defaults to None.
            dataframe (DataFrame | None, optional):
                A proxy dataframe. Defaults to None.

        Returns
        -------
            list[str]:
                The list of proxies.
        """
        datas = (
            self.load(limit=limit) if dataframe is None else dataframe.head(n=limit)
        )[[self.headers.host, self.headers.port, self.headers.https]]

        return [
            f"{'https' if https == 'yes' else 'http'}://{host}:{port}"
            if protocol
            else f"{host}:{port}"
            for _, (host, port, https) in datas.iterrows()
        ]

    def extract_https(self: Proxies) -> list[str]:
        """Extract a list of HTTPS proxies."""
        return self.extract(
            dataframe=self.query(
                queries=[
                    Query(
                        data="yes",
                        key=self.headers.https,
                        operator=self.operators.eq,
                    ),
                ],
                dataframe=self.load(),
            ),
        )

    def load(
        self: Proxies,
        limit: int | None = None,
    ) -> DataFrame:
        """Load the proxy dataframe.

        Args:
        ----
            limit (int | None, optional):
                The maximum number of proxies. Defaults to None.

        Returns
        -------
            DataFrame:
                The proxy dataframe.
        """
        return pd.read_csv(filepath_or_buffer=self.path_csv, nrows=limit)

    def save(
        self: Proxies,
        data: list[str],
        datetime: datetime,
        path: Path | None = None,
    ) -> None:
        """Save the proxy list as a dataframe.

        Args:
        ----
            data (list[str]):
                The proxy list.
            path (Path | None, optional):
                The save path. Defaults to None.
        """
        dataframe = DataFrame(data=data, columns=self.keys)
        dataframe.to_csv(path_or_buf=path or self.path_csv, index=False)
        self.path_time.write_text(
            json.dumps(obj=datetime.strftime(format="%d/%m/%Y, %H:%M:%S")),
        )

    def save_active(
        self: Proxies,
        proxies: list[str],
    ) -> None:
        """Save the active proxy list.

        Args:
        ----
            proxies (list[str]):
                The proxy list.
        """
        self.path_active.write_text(json.dumps(obj=proxies))

    def load_active(self: Proxies) -> list[str]:
        """Load the active proxy list."""
        return json.loads(s=self.path_active.read_text())
