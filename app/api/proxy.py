from __future__ import annotations

from typing import Any

import httpx
from fastapi import HTTPException


async def proxy_get(
    client: httpx.AsyncClient,
    url_path: str,
    params: dict[str, Any] | None = None,
) -> Any:
    """Proxy a GET request to database-core and return the parsed JSON body."""
    data, status = await _fetch_get(client, url_path, params)
    if status >= 400:
        raise HTTPException(status_code=status, detail=data)
    return data


async def _fetch_get(
    client: httpx.AsyncClient,
    url_path: str,
    params: dict[str, Any] | None = None,
) -> tuple[Any, int]:
    full_url = f"{client.base_url}/{url_path}"
    try:
        response = await client.get(full_url, params=params, timeout=10)
        response.raise_for_status()
        return response.json(), 200
    except httpx.RequestError as exc:
        return {"error": str(exc)}, 503
    except httpx.HTTPStatusError as exc:
        return {"error": str(exc)}, exc.response.status_code


async def proxy_post(
    client: httpx.AsyncClient,
    url_path: str,
    body: dict | list,
    success_status: int = 201,
) -> Any:
    """Proxy a POST request to database-core and return the parsed JSON body."""
    data, status = await _fetch_post(client, url_path, body, success_status)
    if status >= 400:
        raise HTTPException(status_code=status, detail=data)
    return data


async def _fetch_post(
    client: httpx.AsyncClient,
    url_path: str,
    body: dict | list,
    success_status: int = 201,
) -> tuple[Any, int]:
    full_url = f"{client.base_url}/{url_path}"
    try:
        response = await client.post(full_url, json=body, timeout=10)
        response.raise_for_status()
        return response.json(), success_status
    except httpx.RequestError as exc:
        return {"error": str(exc)}, 503
    except httpx.HTTPStatusError as exc:
        return {"error": str(exc)}, exc.response.status_code


async def proxy_patch(
    client: httpx.AsyncClient,
    url_path: str,
    body: dict | list,
) -> Any:
    """Proxy a PATCH request to database-core and return the parsed JSON body."""
    full_url = f"{client.base_url}/{url_path}"
    try:
        response = await client.patch(full_url, json=body, timeout=10)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail={"error": str(exc)})
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail={"error": str(exc)})


async def proxy_delete(
    client: httpx.AsyncClient,
    url_path: str,
) -> None:
    """Proxy a DELETE request to database-core."""
    full_url = f"{client.base_url}/{url_path}"
    try:
        response = await client.delete(full_url, timeout=10)
        response.raise_for_status()
        return None
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail={"error": str(exc)})
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail={"error": str(exc)})
