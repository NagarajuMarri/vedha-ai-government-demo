"use strict";

(function initializeStudentTutor(document, api) {
  const MAX_QUESTION_LENGTH = 1500;
  const state = { setup: null, question: "", loading: false, practiceLoading: false, error: null, lesson: null, practice: null, submitted: false };
  const byId = (id) => document.getElementById(id);
  const setupForm = byId("setup-form");
  const questionForm = byId("question-form");
  const questionInput = byId("question");
  const askButton = byId("ask-button");

  const messages = {
    english_medium: {
      loading: "Vedha is preparing your lesson...",
      error: "We could not prepare the lesson. Please try again.",
      fallback: "Vedha is showing a basic lesson while the advanced tutor service is unavailable.",\n      practiceLoading: "Vedha is preparing 15 practice questions...",\n      practiceError: "We could not prepare practice. Please try again.",
    },
    telugu_assisted_english: {
      loading: "Vedha మీ lesson సిద్ధం చేస్తోంది...",
      error: "Lesson సిద్ధం కాలేదు. దయచేసి మళ్లీ ప్రయత్నించండి.",
      fallback: "Advanced tutor service అందుబాటులో లేనందున Vedha ఒక basic lesson చూపిస్తోంది.",\n      practiceLoading: "Vedha 15 practice questions సిద్ధం చేస్తోంది...",\n      practiceError: "Practice సిద్ధం కాలేదు. దయచేసి మళ్లీ ప్రయత్నించండి.",
    },
    pure_telugu: {
      loading: "వేద మీ పాఠాన్ని సిద్ధం చేస్తోంది...",
      error: "పాఠాన్ని సిద్ధం చేయలేకపోయాం. దయచేసి మళ్లీ ప్రయత్నించండి.",
      fallback: "అధునాతన బోధనా సేవ అందుబాటులో లేనందున వేద ప్రాథమిక పాఠాన్ని చూపిస్తోంది.",\n      practiceLoading: "వేద 15 అభ్యాస ప్రశ్నలను సిద్ధం చేస్తోంది...",\n      practiceError: "అభ్యాస ప్రశ్నలను సిద్ధం చేయలేకపోయాం. మళ్లీ ప్రయత్నించండి.",
    },
  };

  function setList(element, items) {
    element.replaceChildren(...items.map((text) => {
      const item = document.createElement("li");
      item.textContent = text;
      return item;
    }));
  }

  function renderLesson(lesson) {
    byId("lesson-title").textContent = lesson.title;
    byId("lesson-introduction").textContent = lesson.introduction;
    setList(byId("lesson-steps"), lesson.explanation_steps);
    byId("lesson-example").textContent = lesson.example;
    setList(byId("lesson-points"), lesson.key_points);
    byId("lesson-check").textContent = lesson.check_question;
    const fallbackNote = byId("fallback-note");
    const isFallback = lesson.source === "fallback" || lesson.fallback_used;
    fallbackNote.hidden = !isFallback;
    fallbackNote.textContent = isFallback ? messages[state.setup.learning_profile].fallback : "";
    byId("lesson-result").hidden = false;
    byId("lesson-result").focus({ preventScroll: true });
    byId("lesson-result").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderPractice(practice) {
    ["easy", "medium", "hard"].forEach((difficulty) => {
      const questions = practice.questions.filter((question) => question.difficulty === difficulty);
      const list = byId(`practice-${difficulty}`);
      list.replaceChildren(...questions.map((question) => {
        const item = document.createElement("li");
        const prompt = document.createElement("p");
        const hint = document.createElement("small");
        prompt.textContent = question.prompt;
        hint.textContent = `Hint: ${question.hint}`;
        item.append(prompt, hint);
        return item;
      }));
    });
    byId("practice-result").hidden = false;
    byId("practice-result").focus({ preventScroll: true });
    byId("practice-result").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function setPracticeLoading(isLoading) {
    state.practiceLoading = isLoading;
    const button = byId("generate-practice");
    button.disabled = isLoading;
    button.textContent = isLoading ? "Preparing 15 questions…" : "Generate Practice";
    byId("practice-status").textContent = isLoading ? messages[state.setup.learning_profile].practiceLoading : "";
  }

  function setLoading(isLoading) {
    state.loading = isLoading;
    askButton.disabled = isLoading;
    askButton.textContent = isLoading ? "Preparing lesson…" : "Ask Vedha";
    byId("status-message").textContent = isLoading ? messages[state.setup.learning_profile].loading : "";
  }

  function showSafeError() {
    const error = byId("error-message");
    error.textContent = messages[state.setup.learning_profile].error;
    error.hidden = false;
    error.focus();
  }

  function validateQuestion() {
    const trimmed = questionInput.value.trim();
    const error = byId("question-error");
    let message = "";
    if (!trimmed) message = "Enter a question before asking Vedha.";
    else if (questionInput.value.length > MAX_QUESTION_LENGTH) message = "Your question must be 1500 characters or fewer.";
    error.textContent = message;
    error.hidden = !message;
    questionInput.setAttribute("aria-invalid", String(Boolean(message)));
    return message ? null : trimmed;
  }

  setupForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!setupForm.reportValidity()) return;
    const form = new FormData(setupForm);
    state.setup = {
      student_name: String(form.get("student_name")).trim(),
      class_level: Number(form.get("class_level")),
      subject: String(form.get("subject")),
      learning_profile: String(form.get("learning_profile")),
    };
    byId("student-context").textContent = `${state.setup.student_name} · Class ${state.setup.class_level} · ${state.setup.subject} · ${state.setup.concept}`;
    byId("setup-view").hidden = true;
    byId("tutor-view").hidden = false;
    questionInput.focus();
  });

  byId("edit-setup").addEventListener("click", () => {
    byId("tutor-view").hidden = true;
    byId("setup-view").hidden = false;
    byId("student-name").focus();
  });

  questionInput.addEventListener("input", () => {
    state.question = questionInput.value;
    byId("question-counter").textContent = `${questionInput.value.length} / ${MAX_QUESTION_LENGTH}`;
    if (!byId("question-error").hidden) validateQuestion();
  });
  questionInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (!state.loading) questionForm.requestSubmit();
    }
  });

  questionForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (state.loading) return;
    const question = validateQuestion();
    if (!question) return;
    state.question = questionInput.value;
    state.error = null;
    state.submitted = true;
    byId("error-message").hidden = true;
    byId("lesson-result").hidden = true;
    setLoading(true);
    try {
      state.lesson = await api.requestLesson({ ...state.setup, question });
      renderLesson(state.lesson);
    } catch (_error) {
      state.error = "lesson_request_failed";
      showSafeError();
    } finally {
      setLoading(false);
    }
  });
})(document, window.VedhaLessonApi);
