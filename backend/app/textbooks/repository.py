"""Provider-independent textbook metadata repository contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
import json
from pathlib import Path

from backend.app.textbooks.models import TextbookIngestionResult


class DuplicateTextbookError(ValueError):
    """An exact file checksum is already registered."""


class TextbookRepository(ABC):
    @abstractmethod
    def add(self, result: TextbookIngestionResult) -> None: ...

    @abstractmethod
    def get_by_checksum(self, checksum: str) -> TextbookIngestionResult | None: ...

    @abstractmethod
    def list_all(self) -> tuple[TextbookIngestionResult, ...]: ...


class InMemoryTextbookRepository(TextbookRepository):
    """Deterministic adapter for tests and the ingestion foundation."""

    def __init__(self) -> None:
        self._by_checksum: dict[str, TextbookIngestionResult] = {}

    def add(self, result: TextbookIngestionResult) -> None:
        if result.checksum in self._by_checksum:
            raise DuplicateTextbookError("An exact textbook file is already registered")
        self._by_checksum[result.checksum] = result

    def get_by_checksum(self, checksum: str) -> TextbookIngestionResult | None:
        return self._by_checksum.get(checksum)

    def list_all(self) -> tuple[TextbookIngestionResult, ...]:
        return tuple(self._by_checksum.values())


class JsonTextbookRepository(TextbookRepository):
    """Private local metadata adapter with atomic file replacement."""

    def __init__(self, metadata_file: Path) -> None:
        self._metadata_file = metadata_file.resolve()
        self._metadata_file.parent.mkdir(parents=True, exist_ok=True)

    def add(self, result: TextbookIngestionResult) -> None:
        records = list(self.list_all())
        if any(record.checksum == result.checksum for record in records):
            raise DuplicateTextbookError("An exact textbook file is already registered")
        records.append(result)
        temporary = self._metadata_file.with_suffix(".tmp")
        temporary.write_text(
            json.dumps([record.model_dump(mode="json") for record in records], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(self._metadata_file)

    def get_by_checksum(self, checksum: str) -> TextbookIngestionResult | None:
        return next((record for record in self.list_all() if record.checksum == checksum), None)

    def list_all(self) -> tuple[TextbookIngestionResult, ...]:
        if not self._metadata_file.exists():
            return ()
        try:
            payload = json.loads(self._metadata_file.read_text(encoding="utf-8"))
            return tuple(TextbookIngestionResult.model_validate(item) for item in payload)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise ValueError("Textbook metadata repository is unreadable") from exc
