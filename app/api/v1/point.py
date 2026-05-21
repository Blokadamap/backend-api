from typing import Optional

from fastapi import APIRouter, Depends, Request

from app.api.cache import cached_proxy_get
from app.api.proxy import proxy_get, proxy_post
from app.auth import admin_required
from app.schemas import (
    CoordinatesCreate,
    PointCoordinatesResponse,
    PointCreate,
    PointFilters,
    PointResponse,
    PointSubSubTypeCreate,
    PointSubTypeCreate,
    PointTypeCreate,
)

router = APIRouter(prefix="/points", tags=["points"])


@router.get("/filters", response_model=PointFilters)
async def point_filters(request: Request):
    """Get type hierarchy filter options for points."""
    return await cached_proxy_get(request.app.state.db_client, request.app.state.filter_cache, "points/filters")


@router.get("/", response_model=list[PointResponse])
async def list_points(
    request: Request,
    search: Optional[str] = None,
    rayon_ids: Optional[str] = None,
    point_type_ids: Optional[str] = None,
    point_subtype_ids: Optional[str] = None,
    point_subsubtype_ids: Optional[str] = None,
):
    """List points with optional filtering. Multi-value filters take comma-separated ids."""
    params: dict = {"extended": "true"}
    if search:
        params["search"] = search
    for key, value in (
        ("rayon_ids", rayon_ids),
        ("point_type_ids", point_type_ids),
        ("point_subtype_ids", point_subtype_ids),
        ("point_subsubtype_ids", point_subsubtype_ids),
    ):
        if value:
            params[key] = value
    return await proxy_get(request.app.state.db_client, "points/", params=params)


@router.post("/", response_model=PointResponse, status_code=201, dependencies=[Depends(admin_required)])
async def create_point(body: PointCreate, request: Request):
    """Create a new point."""
    return await proxy_post(
        request.app.state.db_client,
        "points/",
        body.model_dump(mode="json"),
    )


# Point taxonomy creation — admin only
@router.post("/point-types", status_code=201, dependencies=[Depends(admin_required)])
async def create_point_type(body: PointTypeCreate, request: Request):
    return await proxy_post(
        request.app.state.db_client,
        "points/point-types",
        body.model_dump(mode="json"),
    )


@router.post("/point-subtypes", status_code=201, dependencies=[Depends(admin_required)])
async def create_point_subtype(body: PointSubTypeCreate, request: Request):
    return await proxy_post(
        request.app.state.db_client,
        "points/point-subtypes",
        body.model_dump(mode="json"),
    )


@router.post("/point-subsubtypes", status_code=201, dependencies=[Depends(admin_required)])
async def create_point_subsubtype(body: PointSubSubTypeCreate, request: Request):
    return await proxy_post(
        request.app.state.db_client,
        "points/point-subsubtypes",
        body.model_dump(mode="json"),
    )


@router.get("/{point_id}", response_model=PointResponse)
async def get_point(point_id: int, request: Request):
    """Get full point details with all relations."""
    return await proxy_get(
        request.app.state.db_client,
        f"points/{point_id}",
        params={"extended": "true"},
    )


@router.get("/{point_id}/coordinates", response_model=PointCoordinatesResponse)
async def get_point_coordinates(point_id: int, request: Request):
    """Get all coordinates for a point."""
    return await proxy_get(
        request.app.state.db_client,
        f"points/{point_id}/coordinates",
    )


@router.get("/{point_id}/notes")
async def get_point_notes(point_id: int, request: Request):
    """Get all notes associated with a point."""
    return await proxy_get(
        request.app.state.db_client,
        f"points/{point_id}/notes",
    )


@router.post("/{point_id}/coordinates", status_code=201, dependencies=[Depends(admin_required)])
async def add_point_coordinates(
    point_id: int, body: CoordinatesCreate, request: Request
):
    """Add coordinates to an existing point."""
    return await proxy_post(
        request.app.state.db_client,
        f"points/{point_id}/coordinates",
        body.model_dump(mode="json"),
    )
