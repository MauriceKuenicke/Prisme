import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from ...api.dependencies import get_current_admin
from ...core.database import get_db
from ...schemas.admin import (
    AdminCreate,
    AdminPasswordUpdate,
    AdminProfileUpdate,
    AdminResponse,
    AdminSuperAdminUpdate,
    LoginRequest,
    Token,
)
from ...services.auth_service import (
    authenticate_admin,
    count_super_admins,
    create_admin,
    create_admin_token,
    get_admin_by_id,
    get_admin_by_email,
    get_admin_by_username,
    list_admins,
    update_admin_last_login,
    update_admin_password,
    update_admin_profile,
    update_admin_super_admin_status,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Admin login endpoint"""
    with get_db() as conn:
        admin = await authenticate_admin(conn, login_data.username, login_data.password)
        if admin:
            admin = await update_admin_last_login(conn, admin["id"]) or admin

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_admin_token(admin)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh_token(admin: dict = Depends(get_current_admin)):
    """Refresh the access token for the authenticated admin."""
    access_token = create_admin_token(admin)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=AdminResponse)
async def get_current_admin_profile(admin: dict = Depends(get_current_admin)):
    """Get the currently authenticated admin profile."""
    return admin


@router.put("/me", response_model=AdminResponse)
async def update_current_admin_profile(
    profile_data: AdminProfileUpdate,
    current_admin: dict = Depends(get_current_admin),
):
    """Update username/email for the currently authenticated admin."""
    with get_db() as conn:
        username_owner = await get_admin_by_username(conn, profile_data.username)
        if username_owner and username_owner["id"] != current_admin["id"]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already in use")

        email_owner = await get_admin_by_email(conn, profile_data.email)
        if email_owner and email_owner["id"] != current_admin["id"]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

        try:
            updated_admin = await update_admin_profile(
                conn,
                admin_id=current_admin["id"],
                username=profile_data.username,
                email=profile_data.email,
            )
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already in use") from exc

    return updated_admin


@router.put("/me/password")
async def change_current_admin_password(
    password_data: AdminPasswordUpdate,
    current_admin: dict = Depends(get_current_admin),
):
    """Change password for the currently authenticated admin."""
    with get_db() as conn:
        password_changed = await update_admin_password(
            conn,
            admin_id=current_admin["id"],
            current_password=password_data.current_password,
            new_password=password_data.new_password,
        )

    if not password_changed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    return {
        "message": "Password updated successfully. Please sign in again with your new credentials.",
        "logout_required": True,
    }


@router.get("/admins", response_model=list[AdminResponse])
async def get_admin_accounts(_: dict = Depends(get_current_admin)):
    """List all admin accounts."""
    with get_db() as conn:
        admins = await list_admins(conn)
    return admins


@router.post("/admins", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_account(
    admin_data: AdminCreate,
    current_admin: dict = Depends(get_current_admin),
):
    """Create a new admin account."""
    if not current_admin.get("is_super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can create admin accounts",
        )

    with get_db() as conn:
        existing_username = await get_admin_by_username(conn, admin_data.username)
        if existing_username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already in use")

        existing_email = await get_admin_by_email(conn, admin_data.email)
        if existing_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

        try:
            created_admin = await create_admin(conn, admin_data)
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already in use") from exc

    return created_admin


@router.put("/admins/{admin_id}/super-admin", response_model=AdminResponse)
async def update_admin_super_admin_role(
    admin_id: int,
    role_data: AdminSuperAdminUpdate,
    current_admin: dict = Depends(get_current_admin),
):
    """Update super admin status for another admin account."""
    if not current_admin.get("is_super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can update super admin status",
        )

    if admin_id == current_admin["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own super admin status",
        )

    with get_db() as conn:
        target_admin = await get_admin_by_id(conn, admin_id)
        if not target_admin:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

        if target_admin.get("is_super_admin") and not role_data.is_super_admin:
            super_admin_count = await count_super_admins(conn)
            if super_admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="At least one super admin is required",
                )

        updated_admin = await update_admin_super_admin_status(
            conn, admin_id=admin_id, is_super_admin=role_data.is_super_admin
        )

    return updated_admin


@router.post("/logout")
async def logout():
    """Admin logout endpoint"""
    # Since we're using JWT, logout is handled client-side
    return {"message": "Successfully logged out"}
