"use strict";

(function initializeGovernmentDashboard(document) {
  const syntheticData = {
    statewide: {
      label: "Andhra Pradesh",
      learners: 128460,
      lessons: 486920,
      practice: 72,
      mastery: 68,
      telugu: 61,
      improvement: 14,
      subjects: { Mathematics: 71, Science: 69, English: 62, Telugu: 76, "Social Studies": 66 },
    },
    visakhapatnam: {
      label: "Visakhapatnam",
      learners: 24180,
      lessons: 92640,
      practice: 76,
      mastery: 72,
      telugu: 54,
      improvement: 16,
      subjects: { Mathematics: 75, Science: 73, English: 68, Telugu: 77, "Social Studies": 69 },
    },
    guntur: {
      label: "Guntur",
      learners: 22640,
      lessons: 86410,
      practice: 73,
      mastery: 69,
      telugu: 59,
      improvement: 15,
      subjects: { Mathematics: 72, Science: 70, English: 63, Telugu: 76, "Social Studies": 67 },
    },
    kurnool: {
      label: "Kurnool",
      learners: 19870,
      lessons: 71820,
      practice: 66,
      mastery: 61,
      telugu: 72,
      improvement: 11,
      subjects: { Mathematics: 64, Science: 62, English: 54, Telugu: 71, "Social Studies": 59 },
    },
    tirupati: {
      label: "Tirupati",
      learners: 17620,
      lessons: 68450,
      practice: 74,
      mastery: 70,
      telugu: 57,
      improvement: 15,
      subjects: { Mathematics: 73, Science: 72, English: 65, Telugu: 75, "Social Studies": 67 },
    },
    east_godavari: {
      label: "East Godavari",
      learners: 21750,
      lessons: 83210,
      practice: 70,
      mastery: 67,
      telugu: 68,
      improvement: 13,
      subjects: { Mathematics: 69, Science: 68, English: 59, Telugu: 78, "Social Studies": 64 },
    },
  };

  const districtComparison = [
    ["Visakhapatnam", 72],
    ["Tirupati", 70],
    ["Guntur", 69],
    ["East Godavari", 67],
    ["Kurnool", 61],
  ];

  const byId = (id) => document.getElementById(id);
  const formatNumber = (value) => new Intl.NumberFormat("en-IN").format(value);

  function renderMetric(id, value, suffix = "") {
    byId(id).textContent = `${value}${suffix}`;
  }

  function createBar(label, value, accent = "teal") {
    const row = document.createElement("div");
    row.className = "dashboard-bar-row";
    const heading = document.createElement("div");
    const name = document.createElement("span");
    const score = document.createElement("strong");
    const track = document.createElement("div");
    const fill = document.createElement("span");
    name.textContent = label;
    score.textContent = `${value}%`;
    heading.append(name, score);
    track.className = "dashboard-bar-track";
    fill.className = `dashboard-bar-fill ${accent}`;
    fill.style.width = `${value}%`;
    track.append(fill);
    row.append(heading, track);
    return row;
  }

  function renderDashboard() {
    const selected = byId("district-filter").value;
    const data = syntheticData[selected];
    byId("dashboard-scope").textContent = data.label;
    renderMetric("metric-learners", formatNumber(data.learners));
    renderMetric("metric-lessons", formatNumber(data.lessons));
    renderMetric("metric-practice", data.practice, "%");
    renderMetric("metric-mastery", data.mastery, "%");
    renderMetric("metric-telugu", data.telugu, "%");
    renderMetric("metric-improvement", `+${data.improvement}`, "%");

    const subjects = byId("subject-performance");
    subjects.replaceChildren(...Object.entries(data.subjects).map(([subject, score], index) =>
      createBar(subject, score, index === 3 ? "gold" : "teal")
    ));

    const districts = byId("district-performance");
    const rows = selected === "statewide"
      ? districtComparison
      : [[data.label, data.mastery], ["State average", syntheticData.statewide.mastery]];
    districts.replaceChildren(...rows.map(([district, score], index) =>
      createBar(district, score, index === 0 ? "navy" : "teal")
    ));

    byId("filter-announcement").textContent =
      `Dashboard updated for ${data.label}. All figures are synthetic demonstration data.`;
  }

  const districtAliases = {
    "andhra pradesh": "statewide", "ఆంధ్రప్రదేశ్": "statewide",
    visakhapatnam: "visakhapatnam", "విశాఖపట్నం": "visakhapatnam",
    guntur: "guntur", "గుంటూరు": "guntur",
    kurnool: "kurnool", "కర్నూలు": "kurnool",
    tirupati: "tirupati", "తిరుపతి": "tirupati",
    "east godavari": "east_godavari", "తూర్పు గోదావరి": "east_godavari",
  };

  function applyVoiceQuery(event) {
    event.preventDefault();
    const query = byId("government-voice-query").value.trim().toLowerCase();
    const match = Object.entries(districtAliases).find(([alias]) => query.includes(alias.toLowerCase()));
    const profile = byId("government-voice-language").value;
    if (!match) {
      byId("government-voice-status").hidden = false;
      byId("government-voice-status").textContent = profile === "pure_telugu"
        ? "ఆంధ్రప్రదేశ్, విశాఖపట్నం, గుంటూరు, కర్నూలు, తిరుపతి లేదా తూర్పు గోదావరిలో ఒక ప్రాంతాన్ని పేర్కొనండి."
        : profile === "telugu_assisted_english"
          ? "Andhra Pradesh, Visakhapatnam, Guntur, Kurnool, Tirupati లేదా East Godavari districtను mention చేయండి."
          : "Mention Andhra Pradesh, Visakhapatnam, Guntur, Kurnool, Tirupati or East Godavari.";
      byId("government-answer").hidden = true;
      return;
    }
    byId("district-filter").value = match[1];
    renderDashboard();
    const data = syntheticData[match[1]];
    const insight = profile === "pure_telugu"
      ? `${data.label} పరిధిలో ${formatNumber(data.learners)} మంది విద్యార్థులు చేరుకున్నారు. భావనల పట్టు ${data.mastery} శాతం, అభ్యాస పూర్తి ${data.practice} శాతం, సరిదిద్దే మార్గదర్శకానంతర మెరుగుదల ${data.improvement} శాతం. ఇవన్నీ కల్పిత ప్రదర్శన సూచికలు.`
      : profile === "telugu_assisted_english"
        ? `${data.label} scopeలో ${formatNumber(data.learners)} learners చేరుకున్నారు. Concept mastery ${data.mastery}%, practice completion ${data.practice}%, corrective guidance తర్వాత improvement ${data.improvement}%. ఇవన్నీ synthetic demo indicators.`
        : `${data.label} reaches ${formatNumber(data.learners)} learners. Concept mastery is ${data.mastery}%, practice completion is ${data.practice}%, and improvement after corrective guidance is ${data.improvement}%. All indicators are synthetic.`;
    byId("government-voice-status").hidden = false;
    byId("government-voice-status").textContent = profile === "pure_telugu" ? "అభ్యర్థన వర్తింపజేయబడింది. దిగువ కల్పిత సూచికలను పరిశీలించండి." : profile === "telugu_assisted_english" ? "Request apply అయింది. Updated synthetic indicators చూడండి." : `Applied the request for ${data.label}.`;
    byId("government-answer-text").textContent = insight;
    byId("government-answer").hidden = false;
    byId("government-answer").scrollIntoView({ behavior: "smooth", block: "center" });
  }

  byId("government-voice-form").addEventListener("submit", applyVoiceQuery);
  byId("district-filter").addEventListener("change", renderDashboard);
  byId("government-voice-language").addEventListener("change", () => { document.documentElement.lang = byId("government-voice-language").value === "english_medium" ? "en" : "te"; byId("government-answer").hidden = true; });
  byId("class-filter").addEventListener("change", () => {
    const classLabel = byId("class-filter").selectedOptions[0].textContent;
    byId("class-scope").textContent = classLabel;
    byId("filter-announcement").textContent =
      `Class filter changed to ${classLabel}. Synthetic demonstration indicators are shown.`;
  });

  renderDashboard();
})(document);
