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
    const timeoutId = global.setTimeout(() => controller.abort(), options.timeoutMs || 20000);
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

  global.VedhaLessonApi = { requestLesson, validateLesson, LessonApiError, DEFAULT_BASE_URL };
})(window);
