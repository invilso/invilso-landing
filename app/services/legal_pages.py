from __future__ import annotations

from functools import lru_cache

from app.models.legal import LegalContent, LegalPageModel, load_legal_content


@lru_cache()
def _pages_by_slug() -> dict[str, LegalPageModel]:
    content = load_legal_content()
    return {page.slug: page for page in content.iter_pages()}


def get_legal_page(slug: str) -> LegalPageModel | None:
    pages = _pages_by_slug()
    return pages.get(slug)


def get_legal_links() -> tuple[dict[str, str], ...]:
    content: LegalContent = load_legal_content()
    pages = _pages_by_slug()
    return tuple({"slug": slug, "title": pages[slug].link_title} for slug in content.order if slug in pages)


def get_ordered_pages() -> tuple[LegalPageModel, ...]:
    content = load_legal_content()
    pages = _pages_by_slug()
    return tuple(pages[slug] for slug in content.order if slug in pages)
