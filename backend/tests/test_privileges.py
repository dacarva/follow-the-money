from __future__ import annotations

from urllib.parse import urlparse

import psycopg


def test_p1_no_grants_on_ftm_tables(pg_conn: psycopg.Connection) -> None:
    count = pg_conn.execute(
        """
        SELECT count(*) FROM information_schema.role_table_grants
        WHERE table_schema = 'ftm' AND grantee IN ('anon', 'authenticated', 'PUBLIC')
        """
    ).fetchone()[0]
    assert count == 0


def test_p2_all_public_tables_have_rls(pg_conn: psycopg.Connection) -> None:
    count = pg_conn.execute(
        "SELECT count(*) FROM pg_tables WHERE schemaname = 'public' AND NOT rowsecurity"
    ).fetchone()[0]
    assert count == 0


def test_p3_anon_and_authenticated_lack_ftm_usage(pg_conn: psycopg.Connection) -> None:
    anon_usage = pg_conn.execute("SELECT has_schema_privilege('anon', 'ftm', 'USAGE')").fetchone()[
        0
    ]
    authenticated_usage = pg_conn.execute(
        "SELECT has_schema_privilege('authenticated', 'ftm', 'USAGE')"
    ).fetchone()[0]
    assert anon_usage is False
    assert authenticated_usage is False


def test_p4_scratch_table_by_migration_role_gets_no_grants(
    database_url: str, pg_conn: psycopg.Connection
) -> None:
    expected_user = urlparse(database_url).username
    current_user = pg_conn.execute("SELECT current_user").fetchone()[0]
    assert current_user == expected_user

    with psycopg.connect(database_url) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS ftm.__priv_scratch (id int)")
        count = conn.execute(
            """
            SELECT count(*) FROM information_schema.role_table_grants
            WHERE table_schema = 'ftm' AND table_name = '__priv_scratch'
              AND grantee IN ('anon', 'authenticated', 'PUBLIC')
            """
        ).fetchone()[0]
        conn.rollback()

    assert count == 0
