from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pytest

from qa_cli.ai.openai_bug_enhancer import enhance_bug_report


@dataclass(frozen=True)
class RunConfig:
    scenario_id: str
    base_url: str
    mode: str = "smoke"
    seed: int = 123


def run(cfg: RunConfig) -> int:
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    artifacts_dir = Path("artifacts") / ts
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    print(f"[RUNNER] Prepared run at: {artifacts_dir}")

    args = [
        "-q",
        "-s",
        "--disable-warnings",
        f"--scenario-id={cfg.scenario_id}",
        f"--base-url={cfg.base_url}",
        f"--mode={cfg.mode}",
        f"--seed={cfg.seed}",
        f"--artifacts-dir={artifacts_dir}",
        "tests/test_engine.py::test_engine",
    ]

    code = pytest.main(args)
    status = "PASSED" if code == 0 else "FAILED"
    print(f"[RUNNER] Finished with status: {status}")

    #  AI enhancement 
    try:
        bug_files = list(artifacts_dir.glob("bug_*.md"))
        for bug_file in bug_files:
            enhance_bug_report(bug_file)
    except Exception as e:
        print(f"[RUNNER] AI step failed (ignored): {e}")

    return int(code)