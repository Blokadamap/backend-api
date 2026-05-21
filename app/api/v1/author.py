from typing import Optional

from fastapi import APIRouter, Depends, Request

from app.api.cache import cached_proxy_get
from app.api.proxy import proxy_get, proxy_post
from app.auth import admin_required
from app.schemas import AuthorCreate, AuthorFilters, AuthorResponse, SexEnum

router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("/", response_model=list[AuthorResponse])
async def list_authors(
    request: Request,
    search: Optional[str] = None,
    sex: Optional[SexEnum] = None,
    has_children: Optional[bool] = None,
    family_status_ids: Optional[str] = None,
    social_class_ids: Optional[str] = None,
    nationality_ids: Optional[str] = None,
    religion_ids: Optional[str] = None,
    education_ids: Optional[str] = None,
    occupation_ids: Optional[str] = None,
    political_party_ids: Optional[str] = None,
):
    """List authors with optional filtering. Multi-value filters take comma-separated ids (e.g. `?nationality_ids=1,2,3`)."""
    params: dict = {"extended": "true"}
    if search:
        params["search"] = search
    if sex:
        params["sex"] = sex.value
    if has_children is not None:
        params["has_children"] = str(has_children).lower()
    for key, value in (
        ("family_status_ids", family_status_ids),
        ("social_class_ids", social_class_ids),
        ("nationality_ids", nationality_ids),
        ("religion_ids", religion_ids),
        ("education_ids", education_ids),
        ("occupation_ids", occupation_ids),
        ("political_party_ids", political_party_ids),
    ):
        if value:
            params[key] = value
    return await proxy_get(request.app.state.db_client, "authors/", params=params)


@router.get("/filters", response_model=AuthorFilters)
async def author_filters(request: Request):
    """Get all filter options for authors."""
    return await cached_proxy_get(request.app.state.db_client, request.app.state.filter_cache, "authors/filters")


@router.get("/{author_id}", response_model=AuthorResponse)
async def get_author(author_id: int, request: Request):
    """Get full author details with all relations."""
    return await proxy_get(
        request.app.state.db_client,
        f"authors/{author_id}",
        params={"extended": "true"},
    )


@router.post("/", response_model=AuthorResponse, status_code=201, dependencies=[Depends(admin_required)])
async def create_author(body: AuthorCreate, request: Request):
    """Create a new author."""
    return await proxy_post(
        request.app.state.db_client,
        "authors/",
        body.model_dump(mode="json"),
    )
