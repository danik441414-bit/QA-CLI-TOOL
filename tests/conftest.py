from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def pytest_addoption(parser):
    parser.addoption("--scenario-id", action="store", default="", help="Scenario id to run (from REGISTRY)")
    parser.addoption("--base-url", action="store", default="https://automationexercise.com", help="Base URL")
    parser.addoption("--mode", action="store", default="smoke", help="Run mode: smoke/full")
    parser.addoption("--seed", action="store", default="123", help="Seed for deterministic data")
    parser.addoption("--artifacts-dir", action="store", default="", help="Artifacts output directory")
    parser.addoption("--headless", action="store_true", default=False, help="Run Chrome headless")


@pytest.fixture()
def ctx(request) -> Dict[str, Any]:
    scenario_id = request.config.getoption("--scenario-id")
    base_url = request.config.getoption("--base-url")
    mode = request.config.getoption("--mode")
    seed = int(request.config.getoption("--seed"))

    artifacts_dir_raw = request.config.getoption("--artifacts-dir")
    artifacts_dir = Path(artifacts_dir_raw) if artifacts_dir_raw else Path("artifacts") / "debug"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    headless = bool(request.config.getoption("--headless"))

    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")

    chrome_options.add_argument("--window-size=1400,900")

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)

    data = {
        "scenario_id": scenario_id,
        "base_url": base_url,
        "mode": mode,
        "seed": seed,
        "artifacts_dir": artifacts_dir,
        "driver": driver,
    }

    yield data

    try:
        driver.quit()
    except Exception:
        pass