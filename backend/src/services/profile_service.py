import json
import sqlite3
from datetime import datetime, timezone

from ..core.database import dict_from_row, list_from_rows
from ..schemas.profile import ProfileCreate, ProfileUpdate
from .consultant_service import get_consultant


def _utc_now_iso() -> str:
    """Return current UTC timestamp as ISO string."""
    return datetime.now(timezone.utc).isoformat()


def _parse_json_array(value: str | None) -> list[str]:
    """Parse JSON list values safely and return an empty list for invalid payloads."""
    if not value:
        return []

    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []

    if isinstance(parsed, list):
        return [str(item) for item in parsed]
    return []


def _parse_list_like(value: str | list[str] | None) -> list[str]:
    """Parse list-like customization values (list, JSON string, comma-separated string)."""
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []

        looks_like_json_array = stripped.startswith("[") and stripped.endswith("]")
        if looks_like_json_array:
            try:
                parsed_json = json.loads(stripped)
            except (json.JSONDecodeError, TypeError):
                parsed_json = None

            if isinstance(parsed_json, list):
                return [str(item).strip() for item in parsed_json if str(item).strip()]
            if parsed_json is not None:
                return []

        if "," in stripped:
            return [item.strip() for item in stripped.split(",") if item.strip()]
        return [stripped]

    return []


def _parse_int(value: int | str | None) -> int | None:
    """Parse integer-like customization values."""
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_bool(value: bool | str | None, fallback: bool | None = None) -> bool | None:
    """Parse boolean-like customization values with optional fallback."""
    if value is None:
        return fallback
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False
    return fallback


def _get_customization_value(customization: dict, key: str, fallback):
    """Return customization value when explicitly provided, otherwise fallback."""
    return customization[key] if key in customization else fallback


def _normalize_selected_block_ids(block_ids: list[int]) -> list[int]:
    """Remove duplicates while preserving original selection order."""
    return list(dict.fromkeys(block_ids))


def serialize_block(block: dict, customization: dict | None = None) -> dict:
    """Convert a block row into profile snapshot format with optional customizations."""
    customization = customization or {}
    base = {
        "id": block["id"],
        "title": customization.get("title") or block["title"],
        "block_type": block["block_type"],
    }

    if block["block_type"] == "project":
        if "technologies" in customization:
            technologies = _parse_list_like(customization.get("technologies"))
        else:
            technologies = _parse_json_array(block.get("technologies"))

        if "duration_months" in customization:
            duration_months = _parse_int(customization.get("duration_months"))
        else:
            duration_months = block.get("duration_months")

        is_ongoing = _parse_bool(
            _get_customization_value(customization, "is_ongoing", block.get("is_ongoing")),
            block.get("is_ongoing"),
        )
        end_date = None if is_ongoing else _get_customization_value(
            customization,
            "end_date",
            block.get("end_date"),
        )

        return {
            **base,
            "client_name": _get_customization_value(customization, "client_name", block.get("client_name")),
            "description": _get_customization_value(customization, "description", block.get("project_description")),
            "role": _get_customization_value(customization, "role", block.get("role")),
            "technologies": technologies,
            "duration_months": duration_months,
            "start_date": _get_customization_value(customization, "start_date", block.get("start_date")),
            "end_date": end_date,
            "is_ongoing": is_ongoing,
        }
    if block["block_type"] == "skill":
        return {
            **base,
            "level": _get_customization_value(customization, "level", block.get("proficiency_level")),
        }
    if block["block_type"] == "misc":
        return {
            **base,
            "content": _get_customization_value(customization, "content", block.get("misc_content")),
        }
    if block["block_type"] == "certification":
        return {
            **base,
            "issuing_organization": _get_customization_value(
                customization,
                "issuing_organization",
                block.get("issuing_organization"),
            ),
            "issue_date": _get_customization_value(customization, "issue_date", block.get("issue_date")),
            "expiry_date": _get_customization_value(customization, "expiry_date", block.get("expiry_date")),
            "credential_id": _get_customization_value(customization, "credential_id", block.get("credential_id")),
            "credential_url": _get_customization_value(customization, "credential_url", block.get("credential_url")),
        }

    return base


def _build_profile_snapshot(
    consultant: dict,
    blocks: list[dict],
    selected_block_ids: list[int],
    customizations: dict[str, dict],
    general_customizations: dict,
) -> dict:
    """Build deterministic profile snapshot data from consultant, blocks, and customizations."""
    blocks_by_id = {block["id"]: block for block in blocks}

    selected_blocks: list[dict] = []
    missing_block_ids: list[int] = []
    for block_id in selected_block_ids:
        block = blocks_by_id.get(block_id)
        if block:
            selected_blocks.append(block)
        else:
            missing_block_ids.append(block_id)

    if missing_block_ids:
        raise ValueError("One or more selected blocks were not found for this consultant.")

    snapshot = {
        "consultant": {
            "first_name": consultant["first_name"],
            "last_name": consultant["last_name"],
            "title": consultant["title"],
            "email": consultant["email"],
            "photo_url": consultant.get("photo_url"),
        },
        "blocks_by_type": {},
        "generated_at": _utc_now_iso(),
    }

    snapshot["general_customizations"] = {
        "role": _get_customization_value(general_customizations, "role", consultant.get("role")),
        "focus_areas": _get_customization_value(
            general_customizations,
            "focus_areas",
            consultant.get("focus_areas") or [],
        ),
        "years_experience": _get_customization_value(
            general_customizations,
            "years_experience",
            consultant.get("years_experience"),
        ),
        "motto": _get_customization_value(general_customizations, "motto", consultant.get("motto")),
    }

    for block in selected_blocks:
        block_type = block["block_type"]
        snapshot["blocks_by_type"].setdefault(block_type, [])
        block_id_str = str(block["id"])
        snapshot["blocks_by_type"][block_type].append(
            serialize_block(block, customizations.get(block_id_str))
        )

    return snapshot


async def _get_consultant_blocks(
    conn: sqlite3.Connection,
    consultant_id: int,
    selected_block_ids: list[int],
) -> list[dict]:
    """Load selected blocks for a consultant in a single query."""
    if not selected_block_ids:
        return []

    placeholders = ", ".join(["?"] * len(selected_block_ids))
    cursor = conn.execute(
        f"SELECT * FROM blocks WHERE consultant_id = ? AND id IN ({placeholders})",
        [consultant_id, *selected_block_ids],
    )
    return list_from_rows(cursor.fetchall())


async def create_profile(conn: sqlite3.Connection, profile_data: ProfileCreate, admin_id: int) -> dict:
    """Assemble and persist a profile snapshot from selected consultant blocks."""
    consultant = await get_consultant(conn, profile_data.consultant_id)
    if not consultant:
        raise ValueError("Consultant not found.")
    profile_name = profile_data.profile_name.strip()
    if not profile_name:
        raise ValueError("Profile name cannot be empty.")

    selected_block_ids = _normalize_selected_block_ids(profile_data.selected_block_ids)
    blocks = await _get_consultant_blocks(conn, profile_data.consultant_id, selected_block_ids)
    profile_snapshot = _build_profile_snapshot(
        consultant=consultant,
        blocks=blocks,
        selected_block_ids=selected_block_ids,
        customizations=profile_data.customizations,
        general_customizations=profile_data.general_customizations.model_dump(),
    )

    cursor = conn.execute(
        """
        INSERT INTO profiles (consultant_id, profile_name, selected_block_ids, profile_data, created_by_admin_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            profile_data.consultant_id,
            profile_name,
            json.dumps(selected_block_ids),
            json.dumps(profile_snapshot),
            admin_id,
        ),
    )
    profile_id = cursor.lastrowid
    cursor = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
    return dict_from_row(cursor.fetchone())


async def get_profile(conn: sqlite3.Connection, profile_id: int) -> dict | None:
    """Get a profile by id."""
    cursor = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
    row = cursor.fetchone()
    return dict_from_row(row)


async def get_profiles(conn: sqlite3.Connection, skip: int = 0, limit: int = 100) -> list[dict]:
    """Get all profiles ordered by latest creation timestamp."""
    cursor = conn.execute(
        "SELECT * FROM profiles ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, skip),
    )
    return list_from_rows(cursor.fetchall())


async def get_consultant_profiles(conn: sqlite3.Connection, consultant_id: int) -> list[dict]:
    """Get all profiles for a consultant."""
    cursor = conn.execute(
        "SELECT * FROM profiles WHERE consultant_id = ? ORDER BY created_at DESC",
        (consultant_id,),
    )
    return list_from_rows(cursor.fetchall())


async def delete_profile(conn: sqlite3.Connection, profile_id: int) -> bool:
    """Delete a profile and return whether deletion occurred."""
    cursor = conn.execute("SELECT id FROM profiles WHERE id = ?", (profile_id,))
    if not cursor.fetchone():
        return False

    conn.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
    return True


async def update_profile(
    conn: sqlite3.Connection,
    profile_id: int,
    profile_data: ProfileUpdate,
    _admin_id: int,
) -> dict | None:
    """Update an existing profile by rebuilding its snapshot data."""
    cursor = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
    existing = cursor.fetchone()
    if not existing:
        return None

    profile_name = profile_data.profile_name.strip()
    if not profile_name:
        raise ValueError("Profile name cannot be empty.")

    existing_dict = dict_from_row(existing)
    consultant = await get_consultant(conn, existing_dict["consultant_id"])
    if not consultant:
        raise ValueError("Consultant not found.")

    selected_block_ids = _normalize_selected_block_ids(profile_data.selected_block_ids)
    blocks = await _get_consultant_blocks(conn, existing_dict["consultant_id"], selected_block_ids)
    profile_snapshot = _build_profile_snapshot(
        consultant=consultant,
        blocks=blocks,
        selected_block_ids=selected_block_ids,
        customizations=profile_data.customizations,
        general_customizations=profile_data.general_customizations.model_dump(),
    )

    conn.execute(
        """UPDATE profiles
           SET "profile_name" = ?,
               "selected_block_ids" = ?,
               "profile_data" = ?,
               updated_at = CURRENT_TIMESTAMP
           WHERE id = ?""",
        (
            profile_name,
            json.dumps(selected_block_ids),
            json.dumps(profile_snapshot),
            profile_id,
        ),
    )

    cursor = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
    return dict_from_row(cursor.fetchone())


async def duplicate_profile(
    conn: sqlite3.Connection,
    profile_id: int,
    new_profile_name: str,
    admin_id: int,
) -> dict | None:
    """Duplicate an existing profile with a new profile name."""
    cleaned_profile_name = new_profile_name.strip()
    if not cleaned_profile_name:
        raise ValueError("Profile name cannot be empty.")

    cursor = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
    original = cursor.fetchone()
    if not original:
        return None

    original_dict = dict_from_row(original)
    cursor = conn.execute(
        """
        INSERT INTO profiles (consultant_id, profile_name, selected_block_ids, profile_data, created_by_admin_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            original_dict["consultant_id"],
            cleaned_profile_name,
            original_dict["selected_block_ids"],
            original_dict["profile_data"],
            admin_id,
        ),
    )
    new_profile_id = cursor.lastrowid
    cursor = conn.execute("SELECT * FROM profiles WHERE id = ?", (new_profile_id,))
    return dict_from_row(cursor.fetchone())
