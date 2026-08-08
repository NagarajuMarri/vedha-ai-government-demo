"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";

type Profile = "english_medium" | "telugu_medium";
type Setup = { student_name: string; class_level: number; subject: string; concept: string; learning_profile: Profile };
type Lesson = { title: string; introduction: string; explanation_steps: string[]; example: string; key_points: string[]; check_question: string; source: string };
type Difficulty = "Easy" | "Medium" | "Hard";
type Question = { id: string; difficulty: Difficulty; prompt: string; answer: string; explanation: string };
type Attempt = { tries: number; state: "idle" | "wrong" | "correct" | "revealed"; feedback: string };
type AnimationLesson = { title: { en: string; te: string }; steps: { en: string[]; te: string[] } };

const concepts: Record<string, string[]> = {
  Mathematics: ["Addition", "Fractions", "Decimals", "Linear Equations", "Geometry"], Science: ["Plants", "Photosynthesis", "Water Cycle", "Solar System", "Force and Motion", "Electricity", "Human Body"],
  English: ["Nouns", "Tenses", "Reading Comprehension", "Writing"], Telugu: ["అక్షరాలు", "వ్యాకరణం", "పఠనం", "రచన"],
  "Social Studies": ["Our Community", "Indian Constitution", "Rivers of India", "Freedom Movement"],
};

const animationLessons: Record<string, AnimationLesson> = {
  Fractions: { title: { en: "Fractions: equal parts of a whole", te: "భిన్నాలు: మొత్తంలోని సమాన భాగాలు" }, steps: {
    en: ["This pizza is one complete whole.", "One vertical and one horizontal cut divide it into four equal pieces.", "Each piece is one out of four equal parts: one-fourth.", "Three highlighted pieces are three-fourths. Three is the numerator and four is the denominator."],
    te: ["ఈ పిజ్జా ఒక పూర్తి మొత్తం.", "నిలువుగా, అడ్డంగా కోస్తే నాలుగు సమాన భాగాలు ఏర్పడతాయి.", "ఒక్క ముక్క నాలుగు సమాన భాగాలలో ఒకటి — ఒక నాలుగవ వంతు.", "రంగుతో చూపిన మూడు ముక్కలు మూడు నాలుగవ వంతులు. మూడు లవం, నాలుగు హారం."],
  } },
  Geometry: { title: { en: "Geometry: understanding a triangle", te: "జ్యామితి: త్రిభుజాన్ని అర్థం చేసుకుందాం" }, steps: {
    en: ["A point marks an exact position.", "Joining three points makes three line segments and a closed triangle.", "A triangle has three vertices and three interior angles.", "Its interior angles always add to 180 degrees. Here 50 plus 60 plus 70 equals 180."],
    te: ["బిందువు ఒక ఖచ్చితమైన స్థానాన్ని సూచిస్తుంది.", "మూడు బిందువులను రేఖాఖండాలతో కలిపితే త్రిభుజం ఏర్పడుతుంది.", "త్రిభుజానికి మూడు శీర్షాలు, మూడు అంతర్గత కోణాలు ఉంటాయి.", "అంతర్గత కోణాల మొత్తం నూట ఎనభై డిగ్రీలు. యాభై, అరవై, డెబ్బై కలిపితే నూట ఎనభై."],
  } },
  "Water Cycle": { title: { en: "The continuous water cycle", te: "నిరంతర నీటి చక్రం" }, steps: {
    en: ["The Sun heats water in oceans, lakes and rivers.", "Liquid water rises as water vapour through evaporation.", "Cooling vapour condenses into clouds, then falls as precipitation.", "Water collects in rivers and oceans, and the cycle repeats."],
    te: ["సూర్యుడి వేడి సముద్రాలు, సరస్సులు, నదుల నీటిని వేడి చేస్తుంది.", "ద్రవ నీరు ఆవిరీకరణ ద్వారా నీటి ఆవిరిగా పైకి వెళుతుంది.", "చల్లబడిన ఆవిరి మేఘాలుగా మారి వర్షపాతంగా కింద పడుతుంది.", "నీరు నదులు, సముద్రాల్లో చేరి చక్రం మళ్లీ కొనసాగుతుంది."],
  } },
  "Solar System": { title: { en: "Our Solar System", te: "మన సౌర కుటుంబం" }, steps: {
    en: ["The Sun is the star at the centre of our Solar System.", "Mercury, Venus, Earth and Mars are the four inner rocky planets.", "Jupiter, Saturn, Uranus and Neptune are the four large outer planets.", "Gravity keeps every planet moving around the Sun in an orbit."],
    te: ["సూర్యుడు మన సౌర కుటుంబం మధ్యలో ఉన్న నక్షత్రం.", "బుధుడు, శుక్రుడు, భూమి, అంగారకుడు నాలుగు అంతర్గత రాతి గ్రహాలు.", "గురుడు, శని, యురేనస్, నెప్ట్యూన్ నాలుగు పెద్ద బాహ్య గ్రహాలు.", "గురుత్వాకర్షణ ప్రతి గ్రహాన్ని సూర్యుని చుట్టూ కక్ష్యలో ఉంచుతుంది."],
  } },
};

function sampleLesson(setup: Setup): Lesson {
  if (setup.learning_profile === "telugu_medium") return {
    title: `${setup.concept} — సులభంగా నేర్చుకుందాం`, introduction: `${setup.concept} అనే అంశాన్ని రోజువారీ జీవితంలోని ఉదాహరణలతో దశలవారీగా అర్థం చేసుకుందాం.`,
    explanation_steps: ["ముందుగా ముఖ్యమైన భావాన్ని గుర్తించండి.", "ఒక సులభమైన ఉదాహరణను పరిశీలించండి.", "ప్రతి దశ ఎందుకు పనిచేస్తుందో గమనించండి."],
    example: `ఉదాహరణ: ${setup.concept} ను మీ ఇంటి లేదా పాఠశాల అనుభవంతో పోల్చి చూడండి.`, key_points: ["భావాన్ని అర్థం చేసుకోండి", "దశలను క్రమంగా అనుసరించండి", "సమాధానాన్ని మరోసారి తనిఖీ చేయండి"],
    check_question: `మీ మాటల్లో ${setup.concept} అంటే ఏమిటో చెప్పగలరా?`, source: "guided_demo",
  };
  return { title: `${setup.concept} — learn it step by step`, introduction: `Let us understand ${setup.concept} through a clear, age-appropriate example.`,
    explanation_steps: ["Identify the main idea.", "Work through one simple example.", "Explain why each step works."], example: `Example: connect ${setup.concept} to something you see at home or school.`,
    key_points: ["Understand the idea", "Follow the steps in order", "Check your result"], check_question: `Can you explain ${setup.concept} in your own words?`, source: "guided_demo" };
}

function createQuestions(setup: Setup): Question[] {
  const telugu = setup.learning_profile === "telugu_medium"; const levels: Difficulty[] = ["Easy", "Medium", "Hard"]; const items: Question[] = [];
  levels.forEach((level, levelIndex) => { for (let i = 1; i <= 5; i++) {
    const n = levelIndex * 5 + i; const isAddition = setup.subject === "Mathematics" && setup.concept === "Addition";
    const answer = isAddition ? String((n + levelIndex + 1) + (n * (levelIndex + 1))) : `${setup.concept} ${n}`;
    const prompt = isAddition ? (telugu ? `${n + levelIndex + 1} + ${n * (levelIndex + 1)} విలువ ఎంత?` : `What is ${n + levelIndex + 1} + ${n * (levelIndex + 1)}?`) : (telugu ? `${setup.concept} గురించి ${level} స్థాయి ప్రశ్న ${i}: “${setup.concept} ${n}” అని టైప్ చేయండి.` : `${level} question ${i} about ${setup.concept}: type “${setup.concept} ${n}”.`);
    items.push({ id: `${level.toLowerCase()}-${i}`, difficulty: level, prompt, answer, explanation: telugu ? `సరైన సమాధానం: ${answer}. భావాన్ని గుర్తించి, ప్రతి దశను తనిఖీ చేయండి.` : `The correct answer is ${answer}. Identify the idea and check each step.` });
  }}); return items;
}

export default function StudentPage() {
  const [subject, setSubject] = useState("Mathematics"); const [profile, setProfile] = useState<Profile>("telugu_medium"); const [lesson, setLesson] = useState<Lesson | null>(null); const [setup, setSetup] = useState<Setup | null>(null);
  const [loading, setLoading] = useState(false); const [notice, setNotice] = useState(""); const [questions, setQuestions] = useState<Question[]>([]); const [attempts, setAttempts] = useState<Record<string, Attempt>>({}); const [answers, setAnswers] = useState<Record<string, string>>({});
  const [speaking, setSpeaking] = useState(false); const [visualOpen, setVisualOpen] = useState(false); const [visualStep, setVisualStep] = useState(0); const [visualPlaying, setVisualPlaying] = useState(false); const practiceRef = useRef<HTMLElement>(null); const availableConcepts = useMemo(() => concepts[subject] ?? [], [subject]);
  useEffect(() => () => { if (typeof window !== "undefined") window.speechSynthesis?.cancel(); }, []);

  async function begin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setLoading(true); setNotice(""); setQuestions([]); setAttempts({}); setAnswers({}); const data = new FormData(event.currentTarget);
    const next: Setup = { student_name: String(data.get("student_name")), class_level: Number(data.get("class_level")), subject, concept: String(data.get("concept")), learning_profile: profile }; setSetup(next);
    const apiBase = process.env.NEXT_PUBLIC_VEDHA_API_BASE_URL?.replace(/\/$/, "");
    if (apiBase) try { const response = await fetch(`${apiBase}/api/v1/lessons/explain`, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(next) }); if (!response.ok) throw new Error(); setLesson(await response.json() as Lesson); setNotice("Live Vedha tutor response"); }
    catch { setLesson(sampleLesson(next)); setNotice("Live tutor unavailable — guided demo lesson shown."); }
    else { setLesson(sampleLesson(next)); setNotice("Guided demo mode — FastAPI connection ready."); } setLoading(false);
  }
  function toggleAudio() {
    if (!lesson || typeof window === "undefined" || !("speechSynthesis" in window)) return; if (speaking) { window.speechSynthesis.cancel(); setSpeaking(false); return; }
    const utterance = new SpeechSynthesisUtterance([lesson.title, lesson.introduction, ...lesson.explanation_steps, lesson.example, ...lesson.key_points].join(". ")); utterance.lang = profile === "telugu_medium" ? "te-IN" : "en-IN"; utterance.rate = .9; utterance.onend = () => setSpeaking(false); utterance.onerror = () => setSpeaking(false); window.speechSynthesis.speak(utterance); setSpeaking(true);
  }
  function stopNarration() { if (typeof window !== "undefined") window.speechSynthesis?.cancel(); setSpeaking(false); setVisualPlaying(false); }
  function closeVisual() { stopNarration(); setVisualOpen(false); }
  function narrateVisual(index: number) {
    if (!setup || typeof window === "undefined") return;
    const animation = animationLessons[setup.concept]; if (!animation) return;
    const lang = setup.learning_profile === "telugu_medium" ? "te" : "en"; const text = animation.steps[lang][index];
    window.speechSynthesis.cancel(); const utterance = new SpeechSynthesisUtterance(text); utterance.lang = lang === "te" ? "te-IN" : "en-IN"; utterance.rate = .86;
    utterance.onend = () => { if (index < animation.steps[lang].length - 1) { const next = index + 1; setVisualStep(next); narrateVisual(next); } else setVisualPlaying(false); };
    utterance.onerror = () => setVisualPlaying(false); setVisualPlaying(true); window.speechSynthesis.speak(utterance);
  }
  function openVisual() { if (!setup || !animationLessons[setup.concept]) return; setVisualStep(0); setVisualOpen(true); window.setTimeout(() => narrateVisual(0), 120); }
  function startPractice() { if (!setup) return; const next = createQuestions(setup); setQuestions(next); setAttempts(Object.fromEntries(next.map(q => [q.id, { tries: 0, state: "idle", feedback: "" }]))); setTimeout(() => practiceRef.current?.scrollIntoView({ behavior: "smooth" }), 50); }
  function check(q: Question) {
    const previous = attempts[q.id] ?? { tries: 0, state: "idle", feedback: "" }; if (previous.state === "correct" || previous.state === "revealed") return;
    const correct = (answers[q.id] ?? "").trim().toLocaleLowerCase() === q.answer.trim().toLocaleLowerCase(); const tries = previous.tries + 1;
    setAttempts(current => ({ ...current, [q.id]: correct ? { tries, state: "correct", feedback: profile === "telugu_medium" ? "సరైన సమాధానం!" : "Correct — well done!" } : tries >= 2 ? { tries, state: "revealed", feedback: q.explanation } : { tries, state: "wrong", feedback: profile === "telugu_medium" ? "మరోసారి ప్రయత్నించండి. సూచన: ముఖ్య భావాన్ని గుర్తించండి." : "Try once more. Hint: identify the key idea." } }));
  }
  const completed = Object.values(attempts).filter(a => a.state === "correct" || a.state === "revealed").length;

  return <main className="studentStudio"><header className="studentNav shell"><Link className="brand" href="/"><span className="brandMark">V</span><span>Vedha <em>AI</em></span></Link><span className="studioBadge"><i /> Student Learning Studio</span></header>
    <section className="studentShell shell"><div className="steps"><b className="active">1 <span>Choose</span></b><i/><b className={lesson ? "active" : ""}>2 <span>Learn</span></b><i/><b className={questions.length ? "active" : ""}>3 <span>Practise</span></b><i/><b className={completed === 15 ? "active" : ""}>4 <span>Improve</span></b></div><div className="studioGrid">
      <section className="setupCard"><p className="eyebrow">Your learning, your way</p><h1>What shall we discover today?</h1><p>Choose your class, subject and language. Vedha shapes the explanation around you.</p><form onSubmit={begin}><label>Student name<input name="student_name" minLength={2} maxLength={80} required placeholder="Enter your name" /></label><div className="formRow"><label>Class<select name="class_level" defaultValue="6">{Array.from({length:12},(_,i)=><option key={i+1} value={i+1}>Class {i+1}</option>)}</select></label><label>Subject<select value={subject} onChange={e=>setSubject(e.target.value)}>{Object.keys(concepts).map(item=><option key={item}>{item}</option>)}</select></label></div><label>Concept<select name="concept" key={subject}>{availableConcepts.map(item=><option key={item}>{item}</option>)}</select></label><fieldset><legend>Learning profile</legend><label><input type="radio" checked={profile==="english_medium"} onChange={()=>setProfile("english_medium")}/> English Medium</label><label><input type="radio" checked={profile==="telugu_medium"} onChange={()=>setProfile("telugu_medium")}/> తెలుగు Medium</label></fieldset><button disabled={loading}>{loading ? "Preparing your lesson…" : "Start learning →"}</button></form></section>
      <aside className="tutorCard" aria-live="polite">{!lesson ? <div className="emptyLesson"><span>✦</span><h2>Your personal lesson will appear here.</h2><p>Learn by reading, listening or watching a guided visual explanation.</p><div className="mediaPreview"><span>🔊 Audio lesson</span><span>▶ Visual lesson</span></div><div className="practiceSplit"><b>5<small>Easy</small></b><b>5<small>Medium</small></b><b>5<small>Hard</small></b></div></div> : <article className="lesson"><span className="modeNote">{notice}</span><h2>{lesson.title}</h2><div className="lessonMedia"><button type="button" onClick={toggleAudio}>{speaking ? "■ Stop audio" : "🔊 Listen to lesson"}</button><button type="button" onClick={openVisual} disabled={!setup || !animationLessons[setup.concept]}>▶ Watch animated lesson with audio</button></div><small className="mediaDisclosure">The original Vedha bilingual narration is used for the text lesson and supported concept animations. Animations are available for Fractions, Geometry, Water Cycle and Solar System.</small><p>{lesson.introduction}</p><ol>{lesson.explanation_steps.map(step=><li key={step}>{step}</li>)}</ol><div className="example"><b>Worked example</b><p>{lesson.example}</p></div><h3>Key points</h3><ul>{lesson.key_points.map(point=><li key={point}>{point}</li>)}</ul><div className="check"><b>Quick check</b><p>{lesson.check_question}</p></div><button className="practiceButton" type="button" onClick={startPractice}>Generate 15 practice questions</button></article>}</aside>
    </div></section>
    {questions.length > 0 && <section className="practiceArea shell" ref={practiceRef}><div className="practiceHeader"><div><p className="eyebrow">Adaptive practice</p><h2>15 unique questions</h2><p>One retry is allowed. After the second incorrect attempt, Vedha reveals and explains the answer.</p></div><div className="progressRing"><b>{completed}</b><span>/ 15 complete</span></div></div><div className="questionGrid">{questions.map((q,index)=>{const result=attempts[q.id];return <article className={`questionCard ${result?.state ?? "idle"}`} key={q.id}><div><span className={`level ${q.difficulty.toLowerCase()}`}>{q.difficulty}</span><small>Question {index+1} of 15</small></div><h3>{q.prompt}</h3><div className="answerRow"><input aria-label={`Answer for question ${index+1}`} value={answers[q.id] ?? ""} disabled={result?.state === "correct" || result?.state === "revealed"} onChange={e=>setAnswers(a=>({...a,[q.id]:e.target.value}))} placeholder="Type your answer"/><button type="button" onClick={()=>check(q)}>Check</button></div>{result?.feedback && <p className="feedback">{result.feedback}{result.state === "revealed" && <strong>Answer: {q.answer}</strong>}</p>}</article>})}</div></section>}
    {visualOpen && setup && animationLessons[setup.concept] && (()=>{const animation=animationLessons[setup.concept];const lang=profile==="telugu_medium"?"te":"en";const steps=animation.steps[lang];return <div className="visualModal" role="dialog" aria-modal="true" aria-label="Animated lesson with narration"><div className="visualPlayer"><button className="closeVisual" onClick={closeVisual} aria-label="Close visual lesson">×</button><span className="visualLabel">VEDHA ANIMATED LESSON · {visualStep+1} / {steps.length}</span><div className={`visualScene concept-${setup.concept.toLowerCase().replaceAll(" ","-")} scene-${visualStep}`}><div className="conceptVisual" aria-hidden="true">{setup.concept==="Fractions"?<div className="pizza"><i/><i/><i/><i/></div>:setup.concept==="Geometry"?<div className="triangle"><b>A</b><b>B</b><b>C</b></div>:setup.concept==="Water Cycle"?<div className="waterCycle"><b>☀</b><i>☁</i><em>💧</em><span>≈≈≈</span></div>:<div className="solar"><b>☀</b><i/><i/><i/></div>}</div><h2>{animation.title[lang]}</h2><p>{steps[visualStep]}</p></div><div className="animationProgress"><i style={{width:`${((visualStep+1)/steps.length)*100}%`}}/></div><div className="visualControls"><button disabled={visualStep===0} onClick={()=>{stopNarration();const next=visualStep-1;setVisualStep(next);narrateVisual(next)}}>← Previous</button><button onClick={()=>visualPlaying?stopNarration():narrateVisual(visualStep)}>{visualPlaying?"⏸ Pause":"▶ Play with audio"}</button><button disabled={visualStep===steps.length-1} onClick={()=>{stopNarration();const next=visualStep+1;setVisualStep(next);narrateVisual(next)}}>Next →</button><button onClick={()=>{stopNarration();setVisualStep(0);narrateVisual(0)}}>↻ Replay</button></div><small>Animation and bilingual narration migrated from the original Vedha government demo.</small></div></div>})()}
  </main>;
}
