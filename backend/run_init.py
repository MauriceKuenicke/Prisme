"""CLI entrypoint to apply database migrations."""

import subprocess
import sys
from pathlib import Path


def run_migrations() -> None:
    """Apply Alembic migrations to the latest revision."""
    backend_root = Path(__file__).resolve().parent
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=backend_root,
        check=True,
    )


if __name__ == "__main__":
    print("Applying database migrations...")
    try:
        run_migrations()
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] Migration failed: {exc}")
        raise SystemExit(1) from exc

    print("[OK] Database migrations complete.")
    print("[INFO] Default admin credentials are seeded by Alembic migrations.")
