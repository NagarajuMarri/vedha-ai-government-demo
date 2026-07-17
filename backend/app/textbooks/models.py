"""Immutable textbook repository and ingestion contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


BookPart = Literal[
    "full_year", "semester_1", "semester_2", "volume_1", "volume_2",
    "part_1", "part_2", "custom",
]
IngestionStatus = Literal["pending", "inspecting", "completed", "failed", "duplicate"]


class TextbookModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)


class TextbookSource(TextbookModel):
    source_type: Literal["local_file", "government_portal", "publisher", "manual"]
    source_reference: str = Field(..., min_length=1, max_length=500)


class TextbookEdition(TextbookModel):
    edition: str = Field(..., min_length=1, max_length=80)
    publication_year: int = Field(..., ge=1900, le=2200)
    publisher: str = Field(..., min_length=1, max_length=200)


class TextbookRegistration(TextbookModel):
    board: str
    academic_year: str = Field(..., pattern=r"^\d{4}-\d{4}$")
    curriculum_version: str
    class_level: int = Field(..., ge=1, le=12)
    subject: str
    medium: str
    language: str
    book_part: BookPart
    edition: TextbookEdition
    title: str
    source: TextbookSource


class TextbookProvenance(TextbookModel):
    source_type: str
    source_reference: str
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
    book_part: BookPart
    edition: str
    publication_year: int
    publisher: str
    title: str
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
