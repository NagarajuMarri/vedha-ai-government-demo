"""Secure provider-independent textbook file storage."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
import shutil


class TextbookStorage(ABC):
    @abstractmethod
    def store(self, source_path: Path, textbook_id: str, filename: str) -> str: ...

    @abstractmethod
    def remove(self, storage_key: str) -> None: ...


class LocalTextbookStorage(TextbookStorage):
    def __init__(self, root_path: Path) -> None:
        self._root = root_path.resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def store(self, source_path: Path, textbook_id: str, filename: str) -> str:
        if Path(filename).name != filename or not filename.lower().endswith(".pdf"):
            raise ValueError("Invalid textbook filename")
        safe_id = "".join(character for character in textbook_id if character.isalnum() or character in "-_")
        if safe_id != textbook_id:
            raise ValueError("Invalid textbook identifier")
        destination = (self._root / safe_id / filename).resolve()
        if self._root not in destination.parents:
            raise ValueError("Invalid textbook storage destination")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination)
        return f"{safe_id}/{filename}"

    def remove(self, storage_key: str) -> None:
        relative = Path(storage_key)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Invalid textbook storage key")
        target = (self._root / relative).resolve()
        if self._root not in target.parents:
            raise ValueError("Invalid textbook storage key")
        if target.is_file():
            target.unlink()
        parent = target.parent
        if parent != self._root and parent.is_dir() and not any(parent.iterdir()):
            parent.rmdir()
