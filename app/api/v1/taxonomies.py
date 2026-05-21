"""Admin-only CUD endpoints for filter taxonomies (family statuses, nationalities, tags, etc.)."""
from fastapi import APIRouter, Depends, Request

from app.api.proxy import proxy_delete, proxy_get, proxy_patch, proxy_post
from app.auth import admin_required
from app.schemas import NamedCreate

router = APIRouter(prefix="/taxonomies", tags=["taxonomies"])


# (api_prefix, db_path) pairs — backend exposes them under /api/v1/taxonomies/<api_prefix>
NAMED_TAXONOMIES = {
    "family-statuses": "authors/family-statuses",
    "social-classes": "authors/social-classes",
    "nationalities": "authors/nationalities",
    "religions": "authors/religions",
    "educations": "authors/educations",
    "occupations": "authors/occupations",
    "political-parties": "authors/political-parties",
    "cards": "authors/cards",
    "note-types": "notes/note-types",
    "temporalities": "notes/temporalities",
    "tags": "notes/tags",
    "rayons": "points/rayons",
}


def _register(api_prefix: str, db_path: str) -> None:
    @router.get(f"/{api_prefix}", name=f"list_{api_prefix}")
    async def list_items(request: Request):
        return await proxy_get(request.app.state.db_client, f"{db_path}/")

    @router.post(
        f"/{api_prefix}",
        status_code=201,
        name=f"create_{api_prefix}",
        dependencies=[Depends(admin_required)],
    )
    async def create_item(body: NamedCreate, request: Request):
        return await proxy_post(
            request.app.state.db_client,
            f"{db_path}/",
            body.model_dump(mode="json"),
        )

    @router.patch(
        f"/{api_prefix}/{{item_id}}",
        name=f"update_{api_prefix}",
        dependencies=[Depends(admin_required)],
    )
    async def update_item(item_id: int, body: NamedCreate, request: Request):
        return await proxy_patch(
            request.app.state.db_client,
            f"{db_path}/{item_id}",
            body.model_dump(mode="json"),
        )

    @router.delete(
        f"/{api_prefix}/{{item_id}}",
        status_code=204,
        name=f"delete_{api_prefix}",
        dependencies=[Depends(admin_required)],
    )
    async def delete_item(item_id: int, request: Request):
        return await proxy_delete(request.app.state.db_client, f"{db_path}/{item_id}")


for api_prefix, db_path in NAMED_TAXONOMIES.items():
    _register(api_prefix, db_path)
