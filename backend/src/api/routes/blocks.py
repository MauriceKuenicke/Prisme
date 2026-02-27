from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status, Query

from ...core.database import get_db
from ...api.dependencies import get_current_admin, validate_temp_link
from ...schemas.block import BlockCreate, BlockUpdate, BlockResponse, BlockReorderRequest
from ...services import block_service

router = APIRouter(prefix="/blocks", tags=["blocks"])


# Admin routes (authenticated)
@router.get("/consultant/{consultant_id}", response_model=list[BlockResponse])
async def get_consultant_blocks(
    consultant_id: int,
    block_type: Literal["project", "skill", "misc", "certification"] | None = Query(default=None),
    _admin: dict = Depends(get_current_admin),
):
    """Get all blocks for a consultant (admin access)"""
    with get_db() as conn:
        blocks = await block_service.get_consultant_blocks(conn, consultant_id, block_type)
    return blocks


# Temporary link routes (no auth, token in URL)
@router.get("/edit/{token}", response_model=list[BlockResponse])
async def get_blocks_via_token(
    token: str,
    block_type: Literal["project", "skill", "misc", "certification"] | None = Query(default=None),
):
    """Get consultant blocks via temporary link"""
    link = await validate_temp_link(token)
    with get_db() as conn:
        blocks = await block_service.get_consultant_blocks(conn, link['consultant_id'], block_type)
    return blocks


@router.post("/edit/{token}", response_model=BlockResponse, status_code=status.HTTP_201_CREATED)
async def create_block_via_token(
    token: str,
    block_data: BlockCreate,
):
    """Create block via temp link"""
    link = await validate_temp_link(token)
    with get_db() as conn:
        block = await block_service.create_block(conn, link['consultant_id'], block_data)
    return block


@router.put("/edit/{token}/{block_id}", response_model=BlockResponse)
async def update_block_via_token(
    token: str,
    block_id: int,
    block_data: BlockUpdate,
):
    """Update block via temp link"""
    link = await validate_temp_link(token)

    # Verify block belongs to consultant
    with get_db() as conn:
        block = await block_service.get_block(conn, block_id)
        if not block or block["consultant_id"] != link["consultant_id"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")

        updated_block = await block_service.update_block(conn, block_id, block_data)
    return updated_block


@router.delete("/edit/{token}/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_block_via_token(
    token: str,
    block_id: int,
):
    """Delete block via temp link"""
    link = await validate_temp_link(token)

    # Verify block belongs to consultant
    with get_db() as conn:
        block = await block_service.get_block(conn, block_id)
        if not block or block["consultant_id"] != link["consultant_id"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")

        await block_service.delete_block(conn, block_id)
    return None


@router.post("/edit/{token}/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_blocks_via_token(
    token: str,
    reorder_data: BlockReorderRequest,
):
    """Reorder blocks via temp link"""
    link = await validate_temp_link(token)
    with get_db() as conn:
        await block_service.reorder_blocks(conn, link['consultant_id'], reorder_data.block_orders)
    return None
