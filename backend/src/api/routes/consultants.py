import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...core.database import get_db
from ...api.dependencies import get_current_admin, validate_temp_link
from ...schemas.consultant import ConsultantCreate, ConsultantUpdate, ConsultantResponse
from ...services import consultant_service

router = APIRouter(prefix="/consultants", tags=["consultants"])


def _is_unique_email_error(exc: sqlite3.IntegrityError) -> bool:
    """Detect unique email violations for consultant writes."""
    message = str(exc)
    return "consultants.email" in message or "UNIQUE constraint failed: consultants.email" in message


@router.post("", response_model=ConsultantResponse, status_code=status.HTTP_201_CREATED)
async def create_consultant(
    consultant_data: ConsultantCreate,
    admin: dict = Depends(get_current_admin),
):
    """Create a new consultant"""
    try:
        with get_db() as conn:
            consultant = await consultant_service.create_consultant(conn, consultant_data, admin["id"])
    except sqlite3.IntegrityError as exc:
        if _is_unique_email_error(exc):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use") from exc
        raise
    return consultant


@router.get("", response_model=list[ConsultantResponse])
async def list_consultants(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    _admin: dict = Depends(get_current_admin),
):
    """List all consultants"""
    with get_db() as conn:
        consultants = await consultant_service.get_consultants(conn, skip, limit)
    return consultants


@router.get("/{consultant_id}", response_model=ConsultantResponse)
async def get_consultant(
    consultant_id: int,
    _admin: dict = Depends(get_current_admin)
):
    """Get consultant details"""
    with get_db() as conn:
        consultant = await consultant_service.get_consultant(conn, consultant_id)
    if not consultant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultant not found")
    return consultant


@router.put("/{consultant_id}", response_model=ConsultantResponse)
async def update_consultant(
    consultant_id: int,
    consultant_data: ConsultantUpdate,
    _admin: dict = Depends(get_current_admin),
):
    """Update consultant"""
    try:
        with get_db() as conn:
            consultant = await consultant_service.update_consultant(conn, consultant_id, consultant_data)
    except sqlite3.IntegrityError as exc:
        if _is_unique_email_error(exc):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use") from exc
        raise
    if not consultant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultant not found")
    return consultant


@router.delete("/{consultant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_consultant(
    consultant_id: int,
    _admin: dict = Depends(get_current_admin)
):
    """Delete consultant"""
    with get_db() as conn:
        success = await consultant_service.delete_consultant(conn, consultant_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultant not found")
    return None


# Temporary link routes (no auth, token in URL)
@router.get("/edit/{token}", response_model=ConsultantResponse)
async def get_consultant_via_token(token: str):
    """Get consultant data via temporary link"""
    link = await validate_temp_link(token)
    with get_db() as conn:
        consultant = await consultant_service.get_consultant(conn, link['consultant_id'])
    if not consultant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultant not found")
    return consultant


@router.put("/edit/{token}", response_model=ConsultantResponse)
async def update_consultant_via_token(
    token: str,
    consultant_data: ConsultantUpdate
):
    """Update consultant general section via temporary link"""
    link = await validate_temp_link(token)
    try:
        with get_db() as conn:
            consultant = await consultant_service.update_consultant(conn, link["consultant_id"], consultant_data)
    except sqlite3.IntegrityError as exc:
        if _is_unique_email_error(exc):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use") from exc
        raise
    if not consultant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultant not found")
    return consultant
