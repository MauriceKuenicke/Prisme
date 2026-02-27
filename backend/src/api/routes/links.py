from fastapi import APIRouter, Depends, HTTPException, status

from ...core.database import get_db
from ...api.dependencies import get_current_admin
from ...schemas.access_link import AccessLinkCreate, AccessLinkResponse
from ...services import link_service

router = APIRouter(prefix="/access-links", tags=["access-links"])


@router.post("", response_model=AccessLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_access_link(
    link_data: AccessLinkCreate,
    admin: dict = Depends(get_current_admin),
):
    """Generate temporary access link for consultant"""
    try:
        with get_db() as conn:
            link = await link_service.create_access_link(
                conn,
                link_data.consultant_id,
                admin["id"],
                link_data.validity_hours,
            )
    except ValueError as exc:
        error_message = str(exc)
        error_status = status.HTTP_404_NOT_FOUND if error_message == "Consultant not found." else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=error_status, detail=error_message) from exc
    return link


@router.get("/consultant/{consultant_id}", response_model=list[AccessLinkResponse])
async def get_consultant_links(
    consultant_id: int,
    _admin: dict = Depends(get_current_admin),
):
    """Get all access links for a consultant"""
    with get_db() as conn:
        links = await link_service.get_consultant_links(conn, consultant_id)
    return links


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_access_link(
    link_id: int,
    _admin: dict = Depends(get_current_admin),
):
    """Revoke an access link"""
    with get_db() as conn:
        success = await link_service.revoke_access_link(conn, link_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access link not found")
    return None
