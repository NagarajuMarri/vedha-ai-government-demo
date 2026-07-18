"""Static frontend skeleton smoke tests."""

from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
STUDENT_HTML = (FRONTEND_ROOT / "student" / "index.html").read_text(encoding="utf-8")
TUTOR_JS = (FRONTEND_ROOT / "assets" / "js" / "student-tutor.js").read_text(encoding="utf-8")
API_JS = (FRONTEND_ROOT / "assets" / "js" / "api-client.js").read_text(encoding="utf-8")


def test_landing_page_contains_required_interface_navigation() -> None:
    content = (FRONTEND_ROOT / "index.html").read_text(encoding="utf-8")

    assert "Vedha AI Government Demo" in content
    assert 'href="student/"' in content
    assert 'href="teacher/"' in content
    assert 'href="parent/"' in content
    assert 'href="government/"' in content
    assert 'href="assets/css/styles.css"' in content
    assert 'src="assets/js/main.js"' in content


def test_interface_shells_exist() -> None:
    for interface in ("student", "teacher", "parent", "government"):
        assert (FRONTEND_ROOT / interface / "index.html").is_file()


def test_student_setup_uses_exact_api_values() -> None:
    for value in ("english_medium", "telugu_assisted_english", "pure_telugu"):
        assert f'value="{value}"' in STUDENT_HTML
    for subject in ("Mathematics", "Science", "English", "Telugu", "Social Studies"):
        assert f'value="{subject}"' in STUDENT_HTML
    assert "class_level: Number" in TUTOR_JS


def test_api_client_centralizes_endpoint_and_json_request() -> None:
    assert 'DEFAULT_BASE_URL = "http://127.0.0.1:8000"' in API_JS
    assert '`${baseUrl}/api/v1/lessons/explain`' in API_JS
    assert 'method: "POST"' in API_JS
    assert 'body: JSON.stringify(payload)' in API_JS
    assert "...state.setup, question" in TUTOR_JS


def test_loading_disables_submit_and_prevents_duplicates() -> None:
    assert "askButton.disabled = isLoading" in TUTOR_JS
    assert "if (state.loading) return" in TUTOR_JS
    assert "if (!state.loading) questionForm.requestSubmit()" in TUTOR_JS
    assert 'aria-live="polite"' in STUDENT_HTML


def test_successful_lesson_renders_every_section_safely() -> None:
    for element_id in ("lesson-title", "lesson-introduction", "lesson-steps", "lesson-example", "lesson-points", "lesson-check"):
        assert f'id="{element_id}"' in STUDENT_HTML
    assert "textContent = lesson.title" in TUTOR_JS
    assert "textContent = lesson.introduction" in TUTOR_JS
    assert "textContent = lesson.example" in TUTOR_JS
    assert "textContent = lesson.check_question" in TUTOR_JS
    assert "innerHTML" not in TUTOR_JS


def test_steps_and_key_points_are_semantic_lists() -> None:
    assert re.search(r'<ol id="lesson-steps"></ol>', STUDENT_HTML)
    assert re.search(r'<ul id="lesson-points"></ul>', STUDENT_HTML)
    assert 'setList(byId("lesson-steps"), lesson.explanation_steps)' in TUTOR_JS
    assert 'setList(byId("lesson-points"), lesson.key_points)' in TUTOR_JS


def test_telugu_profile_messages_are_preserved_as_unicode() -> None:
    for text in ("మీ lesson సిద్ధం చేస్తోంది", "వేద మీ పాఠాన్ని సిద్ధం చేస్తోంది", "పాఠాన్ని సిద్ధం చేయలేకపోయాం"):
        assert text in TUTOR_JS


def test_fallback_indicator_is_conditional_and_student_friendly() -> None:
    assert 'lesson.source === "fallback" || lesson.fallback_used' in TUTOR_JS
    assert "fallbackNote.hidden = !isFallback" in TUTOR_JS
    assert "provider failure" not in TUTOR_JS.lower()
    assert "api key missing" not in TUTOR_JS.lower()
    assert "openai unavailable" not in TUTOR_JS.lower()


def test_api_client_validates_complete_response_shape() -> None:
    for field in ("request_id", "lesson_id", "title", "introduction", "explanation_steps", "example", "key_points", "check_question", "learning_profile", "subject", "class_level", "source", "fallback_used", "created_at"):
        assert field in API_JS
    assert "Array.isArray(data.explanation_steps)" in API_JS
    assert "Array.isArray(data.key_points)" in API_JS
    assert 'typeof data.fallback_used !== "boolean"' in API_JS


def test_safe_error_paths_and_question_retention_are_implemented() -> None:
    for error_kind in ("timeout", "network", "non_json_response", "validation", "server", "request", "malformed_response"):
        assert f'"{error_kind}"' in API_JS
    assert "questionInput.value =" not in TUTOR_JS
    assert "error.textContent = messages[state.setup.learning_profile].error" in TUTOR_JS
    assert "stack" not in TUTOR_JS.lower()


def test_question_limit_counter_and_keyboard_behavior() -> None:
    assert 'maxlength="1500"' in STUDENT_HTML
    assert 'id="question-counter"' in STUDENT_HTML
    assert "MAX_QUESTION_LENGTH = 1500" in TUTOR_JS
    assert 'event.key === "Enter" && !event.shiftKey' in TUTOR_JS
    assert "questionInput.value.trim()" in TUTOR_JS


def test_future_microphone_and_attachment_controls_are_accessibly_disabled() -> None:
    assert re.search(r'<button type="button" disabled aria-label="Microphone[^>]+>', STUDENT_HTML)
    assert re.search(r'<button type="button" disabled aria-label="Attachments[^>]+>', STUDENT_HTML)


def test_student_tutor_assets_are_separate_and_responsive() -> None:
    assert 'src="../assets/js/api-client.js"' in STUDENT_HTML
    assert 'src="../assets/js/student-tutor.js"' in STUDENT_HTML
    assert 'href="../assets/css/styles.css"' in STUDENT_HTML
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    assert "@media (max-width: 48rem)" in styles
    assert "@media (max-width: 30rem)" in styles


def test_student_practice_ui_and_api_integration() -> None:
    assert 'id="concept"' in STUDENT_HTML
    assert 'id="generate-practice"' in STUDENT_HTML
    assert 'id="practice-result"' in STUDENT_HTML
    for difficulty in ("easy", "medium", "hard"):
        assert f'id="practice-{difficulty}"' in STUDENT_HTML
    assert '/api/v1/practice/generate' in API_JS
    assert 'data.questions.length !== 15' in API_JS
    assert 'counts.easy !== 5' in API_JS
    assert 'api.requestPractice(state.setup)' in TUTOR_JS
    assert 'question.difficulty === difficulty' in TUTOR_JS


def test_practice_ui_has_bilingual_states_and_responsive_layout() -> None:
    for text in ("Vedha is preparing 15 practice questions", "Vedha 15 practice questions సిద్ధం చేస్తోంది", "వేద 15 అభ్యాస ప్రశ్నలను సిద్ధం చేస్తోంది"):
        assert text in TUTOR_JS
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    assert ".practice-result" in styles
    assert "grid-template-columns: repeat(3" in styles


def test_practice_answer_evaluation_is_connected_safely() -> None:
    assert '/api/v1/practice/evaluate' in API_JS
    assert 'requestPracticeEvaluation' in API_JS
    assert 'typeof data.correct !== "boolean"' in API_JS
    assert 'Array.isArray(data.corrective_guidance)' in API_JS
    assert 'practice_set_id: state.practice.practice_set_id' in TUTOR_JS
    assert 'student_answer: studentAnswer' in TUTOR_JS
    assert 'textContent = evaluation.feedback' in TUTOR_JS
    assert 'innerHTML' not in TUTOR_JS


def test_practice_answer_ui_supports_keyboard_feedback_and_retry() -> None:
    assert 'input.className = "practice-answer"' in TUTOR_JS
    assert 'button.textContent = "Check Answer"' in TUTOR_JS
    assert 'event.key === "Enter"' in TUTOR_JS
    assert 'aria-live", "polite"' in TUTOR_JS
    assert 'answerRequired' in TUTOR_JS
    assert 'evaluationError' in TUTOR_JS
    assert '.answer-correct' in (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
