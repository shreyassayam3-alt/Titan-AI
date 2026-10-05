from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: str | Path | None = None) -> dict[str, str]:
    env_path = Path(path or Path(__file__).resolve().parents[2] / ".env")
    values: dict[str, str] = {}
    if not env_path.exists():
        return values
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        values[key.strip()] = value
        os.environ.setdefault(key.strip(), value)
    return values


def get_env_value(key: str) -> str | None:
    load_dotenv()
    return os.getenv(key)
