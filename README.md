# QA Automation CLI Tool

Production-style QA Automation framework built with Python + Selenium + Pytest.

Runs UI scenarios via CLI (login/logout/register), supports smoke/full modes, uses Page Object Model, and generates run artifacts (checklists, bug drafts, screenshots, HTML page sources).

---

## Features

- CLI runner: qa-cli list, qa-cli run
- Smoke / Full modes
- Page Object Model (POM)
- Data-driven negative scenarios
- Artifacts per run (artifacts/<timestamp>/):
  - checklist_<scenario>.md
  - bug_<scenario>.md
  - screenshot_case_XXX.png
  - page_source_case_XXX.html
- Optional AI bug report enhancement (OpenAI API)

---

## Architecture

- cli.py — CLI entry point  
- runner.py — prepares run config and invokes pytest  
- scenarios/ — business test logic  
- pages/ — Page Object Model layer  
- data/ — test data generators  
- tests/test_engine.py — executes selected scenario  

Execution flow:

CLI → Runner → Pytest → Scenario → Page Objects → Artifacts

---

## Installation

python -m venv .venv

Windows:
.venv\Scripts\activate

pip install -e .

---

## Run

List scenarios:

qa-cli list

Interactive run:

qa-cli run

Modes:

smoke — fast sanity checks  
full — extended data-driven execution  

---

## Example Artifacts

Artifacts are saved to:

artifacts/<timestamp>/

Example structure:

artifacts/2026-03-03_15-32-43/
  checklist_register_negative.md
  bug_register_negative.md
  screenshot_case_003.png
  page_source_case_003.html

---

## Tech Stack

- Python 3.12
- Selenium
- Pytest
- Page Object Model
- Data-driven testing

---

## Optional OpenAI Integration

Set environment variable:

OPENAI_API_KEY=your_key_here

If the key is missing or quota is exceeded, AI enhancement is safely skipped.

---

## Author

Daniil — Junior QA Automation Engineer