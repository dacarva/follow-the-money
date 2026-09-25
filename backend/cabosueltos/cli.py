from __future__ import annotations

import typer

from cabosueltos.db.migrate import ChecksumMismatchError
from cabosueltos.db.migrate import migrate as run_migrate
from cabosueltos.db.migrate import status as run_status
from cabosueltos.settings import load_settings

app = typer.Typer(no_args_is_help=True)
db_app = typer.Typer(no_args_is_help=True)
app.add_typer(db_app, name="db")


@db_app.command("migrate")
def db_migrate() -> None:
    settings = load_settings()
    try:
        applied = run_migrate(settings.database_url)
    except ChecksumMismatchError as exc:
        typer.echo(f"migration {exc.version} has changed since it was applied", err=True)
        raise typer.Exit(code=1) from None
    for version in applied:
        typer.echo(f"applied {version}")


@db_app.command("status")
def db_status() -> None:
    settings = load_settings()
    for version, state in run_status(settings.database_url):
        typer.echo(f"{version} {state}")


if __name__ == "__main__":
    app()
