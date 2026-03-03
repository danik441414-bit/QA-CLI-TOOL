from __future__ import annotations

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    """
    AutomationExercise login page:
    /login -> блок "Login to your account" (email + password + Login button)
    """

    PATH = "/login"

    EMAIL = (By.CSS_SELECTOR, 'input[data-qa="login-email"]')
    PASSWORD = (By.CSS_SELECTOR, 'input[data-qa="login-password"]')
    BTN_LOGIN = (By.CSS_SELECTOR, 'button[data-qa="login-button"]')

    
    ERROR = (By.CSS_SELECTOR, 'form[action="/login"] p')

    
    LOGGED_IN_AS = (
        By.XPATH,
        "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'logged in as')]",
    )
    LOGOUT_LINK = (By.CSS_SELECTOR, 'a[href="/logout"]')

    def __init__(self, driver: WebDriver, base_url: str, timeout: int = 10):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    def open(self) -> None:
        self.driver.get(self.base_url + self.PATH)
        self.wait.until(EC.presence_of_element_located(self.EMAIL))
        self.wait.until(EC.presence_of_element_located(self.PASSWORD))
        self.wait.until(EC.element_to_be_clickable(self.BTN_LOGIN))

    def login(self, email: str, password: str) -> None:
        email = (email or "").strip()
        password = password or ""

        email_el = self.driver.find_element(*self.EMAIL)
        pwd_el = self.driver.find_element(*self.PASSWORD)

        email_el.clear()
        email_el.send_keys(email)

        pwd_el.clear()
        pwd_el.send_keys(password)

        self.driver.find_element(*self.BTN_LOGIN).click()

    def get_error_text(self) -> str | None:
        try:
            el = self.driver.find_element(*self.ERROR)
            text = (el.text or "").strip()
            return text if text else None
        except Exception:
            return None

    def _logged_in_marker_present(self) -> bool:
        
        try:
            self.driver.find_element(*self.LOGOUT_LINK)
            return True
        except Exception:
            pass

        try:
            self.driver.find_element(*self.LOGGED_IN_AS)
            return True
        except Exception:
            return False

    def is_logged_in(self, timeout: int = 5) -> bool:
        """
        Устойчиво: ждём чуть-чуть, пока хедер обновится после логина.
        Считаем успехом: появился Logout или "Logged in as".
        """
        try:
            WebDriverWait(self.driver, timeout).until(lambda d: self._logged_in_marker_present())
            return True
        except TimeoutException:
            return False