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
    for text in ("మార్గదర్శక అభ్యాసం", "సులభం · 5", "సమాధానం తనిఖీ", "చేతిరాత పరిష్కారం జోడించండి", "అభ్యాసం రూపొందించండి"):
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


def test_all_available_concepts_have_synchronized_animation_templates() -> None:
    animation_js = (FRONTEND_ROOT / "assets" / "js" / "concept-animations.js").read_text(encoding="utf-8")
    for concept in (
        "Fractions", "Decimals", "Geometry", "Solar System", "Water Cycle",
        "Photosynthesis", "Grammar", "Telugu Grammar", "Indian Constitution",
        "Indian Freedom Movement", "Andhra Pradesh Geography", "Local Government",
        "Climate and Natural Resources",
    ):
        assert concept in animation_js
    for telugu in ("భిన్నాలు", "జ్యామితి", "నీటి చక్రం", "సౌర కుటుంబం"):
        assert telugu in animation_js
    assert "window.VedhaVoice?.speakText" in animation_js
    assert "onEnd: scheduleAdvanceAfterNarration" in animation_js
    assert "prefers-reduced-motion: reduce" in (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")


def test_lesson_generation_prepares_animation_for_exact_selected_concept() -> None:
    assert "window.VedhaAnimations?.prepare(state.setup.concept, state.setup.learning_profile, lesson)" in TUTOR_JS


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


def test_fraction_animation_cuts_whole_pizza_in_narrated_sequence() -> None:
    animation_js = (FRONTEND_ROOT / "assets" / "js" / "concept-animations.js").read_text(encoding="utf-8")
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    assert 'node("pizza-cut cut-vertical")' in animation_js
    assert 'node("pizza-cut cut-horizontal")' in animation_js
    assert "ముందుగా మధ్యలో నిలువుగా ఒక కోత" in animation_js
    assert "మధ్యలో అడ్డంగా రెండవ కోత" in animation_js
    assert '.animation-stage[data-concept="fractions"][data-step="2"] .cut-vertical' in styles
    assert '.animation-stage[data-concept="fractions"][data-step="3"] .cut-horizontal' in styles
    assert 'node("piece-number", String(index + 1))' in animation_js


def test_all_animated_lessons_are_between_one_and_five_minutes() -> None:
    animation_js = (FRONTEND_ROOT / "assets" / "js" / "concept-animations.js").read_text(encoding="utf-8")
    durations = [int(value) for value in re.findall(r"durationSeconds: (\d+)", animation_js)]
    assert len(durations) == 13
    assert all(60 <= duration <= 300 for duration in durations)
    assert "estimateNarrationSeconds" in animation_js
    assert "Math.max(60, Math.min(300" in animation_js
    assert 'id="animation-duration"' in STUDENT_HTML


def test_fraction_animation_has_extended_eight_step_instruction() -> None:
    animation_js = (FRONTEND_ROOT / "assets" / "js" / "concept-animations.js").read_text(encoding="utf-8")
    fraction_block = animation_js.split("Fractions:", 1)[1].split("Geometry:", 1)[0]
    english_steps = fraction_block.split("en: [", 1)[1].split("],", 1)[0]
    assert english_steps.count('",') >= 7
    assert "Three is the numerator" in fraction_block
    assert "four equal pieces" in fraction_block


def test_animation_narrates_the_complete_generated_text_lesson() -> None:
    animation_js = (FRONTEND_ROOT / "assets" / "js" / "concept-animations.js").read_text(encoding="utf-8")
    assert "function buildFullLessonNarration(generatedLesson)" in animation_js
    for lesson_part in (
        "generatedLesson.introduction",
        "...generatedLesson.explanation_steps",
        "generatedLesson.example",
        "...generatedLesson.key_points",
        "generatedLesson.check_question",
    ):
        assert lesson_part in animation_js
    assert "steps: { en: fullNarration, te: fullNarration }" in animation_js
    assert "generatedLesson.title" in animation_js


def test_practice_answers_support_voice_input_in_selected_language() -> None:
    assert 'voiceAnswer:' in TUTOR_JS
    assert 'input.id = `practice-answer-${question.question_id}`' in TUTOR_JS
    assert 'voiceButton.dataset.voiceTarget = `#${input.id}`' in TUTOR_JS
    assert 'voiceButton.dataset.voiceStatus = `#practice-voice-status-${question.question_id}`' in TUTOR_JS
    assert 'voiceButton.dataset.voiceLanguageSource = \'input[name="learning_profile"]:checked\'' in TUTOR_JS
    assert 'answerRow.append(input, voiceButton, button)' in TUTOR_JS
    assert 'input.className = "practice-answer"' in TUTOR_JS


def test_all_animation_templates_have_distinct_visual_scenes() -> None:
    animation_js = (FRONTEND_ROOT / "assets" / "js" / "concept-animations.js").read_text(encoding="utf-8")
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    for visual in (
        "decimal-scene", "plant-scene", "grammar-scene", "constitution-scene",
        "freedom-scene", "ap-scene", "local-government-scene", "resources-scene",
    ):
        assert visual in animation_js
        assert f".{visual}" in styles


def test_animation_narration_autoplays_and_manual_navigation_speaks() -> None:
    animation_js = (FRONTEND_ROOT / "assets" / "js" / "concept-animations.js").read_text(encoding="utf-8")
    voice_js = (FRONTEND_ROOT / "assets" / "js" / "voice-assistant.js").read_text(encoding="utf-8")
    assert 'if (animationMode)' in animation_js
    assert "play();" in animation_js
    assert 'if (event.target.closest("#animation-next"))' in animation_js
    assert 'if (event.target.closest("#animation-previous"))' in animation_js
    assert animation_js.count("narrateCurrentStep();") >= 4
    assert "if (synth.paused) synth.resume()" in voice_js
    assert "function narrationChunks(text, maxLength = 170)" in voice_js
    assert "window.setTimeout(speakChunk, 80)" in voice_js
    assert "speechToken" in voice_js


def test_animation_visual_phase_tracks_narrated_sentence() -> None:
    animation_js = (FRONTEND_ROOT / "assets" / "js" / "concept-animations.js").read_text(encoding="utf-8")
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    assert "function visualPhase(concept, caption, index, total)" in animation_js
    assert "stage.dataset.phase = activePhase" in animation_js
    for phase in ("roots-water", "carbon", "food", "oxygen"):
        assert phase in animation_js
        assert f'data-phase="{phase}"' in styles
    for animation in ("water-into-roots", "gas-into-leaf", "oxygen-release"):
        assert f"@keyframes {animation}" in styles


def test_photosynthesis_animation_progressively_shows_inputs_and_outputs() -> None:
    animation_js = (FRONTEND_ROOT / "assets" / "js" / "concept-animations.js").read_text(encoding="utf-8")
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    assert 'node("sunlight-rays")' in animation_js
    assert 'node(`sunlight-ray sunlight-ray-${index + 1}`)' in animation_js
    assert 'node("water-particles")' in animation_js
    assert 'stage.classList.add(`seen-${resolvedVisualPhase' in animation_js
    for selector in (
        ".seen-sunlight .sunlight-rays",
        ".seen-roots-water .water-particles",
        ".seen-carbon .carbon-flow",
        ".seen-food .plant-food",
        ".seen-oxygen .oxygen-flow",
    ):
        assert selector in styles
    assert "@keyframes sunbeam-fall" in styles
    assert "@keyframes water-up-stem" in styles


def test_every_narration_point_renders_a_fresh_storyboard_action() -> None:
    animation_js = (FRONTEND_ROOT / "assets" / "js" / "concept-animations.js").read_text(encoding="utf-8")
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    assert "const fallbackPhaseSequence" in animation_js
    assert "function resolvedVisualPhase(concept, caption, index, total)" in animation_js
    assert "function renderSentenceScene(stage, concept, phase, index)" in animation_js
    assert 'stage.querySelector(".sentence-scene")?.remove()' in animation_js
    assert "renderSentenceScene(stage, state.concept, activePhase, state.index)" in animation_js
    assert ".sentence-scene" in styles
    assert "@keyframes sentence-scene-cut" in styles
    for phase in ("sunlight", "roots-water", "carbon", "food", "oxygen"):
        assert f'data-action="{phase}"' in styles


def test_practice_presents_one_validated_question_at_a_time() -> None:
    assert "practiceIndex: 0" in TUTOR_JS
    assert "function showPracticeQuestion(index)" in TUTOR_JS
    assert 'item.dataset.practiceIndex = String(questionIndexes.get(question.question_id))' in TUTOR_JS
    assert 'item.className = "focused-practice-question"' in TUTOR_JS
    assert 'item.hidden = true' in TUTOR_JS
    assert "Question ${state.practiceIndex + 1} of ${questions.length}" in TUTOR_JS
    assert "function unlockNextQuestion(item, evaluation)" in TUTOR_JS
    assert "if (!evaluation.correct && evaluation.attempt_number < 2) return" in TUTOR_JS
    assert 'nextButton.className = "primary-button next-question"' in TUTOR_JS
    assert "showPracticeQuestion(currentIndex + 1)" in TUTOR_JS


def test_focused_practice_card_keeps_all_answer_methods_responsive() -> None:
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    assert ".practice-result.sequential-practice" in styles
    assert ".focused-practice-question" in styles
    assert ".focused-practice-question .practice-answer-row" in styles
    assert ".focused-practice-question .next-question" in styles
    assert "@keyframes question-card-enter" in styles
    assert "Upload Handwritten Work" in TUTOR_JS
    assert "Speak Answer" in TUTOR_JS


def test_photosynthesis_uses_separate_full_scenes_for_each_process() -> None:
    animation_js = (FRONTEND_ROOT / "assets" / "js" / "concept-animations.js").read_text(encoding="utf-8")
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    for visual in (
        "process-rays", "root-soil-cutaway", "leaf-closeup",
        "chloroplast-factory", "oxygen-bubbles",
    ):
        assert visual in animation_js
        assert f".{visual}" in styles
    for phase in ("sunlight", "roots-water", "carbon", "food", "oxygen"):
        assert f"sentence-phase-{phase}" in styles
    for animation in (
        "light-hit-leaf", "drop-to-root", "co2-enter",
        "o2-release-scene", "sentence-scene-cut",
    ):
        assert f"@keyframes {animation}" in styles


def test_every_available_lesson_has_dedicated_sentence_level_scenes() -> None:
    animation_js = (FRONTEND_ROOT / "assets" / "js" / "concept-animations.js").read_text(encoding="utf-8")
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    concepts = (
        "Fractions", "Decimals", "Geometry", "Water Cycle", "Solar System",
        "Grammar", "Telugu Grammar", "Indian Constitution",
        "Indian Freedom Movement", "Andhra Pradesh Geography",
        "Local Government", "Climate and Natural Resources",
    )
    assert "const dedicatedAnimatedConcepts = new Set" in animation_js
    assert "function renderDedicatedLessonScene(scene, concept, phase)" in animation_js
    for concept in concepts:
        assert f'"{concept}"' in animation_js
        css_name = concept.lower().replace(" ", "-")
        assert f".dedicated-{css_name}" in styles
    assert "dedicatedAnimatedConcepts.has(concept)" in animation_js


def test_dedicated_lesson_scenes_contain_subject_specific_visual_objects() -> None:
    animation_js = (FRONTEND_ROOT / "assets" / "js" / "concept-animations.js").read_text(encoding="utf-8")
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    visuals = (
        "story-pizza", "place-value-table", "geometry-story-board",
        "cycle-story-world", "solar-story-system", "grammar-story-builder",
        "civic-story", "freedom-story-road", "ap-story-map",
        "government-story", "resource-story",
    )
    for visual in visuals:
        assert visual in animation_js
        assert f".{visual}" in styles
    assert "scene.dataset.dedicatedPhase = phase" in animation_js


def test_parent_portal_is_functional_bilingual_and_synthetic() -> None:
    parent_html = (FRONTEND_ROOT / "parent" / "index.html").read_text(encoding="utf-8")
    parent_js = (FRONTEND_ROOT / "assets" / "js" / "parent-dashboard.js").read_text(encoding="utf-8")
    assert 'src="../assets/js/parent-dashboard.js"' in parent_html
    assert "Synthetic demonstration data" in parent_html
    assert "only see explicitly linked children" in parent_html
    assert 'id="child-selector"' in parent_html
    assert 'id="parent-language"' in parent_html
    for element_id in (
        "strengths-list", "attention-list", "activity-list",
        "recommendation-list", "parent-answer",
    ):
        assert f'id="{element_id}"' in parent_html
    assert "const children =" in parent_js
    assert "ananya:" in parent_js
    assert "arjun:" in parent_js
    assert "innerHTML" not in parent_js


def test_parent_portal_supports_voice_queries_and_spoken_insights() -> None:
    parent_html = (FRONTEND_ROOT / "parent" / "index.html").read_text(encoding="utf-8")
    parent_js = (FRONTEND_ROOT / "assets" / "js" / "parent-dashboard.js").read_text(encoding="utf-8")
    assert 'id="parent-voice-form"' in parent_html
    assert 'data-voice-target="#parent-voice-query"' in parent_html
    assert 'data-speak-target="#parent-answer"' in parent_html
    assert "parent-voice-form" in parent_js
    assert "answerQuery" in parent_js
    for telugu in ("ప్రగతిని చూడండి", "సహాయం అవసరమైనవి", "వేదను అడగండి"):
        assert telugu in parent_js


def test_parent_portal_is_responsive_and_presentation_ready() -> None:
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    for selector in (
        ".parent-portal", ".parent-summary", ".parent-metrics",
        ".parent-grid", ".parent-card", ".parent-voice-card",
    ):
        assert selector in styles
    assert "@media(max-width:52rem)" in styles
    assert "@media(max-width:30rem)" in styles


def test_parent_portal_has_subject_weekly_monthly_and_exam_reports() -> None:
    parent_html = (FRONTEND_ROOT / "parent" / "index.html").read_text(encoding="utf-8")
    parent_js = (FRONTEND_ROOT / "assets" / "js" / "parent-dashboard.js").read_text(encoding="utf-8")
    for element_id in (
        "report-period", "subject-completion-list", "overall-completion",
        "exam-completion", "exam-progress-fill", "exam-completed-list",
        "exam-remaining-list", "exam-next-step",
    ):
        assert f'id="{element_id}"' in parent_html
    assert "reports: { weekly:" in parent_js
    assert "monthly:" in parent_js
    assert "subjectCompletion:" in parent_js
    assert "exam: { title:" in parent_js
    assert 'byId("report-period").addEventListener("change",render)' in parent_js
    assert "child.exam.completion" in parent_js
    assert "exam|preparation|complete|పరీక్ష|సిద్ధత|పూర్తి" in parent_js


def test_parent_exam_report_layout_is_responsive() -> None:
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    for selector in (
        ".parent-report-grid", ".exam-readiness-ring", ".exam-progress-track",
        ".exam-plan-columns", ".next-study-step",
    ):
        assert selector in styles
    assert "@media(max-width:58rem)" in styles
    assert "@media(max-width:36rem)" in styles


def test_parent_portal_offers_three_explicit_language_profiles() -> None:
    parent_html = (FRONTEND_ROOT / "parent" / "index.html").read_text(encoding="utf-8")
    parent_js = (FRONTEND_ROOT / "assets" / "js" / "parent-dashboard.js").read_text(encoding="utf-8")
    for profile in ("english_medium", "pure_telugu", "telugu_assisted_english"):
        assert f'value="{profile}"' in parent_html
        assert profile in parent_js
    assert "English terms" in parent_html


def test_parent_portal_localizes_dynamic_report_content_not_only_headings() -> None:
    parent_js = (FRONTEND_ROOT / "assets" / "js" / "parent-dashboard.js").read_text(encoding="utf-8")
    for pure_telugu in (
        "గణితం · భిన్నాలు", "విజ్ఞాన శాస్త్రం · సౌర కుటుంబం",
        "కోణాలు, త్రిభుజ నియమాలను పునశ్చరణ చేయండి",
        "భిన్నాల పాఠం మరియు 5 అభ్యాస ప్రశ్నలను పూర్తి చేశారు",
        "టర్మ్ పరీక్ష సిద్ధత",
    ):
        assert pure_telugu in parent_js
    for assisted in (
        "Angles మరియు triangle rulesను review చేయండి",
        "Fractions lesson మరియు 5 practice questions complete చేశారు",
        "Progress చూడండి",
    ):
        assert assisted in parent_js
    assert "function translate(text, profile)" in parent_js
    assert "progressRow([translate(label, language), score])" in parent_js
    assert "translate(child.exam.title, language)" in parent_js
    assert "translate(recommendation, language)" in parent_js


def test_parent_voice_insights_follow_selected_language_profile() -> None:
    parent_js = (FRONTEND_ROOT / "assets" / "js" / "parent-dashboard.js").read_text(encoding="utf-8")
    assert 'profile === "pure_telugu"' in parent_js
    assert 'profile === "telugu_assisted_english"' in parent_js
    assert "Accuracy" in parent_js
    assert "తదుపరి దశ" in parent_js


def test_teacher_portal_is_functional_and_uses_assigned_synthetic_classes() -> None:
    teacher_html = (FRONTEND_ROOT / "teacher" / "index.html").read_text(encoding="utf-8")
    teacher_js = (FRONTEND_ROOT / "assets" / "js" / "teacher-dashboard.js").read_text(encoding="utf-8")
    assert 'src="../assets/js/teacher-dashboard.js"' in teacher_html
    assert "Synthetic demonstration data" in teacher_html
    assert "only see assigned classes and students" in teacher_html
    for element_id in (
        "teacher-class", "teacher-subject", "concept-performance", "intervention-list",
        "student-roster", "assignment-form", "approval-question", "teacher-voice-form",
    ):
        assert f'id="{element_id}"' in teacher_html
    assert "nineA:" in teacher_js
    assert "sixB:" in teacher_js
    assert "innerHTML" not in teacher_js


def test_teacher_portal_supports_three_language_profiles_and_voice_insights() -> None:
    teacher_html = (FRONTEND_ROOT / "teacher" / "index.html").read_text(encoding="utf-8")
    teacher_js = (FRONTEND_ROOT / "assets" / "js" / "teacher-dashboard.js").read_text(encoding="utf-8")
    for profile in ("english_medium", "pure_telugu", "telugu_assisted_english"):
        assert f'value="{profile}"' in teacher_html
        assert profile in teacher_js
    assert 'data-voice-language-source="#teacher-language"' in teacher_html
    assert 'data-speak-target="#teacher-answer"' in teacher_html
    for telugu in ("భావనల వారీ ఫలితాలు", "సహాయ సంకేతాలు", "పునరభ్యాసం కేటాయించండి"):
        assert telugu in teacher_js


def test_teacher_portal_supports_interventions_assignments_and_ai_approval() -> None:
    teacher_js = (FRONTEND_ROOT / "assets" / "js" / "teacher-dashboard.js").read_text(encoding="utf-8")
    assert 'row[3]<70' in teacher_js
    assert 'byId("assignment-form").addEventListener("submit"' in teacher_js
    assert 'byId("approve-question").addEventListener("click"' in teacher_js
    assert 'byId("reject-question").addEventListener("click"' in teacher_js
    assert "Question student practiceకు approve అయింది." in teacher_js


def test_teacher_dashboard_layout_is_responsive_and_presentation_ready() -> None:
    styles = (FRONTEND_ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    for selector in (".teacher-portal", ".teacher-hero", ".teacher-metrics", ".teacher-grid", ".teacher-table-wrap"):
        assert selector in styles
    assert "@media(max-width:64rem)" in styles
    assert "@media(max-width:38rem)" in styles


def test_gateway_presents_integrated_four_role_ministerial_journey() -> None:
    landing = (FRONTEND_ROOT / "index.html").read_text(encoding="utf-8")
    for text in ("Ministerial demonstration path", "Student learns", "Parent supports", "Teacher intervenes", "Leader sees impact"):
        assert text in landing
    for href in ('href="student/"', 'href="parent/"', 'href="teacher/"', 'href="government/"'):
        assert href in landing
    assert 'href="demo/"' in landing
    assert (FRONTEND_ROOT / "demo" / "index.html").is_file()


def test_government_dashboard_has_three_profile_voice_and_spoken_insight() -> None:
    html = (FRONTEND_ROOT / "government" / "index.html").read_text(encoding="utf-8")
    js = (FRONTEND_ROOT / "assets" / "js" / "government-dashboard.js").read_text(encoding="utf-8")
    for profile in ("english_medium", "pure_telugu", "telugu_assisted_english"):
        assert f'value="{profile}"' in html
        assert profile in js
    assert 'id="government-answer"' in html
    assert 'data-speak-target="#government-answer"' in html
    assert 'data-speech-pause' in html
    assert "ఇవన్నీ కల్పిత ప్రదర్శన సూచికలు" in js
    assert "synthetic demo indicators" in js


def test_demo_runbook_locks_rehearsal_and_recovery_paths() -> None:
    runbook = (PROJECT_ROOT / "docs" / "DEMO_RUNBOOK.md").read_text(encoding="utf-8")
    for section in ("Pre-demo checklist", "Demonstration script", "Bilingual rehearsal matrix", "Recovery plan", "Completion gate"):
        assert section in runbook
    assert "12 minutes presentation" in runbook
    assert "no student-level drill-down" in runbook
    assert "Ctrl+Shift+R" in runbook


def test_government_dashboard_supports_hierarchical_and_subject_filters() -> None:
    html = (FRONTEND_ROOT / "government" / "index.html").read_text(encoding="utf-8")
    js = (FRONTEND_ROOT / "assets" / "js" / "government-dashboard.js").read_text(encoding="utf-8")
    for element_id in ("district-filter", "mandal-filter", "school-filter", "subject-filter", "class-filter"):
        assert f'id="{element_id}"' in html
    assert "const hierarchy=" in js
    assert "function populateMandals()" in js
    assert "function populateSchools()" in js
    assert 'byId("mandal-filter").addEventListener("change"' in js
    assert '"Mathematics":"గణితం"' not in js or "subjectAliases" in js
    for scope in ("Gajuwaka", "Tenali", "Mangalagiri", "Adoni", "Chandragiri", "Rajamahendravaram"):
        assert scope in js
    assert "Vedha Demo ZPHS Tenali" in js


def test_school_analytics_remain_aggregate_and_privacy_safe() -> None:
    html = (FRONTEND_ROOT / "government" / "index.html").read_text(encoding="utf-8")
    js = (FRONTEND_ROOT / "assets" / "js" / "government-dashboard.js").read_text(encoding="utf-8")
    assert "School views remain aggregate" in html
    assert "Math.max(40" in js
    assert "No individual student data is shown." in js
    assert "వ్యక్తిగత విద్యార్థి వివరాలు చూపబడవు" in js
    assert "student_id" not in js
    assert "student-name" not in html


def test_government_voice_query_understands_mandal_school_and_subject() -> None:
    js = (FRONTEND_ROOT / "assets" / "js" / "government-dashboard.js").read_text(encoding="utf-8")
    assert "function findVoiceSelections(query)" in js
    assert "subjectAliases" in js
    assert "mandalKey" in js
    assert "schoolKey" in js
    assert 'byId("subject-filter").value=found.subject' in js
