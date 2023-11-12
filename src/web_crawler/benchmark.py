"""Module Webdriver Benchmark."""

from __future__ import annotations

import time
from logging import INFO, basicConfig, info
from typing import Callable

basicConfig(level=INFO)


def benchmark_crawler(
    url: str,
    selector: str,
    callback: Callable,
    series: int = 10,
) -> float:
    """Benchmark crawler.

    Parameters
    ----------
    url : str
        The url to fetch.
    selector : str
       The selector to extract data from.
    callback : Callable
        The callback to fetch data.
    series : int
        The number of tests to run.
    """
    times: list[float] = []
    function = callback.__name__

    info(f"Start Benchmark ({series}) - {function}")

    for index in range(series):
        start = time.time()
        callback(url=url, selector=selector)
        end = time.time()
        total = end - start
        times.append(total)

        info(f"Benchmark {index + 1} - Time {total:.2f}s")

    info(f"Stop Benchmark - {function}")

    average = sum(times) / series

    info(f"Benchmark average {average:.2f}s\n")

    return average


if __name__ == "__main__":
    from crawler_playwright.benchmark import benchmark_playwright
    from crawler_selenium.benchmark import benchmark_selenium

    url = "https://webscraper.io/test-sites/tables"
    selector = "table.table td"

    time_playwright = benchmark_crawler(
        callback=benchmark_playwright,
        selector=selector,
        url=url,
    )

    time_selenium = benchmark_crawler(
        callback=benchmark_selenium,
        selector=selector,
        url=url,
    )

    time_diff = abs(time_selenium - time_playwright)
    crawler = "Playwright" if time_playwright < time_selenium else "Selenium"

    info(f"On average, Playwright took {time_playwright:.2f}s.")
    info(f"On average, Selenium took {time_selenium:.2f}s.")
    info(f"Fastest was {crawler} by {time_diff:.2f}s.")
