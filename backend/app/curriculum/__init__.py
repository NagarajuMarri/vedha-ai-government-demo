"""Metadata-first multi-board curriculum domain."""

from backend.app.curriculum.models import (
    AcademicYear,
    Board,
    Book,
    Chapter,
    Chunk,
    ChunkMetadata,
    CurriculumCatalog,
    CurriculumClass,
    CurriculumVersion,
    CurriculumSelection,
    Medium,
    Page,
    SubTopic,
    Subject,
    Topic,
)
from backend.app.curriculum.resolver import CurriculumResolver, UnsupportedCurriculumError

__all__ = [
    "AcademicYear", "Board", "Book", "Chapter", "Chunk", "ChunkMetadata",
    "CurriculumCatalog", "CurriculumClass", "CurriculumResolver", "CurriculumVersion",
    "CurriculumSelection", "Medium", "Page", "SubTopic", "Subject", "Topic",
    "UnsupportedCurriculumError",
]
