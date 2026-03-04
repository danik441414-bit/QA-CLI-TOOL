from __future__ import annotations

from pathlib import Path

from selenium.common.exceptions import InvalidSessionIdException, WebDriverException

from qa_cli.scenarios.registry import scenario
from qa_cli.data.password_cases import get_password_cases
from qa_cli.pages.page_factory import make_login_page
from qa_cli.sites.profiles import pick_profile


def _is_non_bmp(s: str) -> bool:
    
    return any(ord(ch) > 0xFFFF for ch in s)


def _is_risky_password(pwd: str, max_len: int = 256) -> str | None:
    
    if pwd is None:
        return "pwd is None"
    if len(pwd) > max_len:
        return f"too long (len={len(pwd)} > {max_len})"
    if "\x00" in pwd:
        return "contains NULL byte \\x00"
    return None


def _save_debug(driver, artifacts_dir: Path, case_idx: int):
    screenshot = artifacts_dir / f"screenshot_case_{case_idx:03d}.png"
    html = artifacts_dir / f"page_source_case_{case_idx:03d}.html"

    try:
        driver.save_screenshot(str(screenshot))
    except Exception:
        screenshot = None

    try:
        html.write_text(driver.page_source, encoding="utf-8")
    except Exception:
        html = None

    return (str(screenshot) if screenshot else None, str(html) if html else None)


def _write_checklist(path: Path, base_url: str, mode: str, seed: int, results: list[dict]):
    lines = []
    lines.append("# Checklist: login_negative")
    lines.append("")
    lines.append(f"- Base URL input: {base_url}")
    lines.append(f"- Mode: {mode}")
    lines.append(f"- Seed: {seed}")
    lines.append(f"- Total cases: {len(results)}")
    lines.append("")
    lines.append("## Results")
    lines.append("")

    for r in results:
        status = r["status"]
        mark = "[x]" if status == "PASSED" else ("[-]" if status == "SKIPPED" else "[ ]")
        extra = ""
        if r.get("exception"):
            extra = f" | EXCEPTION={r['exception']}"
        elif r.get("error") is not None:
            extra = f" | error={r['error']}"
        if r.get("skip_reason"):
            extra += f" | skip_reason={r['skip_reason']}"

        ss = f" | screenshot={r['screenshot']}" if r.get("screenshot") else ""
        html = f" | html={r['html']}" if r.get("html") else ""

        lines.append(
            f"{mark} CASE {r['index']:03d} — {r['name']} | status={status} | pwd_len={r['password_len']} | pwd={r['password_preview']}{extra}{ss}{html}"
        )

    path.write_text("\n".join(lines), encoding="utf-8")


@scenario(id="login_negative", title="Login negative (data-driven)", tags=["auth", "full"])
def login_negative(ctx):
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

        error_text = None
        exception_text = None
        status = "FAILED"
        screenshot = None
        html = None
        skip_reason = None

        try:
            
            if _is_non_bmp(pwd):
                status = "SKIPPED"
                skip_reason = "non-BMP chars (emoji). ChromeDriver may fail send_keys."
            else:
                
                risky = _is_risky_password(pwd, max_len=256)
                if risky:
                    status = "SKIPPED"
                    skip_reason = risky
                else:
                    page.open()

                    if type(page).__name__ == "LoginPage":
                        
                        page.login(email="someone@example.com", password=pwd)
                        error_text = page.get_error_text()

                        
                        status = "PASSED" if (error_text and error_text.strip()) or page.is_on_login() else "FAILED"

                    else:
                        
                        page.login(username="wrong_user", password=pwd)
                        error_text = page.get_flash_text()
                        status = "PASSED" if (error_text and error_text.strip()) else "FAILED"

        except InvalidSessionIdException as e:
            exception_text = f"{type(e).__name__}: {e}"
            status = "FAILED"
            print(f"[CASE {i:03d}] FATAL: driver session died. Stop further cases.")
            results.append(
                {
                    "index": i,
                    "name": name,
                    "password_len": len(pwd),
                    "password_preview": repr(pwd[:30]) + ("..." if len(pwd) > 30 else ""),
                    "status": status,
                    "error": error_text,
                    "exception": exception_text,
                    "skip_reason": skip_reason,
                    "screenshot": None,
                    "html": None,
                }
            )
            break

        except WebDriverException as e:
            exception_text = f"{type(e).__name__}: {e}"
            status = "FAILED"
            try:
                screenshot, html = _save_debug(driver, artifacts_dir, i)
            except Exception:
                screenshot, html = None, None

        except Exception as e:
            exception_text = f"{type(e).__name__}: {e}"
            status = "FAILED"
            try:
                screenshot, html = _save_debug(driver, artifacts_dir, i)
            except Exception:
                screenshot, html = None, None

        if status == "FAILED" and screenshot is None and html is None:
            try:
                screenshot, html = _save_debug(driver, artifacts_dir, i)
            except Exception:
                pass

        results.append(
            {
                "index": i,
                "name": name,
                "password_len": len(pwd),
                "password_preview": repr(pwd[:30]) + ("..." if len(pwd) > 30 else ""),
                "status": status,
                "error": error_text,
                "exception": exception_text,
                "skip_reason": skip_reason,
                "screenshot": screenshot,
                "html": html,
            }
        )

        if exception_text:
            print(f"[CASE {i:03d}] exception: {exception_text}")
        if skip_reason:
            print(f"[CASE {i:03d}] SKIP reason: {skip_reason}")
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

    profile = pick_profile(base_url)
    page = make_login_page(driver, base_url)
    page.open()

    if type(page).__name__ == "HerokuLoginPage":
        page.login(username="tomsmith", password="SuperSecretPassword!")
        assert page.is_logout_visible(), "Logout button not visible after login (Heroku)"
        return None

    
    assert profile.email and profile.password, "Missing fixed creds in qa_cli/sites/profiles.py (AUTOMATION_EXERCISE)"
    page.login(email=profile.email, password=profile.password)
    assert page.is_logged_in(), "Not logged in (AutomationExercise)"
    return None