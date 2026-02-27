import sqlite3
import json
from ..schemas.block import BlockCreate, BlockUpdate
from ..core.database import dict_from_row, list_from_rows


def _normalize_technologies_value(value: list[str] | str | None) -> str | None:
    """Normalize technologies input to a JSON array string."""
    if value is None:
        return None

    if isinstance(value, list):
        cleaned = [str(item).strip() for item in value if str(item).strip()]
        return json.dumps(cleaned) if cleaned else None

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None

        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, list):
                cleaned = [str(item).strip() for item in parsed if str(item).strip()]
                return json.dumps(cleaned) if cleaned else None
        except json.JSONDecodeError:
            pass

        cleaned = [item.strip() for item in stripped.split(",") if item.strip()]
        return json.dumps(cleaned) if cleaned else None

    return None


async def create_block(conn: sqlite3.Connection, consultant_id: int, block_data: BlockCreate) -> dict:
    """Create a new content block."""
    data = block_data.model_dump()
    if "technologies" in data:
        data["technologies"] = _normalize_technologies_value(data["technologies"])

    # Build INSERT query with all fields (quote column names for SQL reserved words)
    columns = ["consultant_id"] + list(data.keys())
    placeholders = ", ".join(["?"] * len(columns))
    column_names = ", ".join([f'"{col}"' for col in columns])
    values = [consultant_id] + list(data.values())

    cursor = conn.execute(
        f"INSERT INTO blocks ({column_names}) VALUES ({placeholders})",
        values
    )
    block_id = cursor.lastrowid

    # Fetch the created block
    cursor = conn.execute("SELECT * FROM blocks WHERE id = ?", (block_id,))
    return dict_from_row(cursor.fetchone())


async def get_block(conn: sqlite3.Connection, block_id: int) -> dict | None:
    """Get a block by id."""
    cursor = conn.execute("SELECT * FROM blocks WHERE id = ?", (block_id,))
    row = cursor.fetchone()
    return dict_from_row(row)


async def get_consultant_blocks(
    conn: sqlite3.Connection, consultant_id: int, block_type: str | None = None
) -> list[dict]:
    """Get all blocks for a consultant, optionally filtered by type"""
    if block_type:
        cursor = conn.execute(
            """SELECT * FROM blocks
               WHERE consultant_id = ? AND block_type = ? AND is_active = 1
               ORDER BY "order", created_at DESC""",
            (consultant_id, block_type)
        )
    else:
        cursor = conn.execute(
            """SELECT * FROM blocks
               WHERE consultant_id = ? AND is_active = 1
               ORDER BY "order", created_at DESC""",
            (consultant_id,)
        )
    return list_from_rows(cursor.fetchall())


async def get_blocks_by_ids(conn: sqlite3.Connection, block_ids: list[int]) -> list[dict]:
    """Get blocks by list of ids."""
    if not block_ids:
        return []

    placeholders = ", ".join(["?"] * len(block_ids))
    cursor = conn.execute(
        f"SELECT * FROM blocks WHERE id IN ({placeholders})",
        block_ids
    )
    return list_from_rows(cursor.fetchall())


async def update_block(conn: sqlite3.Connection, block_id: int, block_data: BlockUpdate) -> dict | None:
    """Update a content block."""
    # Get current block
    cursor = conn.execute("SELECT * FROM blocks WHERE id = ?", (block_id,))
    block = cursor.fetchone()

    if not block:
        return None

    # Build update query dynamically for only provided fields
    updates = block_data.model_dump(exclude_unset=True)
    if not updates:
        return dict_from_row(block)

    allowed_fields = {
        "title",
        "order",
        "client_name",
        "project_description",
        "role",
        "technologies",
        "start_date",
        "end_date",
        "is_ongoing",
        "duration_months",
        "proficiency_level",
        "misc_content",
        "issuing_organization",
        "issue_date",
        "expiry_date",
        "credential_id",
        "credential_url",
    }
    updates = {key: value for key, value in updates.items() if key in allowed_fields}
    if not updates:
        return dict_from_row(block)

    if "technologies" in updates:
        updates["technologies"] = _normalize_technologies_value(updates["technologies"])

    set_clause = ", ".join([f'"{key}" = ?' for key in updates.keys()])
    values = list(updates.values()) + [block_id]

    conn.execute(
        f"UPDATE blocks SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        values
    )

    # Fetch updated block
    cursor = conn.execute("SELECT * FROM blocks WHERE id = ?", (block_id,))
    return dict_from_row(cursor.fetchone())


async def delete_block(conn: sqlite3.Connection, block_id: int) -> bool:
    """Delete a content block and return whether deletion occurred."""
    cursor = conn.execute("SELECT id FROM blocks WHERE id = ?", (block_id,))
    if not cursor.fetchone():
        return False

    conn.execute("DELETE FROM blocks WHERE id = ?", (block_id,))
    return True


async def reorder_blocks(conn: sqlite3.Connection, consultant_id: int, block_orders: list[dict]) -> None:
    """Update display order of blocks for a consultant."""
    if not block_orders:
        return

    block_ids = [item["id"] for item in block_orders]
    placeholders = ", ".join(["?"] * len(block_ids))
    cursor = conn.execute(
        f"SELECT id FROM blocks WHERE consultant_id = ? AND id IN ({placeholders})",
        [consultant_id, *block_ids],
    )
    allowed_ids = {row["id"] for row in cursor.fetchall()}
    updates = [(item["order"], item["id"]) for item in block_orders if item["id"] in allowed_ids]

    if updates:
        conn.executemany('UPDATE blocks SET "order" = ? WHERE id = ?', updates)
