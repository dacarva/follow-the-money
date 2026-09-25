from __future__ import annotations

from psycopg_pool import ConnectionPool

CONNECT_TIMEOUT_SECONDS = 1


def create_pool(conninfo: str) -> ConnectionPool:
    return ConnectionPool(
        conninfo,
        min_size=1,
        max_size=5,
        kwargs={"connect_timeout": CONNECT_TIMEOUT_SECONDS},
        open=True,
    )
