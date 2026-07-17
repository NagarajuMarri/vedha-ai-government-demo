"""Deterministic curriculum hierarchy resolution with no AI dependency."""

from __future__ import annotations

from backend.app.curriculum.models import CurriculumCatalog, CurriculumSelection


class UnsupportedCurriculumError(ValueError):
    """A requested curriculum node does not exist in the configured hierarchy."""


class CurriculumResolver:
    """Validate Board -> Year -> Class -> Subject -> Medium in order."""

    def __init__(self, catalog: CurriculumCatalog, supported_boards: tuple[str, ...]) -> None:
        self._catalog = catalog
        self._supported_boards = frozenset(supported_boards)

    def resolve(
        self,
        *,
        board: str,
        academic_year: str,
        class_level: int,
        subject: str,
        medium: str,
    ) -> CurriculumSelection:
        board_node = self._find(
            self._catalog.boards,
            board,
            key=lambda item: item.id,
            level="board",
            allowed=self._supported_boards,
        )
        year_node = self._find(board_node.academic_years, academic_year, key=lambda item: item.id, level="academic_year")
        class_node = self._find(year_node.classes, class_level, key=lambda item: item.class_level, level="class_level")
        subject_node = self._find(class_node.subjects, subject, key=lambda item: item.id, level="subject")
        medium_node = self._find(subject_node.media, medium, key=lambda item: item.id, level="medium")
        return CurriculumSelection(
            board=board_node.id,
            academic_year=year_node.id,
            class_level=class_node.class_level,
            subject=subject_node.id,
            medium=medium_node.id,
            language=medium_node.language,
        )

    @staticmethod
    def _find(items, requested, *, key, level: str, allowed: frozenset[str] | None = None):
        if allowed is not None and requested not in allowed:
            raise UnsupportedCurriculumError(f"Unsupported {level}: {requested}")
        for item in items:
            if key(item) == requested:
                return item
        raise UnsupportedCurriculumError(f"Unsupported {level}: {requested}")
