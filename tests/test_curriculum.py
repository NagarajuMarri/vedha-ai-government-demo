"""Sprint 4B curriculum domain and deterministic resolver tests."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend.app.core.config import get_settings
from backend.app.curriculum import (
    AcademicYear,
    Board,
    Chunk,
    ChunkMetadata,
    CurriculumCatalog,
    CurriculumClass,
    CurriculumResolver,
    CurriculumVersion,
    Medium,
    Subject,
    UnsupportedCurriculumError,
)


SUPPORTED_BOARDS = (
    "andhra_pradesh_state_board",
    "telangana_state_board",
    "cbse",
    "icse",
)


def _catalog(board_ids: tuple[str, ...] = SUPPORTED_BOARDS) -> CurriculumCatalog:
    boards = []
    for board_id in board_ids:
        subject = Subject(
            id="mathematics",
            name="Mathematics",
            media=(
                Medium(id="english", name="English Medium", language="en"),
                Medium(id="telugu", name="Telugu Medium", language="te"),
            ),
        )
        curriculum_class = CurriculumClass(class_level=5, subjects=(subject,))
        version = CurriculumVersion(id="2025.1", classes=(curriculum_class,))
        year = AcademicYear(id="2025-2026", curriculum_versions=(version,))
        boards.append(Board(
            id=board_id,
            name=board_id.replace("_", " ").title(),
            academic_years=(year,),
        ))
    return CurriculumCatalog(boards=tuple(boards))


@pytest.mark.parametrize("board", SUPPORTED_BOARDS)
def test_each_required_board_resolves(board: str) -> None:
    selection = CurriculumResolver(_catalog(), SUPPORTED_BOARDS).resolve(
        board=board,
        academic_year="2025-2026",
        curriculum_version="2025.1",
        class_level=5,
        subject="mathematics",
        medium="telugu",
    )
    assert selection.model_dump() == {
        "board": board,
        "academic_year": "2025-2026",
        "curriculum_version": "2025.1",
        "class_level": 5,
        "subject": "mathematics",
        "medium": "telugu",
        "language": "te",
    }


def test_unsupported_board_is_rejected_before_hierarchy_lookup() -> None:
    with pytest.raises(UnsupportedCurriculumError, match="Unsupported board"):
        CurriculumResolver(_catalog(), SUPPORTED_BOARDS).resolve(
            board="unknown_board",
            academic_year="2025-2026",
            curriculum_version="2025.1",
            class_level=5,
            subject="mathematics",
            medium="english",
        )


@pytest.mark.parametrize(
    ("override", "expected_level"),
    [
        ({"academic_year": "2026-2027"}, "academic_year"),
        ({"curriculum_version": "old"}, "curriculum_version"),
        ({"class_level": 6}, "class_level"),
        ({"subject": "science"}, "subject"),
        ({"medium": "hindi"}, "medium"),
    ],
)
def test_resolver_rejects_invalid_hierarchy_node(override: dict, expected_level: str) -> None:
    request = {
        "board": "cbse",
        "academic_year": "2025-2026",
        "curriculum_version": "2025.1",
        "class_level": 5,
        "subject": "mathematics",
        "medium": "english",
    }
    request.update(override)
    with pytest.raises(UnsupportedCurriculumError, match=f"Unsupported {expected_level}"):
        CurriculumResolver(_catalog(), SUPPORTED_BOARDS).resolve(**request)


def test_new_configured_board_requires_no_resolver_code_change() -> None:
    boards = (*SUPPORTED_BOARDS, "cambridge")
    selection = CurriculumResolver(_catalog(boards), boards).resolve(
        board="cambridge",
        academic_year="2025-2026",
        curriculum_version="2025.1",
        class_level=5,
        subject="mathematics",
        medium="english",
    )
    assert selection.board == "cambridge"


def test_chunk_metadata_serialization_and_future_compatibility() -> None:
    timestamp = datetime(2026, 7, 17, 10, 30, tzinfo=timezone.utc)
    metadata = ChunkMetadata(
        board="andhra_pradesh_state_board",
        academic_year="2025-2026",
        class_level=5,
        subject="Mathematics",
        medium="Telugu",
        book_id="ap-5-maths-te-v1",
        book_name="5వ తరగతి గణితం",
        chapter_number=3,
        chapter_name="భిన్నాలు",
        topic="భిన్నాల పరిచయం",
        sub_topic="లవం మరియు హారం",
        page_number=42,
        chunk_id="ap-math-5-te-003-042-01",
        language="te",
        version="1.0.0",
        created_at=timestamp,
        updated_at=timestamp,
    )
    chunk = Chunk(chunk_id=metadata.chunk_id, content="భిన్నం సమాన భాగాలను చూపుతుంది.", metadata=metadata)
    serialized = chunk.model_dump(mode="json")

    assert serialized["metadata"]["board"] == "andhra_pradesh_state_board"
    assert serialized["metadata"]["created_at"] == "2026-07-17T10:30:00Z"
    assert serialized["metadata"]["embedding"] is None
    assert serialized["metadata"]["image_refs"] == []
    assert serialized["metadata"]["diagram_refs"] == []
    assert serialized["metadata"]["animation_tags"] == []
    assert serialized["metadata"]["voice_tags"] == []
    assert serialized["metadata"]["learning_objectives"] == []
    assert serialized["metadata"]["bloom_level"] is None


def test_chunk_metadata_is_immutable_and_identity_is_consistent() -> None:
    timestamp = datetime.now(timezone.utc)
    metadata = ChunkMetadata(
        board="cbse", academic_year="2025-2026", class_level=5,
        subject="Mathematics", medium="English", book_id="book-1", book_name="Maths",
        chapter_number=1, chapter_name="Fractions", topic="Fractions", page_number=1,
        chunk_id="chunk-1", language="en", version="1", created_at=timestamp, updated_at=timestamp,
    )
    with pytest.raises(ValidationError):
        metadata.board = "icse"
    with pytest.raises(ValidationError, match="chunk_id must match"):
        Chunk(chunk_id="chunk-2", content="Fraction content", metadata=metadata)


def test_curriculum_configuration_defaults_and_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("SUPPORTED_BOARDS", "DEFAULT_BOARD", "DEFAULT_ACADEMIC_YEAR"):
        monkeypatch.delenv(name, raising=False)
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.supported_boards == SUPPORTED_BOARDS
    assert settings.default_board == "andhra_pradesh_state_board"
    assert settings.default_academic_year == "2025-2026"

    monkeypatch.setenv("SUPPORTED_BOARDS", "cbse,icse")
    monkeypatch.setenv("DEFAULT_BOARD", "unknown")
    get_settings.cache_clear()
    with pytest.raises(ValueError, match="DEFAULT_BOARD"):
        get_settings()
