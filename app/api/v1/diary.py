from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Request

from app.api.proxy import proxy_delete, proxy_get, proxy_patch, proxy_post
from app.auth import admin_required
from app.schemas import DiaryCreate, DiaryResponse, NoteResponse

router = APIRouter(prefix="/diaries", tags=["diaries"])


@router.get("/")
async def list_diaries(
    request: Request,
    author_ids: Optional[str] = None,
    search: Optional[str] = None,
    started_after: Optional[date] = None,
    finished_before: Optional[date] = None,
):
    """List diaries with optional filtering. `author_ids` is comma-separated."""
    params: dict = {"extended": "true"}
    if author_ids:
        params["author_ids"] = author_ids
    if search:
        params["search"] = search
    if started_after:
        params["started_after"] = started_after.isoformat()
    if finished_before:
        params["finished_before"] = finished_before.isoformat()
    return await proxy_get(request.app.state.db_client, "diaries/", params=params)


@router.get("/{diary_id}", response_model=DiaryResponse)
async def get_diary(diary_id: int, request: Request):
    """Get diary by ID with author info."""
    return await proxy_get(
        request.app.state.db_client,
        f"diaries/{diary_id}",
        params={"extended": "true"},
    )


@router.get("/{diary_id}/notes", response_model=list[NoteResponse])
async def get_diary_notes(diary_id: int, request: Request):
    """Get all notes for a diary."""
    return await proxy_get(
        request.app.state.db_client,
        f"diaries/{diary_id}/notes",
        params={"extended": "true"},
    )


@router.post("/", status_code=201, dependencies=[Depends(admin_required)])
async def create_diary(body: DiaryCreate, request: Request):
    """Create a new diary."""
    return await proxy_post(
        request.app.state.db_client,
        "diaries/",
        body.model_dump(mode="json"),
    )


@router.patch("/{diary_id}", dependencies=[Depends(admin_required)])
async def update_diary(diary_id: int, body: DiaryCreate, request: Request):
    """Update a diary."""
    return await proxy_patch(
        request.app.state.db_client,
        f"diaries/{diary_id}",
        body.model_dump(mode="json"),
    )


@router.delete("/{diary_id}", status_code=204, dependencies=[Depends(admin_required)])
async def delete_diary(diary_id: int, request: Request):
    """Delete a diary."""
    return await proxy_delete(request.app.state.db_client, f"diaries/{diary_id}")
