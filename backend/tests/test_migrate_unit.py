from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from cabosueltos.db.migrate import (
    DuplicateMigrationVersionError,
    InvalidMigrationFilenameError,
    MigrationsDirectoryMissingError,
    discover_migrations,
)


@given(
    numbers=st.lists(st.integers(min_value=0, max_value=9999), min_size=1, max_size=8, unique=True)
)
def test_discover_migrations_orders_numerically(numbers: list[int]) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        for n in numbers:
            (directory / f"{n:04d}_change.sql").write_text("SELECT 1;")

        migrations = discover_migrations(directory)

        assert [m.version for m in migrations] == sorted(f"{n:04d}" for n in numbers)


def test_discover_migrations_checksum_is_sha256_of_file_bytes(tmp_path: Path) -> None:
    content = b"CREATE TABLE t (id int);"
    path = tmp_path / "0001_t.sql"
    path.write_bytes(content)

    migrations = discover_migrations(tmp_path)

    assert migrations[0].checksum == hashlib.sha256(content).hexdigest()


def test_discover_migrations_ignores_non_matching_files(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("not a migration")
    (tmp_path / "0001_change.sql").write_text("SELECT 1;")

    migrations = discover_migrations(tmp_path)

    assert [m.version for m in migrations] == ["0001"]


def test_discover_migrations_orders_numerically_across_digit_widths(tmp_path: Path) -> None:
    # A lexical sort would put "10_x.sql" before "2_x.sql" ("1" < "2").
    (tmp_path / "2_change.sql").write_text("SELECT 1;")
    (tmp_path / "10_change.sql").write_text("SELECT 1;")

    migrations = discover_migrations(tmp_path)

    assert [m.version for m in migrations] == ["2", "10"]


def test_discover_migrations_rejects_sql_file_with_bad_name(tmp_path: Path) -> None:
    (tmp_path / "0002-add-column.sql").write_text("SELECT 1;")

    with pytest.raises(InvalidMigrationFilenameError):
        discover_migrations(tmp_path)


def test_discover_migrations_rejects_duplicate_version(tmp_path: Path) -> None:
    (tmp_path / "0001_first.sql").write_text("SELECT 1;")
    (tmp_path / "0001_second.sql").write_text("SELECT 2;")

    with pytest.raises(DuplicateMigrationVersionError):
        discover_migrations(tmp_path)


def test_discover_migrations_raises_when_directory_missing(tmp_path: Path) -> None:
    with pytest.raises(MigrationsDirectoryMissingError):
        discover_migrations(tmp_path / "does-not-exist")
