"use strict";

(function initializeStudentTutor(document, api) {
  const MAX_QUESTION_LENGTH = 1500;
  const state = { setup: null, question: "", loading: false, practiceLoading: false, evaluating: new Set(), uploading: new Set(), error: null, lesson: null, practice: null, submitted: false };
  const byId = (id) => document.getElementById(id);
  const setupForm = byId("setup-form");
  const questionForm = byId("question-form");
  const questionInput = byId("question");
  const askButton = byId("ask-button");

  const messages = {
    english_medium: {
      loading: "Vedha is preparing your lesson...",
      error: "We could not prepare the lesson. Please try again.",
      fallback: "Vedha is showing a basic lesson while the advanced tutor service is unavailable.",
      practiceLoading: "Vedha is preparing 15 practice questions...",
      practiceError: "We could not prepare practice. Please try again.",
      answerRequired: "Type an answer before checking.",
      evaluationError: "We could not check this answer. Please try again.",
      uploadError: "Use a clear JPG or PNG phone photo, 5 MB or smaller.",
      uploadLoading: "Vedha is reading your handwritten work…",
    },
    telugu_assisted_english: {
      loading: "Vedha మీ lesson సిద్ధం చేస్తోంది...",
      error: "Lesson సిద్ధం కాలేదు. దయచేసి మళ్లీ ప్రయత్నించండి.",
      fallback: "Advanced tutor service అందుబాటులో లేనందున Vedha ఒక basic lesson చూపిస్తోంది.",
      practiceLoading: "Vedha 15 practice questions సిద్ధం చేస్తోంది...",
      practiceError: "Practice సిద్ధం కాలేదు. దయచేసి మళ్లీ ప్రయత్నించండి.",
      answerRequired: "Check చేసే ముందు answer type చేయండి.",
      evaluationError: "ఈ answerను check చేయలేకపోయాం. మళ్లీ ప్రయత్నించండి.",
      uploadError: "Clear JPG లేదా PNG phone photo upload చేయండి; 5 MBలోపు ఉండాలి.",
      uploadLoading: "Vedha మీ handwritten workను చదువుతోంది…",
    },
    pure_telugu: {
      loading: "వేద మీ పాఠాన్ని సిద్ధం చేస్తోంది...",
      error: "పాఠాన్ని సిద్ధం చేయలేకపోయాం. దయచేసి మళ్లీ ప్రయత్నించండి.",
      fallback: "అధునాతన బోధనా సేవ అందుబాటులో లేనందున వేద ప్రాథమిక పాఠాన్ని చూపిస్తోంది.",
      practiceLoading: "వేద 15 అభ్యాస ప్రశ్నలను సిద్ధం చేస్తోంది...",
      practiceError: "అభ్యాస ప్రశ్నలను సిద్ధం చేయలేకపోయాం. మళ్లీ ప్రయత్నించండి.",
      answerRequired: "తనిఖీ చేసే ముందు సమాధానం రాయండి.",
      evaluationError: "ఈ సమాధానాన్ని తనిఖీ చేయలేకపోయాం. మళ్లీ ప్రయత్నించండి.",
      uploadError: "స్పష్టమైన JPG లేదా PNG ఫోన్ ఫోటోను ఎంచుకోండి; పరిమాణం 5 MBలోపు ఉండాలి.",
      uploadLoading: "వేద మీ చేతిరాత పరిష్కారాన్ని చదువుతోంది…",
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

  function renderEvaluation(item, evaluation) {
    const feedback = item.querySelector(".answer-feedback");
    const guidance = item.querySelector(".corrective-guidance");
    feedback.textContent = evaluation.feedback;
    feedback.className = `answer-feedback ${evaluation.correct ? "answer-correct" : "answer-incorrect"}`;
    guidance.replaceChildren(...evaluation.corrective_guidance.map((text) => {
      const step = document.createElement("li");
      step.textContent = text;
      return step;
    }));
    guidance.hidden = false;
    feedback.focus({ preventScroll: true });
  }

  async function evaluateAnswer(question, item) {
    const input = item.querySelector(".practice-answer");
    const button = item.querySelector(".check-answer");
    const feedback = item.querySelector(".answer-feedback");
    const studentAnswer = input.value.trim();
    if (!studentAnswer) {
      feedback.textContent = messages[state.setup.learning_profile].answerRequired;
      feedback.className = "answer-feedback answer-incorrect";
      feedback.focus();
      return;
    }
    if (state.evaluating.has(question.question_id)) return;
    state.evaluating.add(question.question_id);
    button.disabled = true;
    button.textContent = "Checking…";
    feedback.textContent = "";
    try {
      const evaluation = await api.requestPracticeEvaluation({
        practice_set_id: state.practice.practice_set_id,
        question_id: question.question_id,
        student_answer: studentAnswer,
      });
      renderEvaluation(item, evaluation);
    } catch (_error) {
      feedback.textContent = messages[state.setup.learning_profile].evaluationError;
      feedback.className = "answer-feedback answer-incorrect";
      feedback.focus();
    } finally {
      state.evaluating.delete(question.question_id);
      button.disabled = false;
      button.textContent = "Check Answer";
    }
  }

  function readImage(file) {
    return new Promise((resolve, reject) => {
      if (!file || !["image/jpeg", "image/png"].includes(file.type) || file.size > 5 * 1024 * 1024) {
        reject(new Error("invalid_image"));
        return;
      }
      const reader = new FileReader();
      reader.addEventListener("load", () => resolve(String(reader.result)));
      reader.addEventListener("error", () => reject(new Error("read_failed")));
      reader.readAsDataURL(file);
    });
  }

  async function evaluateHandwriting(question, item, file) {
    const uploadButton = item.querySelector(".upload-work");
    const uploadStatus = item.querySelector(".upload-status");
    if (state.uploading.has(question.question_id)) return;
    state.uploading.add(question.question_id);
    uploadButton.disabled = true;
    uploadStatus.textContent = messages[state.setup.learning_profile].uploadLoading;
    uploadStatus.className = "upload-status";
    try {
      const imageDataUrl = await readImage(file);
      const evaluation = await api.requestHandwritingEvaluation({
        practice_set_id: state.practice.practice_set_id,
        question_id: question.question_id,
        image_data_url: imageDataUrl,
      });
      uploadStatus.textContent = `Transcribed work: ${evaluation.transcribed_work} · Confidence: ${Math.round(evaluation.confidence * 100)}%`;
      renderEvaluation(item, evaluation);
    } catch (_error) {
      uploadStatus.textContent = messages[state.setup.learning_profile].uploadError;
      uploadStatus.className = "upload-status answer-incorrect";
      uploadStatus.focus();
    } finally {
      state.uploading.delete(question.question_id);
      uploadButton.disabled = false;
      uploadButton.textContent = "Upload Handwritten Work";
    }
  }

  function renderPractice(practice) {
    ["easy", "medium", "hard"].forEach((difficulty) => {
      const questions = practice.questions.filter((question) => question.difficulty === difficulty);
      const list = byId(`practice-${difficulty}`);
      list.replaceChildren(...questions.map((question) => {
        const item = document.createElement("li");
        const prompt = document.createElement("p");
        const hint = document.createElement("small");
        const answerRow = document.createElement("div");
        const input = document.createElement("input");
        const button = document.createElement("button");
        const feedback = document.createElement("p");
        const guidance = document.createElement("ul");
        const uploadRow = document.createElement("div");
        const uploadInput = document.createElement("input");
        const uploadButton = document.createElement("button");
        const uploadStatus = document.createElement("p");
        prompt.textContent = question.prompt;
        hint.textContent = `Hint: ${question.hint}`;
        input.type = "text";
        input.className = "practice-answer";
        input.placeholder = "Type your answer";
        input.setAttribute("aria-label", `Answer for: ${question.prompt}`);
        button.type = "button";
        button.className = "secondary-button check-answer";
        button.textContent = "Check Answer";
        feedback.className = "answer-feedback";
        feedback.tabIndex = -1;
        feedback.setAttribute("aria-live", "polite");
        guidance.className = "corrective-guidance";
        guidance.hidden = true;
        uploadInput.type = "file";
        uploadInput.accept = "image/jpeg,image/png";
        uploadInput.className = "handwriting-input";
        uploadInput.hidden = true;
        uploadButton.type = "button";
        uploadButton.className = "secondary-button upload-work";
        uploadButton.textContent = "Upload Handwritten Work";
        uploadStatus.className = "upload-status";
        uploadStatus.tabIndex = -1;
        uploadStatus.setAttribute("aria-live", "polite");
        uploadButton.addEventListener("click", () => uploadInput.click());
        uploadInput.addEventListener("change", () => {
          const file = uploadInput.files && uploadInput.files[0];
          if (file) evaluateHandwriting(question, item, file);
          uploadInput.value = "";
        });
        button.addEventListener("click", () => evaluateAnswer(question, item));
        input.addEventListener("keydown", (event) => {
          if (event.key === "Enter") {
            event.preventDefault();
            button.click();
          }
        });
        answerRow.className = "practice-answer-row";
        answerRow.append(input, button);
        uploadRow.className = "handwriting-upload-row";
        uploadRow.append(uploadInput, uploadButton);
        item.append(prompt, hint, answerRow, uploadRow, uploadStatus, feedback, guidance);
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
      concept: String(form.get("concept")),
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

  byId("generate-practice").addEventListener("click", async () => {
    if (state.practiceLoading || !state.setup) return;
    byId("practice-error").hidden = true;
    byId("practice-result").hidden = true;
    setPracticeLoading(true);
    try {
      state.practice = await api.requestPractice(state.setup);
      renderPractice(state.practice);
    } catch (_error) {
      const error = byId("practice-error");
      error.textContent = messages[state.setup.learning_profile].practiceError;
      error.hidden = false;
      error.focus();
    } finally {
      setPracticeLoading(false);
    }
  });
})(document, window.VedhaLessonApi);
