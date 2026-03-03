
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class SiteProfile:
    name: str
    default_base_url: str
    
    email: str | None = None
    password: str | None = None


AUTOMATION_EXERCISE = SiteProfile(
    name="automation_exercise",
    default_base_url="https://automationexercise.com",
    
    email="test2026@test.com",
    password="test2026",
)

HEROKU = SiteProfile(
    name="heroku",
    default_base_url="https://the-internet.herokuapp.com",
    email=None,
    password=None,
)

DEFAULT_SITE: SiteProfile = AUTOMATION_EXERCISE


def pick_profile(base_url: str) -> SiteProfile:
    host = urlparse(base_url).netloc.lower()
    if "the-internet.herokuapp.com" in host:
        return HEROKU
    return AUTOMATION_EXERCISE