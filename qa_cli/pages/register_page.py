from __future__ import annotations

from dataclasses import dataclass

from selenium.webdriver.common.by import By

from qa_cli.pages.base_page import BasePage


@dataclass(frozen=True)
class SignupOutcome:
    html5_block: bool
    validation_message: str
    error_text: str
    navigated: bool
    landed_on_account_info: bool


class RegisterPage(BasePage):
    

    PATH = "/login"

    NAME = (By.CSS_SELECTOR, 'input[data-qa="signup-name"]')
    EMAIL = (By.CSS_SELECTOR, 'input[data-qa="signup-email"]')
    BTN_SIGNUP = (By.CSS_SELECTOR, 'button[data-qa="signup-button"]')

    
    SIGNUP_ERROR = (By.CSS_SELECTOR, "form[action='/signup'] p")

    
    ACCOUNT_INFO = (By.XPATH, "//*[@class='login-form']//*[text()='Enter Account Information']")

    def open(self) -> None:
        self.open_url(self.PATH)
        self.waits.visible(self.NAME)
        self.waits.visible(self.EMAIL)
        self.waits.clickable(self.BTN_SIGNUP)

    def _validation_message(self) -> str:
        try:
            el = self.driver.find_element(*self.EMAIL)
            msg = self.driver.execute_script("return arguments[0].validationMessage;", el)
            return (msg or "").strip()
        except Exception:
            return ""

    def _signup_error(self) -> str:
        try:
            el = self.driver.find_element(*self.SIGNUP_ERROR)
            return (el.text or "").strip()
        except Exception:
            return ""

    def _is_account_info(self) -> bool:
        try:
            self.driver.find_element(*self.ACCOUNT_INFO)
            return True
        except Exception:
            return False

    def submit_signup(self, name: str, email: str) -> SignupOutcome:
        self.waits.visible(self.NAME).clear()
        self.driver.find_element(*self.NAME).send_keys(name)

        self.waits.visible(self.EMAIL).clear()
        self.driver.find_element(*self.EMAIL).send_keys(email)

        before_url = self.driver.current_url
        self.waits.clickable(self.BTN_SIGNUP).click()

        
        try:
            self.waits._w().until(lambda d: d.current_url != before_url or self._signup_error() or self._validation_message())
        except Exception:
            pass

        navigated = self.driver.current_url != before_url
        validation_message = self._validation_message()
        error_text = self._signup_error()
        landed_on_account_info = self._is_account_info()

        html5_block = (not navigated) and bool(validation_message)

        return SignupOutcome(
            html5_block=html5_block,
            validation_message=validation_message,
            error_text=error_text,
            navigated=navigated,
            landed_on_account_info=landed_on_account_info,
        )