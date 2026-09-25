from __future__ import annotations

from collections.abc import Iterator

import psycopg
import pytest

from cabosueltos.settings import load_settings


@pytest.fixture(scope="session")
def database_url() -> str:
    return load_settings().database_url


@pytest.fixture
def pg_conn(database_url: str) -> Iterator[psycopg.Connection]:
    with psycopg.connect(database_url, autocommit=True) as conn:
        yield conn
