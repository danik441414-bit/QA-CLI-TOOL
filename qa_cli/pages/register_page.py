from __future__ import annotations

from dataclasses import dataclass

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@dataclass(frozen=True)
class SignupOutcome:
    html5_block: bool
    validation_message: str
    error_text: str
    navigated: bool
    landed_on_account_info: bool


class RegisterPage:
    """
    AutomationExercise регистрация:
    /login -> блок "New User Signup!" (name + email + Signup button)
    """

    PATH = "/login"

    # New User Signup!
    NAME = (By.CSS_SELECTOR, 'input[data-qa="signup-name"]')
    EMAIL = (By.CSS_SELECTOR, 'input[data-qa="signup-email"]')
    BTN_SIGNUP = (By.CSS_SELECTOR, 'button[data-qa="signup-button"]')

    # Текст под формой signup: "Email Address already exist!"
    SIGNUP_ERROR = (By.CSS_SELECTOR, "form[action='/signup'] p")

    # Маркеры следующей страницы (Account Information)
    ACCOUNT_INFO_HEADING = (By.XPATH, "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'enter account information')]")
    ACCOUNT_INFO_FORM = (By.CSS_SELECTOR, 'form[action="/signup"]')  # на AE иногда форма остаётся, поэтому не единственный маркер
    ACCOUNT_INFO_PASSWORD = (By.CSS_SELECTOR, 'input[data-qa="password"]')  # на странице account info это поле есть

    def __init__(self, driver: WebDriver, base_url: str, timeout: int = 10):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    def open(self) -> None:
        self.driver.get(self.base_url + self.PATH)

        # ждём, что реально появилась форма signup
        self.wait.until(EC.presence_of_element_located(self.NAME))
        self.wait.until(EC.presence_of_element_located(self.EMAIL))
        self.wait.until(EC.element_to_be_clickable(self.BTN_SIGNUP))

    def _validation_message(self) -> str:
        """
        HTML5 validationMessage на email input.
        Если форма не сабмитится из-за HTML5 валидации, тут будет текст.
        """
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
        """
        Надёжная проверка, что мы попали на "ENTER ACCOUNT INFORMATION".
        Иногда текст может быть в разном регистре/месте.
        """
        try:
            # Самый надёжный маркер на AE — поле password (Account Info page)
            self.driver.find_element(*self.ACCOUNT_INFO_PASSWORD)
            return True
        except Exception:
            pass

        try:
            self.driver.find_element(*self.ACCOUNT_INFO_HEADING)
            return True
        except Exception:
            return False

    def submit_signup(self, name: str, email: str) -> SignupOutcome:
        # На всякий случай: если пользователь оставил пробелы
        name = (name or "").strip()
        email = (email or "").strip()

        name_el = self.driver.find_element(*self.NAME)
        email_el = self.driver.find_element(*self.EMAIL)

        name_el.clear()
        name_el.send_keys(name)

        email_el.clear()
        email_el.send_keys(email)

        before_url = self.driver.current_url

        self.wait.until(EC.element_to_be_clickable(self.BTN_SIGNUP))
        self.driver.find_element(*self.BTN_SIGNUP).click()

        # ждём: либо url сменился, либо появилась ошибка, либо HTML5 validation message
        try:
            self.wait.until(
                lambda d: d.current_url != before_url
                or bool(self._signup_error())
                or bool(self._validation_message())
                or self._is_account_info()
            )
        except TimeoutException:
            # не падаем — outcome всё равно снимем
            pass

        navigated = self.driver.current_url != before_url
        validation_message = self._validation_message()
        error_text = self._signup_error()
        landed_on_account_info = self._is_account_info()

        # HTML5 block = не было навигации и есть validation message
        html5_block = (not navigated) and bool(validation_message)

        return SignupOutcome(
            html5_block=html5_block,
            validation_message=validation_message,
            error_text=error_text,
            navigated=navigated,
            landed_on_account_info=landed_on_account_info,
        )