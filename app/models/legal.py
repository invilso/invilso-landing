from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Iterator

from pydantic import BaseModel

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "legal_pages.json"


class LegalSectionModel(BaseModel):
    title: str
    items: tuple[str, ...]


class LegalPageModel(BaseModel):
    slug: str
    meta_title: str
    link_title: str
    heading: str
    tagline: str
    intro: str
    updated_at: str
    sections: tuple[LegalSectionModel, ...]


class LegalContent(BaseModel):
    order: tuple[str, ...]
    pages: tuple[LegalPageModel, ...]

    def iter_pages(self) -> Iterator[LegalPageModel]:
        return iter(self.pages)

    def get_page(self, slug: str) -> LegalPageModel | None:
        for page in self.pages:
            if page.slug == slug:
                return page
        return None


@lru_cache()
def load_legal_content() -> LegalContent:
    raw_data = DATA_PATH.read_text(encoding="utf-8")
    return LegalContent.model_validate_json(raw_data)
