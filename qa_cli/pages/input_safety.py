from __future__ import annotations


class UnsupportedInputError(ValueError):
    """ChromeDriver can't type some chars (e.g., non-BMP emoji) via send_keys()."""


def contains_non_bmp(s: str) -> bool:
    
    return any(ord(ch) > 0xFFFF for ch in s)