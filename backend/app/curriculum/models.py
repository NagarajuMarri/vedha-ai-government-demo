"""Immutable curriculum entities and future retrieval metadata contracts."""

from __future__ import annotations

from datetime import datetime

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CurriculumModel(BaseModel):
    """Strict immutable base for curriculum-owned data."""

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)


class Medium(CurriculumModel):
    id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    language: str = Field(..., min_length=2, max_length=50)


class Subject(CurriculumModel):
    id: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=120)
    media: tuple[Medium, ...] = Field(..., min_length=1)


class CurriculumClass(CurriculumModel):
    class_level: int = Field(..., ge=1, le=12)
    subjects: tuple[Subject, ...] = Field(..., min_length=1)


class CurriculumVersion(CurriculumModel):
    id: str = Field(..., min_length=1, max_length=80)
    classes: tuple[CurriculumClass, ...] = Field(..., min_length=1)


class AcademicYear(CurriculumModel):
    id: str = Field(..., pattern=r"^\d{4}-\d{4}$")
    curriculum_versions: tuple[CurriculumVersion, ...] = Field(..., min_length=1)


class Board(CurriculumModel):
    id: str = Field(..., min_length=2, max_length=80)
    name: str = Field(..., min_length=2, max_length=160)
    academic_years: tuple[AcademicYear, ...] = Field(..., min_length=1)


class CurriculumCatalog(CurriculumModel):
    boards: tuple[Board, ...] = Field(..., min_length=1)


class Book(CurriculumModel):
    book_id: str = Field(..., min_length=1, max_length=120)
    book_name: str = Field(..., min_length=1, max_length=240)
    version: str = Field(..., min_length=1, max_length=50)
    book_part: Literal[
        "full_year", "semester_1", "semester_2", "volume_1", "volume_2",
        "part_1", "part_2", "custom",
    ] = "full_year"


class Chapter(CurriculumModel):
    chapter_number: int = Field(..., ge=1)
    chapter_name: str = Field(..., min_length=1, max_length=240)


class Topic(CurriculumModel):
    name: str = Field(..., min_length=1, max_length=240)


class SubTopic(CurriculumModel):
    name: str = Field(..., min_length=1, max_length=240)


class Page(CurriculumModel):
    page_number: int = Field(..., ge=1)


class ChunkMetadata(CurriculumModel):
    """Portable metadata envelope; future fields carry no processing behavior."""

    board: str = Field(..., min_length=2, max_length=80)
    academic_year: str = Field(..., pattern=r"^\d{4}-\d{4}$")
    class_level: int = Field(..., ge=1, le=12)
    subject: str = Field(..., min_length=1, max_length=120)
    medium: str = Field(..., min_length=1, max_length=100)
    book_id: str = Field(..., min_length=1, max_length=120)
    book_name: str = Field(..., min_length=1, max_length=240)
    chapter_number: int = Field(..., ge=1)
    chapter_name: str = Field(..., min_length=1, max_length=240)
    topic: str = Field(..., min_length=1, max_length=240)
    sub_topic: str | None = Field(default=None, max_length=240)
    page_number: int = Field(..., ge=1)
    chunk_id: str = Field(..., min_length=1, max_length=160)
    language: str = Field(..., min_length=2, max_length=50)
    version: str = Field(..., min_length=1, max_length=50)
    created_at: datetime
    updated_at: datetime

    # Reserved for Sprint 4C+; no embedding or media processing exists in 4B.
    embedding: tuple[float, ...] | None = None
    image_refs: tuple[str, ...] = ()
    diagram_refs: tuple[str, ...] = ()
    animation_tags: tuple[str, ...] = ()
    voice_tags: tuple[str, ...] = ()
    learning_objectives: tuple[str, ...] = ()
    bloom_level: str | None = Field(default=None, max_length=50)

    @model_validator(mode="after")
    def validate_timestamps(self) -> "ChunkMetadata":
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not precede created_at")
        return self


class Chunk(CurriculumModel):
    chunk_id: str = Field(..., min_length=1, max_length=160)
    content: str = Field(..., min_length=1)
    metadata: ChunkMetadata

    @model_validator(mode="after")
    def validate_metadata_identity(self) -> "Chunk":
        if self.chunk_id != self.metadata.chunk_id:
            raise ValueError("chunk_id must match metadata.chunk_id")
        return self


class CurriculumSelection(CurriculumModel):
    """Deterministic canonical output of hierarchy resolution."""

    board: str
    academic_year: str
    curriculum_version: str
    class_level: int
    subject: str
    medium: str
    language: str
