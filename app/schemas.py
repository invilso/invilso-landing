from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class ContactRequest(BaseModel):
    """Validated payload for contact submissions."""

    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    message: str = Field(..., min_length=10, max_length=2000)


class ContactResponse(BaseModel):
    """Acknowledgement returned once a job is queued."""

    queued: bool = Field(..., description="Indicates whether the background job was submitted.")
