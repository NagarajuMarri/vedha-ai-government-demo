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
    assert re.search(r'<ol id="lesson-steps"[^>]*></ol>', STUDENT_HTML)
    assert re.search(r'<ul id="lesson-points"[^>]*></ul>', STUDENT_HTML)
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


def test_student_microphone_is_enabled_and_transcript_remains_editable() -> None:
    assert 'id="student-voice-input"' in STUDENT_HTML
    assert 'data-voice-target="#question"' in STUDENT_HTML
    assert 'data-voice-language-source=\'input[name="learning_profile"]:checked\'' in STUDENT_HTML
    assert 'aria-pressed="false"' in STUDENT_HTML
    assert re.search(r'<button type="button" disabled aria-label="General lesson attachments[^>]+>', STUDENT_HTML)


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
    assert "button.textContent = copy.checkAnswer" in TUTOR_JS
    assert 'event.key === "Enter"' in TUTOR_JS
    assert 'aria-live", "polite"' in TUTOR_JS
    assert 'answerRequired' in TUTOR_JS
    assert 'evaluationError' in TUTOR_JS
    assert '.answer-correct' in (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")


def test_lesson_browser_timeout_exceeds_backend_provider_timeout() -> None:
    assert "options.timeoutMs || 45000" in API_JS


def test_handwritten_phone_photo_evaluation_is_connected() -> None:
    assert '/api/v1/practice/evaluate-handwriting' in API_JS
    assert 'requestHandwritingEvaluation' in API_JS
    assert 'uploadInput.accept = "image/jpeg,image/png"' in TUTOR_JS
    assert 'file.size > 5 * 1024 * 1024' in TUTOR_JS
    assert 'Upload Handwritten Work' in TUTOR_JS
    assert 'image_data_url: imageDataUrl' in TUTOR_JS
    assert 'Transcribed work:' in TUTOR_JS
    assert 'innerHTML' not in TUTOR_JS


def test_pure_telugu_practice_controls_are_localized() -> None:
    for text in ("15 ప్రశ్నల అభ్యాసం", "సులభం · 5", "సమాధానం తనిఖీ", "చేతిరాత పరిష్కారం జోడించండి", "అభ్యాసం రూపొందించండి"):
        assert text in TUTOR_JS
    assert 'hint.textContent = `${copy.hintLabel}: ${question.hint}`' in TUTOR_JS


def test_presentation_brand_identity_is_complete_and_accessible() -> None:
    landing_html = (FRONTEND_ROOT / "index.html").read_text(encoding="utf-8")
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    logo_path = FRONTEND_ROOT / "assets" / "images" / "vedha-mark.png"

    assert logo_path.is_file()
    assert logo_path.stat().st_size > 10_000
    assert 'src="assets/images/vedha-mark.png"' in landing_html
    assert 'src="../assets/images/vedha-mark.png"' in STUDENT_HTML
    assert 'alt="Vedha open-book and sunrise logo"' in landing_html
    assert "Every learner deserves a teacher who" in landing_html
    assert "impact-grid" in landing_html
    assert 'class="learning-journey"' in STUDENT_HTML
    assert "prefers-reduced-motion: reduce" in styles
    assert "@keyframes vedha-float" in styles


def test_subject_specific_concepts_include_pure_telugu_social_studies() -> None:
    assert 'conceptInput.disabled = !subject' in TUTOR_JS
    assert 'subjectInput.addEventListener("change", refreshConceptOptions)' in TUTOR_JS
    for value in (
        "Indian Constitution",
        "Indian Freedom Movement",
        "Andhra Pradesh Geography",
        "Local Government",
        "Climate and Natural Resources",
    ):
        assert value in TUTOR_JS
    for telugu in (
        "భారత రాజ్యాంగం",
        "భారత స్వాతంత్ర్య ఉద్యమం",
        "ఆంధ్రప్రదేశ్ భూగోళ శాస్త్రం",
        "స్థానిక ప్రభుత్వం",
        "వాతావరణం మరియు సహజ వనరులు",
    ):
        assert telugu in TUTOR_JS


def test_frontend_tracks_attempts_per_question_for_solution_reveal() -> None:
    assert "attempts: new Map()" in TUTOR_JS
    assert "const clientAttemptNumber = previousAttempts + 1" in TUTOR_JS
    assert "attempt_number: clientAttemptNumber" in TUTOR_JS
    assert "state.attempts.clear()" in TUTOR_JS


def test_student_session_progress_is_accessible_bilingual_and_question_scoped() -> None:
    for element_id in (
        "progress-panel",
        "progress-attempted",
        "progress-mastered",
        "progress-accuracy",
        "progress-fill",
        "progress-message",
        "progress-total",
    ):
        assert f'id="{element_id}"' in STUDENT_HTML
    assert 'role="progressbar"' in STUDENT_HTML
    assert 'aria-valuemax="15"' in STUDENT_HTML
    assert "progress: new Map()" in TUTOR_JS
    assert "function recordProgress(question, evaluation)" in TUTOR_JS
    assert "state.progress.set(question.question_id" in TUTOR_JS
    assert 'byId("progress-panel").hidden = false' in TUTOR_JS
    assert 'setJourney(4)' in TUTOR_JS
    for telugu in ("ఈ అభ్యాసంలోని ప్రగతి", "ప్రయత్నించినవి", "నేర్చుకున్నవి", "ఖచ్చితత్వం"):
        assert telugu in TUTOR_JS


def test_progress_styles_support_mobile_and_reduced_motion() -> None:
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    assert ".progress-panel" in styles
    assert ".progress-metrics" in styles
    assert ".progress-track span" in styles
    assert ".journey-step.is-complete" in styles
    assert "prefers-reduced-motion: reduce" in styles


def test_government_dashboard_is_synthetic_private_and_filterable() -> None:
    dashboard_html = (FRONTEND_ROOT / "government" / "index.html").read_text(encoding="utf-8")
    dashboard_js = (FRONTEND_ROOT / "assets" / "js" / "government-dashboard.js").read_text(encoding="utf-8")
    assert 'src="../assets/js/government-dashboard.js"' in dashboard_html
    assert "Synthetic demonstration data" in dashboard_html
    assert "No student records or personal information are displayed" in dashboard_html
    assert "Aggregate insight, not surveillance" in dashboard_html
    assert 'id="district-filter"' in dashboard_html
    assert 'id="class-filter"' in dashboard_html
    assert 'role="status"' in dashboard_html
    for metric in ("learners", "lessons", "practice", "mastery", "telugu", "improvement"):
        assert f'id="metric-{metric}"' in dashboard_html
    assert "syntheticData" in dashboard_js
    assert 'byId("district-filter").addEventListener("change", renderDashboard)' in dashboard_js
    assert "innerHTML" not in dashboard_js


def test_government_dashboard_is_responsive_and_motion_safe() -> None:
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    for selector in (".dashboard-metrics", ".dashboard-grid", ".dashboard-card", ".synthetic-banner"):
        assert selector in styles
    assert "@keyframes dashboard-bar-grow" in styles
    assert "prefers-reduced-motion: reduce" in styles


def test_shared_voice_input_is_available_for_all_demo_roles() -> None:
    voice_js = (FRONTEND_ROOT / "assets" / "js" / "voice-assistant.js").read_text(encoding="utf-8")
    assert "SpeechRecognition || window.webkitSpeechRecognition" in voice_js
    assert 'target.dispatchEvent(new Event("input", { bubbles: true }))' in voice_js
    assert '"te-IN"' in voice_js
    assert '"en-IN"' in voice_js
    assert 'telugu_assisted_english: "te-IN"' in voice_js
    for interface in ("student", "teacher", "parent", "government"):
        content = (FRONTEND_ROOT / interface / "index.html").read_text(encoding="utf-8")
        assert 'src="../assets/js/voice-assistant.js"' in content
        assert "data-voice-target=" in content
        assert "voice-status" in content


def test_student_lesson_has_bilingual_read_aloud_controls() -> None:
    assert 'data-speak-target="#lesson-result"' in STUDENT_HTML
    assert "data-speech-pause" in STUDENT_HTML
    assert "data-speech-stop" in STUDENT_HTML
    voice_js = (FRONTEND_ROOT / "assets" / "js" / "voice-assistant.js").read_text(encoding="utf-8")
    assert "SpeechSynthesisUtterance" in voice_js
    assert "synth.pause()" in voice_js
    assert "synth.resume()" in voice_js


def test_government_voice_query_applies_supported_district_filter() -> None:
    dashboard_js = (FRONTEND_ROOT / "assets" / "js" / "government-dashboard.js").read_text(encoding="utf-8")
    for name in ("guntur", "గుంటూరు", "visakhapatnam", "విశాఖపట్నం"):
        assert name in dashboard_js
    assert 'byId("government-voice-form").addEventListener("submit", applyVoiceQuery)' in dashboard_js


def test_telugu_narration_never_silently_falls_back_to_english_voice() -> None:
    voice_js = (FRONTEND_ROOT / "assets" / "js" / "voice-assistant.js").read_text(encoding="utf-8")
    assert "async function preferredVoice" in voice_js
    assert '"voiceschanged"' in voice_js
    assert 'language.startsWith("te") && !voice' in voice_js
    assert "తెలుగు వాయిస్ ఈ బ్రౌజర్‌లో అందుబాటులో లేదు" in voice_js
    assert 'id="lesson-narration-status"' in STUDENT_HTML


def test_lesson_narration_excludes_interface_controls_and_section_labels() -> None:
    voice_js = (FRONTEND_ROOT / "assets" / "js" / "voice-assistant.js").read_text(encoding="utf-8")
    assert 'target.querySelectorAll("[data-narration]")' in voice_js
    for element_id in (
        "lesson-title",
        "lesson-introduction",
        "lesson-steps",
        "lesson-example",
        "lesson-points",
        "lesson-check",
    ):
        assert re.search(fr'id="{element_id}"[^>]*data-narration', STUDENT_HTML)
    assert 'data-speech-pause data-narration' not in STUDENT_HTML
    assert 'data-speech-stop data-narration' not in STUDENT_HTML


def test_student_can_choose_text_or_narrated_animation_mode() -> None:
    assert 'data-explanation-mode="text"' in STUDENT_HTML
    assert 'data-explanation-mode="animation"' in STUDENT_HTML
    assert 'id="concept-animation"' in STUDENT_HTML
    assert 'id="animation-caption"' in STUDENT_HTML
    assert 'id="animation-play"' in STUDENT_HTML
    assert 'id="animation-previous"' in STUDENT_HTML
    assert 'id="animation-next"' in STUDENT_HTML
    assert 'id="animation-replay"' in STUDENT_HTML
    assert 'src="../assets/js/concept-animations.js"' in STUDENT_HTML


def test_animation_mode_hides_written_lesson_and_keeps_only_synchronized_caption() -> None:
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    animation_js = (FRONTEND_ROOT / "assets" / "js" / "concept-animations.js").read_text(encoding="utf-8")
    assert ".lesson-result.animation-mode > .lesson-text-content" in styles
    assert "display: none" in styles
    assert 'lessonResult.classList.toggle("animation-mode", animationMode)' in animation_js
    assert 'byId("animation-caption").textContent = steps[state.index]' in animation_js


def test_four_showcase_concepts_have_bilingual_synchronized_animation_steps() -> None:
    animation_js = (FRONTEND_ROOT / "assets" / "js" / "concept-animations.js").read_text(encoding="utf-8")
    for concept in ("Fractions", "Geometry", "Water Cycle", "Solar System"):
        assert concept in animation_js
    for telugu in ("భిన్నాలు", "జ్యామితి", "నీటి చక్రం", "సౌర కుటుంబం"):
        assert telugu in animation_js
    assert "window.VedhaVoice?.speakText" in animation_js
    assert "onEnd: advanceAfterNarration" in animation_js
    assert "prefers-reduced-motion: reduce" in (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")


def test_lesson_generation_prepares_animation_for_exact_selected_concept() -> None:
    assert "window.VedhaAnimations?.prepare(state.setup.concept, state.setup.learning_profile)" in TUTOR_JS


def test_animation_player_has_government_presentation_controls_and_timeline() -> None:
    assert 'id="animation-fullscreen"' in STUDENT_HTML
    assert 'id="animation-progress"' in STUDENT_HTML
    assert 'role="progressbar"' in STUDENT_HTML
    animation_js = (FRONTEND_ROOT / "assets" / "js" / "concept-animations.js").read_text(encoding="utf-8")
    assert "requestFullscreen" in animation_js
    assert 'byId("animation-progress-fill").style.width' in animation_js


def test_animation_scenes_use_rich_concept_specific_motion_graphics() -> None:
    animation_js = (FRONTEND_ROOT / "assets" / "js" / "concept-animations.js").read_text(encoding="utf-8")
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    for visual in (
        "fraction-plate",
        "pizza-topping",
        "geometry-blueprint",
        "triangle-edge",
        "water-landscape",
        "rain-drop",
        "space-star",
        "planet-surface",
    ):
        assert visual in animation_js
        assert f".{visual}" in styles
    for animation in ("rain-fall", "star-twinkle", "sun-breathe", "water-rise"):
        assert f"@keyframes {animation}" in styles
