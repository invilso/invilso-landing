from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates


@dataclass(frozen=True)
class LegalSection:
    title: str
    items: tuple[str, ...]


@dataclass(frozen=True)
class LegalPage:
    slug: str
    meta_title: str
    link_title: str
    heading: str
    tagline: str
    intro: str
    updated_at: str
    sections: tuple[LegalSection, ...]


templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
STATIC_ROOT = Path(__file__).resolve().parent.parent.parent / "static"
ROBOTS_PATH = STATIC_ROOT / "robots.txt"
SITEMAP_PATH = STATIC_ROOT / "sitemap.xml"

router = APIRouter(include_in_schema=False)


def _legal_page_links(pages: Iterable[LegalPage]) -> tuple[dict[str, str], ...]:
    return tuple({"slug": page.slug, "title": page.link_title} for page in pages)


LEGAL_PAGES = {
    "terms": LegalPage(
        slug="terms",
        meta_title="Terms & Conditions | INVILSO SCRIPTS",
        link_title="Terms & Conditions",
        heading="Terms & Conditions",
        tagline="The legal framework for working with INVILSO SCRIPTS.",
        intro=(
            "These terms outline how I deliver consulting and development services and what"
            " you can expect when we collaborate."
        ),
        updated_at="Last updated: May 7, 2025",
        sections=(
            LegalSection(
                title="Scope of Services",
                items=(
                    "Professional software architecture, API development, automation, and related consulting are provided on a project basis.",
                    "All deliverables, milestones, and acceptance criteria are agreed before the engagement begins.",
                    "Out-of-scope requests are handled through written change requests and may involve revised estimates.",
                ),
            ),
            LegalSection(
                title="Engagement & Communication",
                items=(
                    "Project kick-off, weekly checkpoints, and delivery reviews are coordinated via the preferred communication channels we agree to.",
                    "Response times are typically within one business day, excluding weekends and regional holidays.",
                    "You agree to provide timely feedback, assets, and credentials required to keep the project on schedule.",
                ),
            ),
            LegalSection(
                title="Deliverables & Acceptance",
                items=(
                    "Source code, documentation, and deployment assets are delivered through the version control or infrastructure we select together.",
                    "A deliverable is considered accepted once the agreed review period lapses without written change requests or once it is approved in writing.",
                    "Post-acceptance refinements are handled under a new scope or maintenance agreement unless otherwise specified.",
                ),
            ),
            LegalSection(
                title="Fees & Payment",
                items=(
                    "Pricing follows the proposal or statement of work and can be fixed-fee or time-and-materials depending on project needs.",
                    "Invoices are issued in the agreed currency with payment due within 14 calendar days unless stated otherwise.",
                    "Late payments may pause ongoing work until the outstanding balance is cleared.",
                ),
            ),
            LegalSection(
                title="Intellectual Property",
                items=(
                    "Upon full payment, you receive full rights to the bespoke deliverables created for the project.",
                    "Pre-existing tooling, libraries, or know-how remain the property of INVILSO SCRIPTS and may be reused across engagements.",
                    "Open-source components stay subject to their original licenses, which are referenced in project documentation.",
                ),
            ),
            LegalSection(
                title="Liability & Warranty",
                items=(
                    "All services are provided with industry-standard care and tested against mutually defined criteria.",
                    "Liability for indirect, incidental, or consequential damages is disclaimed to the fullest extent permitted by law.",
                    "If a defect attributable to my work is discovered within 30 days of delivery, I will address it without additional cost.",
                ),
            ),
        ),
    ),
    "privacy": LegalPage(
        slug="privacy",
        meta_title="Privacy Policy | INVILSO SCRIPTS",
        link_title="Privacy Policy",
        heading="Privacy Policy",
        tagline="How INVILSO SCRIPTS handles client and contact data.",
        intro=(
            "I collect only the information required to respond to inquiries, deliver services, and run this site reliably."
        ),
        updated_at="Last updated: May 7, 2025",
        sections=(
            LegalSection(
                title="Data Collected",
                items=(
                    "Contact form submissions capture your name, email address, and message so I can reply.",
                    "Project communications may include files, credentials, and meeting notes shared through agreed secure channels.",
                    "Basic technical telemetry (such as IP address and user agent) is logged by hosting providers for security and auditing.",
                ),
            ),
            LegalSection(
                title="How Data Is Used",
                items=(
                    "Responding to inquiries, preparing proposals, and performing contracted services.",
                    "Maintaining accurate records for accounting, taxation, and project history.",
                    "Protecting the platform against abuse, spam, and security threats.",
                ),
            ),
            LegalSection(
                title="Legal Grounds",
                items=(
                    "Contractual necessity when entering or performing a service agreement.",
                    "Legitimate interest in securing infrastructure and improving services.",
                    "Consent, where required, for optional communications or analytics features.",
                ),
            ),
            LegalSection(
                title="Storage & Security",
                items=(
                    "Project materials are stored in encrypted repositories with access limited to the engagement team.",
                    "Operational data is retained only for as long as necessary to satisfy legal or contractual obligations.",
                    "Reasonable safeguards, including multi-factor authentication and principle of least privilege, protect your information.",
                ),
            ),
            LegalSection(
                title="Your Choices",
                items=(
                    "You may request a copy, correction, or deletion of personal data by emailing support@invilso.pp.ua.",
                    "Requests are processed within 30 days unless a different timeframe is mandated by law.",
                    "You can opt out of optional updates at any time by replying to the message or contacting me directly.",
                ),
            ),
            LegalSection(
                title="Questions",
                items=(
                    "For privacy-related questions, email support@invilso.pp.ua or use the contact form on the home page.",
                    "If we have a standing contract, you can also reach me via the agreed project communication channel.",
                ),
            ),
        ),
    ),
    "cookies": LegalPage(
        slug="cookies",
        meta_title="Cookie Policy | INVILSO SCRIPTS",
        link_title="Cookie Policy",
        heading="Cookie Policy",
        tagline="How cookies and similar technologies keep this site running.",
        intro="This policy explains which cookies are used, what they do, and how you can manage your preferences.",
        updated_at="Last updated: May 7, 2025",
        sections=(
            LegalSection(
                title="What Cookies Are",
                items=(
                    "Cookies are small text files stored on your device to help websites remember preferences and maintain sessions.",
                    "Similar technologies such as local storage or session storage may serve the same purpose depending on your browser.",
                ),
            ),
            LegalSection(
                title="Cookies In Use",
                items=(
                    "Essential cookies keep the site responsive and remember basic preferences like language or previously closed banners.",
                    "No third-party advertising cookies are set, and analytics is limited to aggregated, privacy-conscious metrics when enabled.",
                    "Embedded content such as GitHub or third-party assets may place their own cookies in line with their policies.",
                ),
            ),
            LegalSection(
                title="Managing Cookies",
                items=(
                    "You can delete or block cookies in your browser settings without losing access to core site functionality.",
                    "Opt-out mechanisms provided by third-party services (for example, GitHub) remain available through their documentation.",
                    "If you disable essential cookies, some interactive components such as the contact form may not remember your preferences.",
                ),
            ),
            LegalSection(
                title="Updates",
                items=(
                    "Policy updates reflect changes to the site or applicable regulations and become effective once published here.",
                    "Material updates are highlighted on the home page or communicated directly to active clients, where relevant.",
                ),
            ),
        ),
    ),
}

LEGAL_PAGE_ORDER = ("terms", "privacy", "cookies")
LEGAL_LINKS = _legal_page_links(LEGAL_PAGES[slug] for slug in LEGAL_PAGE_ORDER)


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
    page = LEGAL_PAGES.get(slug)
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
