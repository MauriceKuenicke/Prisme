from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..core.database import get_db
from ..core.security import verify_token
from ..services.auth_service import get_admin_by_id, get_admin_by_username
from ..services.link_service import validate_access_link

security = HTTPBearer(auto_error=False)


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
) -> dict:
    """Resolve the currently authenticated admin from a bearer token."""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    username = payload.get("sub")
    admin_id = payload.get("admin_id")

    if not username and admin_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    with get_db() as conn:
        admin = None
        if admin_id is not None:
            try:
                admin = await get_admin_by_id(conn, int(admin_id))
            except (TypeError, ValueError):
                admin = None

        # Fallback for older tokens or unexpected payload shape.
        if not admin and username:
            admin = await get_admin_by_username(conn, username)

    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")

    if not admin["is_active"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive admin")

    return admin


async def validate_temp_link(token: str) -> dict:
    """Validate temporary access link token and return link metadata."""
    with get_db() as conn:
        link = await validate_access_link(conn, token)

    if not link:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired access link",
        )

    return link
