"""Module Benchmark."""

from __future__ import annotations

import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.logger import set_logger


def benchmark_selenium(url: str, selector: str) -> list[str]:
    """Benchmark Selenium.

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
    logger = logging.getLogger("selenium")
    logger.setLevel(level=logging.CRITICAL)
    set_logger(logger=logger)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=options, service=service)
    driver_wait = WebDriverWait(driver=driver, timeout=10)
    driver.get(url=url)
    driver_wait.until(
        expected_conditions.presence_of_all_elements_located(
            (By.CSS_SELECTOR, selector),
        ),
    )
    elements = driver.find_elements(by=By.CSS_SELECTOR, value=selector)
    data = [element.text for element in elements]
    driver.quit()
    return data
