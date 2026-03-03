from __future__ import annotations

from urllib.parse import urlparse

from qa_cli.pages.heroku_login_page import HerokuLoginPage
from qa_cli.pages.login_page import LoginPage


def make_login_page(driver, base_url: str):
    url = base_url.rstrip("/")
    host = urlparse(url).netloc.lower()

    if "the-internet.herokuapp.com" in host:
        return HerokuLoginPage(driver, url)

    return LoginPage(driver, url)