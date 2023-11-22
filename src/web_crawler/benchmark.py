"""Module Webdriver Benchmark."""

from __future__ import annotations

import functools
import time
from logging import INFO, basicConfig, info
from typing import Callable

from crawler_playwright.benchmark import (
    playwright_extract_lots,
    playwright_extract_table,
    use_playwright,
)
from crawler_selenium.benchmark import (
    selenium_extract_lots,
    selenium_extract_table,
    use_selenium,
)

basicConfig(level=INFO)


def run_benchmark(
    callback: Callable | functools.partial,
    series: int = 10,
) -> float:
    """Run a benchmark series with a callback.

    Parameters
    ----------
    callback : Callable | partial
        The callback for the benchmark series.
    series : int, optional
        The number of times to run, by default 10.

    Returns
    -------
    float
        The average time for the benchmark series.
    """
    times: list[float] = []
    name = (
        callback.func.__name__
        if isinstance(callback, functools.partial)
        else callback.__name__
    )

    info(f"Start Benchmark ({series}) - {name}")

    for index in range(series):
        start = time.time()
        callback()
        end = time.time()
        total = end - start
        times.append(total)

        info(f"Benchmark {index + 1} - Time {total:.2f}s")

    info("Stop Benchmark")

    average = sum(times) / series

    info(f"Benchmark average {average:.2f}s\n")

    return average


def run_benchmarks(
    callback_playwright: Callable,
    callback_selenium: Callable,
    series: int = 10,
) -> None:
    """Run benchmarks series with callbacks.

    Parameters
    ----------
    callback_playwright : Callable
        The Playwright callback.
    callback_selenium : Callable
        The Selenium callback.
    series : int, optional
        The number of times to run, by default 10
    """
    time_playwright = run_benchmark(callback=callback_playwright, series=series)
    time_selenium = run_benchmark(callback=callback_selenium, series=series)
    time_diff = abs(time_selenium - time_playwright)
    crawler = "Playwright" if time_playwright < time_selenium else "Selenium"

    info(f"On average, Playwright took {time_playwright:.2f}s.")
    info(f"On average, Selenium took {time_selenium:.2f}s.")
    info(f"Fastest was {crawler} by {time_diff:.2f}s.")


def benchmarks_extract_lots(
    series: int | None = None,
) -> None:
    """Run extract lots benchmarks.

    Parameters
    ----------
    series : int | None, optional
        The number of times to run, by default None
    """
    lots = ["6227707", "4433198", "3920154"]
    url = "https://demeter.cptaq.gouv.qc.ca/"

    run_benchmarks(
        callback_playwright=functools.partial(
            use_playwright,
            callback=playwright_extract_lots,
            url=url,
            lots=lots,
        ),
        callback_selenium=functools.partial(
            use_selenium,
            callback=selenium_extract_lots,
            url=url,
            lots=lots,
        ),
        series=series,
    )


def benchmarks_extract_table(
    series: int | None = None,
) -> None:
    """Run extract table benchmarks.

    Parameters
    ----------
    series : int | None, optional
        The number of times to run, by default None
    """
    url = "https://webscraper.io/test-sites/tables"
    selector = "table.table td"

    run_benchmarks(
        callback_playwright=functools.partial(
            use_playwright,
            callback=playwright_extract_table,
            url=url,
            selector=selector,
        ),
        callback_selenium=functools.partial(
            use_selenium,
            callback=selenium_extract_table,
            url=url,
            selector=selector,
        ),
        series=series,
    )


def benchmarks_launch(
    series: int | None = None,
) -> None:
    """Run launch benchmarks.

    Parameters
    ----------
    series : int | None, optional
        The number of times to run, by default None
    """
    run_benchmarks(
        callback_playwright=use_playwright,
        callback_selenium=use_selenium,
        series=series,
    )


if __name__ == "__main__":
    benchmarks_launch(series=5)
