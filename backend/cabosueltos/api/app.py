from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from cabosueltos.db.pool import create_pool
from cabosueltos.settings import Settings, load_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    pool = create_pool(settings.pool_url)
    dist_dir = settings.web_dist_path

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        pool.close()

    app = FastAPI(lifespan=lifespan)
    app.state.settings = settings
    app.state.pool = pool

    @app.get("/api/salud")
    def salud() -> JSONResponse:
        try:
            with pool.connection(timeout=1) as conn:
                conn.execute("SELECT 1")
        except Exception:
            return JSONResponse({"estado": "degradado", "db": "error"}, status_code=503)
        return JSONResponse({"estado": "ok", "db": "ok"})

    app.mount(
        "/assets",
        StaticFiles(directory=dist_dir / "assets", check_dir=False),
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
