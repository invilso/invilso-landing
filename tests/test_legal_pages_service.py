from __future__ import annotations

from typing import Iterator

import pytest

from app.models import legal as legal_models
from app.services import legal_pages


@pytest.fixture(autouse=True)
def clear_legal_caches() -> Iterator[None]:
    legal_pages._pages_by_slug.cache_clear()  # type: ignore[attr-defined]
    legal_models.load_legal_content.cache_clear()  # type: ignore[attr-defined]
    yield
    legal_pages._pages_by_slug.cache_clear()  # type: ignore[attr-defined]
    legal_models.load_legal_content.cache_clear()  # type: ignore[attr-defined]


def test_get_legal_page_returns_expected_slug() -> None:
    page = legal_pages.get_legal_page("privacy")
    assert page is not None
    assert page.heading == "Privacy Policy"
    assert len(page.sections) > 0


def test_get_legal_page_returns_none_for_unknown_slug() -> None:
    assert legal_pages.get_legal_page("unknown") is None


def test_get_legal_links_preserves_order() -> None:
    links = legal_pages.get_legal_links()
    slugs = [link["slug"] for link in links]
    assert slugs == ["terms", "privacy", "cookies"]


def test_get_ordered_pages_matches_links() -> None:
    ordered_pages = legal_pages.get_ordered_pages()
    assert [page.slug for page in ordered_pages] == ["terms", "privacy", "cookies"]
    assert all(page.sections for page in ordered_pages)


def test_legal_content_helpers_cover_all_paths() -> None:
    content = legal_models.load_legal_content()
    all_pages = tuple(content.iter_pages())
    assert len(all_pages) == 3
    terms = content.get_page("terms")
    assert terms is not None
    assert terms.slug == "terms"
    assert content.get_page("missing") is None
