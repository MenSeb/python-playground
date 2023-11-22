"""Module Benchmark Selenium."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.logger import set_logger

if TYPE_CHECKING:
    from selenium.webdriver.chrome.webdriver import WebDriver


def selenium_extract_table(
    driver: WebDriver,
    driver_wait: WebDriverWait,
    url: str,
    selector: str,
) -> list[str]:
    """Extract table using Selenium."""
    driver.get(url=url)
    driver_wait.until(
        expected_conditions.presence_of_all_elements_located(
            (By.CSS_SELECTOR, selector),
        ),
    )
    elements = driver.find_elements(by=By.CSS_SELECTOR, value=selector)
    return [element.text for element in elements]


def selenium_extract_lots(
    driver: WebDriver,
    driver_wait: WebDriverWait,
    url: str,
    lots: list[str],
) -> dict[str, float]:
    """Extract lots using Selenium."""
    driver.get(url=url)
    driver_wait.until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, "button[mat-dialog-close]"),
        ),
    ).click()
    search_input = driver.find_element(by=By.CSS_SELECTOR, value="#mat-input-0")

    areas = {}

    for lot in lots:
        search_input.send_keys(lot)
        search_input.clear()
        driver_wait.until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, f"//h4[contains(text(), '{lot}')]"),
            ),
        ).click()
        area = driver_wait.until(
            expected_conditions.presence_of_element_located(
                (
                    By.XPATH,
                    "//td[contains(text(), 'Superficie (pi2)')]/following-sibling::td",
                ),
            ),
        ).get_attribute("innerText")
        areas[lot] = float(area.replace(" ", "").replace(",", "."))

    return areas


def use_selenium(
    callback: Callable | None = None,
    **kwargs: dict[str, Any],
) -> list[str]:
    """Use Selenium with a callback.

    Parameters
    ----------
    callback : Callable
        The callback to use with the browser context.
    """
    logger = logging.getLogger("selenium")
    logger.setLevel(level=logging.CRITICAL)
    set_logger(logger=logger)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=options, service=service)
    driver_wait = WebDriverWait(driver=driver, timeout=10)
    if callback:
        callback(driver=driver, driver_wait=driver_wait, **kwargs)
    driver.quit()
