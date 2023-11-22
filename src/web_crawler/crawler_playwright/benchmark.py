"""Module Benchmark Playwright."""

from __future__ import annotations

from typing import Any, Callable

from playwright.sync_api import Page, sync_playwright


def playwright_extract_table(
    page: Page,
    url: str,
    selector: str,
) -> list[str]:
    """Extract table using Playwright."""
    page.goto(url=url)
    page.wait_for_selector(selector=selector)
    elements = page.locator(selector=f"css={selector}")
    return [element.text_content() for element in elements.element_handles()]


def playwright_extract_lots(
    page: Page,
    url: str,
    lots: list[str],
) -> dict[str, float]:
    """Extract lost using Playwright."""
    page.goto(url=url)
    page.locator(selector="button[mat-dialog-close]").click()
    search_input = page.locator(selector="#mat-input-0")

    areas = {}

    for lot in lots:
        search_input.fill("")
        search_input.type(text=lot)
        search_input.press(key="Enter")
        page.locator(selector=f"//h4[contains(text(), '{lot}')]").click()
        area = page.locator(
            selector="//td[contains(text(), 'Superficie (pi2)')]/following-sibling::td",
        ).text_content()
        areas[lot] = float(area.replace(" ", "").replace(",", "."))

    return areas


def use_playwright(
    callback: Callable | None = None,
    **kwargs: dict[str, Any],
) -> None:
    """Use Playwright with a callback.

    Parameters
    ----------
    callback : Callable
        The callback to use with the browser context.
    """
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        if callback:
            callback(page=page, **kwargs)
        browser.close()
