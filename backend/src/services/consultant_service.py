import sqlite3
import json

from ..schemas.consultant import ConsultantCreate, ConsultantUpdate
from ..core.database import dict_from_row, list_from_rows


def serialize_consultant(consultant: dict) -> dict:
    """Convert consultant row to response format with JSON deserialization."""
    serialized = {**consultant}
    if serialized.get("focus_areas"):
        try:
            parsed = json.loads(serialized["focus_areas"])
            serialized["focus_areas"] = parsed if isinstance(parsed, list) else []
        except (json.JSONDecodeError, TypeError):
            serialized["focus_areas"] = []
    else:
        serialized["focus_areas"] = []
    return serialized


def _normalize_focus_areas(focus_areas: list[str] | None) -> list[str]:
    """Normalize focus areas by trimming entries and removing blanks."""
    if not focus_areas:
        return []
    return [str(area).strip() for area in focus_areas if str(area).strip()]


async def create_consultant(conn: sqlite3.Connection, consultant_data: ConsultantCreate, admin_id: int) -> dict:
    """Create a new consultant."""
    focus_areas = _normalize_focus_areas(consultant_data.focus_areas)
    focus_areas_json = json.dumps(focus_areas) if focus_areas else None

    cursor = conn.execute(
        """
        INSERT INTO consultants (first_name, last_name, email, title, summary, photo_url, role, focus_areas, years_experience, motto, created_by_admin_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            consultant_data.first_name,
            consultant_data.last_name,
            consultant_data.email,
            consultant_data.title,
            consultant_data.summary,
            consultant_data.photo_url,
            consultant_data.role,
            focus_areas_json,
            consultant_data.years_experience,
            consultant_data.motto,
            admin_id
        )
    )
    consultant_id = cursor.lastrowid

    # Fetch the created consultant
    cursor = conn.execute("SELECT * FROM consultants WHERE id = ?", (consultant_id,))
    return serialize_consultant(dict_from_row(cursor.fetchone()))


async def get_consultant(conn: sqlite3.Connection, consultant_id: int) -> dict | None:
    """Get a consultant by id."""
    cursor = conn.execute("SELECT * FROM consultants WHERE id = ?", (consultant_id,))
    row = cursor.fetchone()
    if row:
        return serialize_consultant(dict_from_row(row))
    return None


async def get_consultants(conn: sqlite3.Connection, skip: int = 0, limit: int = 100) -> list[dict]:
    """Get all consultants ordered by latest creation timestamp."""
    cursor = conn.execute(
        "SELECT * FROM consultants ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, skip)
    )
    return [serialize_consultant(c) for c in list_from_rows(cursor.fetchall())]


async def update_consultant(conn: sqlite3.Connection, consultant_id: int, consultant_data: ConsultantUpdate) -> dict | None:
    """Update a consultant with provided fields only."""
    # Get current consultant
    cursor = conn.execute("SELECT * FROM consultants WHERE id = ?", (consultant_id,))
    consultant = cursor.fetchone()

    if not consultant:
        return None

    # Build update query dynamically for only provided fields
    updates = consultant_data.model_dump(exclude_unset=True)
    if not updates:
        return serialize_consultant(dict_from_row(consultant))

    allowed_fields = {
        "first_name",
        "last_name",
        "email",
        "title",
        "summary",
        "photo_url",
        "role",
        "focus_areas",
        "years_experience",
        "motto",
    }
    updates = {key: value for key, value in updates.items() if key in allowed_fields}
    if not updates:
        return serialize_consultant(dict_from_row(consultant))

    # Serialize focus_areas if present
    if "focus_areas" in updates:
        normalized_focus_areas = _normalize_focus_areas(updates["focus_areas"])
        updates["focus_areas"] = json.dumps(normalized_focus_areas) if normalized_focus_areas else None

    set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
    values = list(updates.values()) + [consultant_id]

    conn.execute(
        f"UPDATE consultants SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        values
    )

    # Fetch updated consultant
    cursor = conn.execute("SELECT * FROM consultants WHERE id = ?", (consultant_id,))
    return serialize_consultant(dict_from_row(cursor.fetchone()))


async def delete_consultant(conn: sqlite3.Connection, consultant_id: int) -> bool:
    """Delete a consultant and return whether deletion occurred."""
    cursor = conn.execute("SELECT id FROM consultants WHERE id = ?", (consultant_id,))
    if not cursor.fetchone():
        return False

    conn.execute("DELETE FROM consultants WHERE id = ?", (consultant_id,))
    return True
