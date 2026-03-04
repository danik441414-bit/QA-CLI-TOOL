from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Optional

from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


Locator = Tuple[str, str]


@dataclass
class Waits:
    driver: WebDriver
    timeout: int = 10

    def _w(self, timeout: Optional[int] = None) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout or self.timeout)

    def present(self, locator: Locator, timeout: Optional[int] = None) -> WebElement:
        return self._w(timeout).until(EC.presence_of_element_located(locator))

    def visible(self, locator: Locator, timeout: Optional[int] = None) -> WebElement:
        return self._w(timeout).until(EC.visibility_of_element_located(locator))

    def clickable(self, locator: Locator, timeout: Optional[int] = None) -> WebElement:
        return self._w(timeout).until(EC.element_to_be_clickable(locator))

    def url_changed(self, old_url: str, timeout: Optional[int] = None) -> bool:
        def _changed(d: WebDriver) -> bool:
            return d.current_url != old_url

        return bool(self._w(timeout).until(_changed))