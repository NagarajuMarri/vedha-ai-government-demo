"use strict";

(function initializeConceptAnimations(window, document) {
  const profiles = {
    english_medium: "en",
    telugu_assisted_english: "te",
    pure_telugu: "te",
  };

  const lessons = {
    Fractions: {
      title: { en: "Fractions: equal parts of a whole", te: "భిన్నాలు: మొత్తంలోని సమాన భాగాలు" },
      steps: {
        en: [
          "Start with one complete whole, such as a roti or a circle.",
          "Divide the whole into four equal parts. Equal size is essential.",
          "Select three of the four parts. The selected amount is three-fourths.",
          "In three-fourths, three is the numerator and four is the denominator.",
        ],
        te: [
          "ఒక రొట్టె లేదా వృత్తం వంటి ఒక పూర్తి మొత్తంతో ప్రారంభిద్దాం.",
          "ఆ మొత్తాన్ని నాలుగు సమాన భాగాలుగా విభజించాలి. ప్రతి భాగం సమాన పరిమాణంలో ఉండాలి.",
          "నాలుగు భాగాలలో మూడు భాగాలను ఎంచుకుంటే, తీసుకున్న భాగం మూడు నాలుగవ వంతులు.",
          "మూడు నాలుగవ వంతులలో మూడు లవం, నాలుగు హారం.",
        ],
      },
    },
    Geometry: {
      title: { en: "Geometry: understanding a triangle", te: "జ్యామితి: త్రిభుజాన్ని అర్థం చేసుకుందాం" },
      steps: {
        en: [
          "Three line segments join to make a closed shape called a triangle.",
          "A triangle has three vertices and three interior angles.",
          "The three interior angles of every triangle add up to one hundred and eighty degrees.",
          "If two angles are fifty and sixty degrees, the third angle is seventy degrees.",
        ],
        te: [
          "మూడు రేఖాఖండాలు కలిసి ఏర్పడే మూసిన ఆకారాన్ని త్రిభుజం అంటారు.",
          "త్రిభుజానికి మూడు శీర్షాలు, మూడు అంతర్గత కోణాలు ఉంటాయి.",
          "ప్రతి త్రిభుజంలోని మూడు అంతర్గత కోణాల మొత్తం నూట ఎనభై డిగ్రీలు.",
          "రెండు కోణాలు యాభై, అరవై డిగ్రీలు అయితే మూడవ కోణం డెబ్బై డిగ్రీలు.",
        ],
      },
    },
    "Water Cycle": {
      title: { en: "The continuous water cycle", te: "నిరంతర నీటి చక్రం" },
      steps: {
        en: [
          "The Sun heats water in oceans, lakes, and rivers.",
          "Liquid water changes into water vapour and rises. This is evaporation.",
          "Water vapour cools and forms clouds. This is condensation.",
          "Water returns as rain and collects again, so the cycle continues.",
        ],
        te: [
          "సూర్యుడి వేడి సముద్రాలు, సరస్సులు, నదుల్లోని నీటిని వేడిచేస్తుంది.",
          "ద్రవ నీరు ఆవిరిగా మారి పైకి వెళుతుంది. దీనిని ఆవిరీకరణ అంటారు.",
          "నీటి ఆవిరి చల్లబడి మేఘాలను ఏర్పరుస్తుంది. దీనిని సంఘననం అంటారు.",
          "వర్షంగా నీరు తిరిగి భూమికి వచ్చి జలాశయాల్లో చేరడంతో చక్రం కొనసాగుతుంది.",
        ],
      },
    },
    "Solar System": {
      title: { en: "Our Solar System", te: "మన సౌర కుటుంబం" },
      steps: {
        en: [
          "The Sun is the star at the centre of our Solar System.",
          "Planets travel around the Sun along paths called orbits.",
          "Earth rotates on its axis, producing day and night.",
          "Earth completes one revolution around the Sun in about one year.",
        ],
        te: [
          "సూర్యుడు మన సౌర కుటుంబం మధ్యలో ఉన్న నక్షత్రం.",
          "గ్రహాలు కక్ష్యలు అనే మార్గాల్లో సూర్యుని చుట్టూ తిరుగుతాయి.",
          "భూమి తన అక్షంపై తిరగడం వల్ల పగలు, రాత్రి ఏర్పడతాయి.",
          "భూమి సూర్యుని చుట్టూ ఒక పరిభ్రమణాన్ని సుమారు ఒక సంవత్సరంలో పూర్తి చేస్తుంది.",
        ],
      },
    },
  };

  const state = { lesson: null, concept: null, profile: "english_medium", language: "en", index: 0, playing: false, timer: null };
  const byId = (id) => document.getElementById(id);

  function node(className, text = "") {
    const element = document.createElement("div");
    element.className = className;
    element.textContent = text;
    return element;
  }

  function buildVisual(concept) {
    const stage = byId("animation-stage");
    stage.replaceChildren();
    stage.dataset.concept = concept.toLowerCase().replaceAll(" ", "-");

    const sceneBadge = node("scene-badge");
    sceneBadge.append(node("scene-badge-dot"), node("scene-badge-text", state.language === "te" ? "వేద దృశ్య పాఠం" : "VEDHA VISUAL LESSON"));
    stage.append(sceneBadge);

    if (concept === "Fractions") {
      const table = node("fraction-table");
      const plate = node("fraction-plate");
      const whole = node("visual-fraction");
      for (let index = 0; index < 4; index += 1) {
        const part = node(`fraction-part part-${index + 1}`);
        part.append(node("pizza-cheese"));
        for (let topping = 0; topping < 3; topping += 1) part.append(node(`pizza-topping topping-${topping + 1}`));
        whole.append(part);
      }
      whole.append(node("fraction-label", "3/4"));
      plate.append(whole);
      table.append(plate, node("fraction-story", state.language === "te" ? "4 సమాన భాగాలు" : "4 equal parts"));
      stage.append(table);
    } else if (concept === "Geometry") {
      const blueprint = node("geometry-blueprint");
      blueprint.append(node("axis-label axis-x", "x"), node("axis-label axis-y", "y"));
      const triangle = node("visual-triangle");
      triangle.append(
        node("triangle-edge edge-left"),
        node("triangle-edge edge-right"),
        node("triangle-edge edge-base"),
        node("triangle-vertex vertex-a", "A"),
        node("triangle-vertex vertex-b", "B"),
        node("triangle-vertex vertex-c", "C"),
        node("angle angle-a", "50°"),
        node("angle angle-b", "60°"),
        node("angle angle-c", "70°"),
      );
      blueprint.append(triangle, node("geometry-equation", "50° + 60° + 70° = 180°"));
      stage.append(blueprint);
    } else if (concept === "Water Cycle") {
      const sky = node("water-sky");
      const sun = node("cycle-sun");
      sun.append(node("sun-core"), ...Array.from({ length: 12 }, (_, index) => node(`sun-ray ray-${index + 1}`)));
      const landscape = node("water-landscape");
      landscape.append(
        node("mountain mountain-back"),
        node("mountain mountain-front"),
        node("snow-cap"),
        node("cycle-water", state.language === "te" ? "జలాశయం" : "COLLECTION"),
      );
      const cloud = node("cycle-cloud");
      cloud.append(node("cloud-puff puff-1"), node("cloud-puff puff-2"), node("cloud-puff puff-3"), node("cloud-base"));
      const evaporation = node("cycle-flow evaporation");
      evaporation.append(node("flow-line"), node("flow-label", state.language === "te" ? "ఆవిరీకరణ" : "EVAPORATION"));
      const condensation = node("cycle-flow condensation");
      condensation.append(node("flow-label", state.language === "te" ? "సంఘననం" : "CONDENSATION"));
      const rain = node("rain-system");
      for (let index = 0; index < 14; index += 1) rain.append(node(`rain-drop drop-${index + 1}`));
      rain.append(node("flow-label", state.language === "te" ? "వర్షపాతం" : "PRECIPITATION"));
      sky.append(sun, cloud, evaporation, condensation, rain, landscape);
      stage.append(sky);
    } else if (concept === "Solar System") {
      const space = node("space-scene");
      for (let index = 0; index < 42; index += 1) {
        const star = node(`space-star star-${(index % 9) + 1}`);
        star.style.setProperty("--star-x", `${(index * 37) % 97}%`);
        star.style.setProperty("--star-y", `${(index * 61) % 93}%`);
        star.style.setProperty("--star-delay", `${(index % 7) * -0.35}s`);
        space.append(star);
      }
      const system = node("visual-solar-system");
      const sun = node("solar-sun");
      sun.append(node("solar-glow"), node("solar-core"), node("celestial-label", state.language === "te" ? "సూర్యుడు" : "SUN"));
      system.append(sun);
      const planetData = [
        ["బుధుడు", "MERCURY"], ["భూమి", "EARTH"], ["అంగారకుడు", "MARS"], ["గురుడు", "JUPITER"],
      ];
      planetData.forEach(([te, en], index) => {
        const orbit = node(`solar-orbit orbit-${index + 1}`);
        const planet = node(`solar-planet planet-${index + 1}`);
        planet.append(node("planet-surface"), node("celestial-label", state.language === "te" ? te : en));
        orbit.append(planet);
        system.append(orbit);
      });
      space.append(system);
      stage.append(space);
    }
  }

  function setStep(index) {
    const steps = state.lesson.steps[state.language];
    state.index = Math.max(0, Math.min(index, steps.length - 1));
    byId("animation-stage").dataset.step = String(state.index + 1);
    byId("animation-caption").textContent = steps[state.index];
    byId("animation-step").textContent = `${state.index + 1} / ${steps.length}`;
    byId("animation-progress-fill").style.width = `${((state.index + 1) / steps.length) * 100}%`;
    byId("animation-progress").setAttribute("aria-valuenow", String(state.index + 1));
    byId("animation-previous").disabled = state.index === 0;
    byId("animation-next").disabled = state.index === steps.length - 1;
  }

  function clearTimer() {
    if (state.timer) window.clearTimeout(state.timer);
    state.timer = null;
  }

  function pause() {
    state.playing = false;
    clearTimer();
    window.VedhaVoice?.pause();
    byId("animation-play").textContent = state.language === "te" ? "▶ కొనసాగించండి" : "▶ Continue";
  }

  function advanceAfterNarration() {
    if (!state.playing) return;
    if (state.index >= state.lesson.steps[state.language].length - 1) {
      state.playing = false;
      byId("animation-play").textContent = state.language === "te" ? "↻ మళ్లీ చూడండి" : "↻ Replay";
      byId("animation-check").hidden = false;
      return;
    }
    setStep(state.index + 1);
    narrateCurrentStep();
  }

  async function narrateCurrentStep() {
    clearTimer();
    const caption = state.lesson.steps[state.language][state.index];
    const spoken = await window.VedhaVoice?.speakText(caption, state.profile, {
      onEnd: advanceAfterNarration,
      onUnavailable: () => {
        byId("animation-status").textContent = state.language === "te"
          ? "తెలుగు వాయిస్ అందుబాటులో లేదు. దృశ్యం, సమకాలిక వాక్యంతో కొనసాగుతోంది."
          : "Narration is unavailable. Continuing with synchronized captions.";
      },
    });
    if (!spoken && state.playing) {
      state.timer = window.setTimeout(advanceAfterNarration, Math.max(3500, caption.length * 55));
    }
  }

  function play() {
    if (!state.lesson) return;
    if (state.index >= state.lesson.steps[state.language].length - 1) setStep(0);
    window.VedhaVoice?.cancel();
    state.playing = true;
    byId("animation-check").hidden = true;
    byId("animation-play").textContent = state.language === "te" ? "⏸ విరామం" : "⏸ Pause";
    narrateCurrentStep();
  }

  function setMode(mode) {
    const lessonResult = byId("lesson-result");
    const animationMode = mode === "animation";
    lessonResult.classList.toggle("animation-mode", animationMode);
    byId("concept-animation").hidden = !animationMode;
    document.querySelectorAll("[data-explanation-mode]").forEach((button) => {
      const selected = button.dataset.explanationMode === mode;
      button.classList.toggle("is-selected", selected);
      button.setAttribute("aria-pressed", String(selected));
    });
    if (animationMode) {
      setStep(0);
      byId("concept-animation").focus({ preventScroll: true });
      play();
    } else {
      pause();
      window.VedhaVoice?.cancel();
    }
  }

  function prepare(concept, profile) {
    state.concept = concept;
    state.profile = profile;
    state.language = profiles[profile] || "en";
    state.lesson = lessons[concept] || null;
    state.index = 0;
    state.playing = false;
    clearTimer();
    const animationButton = document.querySelector('[data-explanation-mode="animation"]');
    animationButton.disabled = !state.lesson;
    animationButton.title = state.lesson ? "" : "Animation for this concept is being prepared.";
    byId("animation-unavailable").hidden = Boolean(state.lesson);
    if (!state.lesson) {
      setMode("text");
      return;
    }
    byId("animation-title").textContent = state.lesson.title[state.language];
    byId("animation-status").textContent = "";
    byId("animation-check").textContent = state.language === "te"
      ? "ఈ వివరణను చూసిన తర్వాత భావనను మీ మాటల్లో చెప్పండి."
      : "After watching, explain the concept in your own words.";
    byId("animation-check").hidden = true;
    buildVisual(concept);
    setStep(0);
    setMode("text");
  }

  document.addEventListener("click", (event) => {
    const mode = event.target.closest("[data-explanation-mode]");
    if (mode && !mode.disabled) setMode(mode.dataset.explanationMode);
    if (event.target.closest("#animation-play")) state.playing ? pause() : play();
    if (event.target.closest("#animation-replay")) { setStep(0); play(); }
    if (event.target.closest("#animation-fullscreen")) {
      const panel = byId("concept-animation");
      if (document.fullscreenElement) document.exitFullscreen?.();
      else panel.requestFullscreen?.();
    }
    if (event.target.closest("#animation-previous")) { pause(); setStep(state.index - 1); }
    if (event.target.closest("#animation-next")) { pause(); setStep(state.index + 1); }
  });

  window.VedhaAnimations = { prepare, setMode };
})(window, document);
