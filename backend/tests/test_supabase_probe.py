from __future__ import annotations

import time
from typing import Any

import httpx
import psycopg
import pytest

from cabosueltos.settings import Settings, load_settings

pytestmark = pytest.mark.supabase_probe

# Observed on the staging project on 2026-09-25 (see infra/supabase/README.md):
# with "Enable Data API" off, every Data API endpoint answers 503 PGRST002
# ("Could not query the database for the schema cache"). With it on, an unknown
# table answers 404 PGRST205 and `Accept-Profile: ftm` answers 406 PGRST106.
DATA_API_DISABLED_STATUS = 503
DATA_API_DISABLED_CODE = "PGRST002"
ENABLED_CODES = {"PGRST205", "PGRST106", "PGRST202"}

# An enabled Data API also answers 503 PGRST002 for under 30 s while it restarts
# after a settings change, so one sample cannot tell the two apart. Three samples
# 20 s apart outlast that window.
SAMPLES = 3
SAMPLE_INTERVAL_S = 20.0

UNKNOWN_TABLE = "cabosueltos_probe_no_such_table"


def _headers(publishable_key: str, *, profile: str | None = None) -> dict[str, str]:
    headers = {"apikey": publishable_key, "Authorization": f"Bearer {publishable_key}"}
    if profile is not None:
        headers["Accept-Profile"] = profile
    return headers


def _error_code(response: httpx.Response) -> str | None:
    try:
        body = response.json()
    except ValueError:
        return None
    code = body.get("code") if isinstance(body, dict) else None
    return code if isinstance(code, str) else None


def _ftm_tables(database_url: str) -> list[str]:
    with psycopg.connect(database_url, autocommit=True) as conn:
        rows = conn.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'ftm' ORDER BY tablename"
        ).fetchall()
    return [row[0] for row in rows]


def _data_api_requests(settings: Settings, tables: list[str]) -> list[tuple[str, dict[str, str]]]:
    key = settings.supabase_publishable_key or ""
    base = settings.supabase_url
    requests = [
        (f"{base}/rest/v1/{UNKNOWN_TABLE}", _headers(key)),
        (f"{base}/graphql/v1", _headers(key)),
    ]
    for table in tables:
        requests.append((f"{base}/rest/v1/{table}", _headers(key, profile="ftm")))
        requests.append((f"{base}/rest/v1/{table}", _headers(key)))
    return requests


def _check_disabled(url: str, response: httpx.Response) -> None:
    status = response.status_code
    code = _error_code(response)
    assert not (200 <= status < 300), f"{url} answered {status}: the Data API returned data"
    assert code not in ENABLED_CODES, f"{url} answered {status} {code}: the Data API is enabled"
    if (status, code) != (DATA_API_DISABLED_STATUS, DATA_API_DISABLED_CODE):
        # Neither the disabled signature nor a known enabled answer: an outage or
        # a platform change. Error loudly instead of passing.
        raise RuntimeError(
            f"{url} answered {status} {code}; expected {DATA_API_DISABLED_STATUS} "
            f"{DATA_API_DISABLED_CODE}. Check the project and infra/supabase/README.md."
        )


@pytest.fixture(scope="module")
def probe_settings() -> Settings:
    settings = load_settings()
    if not settings.supabase_url or not settings.supabase_publishable_key:
        pytest.fail("SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY must be set for the probe")
    return settings


def test_0_sanity_auth_settings_reachable(probe_settings: Settings) -> None:
    """A bad key or a paused project must not look like a disabled Data API."""
    response = httpx.get(
        f"{probe_settings.supabase_url}/auth/v1/settings",
        headers=_headers(probe_settings.supabase_publishable_key or ""),
        timeout=10.0,
    )
    response.raise_for_status()
    assert response.status_code == 200


def test_1_data_api_is_disabled(probe_settings: Settings) -> None:
    tables = _ftm_tables(probe_settings.database_url)
    assert tables, "ftm.schema_migrations should always exist"
    requests = _data_api_requests(probe_settings, tables)
    with httpx.Client(timeout=10.0) as client:
        for sample in range(SAMPLES):
            if sample:
                time.sleep(SAMPLE_INTERVAL_S)
            for url, headers in requests:
                _check_disabled(url, client.get(url, headers=headers))


def test_2_privileges_hold_on_staging(probe_settings: Settings) -> None:
    with psycopg.connect(probe_settings.database_url, autocommit=True) as conn:
        p1 = conn.execute(
            """
            SELECT count(*) FROM information_schema.role_table_grants
            WHERE table_schema = 'ftm' AND grantee IN ('anon', 'authenticated', 'PUBLIC')
            """
        ).fetchone()[0]
        p2 = conn.execute(
            "SELECT count(*) FROM pg_tables WHERE schemaname = 'public' AND NOT rowsecurity"
        ).fetchone()[0]
        p3_anon = conn.execute("SELECT has_schema_privilege('anon', 'ftm', 'USAGE')").fetchone()[0]
        p3_authenticated: Any = conn.execute(
            "SELECT has_schema_privilege('authenticated', 'ftm', 'USAGE')"
        ).fetchone()[0]

    assert p1 == 0
    assert p2 == 0
    assert p3_anon is False
    assert p3_authenticated is False
