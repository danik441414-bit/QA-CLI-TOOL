from __future__ import annotations

# Важно: эти импорты выполняют регистрацию сценариев через декоратор @scenario
from . import auth_login  # noqa: F401
from . import auth_logout  # noqa: F401
from . import auth_register  # noqa: F401