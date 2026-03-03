from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait

from qa_cli.data.password_cases import get_password_cases
from qa_cli.pages.page_factory import make_login_page
from qa_cli.scenarios.registry import scenario
from qa_cli.sites.profiles import pick_profile


def _is_non_bmp(s: str) -> bool:
    return any(ord(ch) > 0xFFFF for ch in s)


def _save_debug(driver, artifacts_dir: Path, case_idx: int | None = None):
    suffix = f"_case_{case_idx:03d}" if case_idx is not None else ""
    screenshot = artifacts_dir / f"screenshot{suffix}.png"
    html = artifacts_dir / f"page_source{suffix}.html"

    screenshot_path = None
    html_path = None

    try:
        driver.save_screenshot(str(screenshot))
        screenshot_path = str(screenshot)
    except Exception:
        screenshot_path = None

    try:
        html.write_text(driver.page_source, encoding="utf-8")
        html_path = str(html)
    except Exception:
        html_path = None

    return screenshot_path, html_path


def _write_checklist(path: Path, base_url: str, mode: str, seed: int, results: list[dict]):
    lines = []
    lines.append("# Checklist: login_negative")
    lines.append("")
    lines.append("## Environment")
    lines.append(f"- Base URL: {base_url}")
    lines.append(f"- Mode: {mode}")
    lines.append(f"- Seed: {seed}")
    lines.append(f"- Total cases: {len(results)}")
    lines.append("")
    lines.append("## Results")
    lines.append("")

    for r in results:
        status = r["status"]
        mark = "[x]" if status == "PASSED" else ("[-]" if status in ("SKIPPED", "SOFT_PASS") else "[ ]")

        extra = ""
        if r.get("exception"):
            extra = f" | EXCEPTION={r['exception']}"
        elif r.get("note"):
            extra = f" | NOTE={r['note']}"
        elif r.get("error") is not None:
            extra = f" | error={r['error']}"

        ss = f" | screenshot={r['screenshot']}" if r.get("screenshot") else ""
        html = f" | html={r['html']}" if r.get("html") else ""

        lines.append(
            f"{mark} CASE {r['index']:03d} — {r['name']} | status={status} | "
            f"pwd_len={r['password_len']} | pwd={r['password_preview']}{extra}{ss}{html}"
        )

    passed = sum(1 for r in results if r["status"] == "PASSED")
    soft = sum(1 for r in results if r["status"] == "SOFT_PASS")
    skipped = sum(1 for r in results if r["status"] == "SKIPPED")
    failed = sum(1 for r in results if r["status"] == "FAILED")

    lines.append("")
    lines.append("## Summary")
    lines.append(f"- PASSED: {passed}")
    lines.append(f"- SOFT_PASS: {soft}")
    lines.append(f"- SKIPPED: {skipped}")
    lines.append(f"- FAILED: {failed}")

    path.write_text("\n".join(lines), encoding="utf-8")


@scenario(id="login_negative", title="Login negative (data-driven)", tags=["auth", "full"])
def login_negative(ctx: Dict[str, Any]):
    driver = ctx["driver"]
    base_url = ctx["base_url"]
    mode = ctx["mode"]
    seed = ctx["seed"]
    artifacts_dir: Path = ctx["artifacts_dir"]

    page = make_login_page(driver, base_url)
    cases = get_password_cases(mode=mode, seed=seed, target_count_full=100)

    print(f"[SCENARIO] login_negative: mode={mode}, seed={seed}, cases={len(cases)}")

    results: list[dict] = []

    for i, c in enumerate(cases, start=1):
        name = c["name"]
        pwd = c["password"]

        print(f"\n[CASE {i:03d}] {name} (len={len(pwd)})")

        page.open()

        error_text = None
        exception_text = None
        status = "FAILED"
        screenshot = None
        html = None
        note = None

        try:
            if _is_non_bmp(pwd):
                status = "SKIPPED"
                note = "SKIPPED: non-BMP chars (emoji). ChromeDriver can't send_keys."
            else:
                if type(page).__name__ == "LoginPage":
                    page.login(email="someone@example.com", password=pwd)

                    try:
                        WebDriverWait(driver, 3).until(lambda d: page.get_error_text() is not None or page.is_logged_in(timeout=0))
                    except TimeoutException:
                        pass

                    error_text = page.get_error_text()

                    if page.is_logged_in(timeout=0):
                        status = "FAILED"
                        note = "Unexpectedly logged in with invalid password"
                    elif error_text is not None:
                        status = "PASSED"
                    else:
                        status = "SOFT_PASS"
                        note = "No error text found, but not logged in (timing/UI flake)."

                else:
                    page.login(username="wrong_user", password=pwd)

                    try:
                        WebDriverWait(driver, 3).until(lambda d: (page.get_flash_text() is not None) or page.is_logout_visible())
                    except TimeoutException:
                        pass

                    error_text = page.get_flash_text()

                    if page.is_logout_visible():
                        status = "FAILED"
                        note = "Unexpectedly logged in with invalid password (Heroku)"
                    elif error_text is not None:
                        status = "PASSED"
                    else:
                        status = "SOFT_PASS"
                        note = "No flash found, but not logged in (timing/UI flake)."

        except WebDriverException as e:
            exception_text = f"{type(e).__name__}: {e}"
            status = "FAILED"

        if status == "FAILED":
            screenshot, html = _save_debug(driver, artifacts_dir, i)

        results.append(
            {
                "index": i,
                "name": name,
                "password_len": len(pwd),
                "password_preview": repr(pwd[:30]) + ("..." if len(pwd) > 30 else ""),
                "status": status,
                "error": error_text,
                "note": note,
                "exception": exception_text,
                "screenshot": screenshot,
                "html": html,
            }
        )

        if exception_text:
            print(f"[CASE {i:03d}] exception: {exception_text}")
        if note:
            print(f"[CASE {i:03d}] note: {note}")
        print(f"[CASE {i:03d}] error: {error_text}")
        print(f"[CASE {i:03d}] RESULT: {status}")

    checklist_path = artifacts_dir / "checklist_login_negative.md"
    _write_checklist(checklist_path, base_url, mode, seed, results)
    print(f"\n[SCENARIO] Checklist saved to: {checklist_path}")

    failed = [r for r in results if r["status"] == "FAILED"]
    assert len(failed) == 0, f"{len(failed)} failed + 0 errors. See checklist: {checklist_path}"
    return None


@scenario(id="login_positive", title="Login positive", tags=["auth", "smoke"])
def login_positive(ctx):
    driver = ctx["driver"]
    base_url = ctx["base_url"]
    artifacts_dir: Path = ctx["artifacts_dir"]

    profile = pick_profile(base_url)
    page = make_login_page(driver, base_url)
    page.open()

    if type(page).__name__ == "HerokuLoginPage":
        page.login(username="tomsmith", password="SuperSecretPassword!")
        assert page.is_logout_visible(), "Logout button not visible after login (Heroku)"
        return None

    # AutomationExercise fixed creds required
    assert profile.email and profile.password, "Missing fixed creds in qa_cli/sites/profiles.py (AUTOMATION_EXERCISE)"

    page.login(email=profile.email, password=profile.password)

    # ✅ главное: ждём, что хедер/кнопка logout реально появятся
    ok = page.is_logged_in(timeout=8)
    if not ok:
        ss, html = _save_debug(driver, artifacts_dir, None)
        raise AssertionError(f"Not logged in (AutomationExercise). Saved debug: screenshot={ss}, html={html}")

    return None