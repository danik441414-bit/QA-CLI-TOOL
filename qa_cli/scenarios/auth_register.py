from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from selenium.common.exceptions import WebDriverException

from qa_cli.data.registration_cases import RegisterCase, get_register_negative_cases
from qa_cli.pages.register_page import RegisterPage
from qa_cli.scenarios.registry import scenario


def _save_debug(driver, artifacts_dir: Path, case_idx: int):
    screenshot = artifacts_dir / f"screenshot_case_{case_idx:03d}.png"
    html = artifacts_dir / f"page_source_case_{case_idx:03d}.html"

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


def _write_checklist(path: Path, base_url: str, mode: str, seed: int, results: List[Dict[str, Any]]) -> None:
    lines: List[str] = []
    lines.append("# Checklist: register_negative")
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
        mark = "[x]" if status == "PASSED" else ("[-]" if status == "SKIPPED" else "[ ]")
        ss = f" | screenshot={r['screenshot']}" if r.get("screenshot") else ""
        html = f" | html={r['html']}" if r.get("html") else ""
        details = r.get("details", "")
        lines.append(
            f"{mark} CASE {r['index']:03d} — {r['case_name']} | status={status} | expect={r['expect']} | "
            f"name={r['name']!r} | email={r['email']!r}"
            f"{(' | ' + details) if details else ''}{ss}{html}"
        )

    path.write_text("\n".join(lines), encoding="utf-8")


def _write_bug_draft(path: Path, base_url: str, mode: str, seed: int, failed: List[Dict[str, Any]]) -> None:
    lines: List[str] = []
    lines.append("# Bug draft: register_negative")
    lines.append("")
    lines.append("## Environment")
    lines.append(f"- Base URL: {base_url}")
    lines.append(f"- Mode: {mode}")
    lines.append(f"- Seed: {seed}")
    lines.append("")
    lines.append("## Failed cases")
    lines.append("")

    if not failed:
        lines.append("- (none)")
    else:
        for r in failed:
            lines.append(f"### CASE {r['index']:03d} — {r['case_name']}")
            lines.append(f"- expect: {r['expect']}")
            lines.append(f"- name: {r['name']!r}")
            lines.append(f"- email: {r['email']!r}")
            if r.get("details"):
                lines.append(f"- details: {r['details']}")
            if r.get("screenshot"):
                lines.append(f"- screenshot: {r['screenshot']}")
            if r.get("html"):
                lines.append(f"- html: {r['html']}")
            lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


@scenario(id="register_positive", title="Register positive (opens account info)", tags=["auth", "smoke"])
def register_positive(ctx: Dict[str, Any]) -> None:
    driver = ctx["driver"]
    base_url: str = ctx["base_url"]
    seed: int = int(ctx["seed"])

    page = RegisterPage(driver, base_url)
    page.open()

    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    email = f"user{seed}_{ts}@example.com"

    out = page.submit_signup(name="UserTest", email=email)

    assert out.landed_on_account_info, (
        f"Expected Account Info page, got: navigated={out.navigated}, "
        f"html5='{out.validation_message}', error='{out.error_text}'"
    )


@scenario(id="register_negative", title="Register negative (data-driven)", tags=["auth", "full"])
def register_negative(ctx: Dict[str, Any]) -> None:
    driver = ctx["driver"]
    base_url: str = ctx["base_url"]
    mode: str = ctx["mode"]
    seed: int = int(ctx["seed"])
    artifacts_dir: Path = ctx["artifacts_dir"]

    page = RegisterPage(driver, base_url)
    cases: List[RegisterCase] = get_register_negative_cases(mode=mode, seed=seed)

    print(f"[SCENARIO] register_negative: mode={mode}, seed={seed}, cases={len(cases)}")

    results: List[Dict[str, Any]] = []

    for i, c in enumerate(cases, start=1):
        status = "FAILED"
        details: List[str] = []
        screenshot = None
        html = None

        try:
            page.open()
            out = page.submit_signup(name=c.name, email=c.email)

            if c.expect == "exists":
                if "already exist" in (out.error_text or "").lower():
                    status = "PASSED"
                    details.append(f"error={out.error_text}")
                else:
                    status = "FAILED"
                    details.append(f"error={out.error_text or 'NO_ERROR_TEXT'}")
                    if out.validation_message:
                        details.append(f"html5={out.validation_message}")
                    if out.landed_on_account_info:
                        details.append("navigated=account_info")

            elif c.expect == "html5_block":
                if out.html5_block:
                    status = "PASSED"
                    details.append(f"html5={out.validation_message}")
                elif out.error_text:
                    status = "PASSED"
                    details.append(f"error={out.error_text}")
                else:
                    status = "FAILED"
                    details.append("Expected html5 or error, got nothing")
                    if out.landed_on_account_info:
                        details.append("navigated=account_info")

            elif c.expect == "unsupported_ok":
                status = "PASSED"
                if out.validation_message:
                    details.append(f"html5={out.validation_message}")
                if out.error_text:
                    details.append(f"error={out.error_text}")
                if out.landed_on_account_info:
                    details.append("note=navigated_bypassed_validation")

            else:
                status = "FAILED"
                details.append(f"unknown expect={c.expect}")

        except WebDriverException as e:
            status = "FAILED"
            details.append(f"exception={type(e).__name__}: {e}")

        if status == "FAILED":
            screenshot, html = _save_debug(driver, artifacts_dir, i)

        results.append(
            {
                "index": i,
                "case_name": c.case_name,
                "name": c.name,
                "email": c.email,
                "expect": c.expect,
                "status": status,
                "details": " | ".join(details),
                "screenshot": screenshot,
                "html": html,
            }
        )

        print(f"[CASE {i:03d}] {c.case_name} => {status}")

    checklist_path = artifacts_dir / "checklist_register_negative.md"
    _write_checklist(checklist_path, base_url, mode, seed, results)
    print(f"[SCENARIO] Checklist saved to: {checklist_path}")

    failed = [r for r in results if r["status"] == "FAILED"]
    bug_path = artifacts_dir / "bug_register_negative.md"
    _write_bug_draft(bug_path, base_url, mode, seed, failed)
    print(f"[SCENARIO] Bug draft saved to: {bug_path}")

    assert len(failed) == 0, f"{len(failed)} failed. See checklist: {checklist_path}"