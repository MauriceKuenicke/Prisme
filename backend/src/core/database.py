import sqlite3
from contextlib import contextmanager
from typing import Generator, Sequence

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings


def _extract_sqlite_path(database_url: str) -> str:
    """Extract a filesystem path from a SQLite database URL."""
    if database_url.startswith("sqlite:///"):
        return database_url.replace("sqlite:///", "", 1)
    if database_url.startswith("sqlite://"):
        return database_url.replace("sqlite://", "", 1)
    raise ValueError("Only SQLite URLs are supported by this backend.")


def _get_sqlalchemy_connect_args(database_url: str) -> dict:
    """Return SQLAlchemy connection args matching configured dialect."""
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


engine = create_engine(settings.DATABASE_URL, connect_args=_get_sqlalchemy_connect_args(settings.DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db_connection() -> sqlite3.Connection:
    """Create a new SQLite database connection with row dict support."""
    db_path = _extract_sqlite_path(settings.DATABASE_URL)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    # Enable foreign keys for SQLite
    conn.execute("PRAGMA foreign_keys = ON")
    # Return rows as dictionaries
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Yield a transaction-scoped database connection."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def dict_from_row(row: sqlite3.Row) -> dict | None:
    """Convert a sqlite row to a dictionary."""
    return dict(row) if row else None


def list_from_rows(rows: Sequence[sqlite3.Row]) -> list[dict]:
    """Convert a list of sqlite rows to dictionaries."""
    return [dict(row) for row in rows]
