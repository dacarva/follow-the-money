from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import psycopg

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent.parent / "migrations"
ADVISORY_LOCK_KEY = "cabosueltos.migrate"

_FILENAME_RE = re.compile(r"^(\d+)_[a-z0-9_]+\.sql$")


@dataclass(frozen=True)
class Migration:
    version: str
    path: Path
    checksum: str


class ChecksumMismatchError(Exception):
    def __init__(self, version: str) -> None:
        self.version = version
        super().__init__(f"migration {version} has changed since it was applied")


def discover_migrations(directory: Path = MIGRATIONS_DIR) -> list[Migration]:
    migrations = []
    for path in directory.glob("*.sql"):
        match = _FILENAME_RE.match(path.name)
        if not match:
            continue
        version = match.group(1)
        checksum = hashlib.sha256(path.read_bytes()).hexdigest()
        migrations.append(Migration(version=version, path=path, checksum=checksum))
    migrations.sort(key=lambda m: m.version)
    return migrations


def _bootstrap(conn: psycopg.Connection) -> None:
    with conn.transaction():
        conn.execute("CREATE SCHEMA IF NOT EXISTS ftm")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ftm.schema_migrations (
                version text PRIMARY KEY,
                checksum text NOT NULL,
                applied_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )


def _applied_versions(conn: psycopg.Connection) -> dict[str, str]:
    rows = conn.execute("SELECT version, checksum FROM ftm.schema_migrations").fetchall()
    return dict(rows)


def migrate(database_url: str, directory: Path = MIGRATIONS_DIR) -> list[str]:
    """Apply every pending migration in `directory`, in numeric order.

    Holds a session-level advisory lock for the whole run so a concurrent
    `migrate` call waits instead of double-applying. Returns the versions
    applied by this call (empty when everything was already applied).
    """
    migrations = discover_migrations(directory)
    applied_now: list[str] = []
    with psycopg.connect(database_url, autocommit=True) as conn:
        conn.execute("SELECT pg_advisory_lock(hashtext(%s))", (ADVISORY_LOCK_KEY,))
        try:
            _bootstrap(conn)
            applied = _applied_versions(conn)
            for migration in migrations:
                if migration.version in applied:
                    if applied[migration.version] != migration.checksum:
                        raise ChecksumMismatchError(migration.version)
                    continue
                sql = migration.path.read_text()
                with conn.transaction():
                    conn.execute(sql)
                    conn.execute(
                        "INSERT INTO ftm.schema_migrations (version, checksum) VALUES (%s, %s)",
                        (migration.version, migration.checksum),
                    )
                applied_now.append(migration.version)
        finally:
            conn.execute("SELECT pg_advisory_unlock(hashtext(%s))", (ADVISORY_LOCK_KEY,))
    return applied_now


def status(database_url: str, directory: Path = MIGRATIONS_DIR) -> list[tuple[str, str]]:
    migrations = discover_migrations(directory)
    with psycopg.connect(database_url, autocommit=True) as conn:
        _bootstrap(conn)
        applied = _applied_versions(conn)
    return [(m.version, "applied" if m.version in applied else "pending") for m in migrations]
