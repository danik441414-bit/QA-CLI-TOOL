from __future__ import annotations

import random


def _random_ascii(rng: random.Random, length: int) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=,.<>/?;:'\"\\|[]{}"
    return "".join(rng.choice(alphabet) for _ in range(length))


def get_password_cases(mode: str, seed: int, target_count_full: int = 100):
    rng = random.Random(seed)

    base = [
        {"name": "empty", "password": ""},
        {"name": "one space", "password": " "},
        {"name": "many spaces", "password": "     "},
        {"name": "tab", "password": "\t"},
        {"name": "newline", "password": "\n"},
        {"name": "1 char", "password": "a"},
        {"name": "7 chars", "password": "aaaaaaa"},
        {"name": "8 chars", "password": "aaaaaaaa"},
        {"name": "16 chars", "password": "a" * 16},
        {"name": "63 chars", "password": "a" * 63},
        {"name": "64 chars", "password": "a" * 64},
        {"name": "65 chars", "password": "a" * 65},
        {"name": "128 chars", "password": "a" * 128},
        {"name": "256 chars", "password": "a" * 256},
        {"name": "1000 chars", "password": "a" * 1000},
        {"name": "digits only", "password": "12345678"},
        {"name": "lower only", "password": "abcdefgh"},
        {"name": "upper only", "password": "ABCDEFGH"},
        {"name": "mixed case", "password": "AbCdEfGh"},
        {"name": "specials only", "password": "!@#$%^&*("},
        {"name": "mixed + specials", "password": "Abc!234?"},
        {"name": "quotes & slashes", "password": "\"'\\//"},
        {"name": "sql-ish", "password": "' OR 1=1"},
        {"name": "html-ish", "password": "<script>alert(1)</script>"},
        {"name": "cyrillic", "password": "парольтестовый"},
        # emoji остаётся — но мы будем SKIP на уровне сценария, чтобы не ломать прогон
        {"name": "emoji", "password": "pass🙂🙂🙂"},
    ]

    if mode == "smoke":
        return base[:10]

    # full: добиваем рандомами
    out = list(base)
    i = 1
    while len(out) < target_count_full:
        length = rng.choice([1, 2, 3, 8, 15, 16, 31, 32, 33, 63, 64, 65, 127, 128, 129, 255, 256, 257])
        out.append({"name": f"random_{i}_len_{length}", "password": _random_ascii(rng, length)})
        i += 1
    return out