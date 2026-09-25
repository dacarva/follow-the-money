from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent

# Relative to the process cwd, which is always `backend/` for the CLI, API and tests.
DEFAULT_ENV_FILE = "../.env"

AppEnv = Literal["local", "ci", "staging", "production"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=DEFAULT_ENV_FILE, env_file_encoding="utf-8", extra="ignore"
    )

    app_env: AppEnv
    database_url: str
    database_pool_url: str | None = None
    web_dist_dir: str | None = None
    supabase_url: str | None = None
    supabase_publishable_key: str | None = None

    @property
    def pool_url(self) -> str:
        return self.database_pool_url or self.database_url

    @property
    def web_dist_path(self) -> Path:
        if self.web_dist_dir:
            return Path(self.web_dist_dir)
        return BACKEND_DIR / ".." / "apps" / "web" / "dist"


def load_settings(_env_file: str | Path | None = DEFAULT_ENV_FILE) -> Settings:
    """Load settings from the environment, exiting with a clear message on failure.

    `_env_file` is overridable so tests can bypass the repo-root `.env` file.
    """
    try:
        return Settings(_env_file=_env_file)  # type: ignore[call-arg]
    except ValidationError as exc:
        names = sorted({str(error["loc"][0]).upper() for error in exc.errors() if error["loc"]})
        detail = ", ".join(names) if names else "settings"
        print(f"Missing or invalid environment variable(s): {detail}", file=sys.stderr)
        raise SystemExit(1) from None
