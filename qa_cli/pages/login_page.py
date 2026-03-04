from __future__ import annotations

from selenium.webdriver.common.by import By

from qa_cli.pages.base_page import BasePage


class LoginPage(BasePage):
    """
    AutomationExercise login page: /login
    """

    PATH = "/login"

    EMAIL = (By.CSS_SELECTOR, 'input[data-qa="login-email"]')
    PASSWORD = (By.CSS_SELECTOR, 'input[data-qa="login-password"]')
    BTN_LOGIN = (By.CSS_SELECTOR, 'button[data-qa="login-button"]')

    
    ERROR = (By.XPATH, "//*[@class='login-form']//p")

    
    LOGGED_IN_EMAIL = (By.XPATH, "//*[contains(@class,'fa-user')]/following-sibling::b")

    LOGOUT_LINK = (By.CSS_SELECTOR, 'a[href="/logout"]')

    def open(self) -> None:
        self.open_url(self.PATH)
        self.waits.visible(self.EMAIL)
        self.waits.visible(self.PASSWORD)
        self.waits.clickable(self.BTN_LOGIN)

    def login(self, email: str, password: str) -> None:
        email = (email or "").strip()
        password = password or ""

        self.waits.visible(self.EMAIL).clear()
        self.driver.find_element(*self.EMAIL).send_keys(email)

        self.waits.visible(self.PASSWORD).clear()
        self.driver.find_element(*self.PASSWORD).send_keys(password)

        self.waits.clickable(self.BTN_LOGIN).click()

    def get_error_text(self) -> str:
        try:
            el = self.driver.find_element(*self.ERROR)
            return (el.text or "").strip()
        except Exception:
            return ""

    def is_logged_in(self, timeout: int = 8) -> bool:
        try:
            self.waits.visible(self.LOGGED_IN_EMAIL, timeout=timeout)
            return True
        except Exception:
            return False

    def is_logout_visible(self, timeout: int = 8) -> bool:
        try:
            self.waits.visible(self.LOGOUT_LINK, timeout=timeout)
            return True
        except Exception:
            return False

    def is_on_login(self) -> bool:
        
        try:
            return "/login" in (self.driver.current_url or "")
        except Exception:
            return False