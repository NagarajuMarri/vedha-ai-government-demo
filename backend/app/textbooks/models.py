"""Immutable textbook repository and ingestion contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


BookPart = Literal[
    "full_year", "semester_1", "semester_2", "volume_1", "volume_2",
    "part_1", "part_2", "custom",
]
LanguageCode = Literal["en", "te"]
IngestionStatus = Literal["pending", "inspecting", "completed", "failed", "duplicate"]


class TextbookModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)


class TextbookSource(TextbookModel):
    source_type: Literal[
        "official_textbook_pdf", "local_file", "government_portal", "publisher", "manual",
    ]
    source_reference: str = Field(..., min_length=1, max_length=500)
    alternate_source_references: tuple[str, ...] = ()


class TextbookEdition(TextbookModel):
    edition: str | None = Field(default=None, min_length=1, max_length=80)
    publication_year: int | None = Field(default=None, ge=1900, le=2200)
    publisher: str | None = Field(default=None, min_length=1, max_length=200)


class TextbookRegistration(TextbookModel):
    board: str
    academic_year: str = Field(..., pattern=r"^\d{4}-\d{4}$")
    curriculum_version: str
    class_level: int = Field(..., ge=1, le=12)
    subject: str
    medium: str
    language: LanguageCode
    languages: tuple[LanguageCode, ...] = ()
    book_part: BookPart
    edition: TextbookEdition
    title: str | None = None
    source: TextbookSource


class TextbookProvenance(TextbookModel):
    source_type: str
    source_reference: str
    alternate_source_references: tuple[str, ...] = ()
    checksum_algorithm: Literal["sha256"] = "sha256"
    checksum: str = Field(..., pattern=r"^[a-f0-9]{64}$")
    ingested_at: datetime
    ingestion_job_id: str


class TextbookFile(TextbookModel):
    filename: str
    mime_type: Literal["application/pdf"]
    file_size_bytes: int = Field(..., gt=0)
    checksum: str = Field(..., pattern=r"^[a-f0-9]{64}$")
    storage_key: str


class TextbookPage(TextbookModel):
    page_number: int = Field(..., ge=1)
    extracted_text: str = ""
    warnings: tuple[str, ...] = ()
    has_images: bool = False
    has_tables: bool = False
    provenance: TextbookProvenance


class TextbookSection(TextbookModel):
    heading: str
    page_number: int = Field(..., ge=1)
    confidence: float = Field(..., ge=0, le=1)


class TextbookSubTopic(TextbookModel):
    name: str
    page_number: int = Field(..., ge=1)


class TextbookTopic(TextbookModel):
    name: str
    page_number: int = Field(..., ge=1)
    sub_topics: tuple[TextbookSubTopic, ...] = ()


class TextbookChapter(TextbookModel):
    name: str
    page_number: int = Field(..., ge=1)
    confidence: float = Field(..., ge=0, le=1)
    topics: tuple[TextbookTopic, ...] = ()
    manually_corrected: bool = False


class TextbookMetadata(TextbookModel):
    textbook_id: str
    board: str
    academic_year: str
    curriculum_version: str
    class_level: int
    subject: str
    medium: str
    language: str
    languages: tuple[LanguageCode, ...] = ()
    book_part: BookPart
    edition: str | None = None
    publication_year: int | None = None
    publisher: str | None = None
    title: str | None = None
    source_type: str
    source_reference: str
    filename: str
    mime_type: str
    file_size_bytes: int
    checksum: str
    page_count: int = Field(..., ge=1)
    created_at: datetime
    updated_at: datetime
    embedding: tuple[float, ...] | None = None
    image_refs: tuple[str, ...] = ()
    diagram_refs: tuple[str, ...] = ()
    animation_tags: tuple[str, ...] = ()
    voice_tags: tuple[str, ...] = ()
    bloom_level: str | None = None
    learning_objectives: tuple[str, ...] = ()


class TextbookIngestionJob(TextbookModel):
    ingestion_job_id: str
    registration: TextbookRegistration
    filename: str
    status: IngestionStatus = "pending"
    created_at: datetime


class TextbookIngestionResult(TextbookModel):
    textbook_id: str
    checksum: str
    page_count: int
    is_scanned: bool
    ocr_required: bool
    detection_reason: str | None = None
    detected_language: Literal["telugu", "english", "bilingual", "mixed", "unreadable", "empty", "scanned"]
    sampled_page_numbers: tuple[int, ...] = ()
    pages_with_text: int = Field(..., ge=0)
    pages_without_text: int = Field(..., ge=0)
    pages_with_warnings: int = Field(..., ge=0)
    likely_scanned_pages: int = Field(..., ge=0)
    image_pages: int = Field(..., ge=0)
    table_pages: int = Field(..., ge=0)
    text_coverage_percent: float = Field(..., ge=0, le=100)
    unicode_valid: bool
    replacement_character_count: int = Field(..., ge=0)
    english_pages: int = Field(default=0, ge=0)
    telugu_pages: int = Field(default=0, ge=0)
    mixed_language_pages: int = Field(default=0, ge=0)
    unreadable_pages: int = Field(default=0, ge=0)
    english_character_count: int = Field(default=0, ge=0)
    telugu_character_count: int = Field(default=0, ge=0)
    bilingual_coverage_percent: float = Field(default=0, ge=0, le=100)
    alternating_language_pairs: int = Field(default=0, ge=0)
    chapters: tuple[TextbookChapter, ...] = ()
    pages: tuple[TextbookPage, ...]
    warnings: tuple[str, ...] = ()
    metadata: TextbookMetadata
    provenance: TextbookProvenance
    status: Literal["completed"] = "completed"


class TextbookError(TextbookModel):
    code: str
    message: str
    ingestion_job_id: str | None = None

    @model_validator(mode="after")
    def prevent_path_disclosure(self) -> "TextbookError":
        if "\\" in self.message or "/" in self.message:
            raise ValueError("Textbook errors must not expose filesystem paths")
        return self
