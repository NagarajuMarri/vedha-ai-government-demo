"use strict";

(function exposeLessonApi(global) {
  const DEFAULT_BASE_URL = "http://127.0.0.1:8000";
  const REQUIRED_TEXT_FIELDS = [
    "request_id", "lesson_id", "title", "introduction", "example",
    "check_question", "learning_profile", "subject", "class_level", "source", "created_at",
  ];

  class LessonApiError extends Error {
    constructor(kind) {
      super(kind);
      this.name = "LessonApiError";
      this.kind = kind;
    }
  }

  function validateLesson(data) {
    const hasText = (field) => typeof data[field] === "string" && data[field].trim().length > 0;
    if (!data || typeof data !== "object" || !REQUIRED_TEXT_FIELDS.every(hasText) ||
        !Array.isArray(data.explanation_steps) || data.explanation_steps.length === 0 ||
        !data.explanation_steps.every((item) => typeof item === "string" && item.trim()) ||
        !Array.isArray(data.key_points) || data.key_points.length === 0 ||
        !data.key_points.every((item) => typeof item === "string" && item.trim()) ||
        typeof data.fallback_used !== "boolean") {
      throw new LessonApiError("malformed_response");
    }
    return data;
  }

  async function requestLesson(payload, options = {}) {
    const baseUrl = (options.baseUrl || global.VEDHA_API_BASE_URL || DEFAULT_BASE_URL).replace(/\/$/, "");
    const controller = new AbortController();
    const timeoutId = global.setTimeout(() => controller.abort(), options.timeoutMs || 45000);
    let response;
    try {
      response = await global.fetch(`${baseUrl}/api/v1/lessons/explain`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });
    } catch (error) {
      throw new LessonApiError(error && error.name === "AbortError" ? "timeout" : "network");
    } finally {
      global.clearTimeout(timeoutId);
    }

    let data;
    try {
      data = await response.json();
    } catch (_error) {
      throw new LessonApiError("non_json_response");
    }
    if (!response.ok) {
      throw new LessonApiError(response.status === 422 ? "validation" : response.status >= 500 ? "server" : "request");
    }
    return validateLesson(data);
  }

  function validatePractice(data) {
    const validDifficulties = new Set(["easy", "medium", "hard"]);
    if (!data || typeof data !== "object" || typeof data.practice_set_id !== "string" ||
        typeof data.concept !== "string" || !Array.isArray(data.questions) || data.questions.length !== 15) {
      throw new LessonApiError("malformed_response");
    }
    const counts = { easy: 0, medium: 0, hard: 0 };
    const ids = new Set();
    const prompts = new Set();
    data.questions.forEach((question) => {
      if (!question || !validDifficulties.has(question.difficulty) ||
          typeof question.question_id !== "string" || typeof question.prompt !== "string" ||
          typeof question.hint !== "string" || !question.prompt.trim() || !question.hint.trim()) {
        throw new LessonApiError("malformed_response");
      }
      counts[question.difficulty] += 1;
      ids.add(question.question_id);
      prompts.add(question.prompt);
    });
    if (counts.easy !== 5 || counts.medium !== 5 || counts.hard !== 5 || ids.size !== 15 || prompts.size !== 15) {
      throw new LessonApiError("malformed_response");
    }
    return data;
  }

  async function requestPractice(payload, options = {}) {
    const baseUrl = (options.baseUrl || global.VEDHA_API_BASE_URL || DEFAULT_BASE_URL).replace(/\/$/, "");
    const controller = new AbortController();
    const timeoutId = global.setTimeout(() => controller.abort(), options.timeoutMs || 20000);
    let response;
    try {
      response = await global.fetch(`${baseUrl}/api/v1/practice/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });
    } catch (error) {
      throw new LessonApiError(error && error.name === "AbortError" ? "timeout" : "network");
    } finally {
      global.clearTimeout(timeoutId);
    }
    let data;
    try {
      data = await response.json();
    } catch (_error) {
      throw new LessonApiError("non_json_response");
    }
    if (!response.ok) {
      throw new LessonApiError(response.status === 422 ? "validation" : response.status >= 500 ? "server" : "request");
    }
    return validatePractice(data);
  }

  function validateEvaluation(data) {
    if (!data || typeof data !== "object" ||
        typeof data.request_id !== "string" ||
        typeof data.practice_set_id !== "string" ||
        typeof data.question_id !== "string" ||
        typeof data.correct !== "boolean" ||
        typeof data.feedback !== "string" || !data.feedback.trim() ||
        !Array.isArray(data.corrective_guidance) || data.corrective_guidance.length === 0 ||
        !data.corrective_guidance.every((step) => typeof step === "string" && step.trim()) ||
        !Number.isInteger(data.attempt_number) || data.attempt_number < 1 ||
        typeof data.evaluated_at !== "string") {
      throw new LessonApiError("malformed_response");
    }
    return data;
  }

  async function requestPracticeEvaluation(payload, options = {}) {
    const baseUrl = (options.baseUrl || global.VEDHA_API_BASE_URL || DEFAULT_BASE_URL).replace(/\/$/, "");
    const controller = new AbortController();
    const timeoutId = global.setTimeout(() => controller.abort(), options.timeoutMs || 15000);
    let response;
    try {
      response = await global.fetch(`${baseUrl}/api/v1/practice/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });
    } catch (error) {
      throw new LessonApiError(error && error.name === "AbortError" ? "timeout" : "network");
    } finally {
      global.clearTimeout(timeoutId);
    }
    let data;
    try {
      data = await response.json();
    } catch (_error) {
      throw new LessonApiError("non_json_response");
    }
    if (!response.ok) {
      throw new LessonApiError(response.status === 404 ? "expired_practice" :
        response.status === 422 ? "validation" : response.status >= 500 ? "server" : "request");
    }
    return validateEvaluation(data);
  }

  global.VedhaLessonApi = {
    requestLesson, validateLesson, requestPractice, validatePractice,
    requestPracticeEvaluation, validateEvaluation, LessonApiError, DEFAULT_BASE_URL,
  };
})(window);
