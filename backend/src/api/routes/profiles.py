import io
import logging
import re
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from ...core.database import get_db
from ...api.dependencies import get_current_admin
from ...schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from ...services import profile_service
from ...services import profile_export_service

router = APIRouter(prefix="/profiles", tags=["profiles"])
logger = logging.getLogger(__name__)
HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    admin: dict = Depends(get_current_admin),
):
    """Create a new profile snapshot."""
    with get_db() as conn:
        try:
            profile = await profile_service.create_profile(conn, profile_data, admin["id"])
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return profile


@router.get("", response_model=list[ProfileResponse])
async def list_profiles(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    _admin: dict = Depends(get_current_admin),
):
    """List all profiles"""
    with get_db() as conn:
        profiles = await profile_service.get_profiles(conn, skip, limit)
    return profiles


@router.get("/consultant/{consultant_id}", response_model=list[ProfileResponse])
async def get_consultant_profiles(
    consultant_id: int,
    _admin: dict = Depends(get_current_admin),
):
    """Get all profiles for a consultant"""
    with get_db() as conn:
        profiles = await profile_service.get_consultant_profiles(conn, consultant_id)
    return profiles


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: int,
    _admin: dict = Depends(get_current_admin),
):
    """Get profile details"""
    with get_db() as conn:
        profile = await profile_service.get_profile(conn, profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int,
    profile_data: ProfileUpdate,
    admin: dict = Depends(get_current_admin),
):
    """Update an existing profile snapshot."""
    with get_db() as conn:
        try:
            profile = await profile_service.update_profile(conn, profile_id, profile_data, admin["id"])
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: int,
    _admin: dict = Depends(get_current_admin),
):
    """Delete profile"""
    with get_db() as conn:
        success = await profile_service.delete_profile(conn, profile_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return None


@router.post("/{profile_id}/duplicate", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_profile(
    profile_id: int,
    new_profile_name: str = Query(min_length=1, max_length=200),
    admin: dict = Depends(get_current_admin),
):
    """Duplicate an existing profile with a new name"""
    try:
        with get_db() as conn:
            profile = await profile_service.duplicate_profile(conn, profile_id, new_profile_name, admin["id"])
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.post("/{profile_id}/export/pdf")
async def export_profile_pdf(
    profile_id: int,
    company_name: Optional[str] = Form(None),
    accent_color: Optional[str] = Form("#0E4B8A"),
    template: Optional[str] = Form("default"),
    _admin: dict = Depends(get_current_admin),
):
    """Export profile as professional PDF document."""

    # Validate profile exists
    with get_db() as conn:
        profile = await profile_service.get_profile(conn, profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    # Validate accent_color format
    if accent_color and not HEX_COLOR_RE.match(accent_color):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid accent_color. Must be hex format like #0E4B8A",
        )

    try:
        # Export profile to PDF
        pdf_bytes, filename = profile_export_service.export_profile_to_pdf(
            profile_data=profile["profile_data"],
            company_name=company_name,
            accent_color=accent_color,
            template=template,
        )

        # Return PDF as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    except Exception:
        logger.exception("PDF export failed for profile %s", profile_id)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Export failed. Please try again or contact support.",
        )


@router.get("/{profile_id}/export")
async def export_profile(
    profile_id: int,
    _admin: dict = Depends(get_current_admin),
):
    """Export profile as formatted document (legacy endpoint, redirects to PDF)"""
    with get_db() as conn:
        profile = await profile_service.get_profile(conn, profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return {"message": "Use POST /profiles/{profile_id}/export/pdf for PDF export"}
