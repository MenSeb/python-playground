"""Module Benchmark."""

from __future__ import annotations

from playwright.sync_api import sync_playwright


def benchmark_playwright(url: str, selector: str) -> list[str]:
    """Benchmark Playwright.

    Parameters
    ----------
    url : str
        The url to fetch.
    selector : str
        The selector to extract data from.

    Returns
    -------
    list[str]
        The extracted data.
    """
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        page.goto(url=url)
        page.wait_for_selector(selector=selector)
        elements = page.locator(selector=f"css={selector}")
        data = [element.text_content() for element in elements.element_handles()]
        browser.close()
    return data
