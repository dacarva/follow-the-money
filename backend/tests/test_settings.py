from __future__ import annotations

import pytest

from cabosueltos.settings import Settings, load_settings


def test_missing_database_url_exits_naming_the_var(monkeypatch, capsys) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("APP_ENV", "local")

    with pytest.raises(SystemExit) as exc_info:
        load_settings(_env_file=None)

    assert exc_info.value.code == 1
    assert "DATABASE_URL" in capsys.readouterr().err


def test_invalid_app_env_exits_naming_the_var(monkeypatch, capsys) -> None:
    monkeypatch.setenv("APP_ENV", "not-a-real-env")
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/x")

    with pytest.raises(SystemExit) as exc_info:
        load_settings(_env_file=None)

    assert exc_info.value.code == 1
    assert "APP_ENV" in capsys.readouterr().err


def test_pool_url_falls_back_to_database_url(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_POOL_URL", raising=False)
    settings = Settings(
        _env_file=None,
        app_env="local",
        database_url="postgresql://localhost/x",
    )
    assert settings.pool_url == "postgresql://localhost/x"


def test_pool_url_uses_database_pool_url_when_set() -> None:
    settings = Settings(
        _env_file=None,
        app_env="local",
        database_url="postgresql://localhost/x",
        database_pool_url="postgresql://localhost/pooled",
    )
    assert settings.pool_url == "postgresql://localhost/pooled"
