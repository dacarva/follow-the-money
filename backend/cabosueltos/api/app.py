from __future__ import annotations

import asyncio
import contextlib
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from cabosueltos.db.pool import CONNECT_TIMEOUT_SECONDS, create_pool
from cabosueltos.settings import Settings, load_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    pool = create_pool(settings.pool_url)
    dist_dir = settings.web_dist_path

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        await asyncio.to_thread(pool.close)

    app = FastAPI(lifespan=lifespan)
    app.state.settings = settings
    app.state.pool = pool

    @app.get("/api/salud")
    def salud() -> JSONResponse:
        try:
            with pool.connection(timeout=CONNECT_TIMEOUT_SECONDS) as conn:
                conn.execute("SELECT 1")
        except Exception:
            return JSONResponse({"estado": "degradado", "db": "error"}, status_code=503)
        return JSONResponse({"estado": "ok", "db": "ok"})

    assets_dir = dist_dir / "assets"
    # `check_dir=False` only skips Starlette's *constructor*-time check; without
    # the directory actually existing, StaticFiles still raises at request time
    # instead of 404ing. Try to create it so a missing/unbuilt dist degrades to
    # 404s, the same way the SPA fallback route already does for `index.html`.
    # Best-effort: on a read-only deployment (no local dist build available)
    # this can fail — don't crash app startup over it, just keep the
    # pre-existing (request-time) failure mode for that one deployment shape.
    with contextlib.suppress(OSError):
        assets_dir.mkdir(parents=True, exist_ok=True)
    app.mount(
        "/assets",
        StaticFiles(directory=assets_dir, check_dir=False),
        name="assets",
    )

    @app.get("/{full_path:path}")
    def spa(full_path: str) -> Response:
        if full_path == "api" or full_path.startswith("api/"):
            return Response(status_code=404)
        index_file = dist_dir / "index.html"
        if not index_file.is_file():
            return Response(status_code=404)
        return FileResponse(index_file)

    return app


def run() -> None:
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(create_app(), host="0.0.0.0", port=port)  # noqa: S104
