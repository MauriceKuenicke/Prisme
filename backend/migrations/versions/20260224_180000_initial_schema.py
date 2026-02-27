"""initial_schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-02-24 18:00:00

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT 1 NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            is_super_admin BOOLEAN DEFAULT 0 NOT NULL,
            last_login_at TIMESTAMP
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_admins_username ON admins(username)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_admins_email ON admins(email)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS consultants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            title VARCHAR(200) NOT NULL,
            summary TEXT,
            photo_url VARCHAR(500),
            role VARCHAR(200),
            focus_areas TEXT,
            years_experience INTEGER,
            motto TEXT,
            created_by_admin_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (created_by_admin_id) REFERENCES admins(id)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_consultants_email ON consultants(email)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_consultants_created_by ON consultants(created_by_admin_id)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consultant_id INTEGER NOT NULL,
            block_type VARCHAR(50) NOT NULL,
            title VARCHAR(200) NOT NULL,
            "order" INTEGER DEFAULT 0 NOT NULL,
            is_active BOOLEAN DEFAULT 1 NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

            client_name VARCHAR(200),
            project_description TEXT,
            role VARCHAR(200),
            technologies TEXT,
            start_date DATE,
            end_date DATE,
            is_ongoing BOOLEAN DEFAULT 0,
            duration_months INTEGER,

            proficiency_level VARCHAR(50),

            misc_content TEXT,

            issuing_organization VARCHAR(200),
            issue_date DATE,
            expiry_date DATE,
            credential_id VARCHAR(200),
            credential_url VARCHAR(500),

            FOREIGN KEY (consultant_id) REFERENCES consultants(id) ON DELETE CASCADE
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_blocks_consultant ON blocks(consultant_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_blocks_type ON blocks(block_type)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_blocks_active ON blocks(is_active)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS access_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consultant_id INTEGER NOT NULL,
            token VARCHAR(255) UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_by_admin_id INTEGER NOT NULL,
            is_used BOOLEAN DEFAULT 0 NOT NULL,
            last_accessed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (consultant_id) REFERENCES consultants(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by_admin_id) REFERENCES admins(id)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_access_links_consultant ON access_links(consultant_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_access_links_token ON access_links(token)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_access_links_expires ON access_links(expires_at)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consultant_id INTEGER NOT NULL,
            profile_name VARCHAR(200) NOT NULL,
            selected_block_ids TEXT NOT NULL,
            profile_data TEXT NOT NULL,
            created_by_admin_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (consultant_id) REFERENCES consultants(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by_admin_id) REFERENCES admins(id)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_profiles_consultant ON profiles(consultant_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS profiles")
    op.execute("DROP TABLE IF EXISTS access_links")
    op.execute("DROP TABLE IF EXISTS blocks")
    op.execute("DROP TABLE IF EXISTS consultants")
    op.execute("DROP TABLE IF EXISTS admins")
