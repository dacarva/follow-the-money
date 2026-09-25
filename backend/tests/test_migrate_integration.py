from __future__ import annotations

import threading
from collections.abc import Iterator
from pathlib import Path

import psycopg
import pytest

from cabosueltos.db.migrate import ChecksumMismatchError, migrate, status


def _write_migration(directory: Path, version: str, sql: str) -> None:
    (directory / f"{version}_test.sql").write_text(sql)


@pytest.fixture
def cleanup_versions(database_url: str, pg_conn: psycopg.Connection) -> Iterator[list[str]]:
    versions: list[str] = []

    yield versions

    for version in versions:
        pg_conn.execute("DELETE FROM ftm.schema_migrations WHERE version = %s", (version,))
        pg_conn.execute(f"DROP TABLE IF EXISTS ftm.test_{version}")


def test_migrate_applies_once_then_is_idempotent(
    tmp_path: Path, database_url: str, cleanup_versions: list[str]
) -> None:
    version = "9001"
    cleanup_versions.append(version)
    _write_migration(tmp_path, version, f"CREATE TABLE ftm.test_{version} (id int);")

    first = migrate(database_url, directory=tmp_path)
    second = migrate(database_url, directory=tmp_path)

    assert first == [version]
    assert second == []


def test_migrate_checksum_mismatch_exits_naming_version(
    tmp_path: Path, database_url: str, cleanup_versions: list[str]
) -> None:
    version = "9002"
    cleanup_versions.append(version)
    _write_migration(tmp_path, version, f"CREATE TABLE ftm.test_{version} (id int);")
    migrate(database_url, directory=tmp_path)

    _write_migration(tmp_path, version, f"CREATE TABLE ftm.test_{version} (id int, extra int);")

    with pytest.raises(ChecksumMismatchError) as exc_info:
        migrate(database_url, directory=tmp_path)

    assert exc_info.value.version == version


def test_migrate_concurrent_runs_apply_once(
    tmp_path: Path, database_url: str, cleanup_versions: list[str], pg_conn: psycopg.Connection
) -> None:
    version = "9003"
    cleanup_versions.append(version)
    _write_migration(tmp_path, version, f"CREATE TABLE ftm.test_{version} (id int);")

    results: list[list[str]] = []

    def run() -> None:
        results.append(migrate(database_url, directory=tmp_path))

    threads = [threading.Thread(target=run) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    count = pg_conn.execute(
        "SELECT count(*) FROM ftm.schema_migrations WHERE version = %s", (version,)
    ).fetchone()[0]

    assert count == 1
    assert sum(len(r) for r in results) == 1


def test_migrate_failed_file_rolls_back(
    tmp_path: Path, database_url: str, pg_conn: psycopg.Connection
) -> None:
    version = "9004"
    _write_migration(tmp_path, version, "CREATE TABLE ftm.test_9004_bad (id int); SELECT 1/0;")

    with pytest.raises(Exception):  # noqa: B017
        migrate(database_url, directory=tmp_path)

    count = pg_conn.execute(
        "SELECT count(*) FROM ftm.schema_migrations WHERE version = %s", (version,)
    ).fetchone()[0]
    table_exists = pg_conn.execute(
        "SELECT to_regclass('ftm.test_9004_bad') IS NOT NULL"
    ).fetchone()[0]

    assert count == 0
    assert table_exists is False


def test_pg_trgm_extension_present(pg_conn: psycopg.Connection) -> None:
    row = pg_conn.execute("SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm'").fetchone()
    assert row is not None


def test_status_lists_applied_and_pending(
    tmp_path: Path, database_url: str, cleanup_versions: list[str]
) -> None:
    applied_version = "9005"
    pending_version = "9006"
    cleanup_versions.append(applied_version)
    cleanup_versions.append(pending_version)
    _write_migration(
        tmp_path, applied_version, f"CREATE TABLE ftm.test_{applied_version} (id int);"
    )
    migrate(database_url, directory=tmp_path)
    _write_migration(
        tmp_path, pending_version, f"CREATE TABLE ftm.test_{pending_version} (id int);"
    )

    result = status(database_url, directory=tmp_path)

    assert (applied_version, "applied") in result
    assert (pending_version, "pending") in result
