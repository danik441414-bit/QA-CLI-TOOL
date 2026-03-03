from __future__ import annotations

from dataclasses import dataclass
from typing import List
import random
import string


@dataclass(frozen=True)
class RegisterCase:
    case_name: str
    name: str
    email: str
    expect: str  # "exists" | "html5_block" | "unsupported_ok"


def _rand_local(rng: random.Random, n: int) -> str:
    chars = string.ascii_lowercase + string.digits
    return "".join(rng.choice(chars) for _ in range(n))


def _rand_domain(rng: random.Random) -> str:
    domains = ["example.com", "mail.com", "test.org", "site.net", "demo.io"]
    return rng.choice(domains)


def get_register_negative_cases(mode: str, seed: int) -> List[RegisterCase]:
    """
    smoke: 7-10 кейсов
    full: 120+ кейсов (детерминировано от seed)
    """
    mode = (mode or "smoke").strip().lower()
    rng = random.Random(seed)

    valid_name = "UserTest"
    exists_email = "someone@example.com"  # специально существующий на AE (как у тебя в логах)

    smoke = [
        RegisterCase("exists_1", valid_name, exists_email, "exists"),
        RegisterCase("no_at", valid_name, "no-at-symbol", "html5_block"),
        RegisterCase("user_at", valid_name, "user@", "html5_block"),
        RegisterCase("at_domain", valid_name, "@domain.com", "html5_block"),
        RegisterCase("no_tld", valid_name, "user@domain", "html5_block"),
        RegisterCase("space", valid_name, "user domain.com", "html5_block"),
        RegisterCase("double_dot", valid_name, "user@domain..com", "html5_block"),
        RegisterCase("empty", valid_name, "", "html5_block"),
        RegisterCase("leading_space", valid_name, " user@example.com", "html5_block"),
        RegisterCase("trailing_space", valid_name, "user@example.com ", "html5_block"),
    ]

    if mode == "smoke":
        return smoke

    
    generated: List[RegisterCase] = []

    # 30 раз "exists" (должно стабильно давать already exist)
    for i in range(2, 32):
        generated.append(RegisterCase(f"exists_{i}", valid_name, exists_email, "exists"))

    # 90 рандомных "битых" емейлов
    for i in range(1, 91):
        local = _rand_local(rng, rng.randint(1, 12))
        dom = _rand_domain(rng)

        kind = rng.choice(
            [
                "missing_at",
                "missing_local",
                "missing_domain",
                "bad_chars",
                "two_ats",
                "newline",
                "tab",
                "comma",
                "no_dot_in_domain",
                "trailing_dot",
            ]
        )

        if kind == "missing_at":
            email = f"{local}{dom}"
            expect = "html5_block"
        elif kind == "missing_local":
            email = f"@{dom}"
            expect = "html5_block"
        elif kind == "missing_domain":
            email = f"{local}@"
            expect = "html5_block"
        elif kind == "bad_chars":
            email = f"{local}@do main.com"
            expect = "html5_block"
        elif kind == "two_ats":
            email = f"{local}@@{dom}"
            expect = "html5_block"
        elif kind == "newline":
            email = f"{local}@{dom}\n"
            expect = "unsupported_ok"
        elif kind == "tab":
            email = f"{local}@{dom}\t"
            expect = "unsupported_ok"
        elif kind == "comma":
            email = f"{local},@{dom}"
            expect = "html5_block"
        elif kind == "no_dot_in_domain":
            email = f"{local}@domain"
            expect = "html5_block"
        elif kind == "trailing_dot":
            email = f"{local}@{dom}."
            expect = "unsupported_ok"
        else:
            email = f"{local}@{dom}"
            expect = "unsupported_ok"

        generated.append(RegisterCase(f"rand_invalid_{i:03d}", valid_name, email, expect))

    return smoke + generated