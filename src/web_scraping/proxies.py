"""Module Proxies."""

from __future__ import annotations

import functools
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, NamedTuple

import numpy as np
import pandas as pd
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
        self.path_html = path / f"{filename}.html"
        self.path_csv = path / f"{filename}.csv"
        self.url = "https://free-proxy-list.net/"
        self.headers = Headers()
        self.operators = Operators()
        self.session = requests.Session()
        self.keys = list(asdict(self.headers).keys())

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
    ) -> None:
        """Convert the proxy HTML table to CSV format."""
        table = BeautifulSoup(markup=self.path_html.read_text(), features="html.parser")
        rows: ResultSet[Tag] = table.find("tbody").find_all("tr")
        rows_cells: list[ResultSet[Tag]] = [row.find_all("td") for row in rows]
        datas: list[str] = [(cell.string for cell in cells) for cells in rows_cells]
        self.save(datas=datas)

    def refresh(
        self: Proxies,
    ) -> None:
        """Refresh the list of proxies."""
        logger.trace_()
        self.fetch()
        self.convert()

    def query(
        self: Proxies,
        queries: list[Query],
        dataframe: DataFrame | None = None,
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
        reducer = functools.reduce(np.logical_and, conditions)
        return dataframe[reducer]

    def extract(
        self: Proxies,
        limit: int | None = None,
        dataframe: DataFrame | None = None,
    ) -> list[str]:
        """Extract a list of proxies in the format {host}:{port}.

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
        )[[self.headers.host, self.headers.port]]
        return [f"{host}:{port}" for _, (host, port) in datas.iterrows()]

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
        datas: list[str],
        path: Path | None = None,
    ) -> None:
        """Save the proxy list as a dataframe.

        Args:
        ----
            datas (list[str]):
                The proxy list.
            path (Path | None, optional):
                The save path. Defaults to None.
        """
        dataframe = DataFrame(data=datas, columns=self.keys)
        dataframe.to_csv(path_or_buf=path or self.path_csv, index=False)
