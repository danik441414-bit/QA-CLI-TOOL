from __future__ import annotations

import qa_cli.scenarios  # noqa: F401  (важно: регистрация сценариев)
from qa_cli.scenarios.registry import REGISTRY


def test_engine(ctx):
    scenario_id = ctx["scenario_id"]
    assert scenario_id, "scenario_id is empty. Runner must pass --scenario-id"

    meta, fn = REGISTRY.get(scenario_id)
    print(f"[ENGINE] Running scenario: {meta.id} — {meta.title} | tags={meta.tags}")

    fn(ctx)