from __future__ import annotations

import time
from pathlib import Path

from fastapi.testclient import TestClient

from cabosueltos.api.app import create_app
from cabosueltos.settings import Settings


def _settings(database_url: str, dist_dir: Path) -> Settings:
    return Settings(
        _env_file=None,
        app_env="local",
        database_url=database_url,
        web_dist_dir=str(dist_dir),
    )


def test_salud_returns_200_when_db_reachable(database_url: str, tmp_path: Path) -> None:
    app = create_app(_settings(database_url, tmp_path))
    with TestClient(app) as client:
        response = client.get("/api/salud")
    assert response.status_code == 200
    assert response.json() == {"estado": "ok", "db": "ok"}


def test_salud_returns_503_within_2s_when_db_unreachable(tmp_path: Path) -> None:
    unreachable_url = "postgresql://postgres:x@127.0.0.1:1/doesnotexist"
    app = create_app(_settings(unreachable_url, tmp_path))
    with TestClient(app) as client:
        start = time.monotonic()
        response = client.get("/api/salud")
        elapsed = time.monotonic() - start
    assert response.status_code == 503
    assert response.json() == {"estado": "degradado", "db": "error"}
    assert elapsed < 2


def test_root_serves_built_index_html(database_url: str, tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text("<h1>hola</h1>")
    app = create_app(_settings(database_url, tmp_path))
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert "hola" in response.text


def test_root_returns_404_and_app_still_starts_when_dist_missing(
    database_url: str, tmp_path: Path
) -> None:
    app = create_app(_settings(database_url, tmp_path / "does-not-exist"))
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 404


def test_unknown_api_path_returns_404_instead_of_spa_fallback(
    database_url: str, tmp_path: Path
) -> None:
    (tmp_path / "index.html").write_text("<h1>hola</h1>")
    app = create_app(_settings(database_url, tmp_path))
    with TestClient(app) as client:
        response = client.get("/api/no-such-route")
    assert response.status_code == 404
    assert "hola" not in response.text


def test_assets_are_served_from_the_dist_assets_directory(
    database_url: str, tmp_path: Path
) -> None:
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "app.js").write_text("console.log('hola');")
    app = create_app(_settings(database_url, tmp_path))
    with TestClient(app) as client:
        response = client.get("/assets/app.js")
    assert response.status_code == 200
    assert "hola" in response.text


def test_assets_request_returns_404_when_assets_directory_missing(
    database_url: str, tmp_path: Path
) -> None:
    # `check_dir=False` lets the app boot without a built `dist/assets`;
    # a request against a missing assets dir should 404, not 500.
    app = create_app(_settings(database_url, tmp_path))
    with TestClient(app) as client:
        response = client.get("/assets/app.js")
    assert response.status_code == 404
