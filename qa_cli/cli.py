from __future__ import annotations

import argparse

import qa_cli.scenarios  # noqa: F401 (важно: импортирует сценарии и регистрирует их)
from qa_cli.runner import RunConfig, run as run_runner
from qa_cli.scenarios.registry import REGISTRY
from qa_cli.sites.profiles import DEFAULT_SITE


def normalize_base_url(url: str) -> str:
    """
    Нормализация base_url:
    - если ввели полный URL с путём (например .../login), оставляем только scheme+host
    - убираем trailing slash
    Примеры:
      https://the-internet.herokuapp.com/login -> https://the-internet.herokuapp.com
      https://automationexercise.com/          -> https://automationexercise.com
    """
    url = url.strip()
    if not url:
        return url

    if "://" not in url:
        
        url = "https://" + url

    
    parts = url.split("://", 1)
    scheme = parts[0]
    rest = parts[1]
    host = rest.split("/", 1)[0]
    return f"{scheme}://{host}".rstrip("/")


def interactive_run() -> int:
    items = sorted(REGISTRY.list(), key=lambda s: s.id)

    print("Choose scenario:")
    for i, s in enumerate(items, start=1):
        print(f"  {i}) {s.id} — {s.title}")

    idx = int(input("Enter number: ").strip())
    scenario_id = items[idx - 1].id

    raw_base_url = input(f"Base URL (default: {DEFAULT_SITE.default_base_url}): ").strip()
    base_url = normalize_base_url(raw_base_url) if raw_base_url else DEFAULT_SITE.default_base_url

    mode = input("Mode (smoke/full) [smoke]: ").strip() or "smoke"
    if mode not in ("smoke", "full"):
        raise SystemExit("Mode must be smoke or full")

    seed_str = input("Seed [123]: ").strip() or "123"
    seed = int(seed_str)

    return run_runner(RunConfig(scenario_id=scenario_id, base_url=base_url, mode=mode, seed=seed))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qa-cli")
    sub = parser.add_subparsers()

    p_list = sub.add_parser("list", help="List available scenarios")
    p_list.set_defaults(
        fn=lambda _args: print("\n".join([f"{s.id}: {s.title} [{', '.join(s.tags)}]" for s in REGISTRY.list()]))
    )

    p_run = sub.add_parser("run", help="Interactive run")
    p_run.set_defaults(fn=lambda _args: interactive_run())

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not hasattr(args, "fn"):
        parser.print_help()
        return 0

    result = args.fn(args)
    if result is None:
        return 0
    return int(result)


if __name__ == "__main__":
    raise SystemExit(main())