from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class HerokuLoginPage:
    

    PATH = "/login"

    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    BTN_LOGIN = (By.CSS_SELECTOR, "button[type='submit']")

    FLASH = (By.ID, "flash")
    BTN_LOGOUT = (By.CSS_SELECTOR, "a[href='/logout']")

    def __init__(self, driver: WebDriver, base_url: str, timeout: int = 10):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    def open(self) -> None:
        self.driver.get(self.base_url + self.PATH)
        self.wait.until(EC.presence_of_element_located(self.USERNAME))
        self.wait.until(EC.presence_of_element_located(self.PASSWORD))
        self.wait.until(EC.element_to_be_clickable(self.BTN_LOGIN))

    
    def login(self, username: str, password: str) -> None:
        username = (username or "").strip()
        password = password or ""

        u = self.driver.find_element(*self.USERNAME)
        p = self.driver.find_element(*self.PASSWORD)

        u.clear()
        u.send_keys(username)

        p.clear()
        p.send_keys(password)

        self.driver.find_element(*self.BTN_LOGIN).click()

    def get_flash_text(self) -> str | None:
        try:
            el = self.driver.find_element(*self.FLASH)
            text = (el.text or "").strip()
            return text if text else None
        except Exception:
            return None

    def is_logout_visible(self) -> bool:
        try:
            self.driver.find_element(*self.BTN_LOGOUT)
            return True
        except Exception:
            return False

    def logout(self) -> None:
        self.driver.find_element(*self.BTN_LOGOUT).click()