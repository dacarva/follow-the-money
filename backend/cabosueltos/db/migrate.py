from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import psycopg

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent.parent / "migrations"
ADVISORY_LOCK_KEY = "cabosueltos.migrate"

# If a prior `migrate` run is killed uncleanly (CI cancel, OOM, network
# partition) after acquiring the advisory lock but before the connection is
# torn down, Postgres won't notice the dead session until TCP keepalives
# time out — which can be hours. Bound how long we'll wait for the lock so a
# wedged run fails loudly instead of hanging every future `migrate` call.
LOCK_TIMEOUT = "30s"

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


class InvalidMigrationFilenameError(Exception):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(
            f"migration file {name!r} does not match the required "
            f"'<digits>_<name>.sql' pattern; rename it or it will never be applied"
        )


class DuplicateMigrationVersionError(Exception):
    def __init__(self, version: str, names: list[str]) -> None:
        self.version = version
        self.names = names
        super().__init__(f"migration version {version} is used by more than one file: {names}")


class MigrationsDirectoryMissingError(Exception):
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        super().__init__(
            f"migrations directory {directory} does not exist. If this is running from an "
            f"installed package (not a source checkout), the migrations/ directory next to "
            f"backend/ was not shipped with it — `migrate` would otherwise silently apply "
            f"nothing and report success."
        )


def discover_migrations(directory: Path = MIGRATIONS_DIR) -> list[Migration]:
    if not directory.is_dir():
        raise MigrationsDirectoryMissingError(directory)
    migrations = []
    seen: dict[str, str] = {}
    for path in directory.glob("*.sql"):
        match = _FILENAME_RE.match(path.name)
        if not match:
            raise InvalidMigrationFilenameError(path.name)
        version = match.group(1)
        if version in seen:
            raise DuplicateMigrationVersionError(version, [seen[version], path.name])
        seen[version] = path.name
        checksum = hashlib.sha256(path.read_bytes()).hexdigest()
        migrations.append(Migration(version=version, path=path, checksum=checksum))
    migrations.sort(key=lambda m: int(m.version))
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
    with psycopg.connect(
        database_url, autocommit=True, options=f"-c lock_timeout={LOCK_TIMEOUT}"
    ) as conn:
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
