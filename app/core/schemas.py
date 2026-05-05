# app/core/schemas.py
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SchemaType(str, Enum):
    """The four supported extraction schema types."""
    JOB_POSTING = "job_posting"
    INVOICE = "invoice"
    CONTACT_INFO = "contact_info"
    NEWS_ARTICLE = "news_article"


# ── Job Posting Schema ────────────────────────────────────────────────────────

class JobRequirement(BaseModel):
    """A single job requirement or qualification."""
    requirement: str = Field(description="The specific requirement or qualification")
    is_required: bool = Field(
        description="True if explicitly required, False if preferred or nice-to-have"
    )


class JobPosting(BaseModel):
    """
    Structured data extracted from a job posting or job description.
    Extract all available information — use null for fields not mentioned.
    """
    job_title: str = Field(description="The exact job title as stated in the posting")
    company_name: Optional[str] = Field(
        default=None,
        description="The name of the hiring company or organisation"
    )
    location: Optional[str] = Field(
        default=None,
        description="Job location — city, country, or 'Remote' if remote"
    )
    employment_type: Optional[str] = Field(
        default=None,
        description="Employment type: Full-time, Part-time, Contract, Freelance, etc."
    )
    experience_required: Optional[str] = Field(
        default=None,
        description="Years of experience required e.g. '3-5 years' or 'Senior level'"
    )
    salary_range: Optional[str] = Field(
        default=None,
        description="Salary or compensation range if mentioned, including currency"
    )
    requirements: list[JobRequirement] = Field(
        default=[],
        description="List of skills, qualifications, and requirements"
    )
    responsibilities: list[str] = Field(
        default=[],
        description="List of job responsibilities and duties"
    )
    benefits: list[str] = Field(
        default=[],
        description="List of benefits, perks, or compensation extras"
    )
    application_deadline: Optional[str] = Field(
        default=None,
        description="Application deadline date if mentioned"
    )
    summary: str = Field(
        description="A two-sentence summary of the role and what makes it distinctive"
    )


# ── Invoice Schema ────────────────────────────────────────────────────────────

class LineItem(BaseModel):
    """A single line item on an invoice."""
    description: str = Field(description="Description of the product or service")
    quantity: Optional[float] = Field(default=None, description="Quantity ordered")
    unit_price: Optional[str] = Field(
        default=None,
        description="Price per unit including currency symbol"
    )
    total: Optional[str] = Field(
        default=None,
        description="Total for this line item including currency symbol"
    )


class Invoice(BaseModel):
    """
    Structured data extracted from an invoice or receipt.
    Extract all financial figures exactly as they appear including currency symbols.
    """
    invoice_number: Optional[str] = Field(
        default=None,
        description="Invoice or receipt number or ID"
    )
    vendor_name: Optional[str] = Field(
        default=None,
        description="Name of the vendor, supplier, or seller"
    )
    vendor_address: Optional[str] = Field(
        default=None,
        description="Vendor's address if present"
    )
    client_name: Optional[str] = Field(
        default=None,
        description="Name of the client or buyer"
    )
    invoice_date: Optional[str] = Field(
        default=None,
        description="Date the invoice was issued"
    )
    due_date: Optional[str] = Field(
        default=None,
        description="Payment due date if mentioned"
    )
    line_items: list[LineItem] = Field(
        default=[],
        description="List of products or services billed"
    )
    subtotal: Optional[str] = Field(
        default=None,
        description="Subtotal before tax including currency symbol"
    )
    tax_amount: Optional[str] = Field(
        default=None,
        description="Tax amount including currency symbol and rate if shown"
    )
    total_amount: Optional[str] = Field(
        default=None,
        description="Final total amount due including currency symbol"
    )
    payment_terms: Optional[str] = Field(
        default=None,
        description="Payment terms e.g. 'Net 30', 'Due on receipt'"
    )
    payment_method: Optional[str] = Field(
        default=None,
        description="Accepted or specified payment method if mentioned"
    )


# ── Contact Info Schema ───────────────────────────────────────────────────────

class ContactPerson(BaseModel):
    """A single person's contact information."""
    name: Optional[str] = Field(default=None, description="Full name of the person")
    title: Optional[str] = Field(default=None, description="Job title or role")
    organisation: Optional[str] = Field(
        default=None,
        description="Company or organisation they belong to"
    )
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(
        default=None,
        description="Phone number including country code if present"
    )
    address: Optional[str] = Field(
        default=None,
        description="Physical address if present"
    )
    linkedin: Optional[str] = Field(
        default=None,
        description="LinkedIn profile URL if present"
    )
    website: Optional[str] = Field(
        default=None,
        description="Personal or company website if present"
    )


class ContactInfo(BaseModel):
    """
    All contact information extracted from any business text.
    Extract every person, organisation, and contact detail mentioned.
    """
    contacts: list[ContactPerson] = Field(
        description="List of all people and their contact details found in the text"
    )
    organisations: list[str] = Field(
        default=[],
        description="List of organisation or company names mentioned"
    )
    total_contacts_found: int = Field(
        description="Total number of distinct people identified"
    )


# ── News Article Schema ───────────────────────────────────────────────────────

class NamedEntity(BaseModel):
    """A named entity mentioned in an article."""
    name: str = Field(description="The entity name")
    entity_type: str = Field(
        description="Type: PERSON, ORGANISATION, LOCATION, PRODUCT, or EVENT"
    )


class NewsArticle(BaseModel):
    """
    Structured data extracted from a news article or press release.
    Be precise — only extract what is explicitly stated in the text.
    """
    headline: str = Field(
        description="The article headline or title, exactly as written or inferred"
    )
    publication_date: Optional[str] = Field(
        default=None,
        description="Publication date if mentioned"
    )
    author: Optional[str] = Field(
        default=None,
        description="Author or byline if mentioned"
    )
    source: Optional[str] = Field(
        default=None,
        description="Publication or news source name if mentioned"
    )
    summary: str = Field(
        description="A factual three-sentence summary of the article's main points"
    )
    key_entities: list[NamedEntity] = Field(
        default=[],
        description="Key people, organisations, locations, and events mentioned"
    )
    sentiment: str = Field(
        description="Overall tone: positive, negative, or neutral"
    )
    topics: list[str] = Field(
        default=[],
        description="Main topics this article covers e.g. 'technology', 'finance'"
    )
    key_facts: list[str] = Field(
        default=[],
        description="The most important specific facts, figures, or claims in the article"
    )


# ── Schema registry ───────────────────────────────────────────────────────────

SCHEMA_REGISTRY: dict[SchemaType, type[BaseModel]] = {
    SchemaType.JOB_POSTING: JobPosting,
    SchemaType.INVOICE: Invoice,
    SchemaType.CONTACT_INFO: ContactInfo,
    SchemaType.NEWS_ARTICLE: NewsArticle,
}

SCHEMA_DESCRIPTIONS: dict[SchemaType, str] = {
    SchemaType.JOB_POSTING: "Extract structured information from a job posting or job description",
    SchemaType.INVOICE: "Extract structured financial data from an invoice or receipt",
    SchemaType.CONTACT_INFO: "Extract all contact information from any business text",
    SchemaType.NEWS_ARTICLE: "Extract structured information from a news article or press release",
}