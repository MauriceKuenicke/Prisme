import sqlite3
from datetime import timedelta

from ..schemas.admin import AdminCreate
from ..core.security import verify_password, get_password_hash, create_access_token
from ..core.config import settings
from ..core.database import dict_from_row


async def authenticate_admin(conn: sqlite3.Connection, username: str, password: str) -> dict | None:
    """Authenticate an admin user"""
    cursor = conn.execute(
        "SELECT * FROM admins WHERE username = ?",
        (username,)
    )
    admin = cursor.fetchone()

    if not admin:
        return None

    admin_dict = dict_from_row(admin)
    if not verify_password(password, admin_dict['hashed_password']):
        return None
    if not admin_dict['is_active']:
        return None

    return admin_dict


async def create_admin(conn: sqlite3.Connection, admin_data: AdminCreate) -> dict:
    """Create a new admin user"""
    hashed_password = get_password_hash(admin_data.password)
    cursor = conn.execute(
        """
        INSERT INTO admins (username, email, hashed_password, is_active, is_super_admin, last_login_at)
        VALUES (?, ?, ?, 1, ?, NULL)
        """,
        (admin_data.username, admin_data.email, hashed_password, 1 if admin_data.is_super_admin else 0)
    )
    admin_id = cursor.lastrowid

    # Fetch the created admin
    cursor = conn.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
    return dict_from_row(cursor.fetchone())


async def list_admins(conn: sqlite3.Connection) -> list[dict]:
    """List all admin users."""
    cursor = conn.execute(
        """
        SELECT id, username, email, is_active, is_super_admin, last_login_at, created_at, updated_at
        FROM admins
        ORDER BY created_at ASC, id ASC
        """
    )
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


async def count_super_admins(conn: sqlite3.Connection) -> int:
    """Count current super admin accounts."""
    cursor = conn.execute("SELECT COUNT(*) AS count FROM admins WHERE is_super_admin = 1")
    row = cursor.fetchone()
    return int(row["count"]) if row else 0


async def get_admin_by_id(conn: sqlite3.Connection, admin_id: int) -> dict | None:
    """Get admin by ID"""
    cursor = conn.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
    row = cursor.fetchone()
    return dict_from_row(row)


async def get_admin_by_username(conn: sqlite3.Connection, username: str) -> dict | None:
    """Get admin by username"""
    cursor = conn.execute("SELECT * FROM admins WHERE username = ?", (username,))
    row = cursor.fetchone()
    return dict_from_row(row)


async def get_admin_by_email(conn: sqlite3.Connection, email: str) -> dict | None:
    """Get admin by email address."""
    cursor = conn.execute("SELECT * FROM admins WHERE email = ?", (email,))
    row = cursor.fetchone()
    return dict_from_row(row)


async def update_admin_profile(conn: sqlite3.Connection, admin_id: int, username: str, email: str) -> dict:
    """Update admin profile fields."""
    conn.execute(
        """
        UPDATE admins
        SET username = ?, email = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (username, email, admin_id),
    )
    cursor = conn.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
    return dict_from_row(cursor.fetchone())


async def update_admin_password(
    conn: sqlite3.Connection, admin_id: int, current_password: str, new_password: str
) -> bool:
    """Update admin password after verifying the current password."""
    cursor = conn.execute("SELECT hashed_password FROM admins WHERE id = ?", (admin_id,))
    row = cursor.fetchone()
    if not row:
        return False

    if not verify_password(current_password, row["hashed_password"]):
        return False

    conn.execute(
        """
        UPDATE admins
        SET hashed_password = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (get_password_hash(new_password), admin_id),
    )
    return True


async def update_admin_last_login(conn: sqlite3.Connection, admin_id: int) -> dict | None:
    """Persist last login timestamp for the given admin and return updated record."""
    conn.execute(
        """
        UPDATE admins
        SET last_login_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (admin_id,),
    )
    cursor = conn.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
    return dict_from_row(cursor.fetchone())


async def update_admin_super_admin_status(
    conn: sqlite3.Connection, admin_id: int, is_super_admin: bool
) -> dict | None:
    """Update super admin status for a specific admin account."""
    conn.execute(
        """
        UPDATE admins
        SET is_super_admin = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (1 if is_super_admin else 0, admin_id),
    )
    cursor = conn.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
    return dict_from_row(cursor.fetchone())


def create_admin_token(admin: dict) -> str:
    """Create access token for admin"""
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        data={"sub": admin['username'], "admin_id": admin['id']},
        expires_delta=expires_delta
    )
