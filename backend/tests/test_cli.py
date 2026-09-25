from __future__ import annotations

from types import SimpleNamespace

from typer.testing import CliRunner

from cabosueltos import cli
from cabosueltos.db.migrate import ChecksumMismatchError

runner = CliRunner()


def _dummy_settings() -> SimpleNamespace:
    return SimpleNamespace(database_url="postgresql://unused/for-this-test")


def test_db_migrate_echoes_each_applied_version(monkeypatch) -> None:
    monkeypatch.setattr(cli, "load_settings", _dummy_settings)
    monkeypatch.setattr(cli, "run_migrate", lambda database_url: ["0001", "0002"])

    result = runner.invoke(cli.app, ["db", "migrate"])

    assert result.exit_code == 0
    assert "applied 0001" in result.output
    assert "applied 0002" in result.output


def test_db_migrate_prints_nothing_when_none_pending(monkeypatch) -> None:
    monkeypatch.setattr(cli, "load_settings", _dummy_settings)
    monkeypatch.setattr(cli, "run_migrate", lambda database_url: [])

    result = runner.invoke(cli.app, ["db", "migrate"])

    assert result.exit_code == 0
    assert result.output == ""


def test_db_migrate_checksum_mismatch_exits_1_naming_version(monkeypatch) -> None:
    monkeypatch.setattr(cli, "load_settings", _dummy_settings)

    def _raise(database_url: str) -> list[str]:
        raise ChecksumMismatchError("0003")

    monkeypatch.setattr(cli, "run_migrate", _raise)

    result = runner.invoke(cli.app, ["db", "migrate"])

    assert result.exit_code == 1
    assert "migration 0003 has changed since it was applied" in result.output


def test_db_status_echoes_version_and_state(monkeypatch) -> None:
    monkeypatch.setattr(cli, "load_settings", _dummy_settings)
    monkeypatch.setattr(
        cli, "run_status", lambda database_url: [("0001", "applied"), ("0002", "pending")]
    )

    result = runner.invoke(cli.app, ["db", "status"])

    assert result.exit_code == 0
    assert "0001 applied" in result.output
    assert "0002 pending" in result.output
