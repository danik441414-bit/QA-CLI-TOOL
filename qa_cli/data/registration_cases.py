from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from random import Random
from typing import List


@dataclass(frozen=True)
class RegisterCase:
    case_name: str
    name: str
    email: str
    expect: str
    


def _unique_email(rng: Random) -> str:
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    n = rng.randint(1000, 9999)
    return f"user_{ts}_{n}@example.com"


def get_register_negative_cases(mode: str, seed: int) -> List[RegisterCase]:
    rng = Random(seed)

    
    smoke: List[RegisterCase] = [
        RegisterCase("empty_email", "User", "", "html5_block"),
        RegisterCase("spaces_email", "User", "   ", "html5_block"),
        RegisterCase("no_at", "User", "user.example.com", "html5_block"),
        RegisterCase("no_domain", "User", "user@", "html5_block"),
        RegisterCase("no_user", "User", "@example.com", "html5_block"),
        RegisterCase("double_at", "User", "a@@example.com", "html5_block"),
        RegisterCase("space_inside", "User", "u ser@example.com", "html5_block"),
        
        RegisterCase("known_existing_email", "User", "test@example.com", "unsupported_ok"),
    ]

    if mode == "smoke":
        return smoke

    
    full: List[RegisterCase] = []

    invalid_emails = [
        "plainaddress",
        "missingatsign.com",
        "missingdomain@",
        "@missinguser.com",
        "user@.com",
        "user@com",
        "user@domain..com",
        "user@domain,com",
        "user@domain com",
        "user@domain#com",
        "user@@domain.com",
        " user@domain.com",
        "user@domain.com ",
        "user@domain..",
        "user@-domain.com",
        "user@domain-.com",
    ]
    for i, e in enumerate(invalid_emails, start=1):
        full.append(RegisterCase(f"invalid_email_{i:02d}", "User", e, "html5_block"))

    
    full.extend(
        [
            RegisterCase("empty_name", "", _unique_email(rng), "unsupported_ok"),
            RegisterCase("spaces_name", "   ", _unique_email(rng), "unsupported_ok"),
            RegisterCase("one_letter_name", "A", _unique_email(rng), "unsupported_ok"),
            RegisterCase("name_with_dash", "Jean-Luc", _unique_email(rng), "unsupported_ok"),
            RegisterCase("name_with_quote", "O'Connor", _unique_email(rng), "unsupported_ok"),
            RegisterCase("cjk_name", "李雷", _unique_email(rng), "unsupported_ok"),
        ]
    )

    
    full.append(RegisterCase("existing_email_full_soft", "User", "test@example.com", "unsupported_ok"))

    return smoke + full