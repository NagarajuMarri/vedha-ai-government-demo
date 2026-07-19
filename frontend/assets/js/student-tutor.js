"use strict";

(function initializeStudentTutor(document, api) {
  const MAX_QUESTION_LENGTH = 1500;
  const state = { setup: null, question: "", loading: false, practiceLoading: false, evaluating: new Set(), uploading: new Set(), attempts: new Map(), progress: new Map(), error: null, lesson: null, practice: null, submitted: false };
  const byId = (id) => document.getElementById(id);
  const setupForm = byId("setup-form");
  const questionForm = byId("question-form");
  const questionInput = byId("question");
  const askButton = byId("ask-button");
  const subjectInput = byId("subject");
  const conceptInput = byId("concept");

  const conceptsBySubject = {
    Mathematics: [
      ["Fractions", "Fractions", "భిన్నాలు"],
      ["Decimals", "Decimals", "దశాంశాలు"],
      ["Geometry", "Geometry", "జ్యామితి"],
    ],
    Science: [
      ["Solar System", "Solar System", "సౌర కుటుంబం"],
      ["Water Cycle", "Water Cycle", "నీటి చక్రం"],
      ["Photosynthesis", "Photosynthesis", "కిరణజన్య సంయోగక్రియ"],
    ],
    English: [["Grammar", "Grammar", "ఆంగ్ల వ్యాకరణం"]],
    Telugu: [["Telugu Grammar", "Telugu Grammar", "తెలుగు వ్యాకరణం"]],
    "Social Studies": [
      ["Indian Constitution", "Indian Constitution", "భారత రాజ్యాంగం"],
      ["Indian Freedom Movement", "Indian Freedom Movement", "భారత స్వాతంత్ర్య ఉద్యమం"],
      ["Andhra Pradesh Geography", "Andhra Pradesh Geography", "ఆంధ్రప్రదేశ్ భూగోళ శాస్త్రం"],
      ["Local Government", "Local Government", "స్థానిక ప్రభుత్వం"],
      ["Climate and Natural Resources", "Climate and Natural Resources", "వాతావరణం మరియు సహజ వనరులు"],
    ],
  };

  function selectedProfile() {
    return setupForm.querySelector('input[name="learning_profile"]:checked')?.value || "english_medium";
  }

  function refreshConceptOptions() {
    const subject = subjectInput.value;
    const profile = selectedProfile();
    const previousValue = conceptInput.value;
    const choices = conceptsBySubject[subject] || [];
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = subject
      ? (profile === "pure_telugu" ? "అంశాన్ని ఎంచుకోండి" : "Choose concept")
      : (profile === "pure_telugu" ? "ముందుగా సబ్జెక్టును ఎంచుకోండి" : "Choose a subject first");
    conceptInput.replaceChildren(placeholder, ...choices.map(([value, english, telugu]) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = profile === "pure_telugu"
        ? telugu
        : profile === "telugu_assisted_english" ? `${english} · ${telugu}` : english;
      return option;
    }));
    conceptInput.disabled = !subject;
    if (choices.some(([value]) => value === previousValue)) conceptInput.value = previousValue;
  }

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
      practiceTitle: "15-question practice", practiceSummary: "Vedha prepares exactly 5 Easy, 5 Medium, and 5 Hard questions.",
      difficulties: { easy: "Easy · 5", medium: "Medium · 5", hard: "Hard · 5" },
      hintLabel: "Hint", answerPlaceholder: "Type your answer", checkAnswer: "Check Answer",
      uploadWork: "Upload Handwritten Work", voiceAnswer: "Speak Answer", generatePractice: "Generate Practice",
      progress: { title: "Progress this session", attempted: "Attempted", mastered: "Mastered", accuracy: "Accuracy", start: "Start answering practice questions to see your progress.", active: "Keep going—every correction builds understanding.", complete: "Excellent! You mastered all 15 questions.", badgeStart: "Getting started", badgeActive: "Learning in progress", badgeComplete: "Practice complete" },
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
      practiceTitle: "15 ప్రశ్నల practice", practiceSummary: "Vedha 5 సులభ, 5 మధ్యస్థ, 5 కఠిన questions సిద్ధం చేస్తుంది.",
      difficulties: { easy: "సులభ · 5", medium: "మధ్యస్థ · 5", hard: "కఠిన · 5" },
      hintLabel: "సూచన", answerPlaceholder: "సమాధానం type చేయండి", checkAnswer: "Answer తనిఖీ",
      uploadWork: "చేతిరాత Work Upload", voiceAnswer: "Answer మాట్లాడండి", generatePractice: "Practice రూపొందించండి",
      progress: { title: "ఈ session progress", attempted: "Attempted", mastered: "Mastered", accuracy: "Accuracy", start: "Questions answer చేయడం ప్రారంభిస్తే progress కనిపిస్తుంది.", active: "Continue చేయండి—ప్రతి correction understandingను పెంచుతుంది.", complete: "Excellent! మొత్తం 15 questions mastered.", badgeStart: "Getting started", badgeActive: "Learning in progress", badgeComplete: "Practice complete" },
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
      practiceTitle: "15 ప్రశ్నల అభ్యాసం", practiceSummary: "వేద 5 సులభ, 5 మధ్యస్థ, 5 కఠిన ప్రశ్నలను సిద్ధం చేస్తుంది.",
      difficulties: { easy: "సులభం · 5", medium: "మధ్యస్థం · 5", hard: "కఠినం · 5" },
      hintLabel: "సూచన", answerPlaceholder: "మీ సమాధానం రాయండి", checkAnswer: "సమాధానం తనిఖీ",
      uploadWork: "చేతిరాత పరిష్కారం జోడించండి", voiceAnswer: "సమాధానం చెప్పండి", generatePractice: "అభ్యాసం రూపొందించండి",
      progress: { title: "ఈ అభ్యాసంలోని ప్రగతి", attempted: "ప్రయత్నించినవి", mastered: "నేర్చుకున్నవి", accuracy: "ఖచ్చితత్వం", start: "మీ ప్రగతిని చూడటానికి అభ్యాస ప్రశ్నలకు సమాధానాలు ఇవ్వడం ప్రారంభించండి.", active: "కొనసాగించండి—ప్రతి సవరణ మీ అవగాహనను పెంచుతుంది.", complete: "అద్భుతం! మీరు మొత్తం 15 ప్రశ్నలను నేర్చుకున్నారు.", badgeStart: "ప్రారంభం", badgeActive: "అభ్యాసం కొనసాగుతోంది", badgeComplete: "అభ్యాసం పూర్తయింది" },
    },
  };

  function setJourney(activeStep) {
    document.querySelectorAll(".journey-step").forEach((step, index) => {
      step.classList.toggle("is-current", index + 1 === activeStep);
      step.classList.toggle("is-complete", index + 1 < activeStep);
    });
  }

  function renderProgress() {
    const copy = messages[state.setup.learning_profile].progress;
    const entries = [...state.progress.values()];
    const attempted = entries.length;
    const mastered = entries.filter((entry) => entry.correct).length;
    const accuracy = attempted ? Math.round((mastered / attempted) * 100) : 0;
    byId("progress-title").textContent = copy.title;
    byId("progress-attempted").textContent = String(attempted);
    byId("progress-mastered").textContent = String(mastered);
    byId("progress-accuracy").textContent = `${accuracy}%`;
    byId("progress-attempted-label").textContent = copy.attempted;
    byId("progress-mastered-label").textContent = copy.mastered;
    byId("progress-accuracy-label").textContent = copy.accuracy;
    byId("progress-total").textContent = `${mastered} / 15`;
    byId("progress-fill").style.width = `${Math.round((mastered / 15) * 100)}%`;
    const track = document.querySelector(".progress-track");
    track.setAttribute("aria-valuenow", String(mastered));
    byId("progress-badge").textContent = mastered === 15 ? copy.badgeComplete : attempted ? copy.badgeActive : copy.badgeStart;
    byId("progress-message").textContent = mastered === 15 ? copy.complete : attempted ? copy.active : copy.start;
  }

  function recordProgress(question, evaluation) {
    const previous = state.progress.get(question.question_id);
    state.progress.set(question.question_id, {
      correct: Boolean(evaluation.correct) || Boolean(previous?.correct),
      attempts: Math.max(evaluation.attempt_number, previous?.attempts || 0),
    });
    renderProgress();
    setJourney(4);
  }

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
    window.VedhaAnimations?.prepare(state.setup.concept, state.setup.learning_profile, lesson);
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
    const previousAttempts = state.attempts.get(question.question_id) || 0;
    const clientAttemptNumber = previousAttempts + 1;
    button.disabled = true;
    button.textContent = "Checking…";
    feedback.textContent = "";
    try {
      const evaluation = await api.requestPracticeEvaluation({
        practice_set_id: state.practice.practice_set_id,
        question_id: question.question_id,
        student_answer: studentAnswer,
        attempt_number: clientAttemptNumber,
      });
      state.attempts.set(question.question_id, Math.max(clientAttemptNumber, evaluation.attempt_number));
      renderEvaluation(item, evaluation);
      recordProgress(question, evaluation);
    } catch (_error) {
      state.attempts.set(question.question_id, previousAttempts);
      feedback.textContent = messages[state.setup.learning_profile].evaluationError;
      feedback.className = "answer-feedback answer-incorrect";
      feedback.focus();
    } finally {
      state.evaluating.delete(question.question_id);
      button.disabled = false;
      button.textContent = messages[state.setup.learning_profile].checkAnswer;
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
      recordProgress(question, evaluation);
    } catch (_error) {
      uploadStatus.textContent = messages[state.setup.learning_profile].uploadError;
      uploadStatus.className = "upload-status answer-incorrect";
      uploadStatus.focus();
    } finally {
      state.uploading.delete(question.question_id);
      uploadButton.disabled = false;
      uploadButton.textContent = messages[state.setup.learning_profile].uploadWork;
    }
  }

  function renderPractice(practice) {
    state.attempts.clear();
    state.progress.clear();
    byId("progress-panel").hidden = false;
    setJourney(3);
    const copy = messages[state.setup.learning_profile];
    byId("practice-title").textContent = copy.practiceTitle;
    byId("practice-panel").querySelector(":scope > p").textContent = copy.practiceSummary;
    ["easy", "medium", "hard"].forEach((difficulty) => {
      const questions = practice.questions.filter((question) => question.difficulty === difficulty);
      const list = byId(`practice-${difficulty}`);
      list.parentElement.querySelector("h3").textContent = copy.difficulties[difficulty];
      list.replaceChildren(...questions.map((question) => {
        const item = document.createElement("li");
        const prompt = document.createElement("p");
        const hint = document.createElement("small");
        const answerRow = document.createElement("div");
        const input = document.createElement("input");
        const button = document.createElement("button");
        const voiceButton = document.createElement("button");
        const voiceStatus = document.createElement("p");
        const feedback = document.createElement("p");
        const guidance = document.createElement("ul");
        const uploadRow = document.createElement("div");
        const uploadInput = document.createElement("input");
        const uploadButton = document.createElement("button");
        const uploadStatus = document.createElement("p");
        prompt.textContent = question.prompt;
        hint.textContent = `${copy.hintLabel}: ${question.hint}`;
        input.type = "text";
        input.className = "practice-answer";
        input.id = `practice-answer-${question.question_id}`;
        input.placeholder = copy.answerPlaceholder;
        input.setAttribute("aria-label", `Answer for: ${question.prompt}`);
        button.type = "button";
        button.className = "secondary-button check-answer";
        button.textContent = copy.checkAnswer;
        voiceButton.type = "button";
        voiceButton.className = "voice-trigger practice-voice-answer";
        voiceButton.textContent = `🎙 ${copy.voiceAnswer}`;
        voiceButton.dataset.startLabel = `🎙 ${copy.voiceAnswer}`;
        voiceButton.dataset.stopLabel = "■ Stop listening";
        voiceButton.dataset.voiceTarget = `#${input.id}`;
        voiceButton.dataset.voiceStatus = `#practice-voice-status-${question.question_id}`;
        voiceButton.dataset.voiceLanguageSource = 'input[name="learning_profile"]:checked';
        voiceButton.setAttribute("aria-pressed", "false");
        voiceButton.setAttribute("aria-label", `${copy.voiceAnswer}: ${question.prompt}`);
        voiceStatus.id = `practice-voice-status-${question.question_id}`;
        voiceStatus.className = "voice-status practice-voice-status";
        voiceStatus.setAttribute("role", "status");
        voiceStatus.setAttribute("aria-live", "polite");
        voiceStatus.hidden = true;
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
        uploadButton.textContent = copy.uploadWork;
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
        answerRow.append(input, voiceButton, button);
        uploadRow.className = "handwriting-upload-row";
        uploadRow.append(uploadInput, uploadButton);
        item.append(prompt, hint, answerRow, voiceStatus, uploadRow, uploadStatus, feedback, guidance);
        return item;
      }));
    });
    byId("practice-result").hidden = false;
    byId("practice-result").focus({ preventScroll: true });
    renderProgress();
    byId("practice-result").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function setPracticeLoading(isLoading) {
    state.practiceLoading = isLoading;
    const button = byId("generate-practice");
    button.disabled = isLoading;
    button.textContent = isLoading ? messages[state.setup.learning_profile].practiceLoading : messages[state.setup.learning_profile].generatePractice;
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

  subjectInput.addEventListener("change", refreshConceptOptions);
  setupForm.querySelectorAll('input[name="learning_profile"]').forEach((input) => {
    input.addEventListener("change", refreshConceptOptions);
  });
  refreshConceptOptions();

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
    setJourney(2);
    questionInput.focus();
  });

  byId("edit-setup").addEventListener("click", () => {
    byId("tutor-view").hidden = true;
    byId("setup-view").hidden = false;
    setJourney(1);
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
