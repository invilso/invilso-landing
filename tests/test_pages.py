from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_home_page_renders(client: httpx.AsyncClient) -> None:
    response = await client.get("/")

    assert response.status_code == httpx.codes.OK
    assert "Python Back-End Contractor & Consultant" in response.text


@pytest.mark.asyncio
async def test_legal_page_renders(client: httpx.AsyncClient) -> None:
    response = await client.get("/legal/privacy")

    assert response.status_code == httpx.codes.OK
    assert "Privacy Policy" in response.text
    assert "Data Collected" in response.text


@pytest.mark.asyncio
async def test_unknown_legal_page_returns_404(client: httpx.AsyncClient) -> None:
    response = await client.get("/legal/unknown")

    assert response.status_code == httpx.codes.NOT_FOUND
    assert response.json()["detail"] == "Legal document not found."
