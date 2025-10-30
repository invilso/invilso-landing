from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from app.services.legal_pages import get_legal_links, get_legal_page

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
STATIC_ROOT = Path(__file__).resolve().parent.parent.parent / "static"
ROBOTS_PATH = STATIC_ROOT / "robots.txt"
SITEMAP_PATH = STATIC_ROOT / "sitemap.xml"

router = APIRouter(include_in_schema=False)

LEGAL_LINKS = get_legal_links()


@router.get("/", name="home")
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"legal_links": LEGAL_LINKS},
    )


@router.get("/robots.txt", include_in_schema=False)
async def robots_txt() -> FileResponse:
    return FileResponse(ROBOTS_PATH, media_type="text/plain")


@router.get("/sitemap.xml", include_in_schema=False)
async def sitemap_xml() -> FileResponse:
    return FileResponse(SITEMAP_PATH, media_type="application/xml")


@router.get("/legal/{slug}", name="legal-page")
async def legal_page(slug: str, request: Request):
    page = get_legal_page(slug)
    if page is None:
        raise HTTPException(status_code=404, detail="Legal document not found.")

    other_links = tuple(link for link in LEGAL_LINKS if link["slug"] != slug)
    return templates.TemplateResponse(
        request,
        "legal.html",
        {
            "page": page,
            "legal_links": LEGAL_LINKS,
            "other_links": other_links,
        },
    )
