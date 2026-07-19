"use strict";

(function initializeVedhaVoice(window, document) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const synth = window.speechSynthesis;
  let activeRecognition = null;
  let activeButton = null;
  let currentUtterance = null;

  const languageCodes = {
    english_medium: "en-IN",
    telugu_assisted_english: "en-IN",
    pure_telugu: "te-IN",
    english: "en-IN",
    telugu: "te-IN",
  };

  function statusElement(button) {
    const selector = button.dataset.voiceStatus;
    return selector ? document.querySelector(selector) : null;
  }

  function setStatus(button, message, kind = "info") {
    const status = statusElement(button);
    if (!status) return;
    status.textContent = message;
    status.dataset.state = kind;
    status.hidden = !message;
  }

  function resolveLanguage(button) {
    const sourceSelector = button.dataset.voiceLanguageSource;
    const selected = sourceSelector ? document.querySelector(sourceSelector)?.value : null;
    const explicit = button.dataset.voiceLanguage;
    return languageCodes[selected || explicit] || explicit || document.documentElement.lang || "en-IN";
  }

  function stopRecognition() {
    if (activeRecognition) activeRecognition.stop();
  }

  function startRecognition(button) {
    const target = document.querySelector(button.dataset.voiceTarget);
    if (!target) return;
    if (!SpeechRecognition) {
      setStatus(button, "Voice input is not available in this browser. Please use Chrome or Edge, or type your message.", "error");
      target.focus();
      return;
    }
    if (activeRecognition) {
      stopRecognition();
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = resolveLanguage(button);
    recognition.interimResults = true;
    recognition.continuous = false;
    let finalTranscript = "";

    recognition.onstart = () => {
      activeRecognition = recognition;
      activeButton = button;
      button.classList.add("is-listening");
      button.setAttribute("aria-pressed", "true");
      button.textContent = button.dataset.stopLabel || "■ Stop listening";
      setStatus(button, recognition.lang.startsWith("te") ? "వింటున్నాను… మాట్లాడండి." : "Listening… speak now.");
    };

    recognition.onresult = (event) => {
      let interimTranscript = "";
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const transcript = event.results[index][0].transcript;
        if (event.results[index].isFinal) finalTranscript += transcript;
        else interimTranscript += transcript;
      }
      const transcript = (finalTranscript || interimTranscript).trim();
      if (transcript) {
        target.value = transcript;
        target.dispatchEvent(new Event("input", { bubbles: true }));
      }
      setStatus(button, recognition.lang.startsWith("te")
        ? "వచనాన్ని తనిఖీ చేసి అవసరమైతే సవరించండి."
        : "Review the transcript and edit it if needed.", "success");
    };

    recognition.onerror = (event) => {
      const messages = {
        "not-allowed": "Microphone permission was denied. Allow microphone access in the browser and retry.",
        "no-speech": "No speech was detected. Please retry and speak clearly.",
        network: "Voice recognition could not connect. You can continue by typing.",
      };
      setStatus(button, messages[event.error] || "Voice input could not be completed. Please retry or type your message.", "error");
    };

    recognition.onend = () => {
      button.classList.remove("is-listening");
      button.setAttribute("aria-pressed", "false");
      button.textContent = button.dataset.startLabel || "🎙 Speak";
      activeRecognition = null;
      activeButton = null;
      target.focus();
    };

    recognition.start();
  }

  function preferredVoice(language) {
    const voices = synth?.getVoices() || [];
    const exact = voices.find((voice) => voice.lang.toLowerCase() === language.toLowerCase());
    return exact || voices.find((voice) => voice.lang.toLowerCase().startsWith(language.slice(0, 2).toLowerCase())) || null;
  }

  function speak(button) {
    if (!synth) {
      const status = document.querySelector(button.dataset.speakStatus || "");
      if (status) status.textContent = "Read-aloud is not available in this browser.";
      return;
    }
    const target = document.querySelector(button.dataset.speakTarget);
    const text = target?.innerText?.trim();
    if (!text) return;

    synth.cancel();
    const language = resolveLanguage(button);
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language;
    utterance.rate = Number(button.dataset.speakRate || "0.9");
    utterance.voice = preferredVoice(language);
    currentUtterance = utterance;

    utterance.onstart = () => button.closest(".speech-controls")?.classList.add("is-speaking");
    utterance.onend = () => {
      button.closest(".speech-controls")?.classList.remove("is-speaking");
      currentUtterance = null;
    };
    utterance.onerror = () => {
      button.closest(".speech-controls")?.classList.remove("is-speaking");
      currentUtterance = null;
    };
    synth.speak(utterance);
  }

  document.addEventListener("click", (event) => {
    const voiceButton = event.target.closest("[data-voice-target]");
    if (voiceButton) {
      if (activeButton && activeButton !== voiceButton) stopRecognition();
      startRecognition(voiceButton);
      return;
    }

    const speakButton = event.target.closest("[data-speak-target]");
    if (speakButton) speak(speakButton);

    if (event.target.closest("[data-speech-pause]") && synth) {
      if (synth.paused) synth.resume();
      else synth.pause();
    }

    if (event.target.closest("[data-speech-stop]") && synth) {
      synth.cancel();
      currentUtterance = null;
      document.querySelectorAll(".speech-controls.is-speaking").forEach((control) => control.classList.remove("is-speaking"));
    }
  });

  window.addEventListener("beforeunload", () => {
    stopRecognition();
    synth?.cancel();
  });
})(window, document);
