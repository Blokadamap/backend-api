from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Request

from app.api.cache import cached_proxy_get
from app.api.proxy import proxy_get, proxy_post
from app.auth import admin_required
from app.schemas import NoteCreate, NoteDetailed, NoteFilters, NoteResponse, TagCreate

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/filters", response_model=NoteFilters)
async def note_filters(request: Request):
    """Get all filter options for notes."""
    return await cached_proxy_get(request.app.state.db_client, request.app.state.filter_cache, "notes/filters")


@router.get("/")
async def list_notes(
    request: Request,
    search: Optional[str] = None,
    note_type_ids: Optional[str] = None,
    temporality_ids: Optional[str] = None,
    diary_ids: Optional[str] = None,
    author_ids: Optional[str] = None,
    tag_ids: Optional[str] = None,
    point_ids: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    """List notes with optional filtering. Multi-value filters take comma-separated ids."""
    params: dict = {"extended": "true"}
    if search:
        params["search"] = search
    for key, value in (
        ("note_type_ids", note_type_ids),
        ("temporality_ids", temporality_ids),
        ("diary_ids", diary_ids),
        ("author_ids", author_ids),
        ("tag_ids", tag_ids),
        ("point_ids", point_ids),
    ):
        if value:
            params[key] = value
    if date_from:
        params["date_from"] = date_from.isoformat()
    if date_to:
        params["date_to"] = date_to.isoformat()
    return await proxy_get(request.app.state.db_client, "notes/", params=params)


@router.post("/tags", status_code=201, dependencies=[Depends(admin_required)])
async def create_tag(body: TagCreate, request: Request):
    """Create a new tag."""
    return await proxy_post(
        request.app.state.db_client,
        "notes/tags/",
        body.model_dump(mode="json"),
    )


@router.get("/detailed/{note_id}", response_model=NoteDetailed)
async def detailed_note(note_id: int, request: Request):
    """Get note with full author and point details."""
    return await proxy_get(request.app.state.db_client, f"notes/detailed/{note_id}")


@router.get("/by-point/{point_id}")
async def notes_by_point(point_id: int, request: Request):
    """List full notes for a specific point."""
    return await proxy_get(
        request.app.state.db_client,
        f"points/{point_id}/notes",
        params={"extended": "true"},
    )


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int, request: Request):
    """Get full note details with relations."""
    return await proxy_get(
        request.app.state.db_client,
        f"notes/{note_id}",
        params={"extended": "true"},
    )


@router.post("/", response_model=NoteResponse, status_code=201, dependencies=[Depends(admin_required)])
async def create_note(body: NoteCreate, request: Request):
    """Create a new note."""
    return await proxy_post(
        request.app.state.db_client,
        "notes/",
        body.model_dump(mode="json"),
    )
