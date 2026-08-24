"""Wait for Docker DNS + PostgreSQL, then exec Alembic.

The migrate service can start immediately after Postgres reports healthy while
the embedded Docker DNS is still settling.  Retrying here avoids flaky
``Temporary failure in name resolution`` errors on ``db``.
"""

from __future__ import annotations

import asyncio
import os
import socket
import sys
import time
from urllib.parse import urlparse


def _db_host_port() -> tuple[str, int]:
    url = os.environ.get("DATABASE_URL", "")
    parsed = urlparse(url.replace("+asyncpg", ""))
    host = parsed.hostname or os.environ.get("DB_HOST", "db")
    port = parsed.port or int(os.environ.get("DB_PORT", "5432"))
    return host, port


def wait_for_dns(host: str, port: int, *, timeout: float = 90.0) -> None:
    """Block until *host* resolves or *timeout* seconds elapse."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
            return
        except OSError as exc:
            print(f"waiting for {host}:{port} dns ({exc})", flush=True)
            time.sleep(2)
    raise SystemExit(f"Timed out waiting for DNS resolution of {host}:{port}")


async def wait_for_database(*, timeout: float = 90.0) -> None:
    """Block until PostgreSQL accepts a connection."""
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.pool import NullPool

    from app.core.config import get_settings

    get_settings.cache_clear()
    url = get_settings().database_url
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        engine = create_async_engine(url, poolclass=NullPool)
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return
        except Exception as exc:
            print(f"waiting for database ({exc})", flush=True)
            await asyncio.sleep(2)
        finally:
            await engine.dispose()
    raise SystemExit("Timed out waiting for database connection")


def main() -> None:
    host, port = _db_host_port()
    wait_for_dns(host, port)
    asyncio.run(wait_for_database())
    os.execvp("alembic", ["alembic", *sys.argv[1:]])


if __name__ == "__main__":
    main()
