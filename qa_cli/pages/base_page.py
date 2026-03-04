from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver

from qa_cli.pages.waits import Waits


class BasePage:
    def __init__(self, driver: WebDriver, base_url: str, timeout: int = 10):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.waits = Waits(driver, timeout=timeout)

    def open_url(self, path: str) -> None:
        self.driver.get(self.base_url + path)