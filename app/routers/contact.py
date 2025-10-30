from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from limits import RateLimitItemPerHour

from app.schemas import ContactRequest, ContactResponse
from app.services.rate_limit import rate_limit_by_ip
from app.services.telegram import send_telegram_message
from app.workers import registry

router = APIRouter(prefix="/contact", tags=["contact"])
CONTACT_REQUESTS_PER_HOUR = 3

contact_rate_limit = rate_limit_by_ip(
    RateLimitItemPerHour(CONTACT_REQUESTS_PER_HOUR),
    namespace="contact",
    detail="Too many contact requests from this address. Please try again later.",
)


@router.post("", response_model=ContactResponse, status_code=status.HTTP_202_ACCEPTED)
async def enqueue_contact_message(
    payload: ContactRequest,
    request: Request,
    rate_limit_check: None = Depends(contact_rate_limit),
) -> ContactResponse:
    redis_queue = getattr(request.app.state, "redis", None)
    if redis_queue is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Job queue unavailable.")

    job_name = registry.job_name(send_telegram_message)
    await redis_queue.enqueue_job(job_name, payload.model_dump())
    return ContactResponse(queued=True)
