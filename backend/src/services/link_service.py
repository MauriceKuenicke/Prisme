import sqlite3
import secrets
from datetime import datetime, timedelta, timezone

from ..core.database import dict_from_row, list_from_rows
from .consultant_service import get_consultant


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def _parse_timestamp(value: str | datetime) -> datetime:
    """Parse SQLite datetime values into timezone-aware UTC datetimes."""
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


async def create_access_link(conn: sqlite3.Connection, consultant_id: int, admin_id: int, validity_hours: int = 72) -> dict:
    """Generate a temporary access link for consultant block editing."""
    if validity_hours < 1 or validity_hours > 168:
        raise ValueError("validity_hours must be between 1 and 168.")

    consultant = await get_consultant(conn, consultant_id)
    if not consultant:
        raise ValueError("Consultant not found.")

    token = secrets.token_urlsafe(32)
    expires_at = _utcnow() + timedelta(hours=validity_hours)

    cursor = conn.execute(
        """
        INSERT INTO access_links (consultant_id, token, expires_at, created_by_admin_id, is_used)
        VALUES (?, ?, ?, ?, 0)
        """,
        (consultant_id, token, expires_at, admin_id)
    )
    link_id = cursor.lastrowid

    # Fetch the created link
    cursor = conn.execute("SELECT * FROM access_links WHERE id = ?", (link_id,))
    return dict_from_row(cursor.fetchone())


async def validate_access_link(conn: sqlite3.Connection, token: str) -> dict | None:
    """Validate temporary link and return associated link if valid."""
    cursor = conn.execute("SELECT * FROM access_links WHERE token = ?", (token,))
    link = cursor.fetchone()

    if not link:
        return None

    link_dict = dict_from_row(link)

    expires_at = _parse_timestamp(link_dict["expires_at"])

    if expires_at < _utcnow():
        return None  # Expired

    # Update last accessed time
    conn.execute(
        "UPDATE access_links SET last_accessed_at = ?, is_used = 1 WHERE id = ?",
        (_utcnow(), link_dict["id"]),
    )

    # Return updated link
    cursor = conn.execute("SELECT * FROM access_links WHERE id = ?", (link_dict['id'],))
    return dict_from_row(cursor.fetchone())


async def get_consultant_links(conn: sqlite3.Connection, consultant_id: int) -> list[dict]:
    """Get all access links for a consultant."""
    cursor = conn.execute(
        "SELECT * FROM access_links WHERE consultant_id = ? ORDER BY created_at DESC",
        (consultant_id,)
    )
    return list_from_rows(cursor.fetchall())


async def revoke_access_link(conn: sqlite3.Connection, link_id: int) -> bool:
    """Revoke an access link."""
    cursor = conn.execute("SELECT id FROM access_links WHERE id = ?", (link_id,))
    if not cursor.fetchone():
        return False

    # Set expiry to now to revoke
    conn.execute(
        "UPDATE access_links SET expires_at = ? WHERE id = ?",
        (_utcnow(), link_id),
    )
    return True
