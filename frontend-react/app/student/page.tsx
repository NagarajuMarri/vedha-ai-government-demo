"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

type Profile = "english_medium" | "telugu_medium";
type Setup = { student_name: string; class_level: number; subject: string; concept: string; learning_profile: Profile };
type Lesson = { title: string; introduction: string; explanation_steps: string[]; example: string; key_points: string[]; check_question: string; source: string };
type Difficulty = "Easy" | "Medium" | "Hard";
type Question = { id: string; difficulty: Difficulty; prompt: string; answer: string; explanation: string };
type Attempt = { tries: number; state: "idle" | "wrong" | "correct" | "revealed"; feedback: string };

const concepts: Record<string, string[]> = {
  Mathematics: ["Addition", "Fractions", "Linear Equations", "Geometry"], Science: ["Plants", "Force and Motion", "Electricity", "Human Body"],
  English: ["Nouns", "Tenses", "Reading Comprehension", "Writing"], Telugu: ["అక్షరాలు", "వ్యాకరణం", "పఠనం", "రచన"],
  "Social Studies": ["Our Community", "Indian Constitution", "Rivers of India", "Freedom Movement"],
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
  const [speaking, setSpeaking] = useState(false); const [visualOpen, setVisualOpen] = useState(false); const [visualStep, setVisualStep] = useState(0); const practiceRef = useRef<HTMLElement>(null); const availableConcepts = useMemo(() => concepts[subject] ?? [], [subject]);
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
  function startPractice() { if (!setup) return; const next = createQuestions(setup); setQuestions(next); setAttempts(Object.fromEntries(next.map(q => [q.id, { tries: 0, state: "idle", feedback: "" }]))); setTimeout(() => practiceRef.current?.scrollIntoView({ behavior: "smooth" }), 50); }
  function check(q: Question) {
    const previous = attempts[q.id] ?? { tries: 0, state: "idle", feedback: "" }; if (previous.state === "correct" || previous.state === "revealed") return;
    const correct = (answers[q.id] ?? "").trim().toLocaleLowerCase() === q.answer.trim().toLocaleLowerCase(); const tries = previous.tries + 1;
    setAttempts(current => ({ ...current, [q.id]: correct ? { tries, state: "correct", feedback: profile === "telugu_medium" ? "సరైన సమాధానం!" : "Correct — well done!" } : tries >= 2 ? { tries, state: "revealed", feedback: q.explanation } : { tries, state: "wrong", feedback: profile === "telugu_medium" ? "మరోసారి ప్రయత్నించండి. సూచన: ముఖ్య భావాన్ని గుర్తించండి." : "Try once more. Hint: identify the key idea." } }));
  }
  const completed = Object.values(attempts).filter(a => a.state === "correct" || a.state === "revealed").length;

  return <main className="studentStudio"><header className="studentNav shell"><a className="brand" href="/"><span className="brandMark">V</span><span>Vedha <em>AI</em></span></a><span className="studioBadge"><i /> Student Learning Studio</span></header>
    <section className="studentShell shell"><div className="steps"><b className="active">1 <span>Choose</span></b><i/><b className={lesson ? "active" : ""}>2 <span>Learn</span></b><i/><b className={questions.length ? "active" : ""}>3 <span>Practise</span></b><i/><b className={completed === 15 ? "active" : ""}>4 <span>Improve</span></b></div><div className="studioGrid">
      <section className="setupCard"><p className="eyebrow">Your learning, your way</p><h1>What shall we discover today?</h1><p>Choose your class, subject and language. Vedha shapes the explanation around you.</p><form onSubmit={begin}><label>Student name<input name="student_name" minLength={2} maxLength={80} required placeholder="Enter your name" /></label><div className="formRow"><label>Class<select name="class_level" defaultValue="6">{Array.from({length:12},(_,i)=><option key={i+1} value={i+1}>Class {i+1}</option>)}</select></label><label>Subject<select value={subject} onChange={e=>setSubject(e.target.value)}>{Object.keys(concepts).map(item=><option key={item}>{item}</option>)}</select></label></div><label>Concept<select name="concept" key={subject}>{availableConcepts.map(item=><option key={item}>{item}</option>)}</select></label><fieldset><legend>Learning profile</legend><label><input type="radio" checked={profile==="english_medium"} onChange={()=>setProfile("english_medium")}/> English Medium</label><label><input type="radio" checked={profile==="telugu_medium"} onChange={()=>setProfile("telugu_medium")}/> తెలుగు Medium</label></fieldset><button disabled={loading}>{loading ? "Preparing your lesson…" : "Start learning →"}</button></form></section>
      <aside className="tutorCard" aria-live="polite">{!lesson ? <div className="emptyLesson"><span>✦</span><h2>Your personal lesson will appear here.</h2><p>Learn by reading, listening or watching a guided visual explanation.</p><div className="mediaPreview"><span>🔊 Audio lesson</span><span>▶ Visual lesson</span></div><div className="practiceSplit"><b>5<small>Easy</small></b><b>5<small>Medium</small></b><b>5<small>Hard</small></b></div></div> : <article className="lesson"><span className="modeNote">{notice}</span><h2>{lesson.title}</h2><div className="lessonMedia"><button type="button" onClick={toggleAudio}>{speaking ? "■ Stop audio" : "🔊 Listen to lesson"}</button><button type="button" onClick={()=>{setVisualStep(0);setVisualOpen(true)}}>▶ Watch visual lesson</button></div><small className="mediaDisclosure">Audio uses your device voice in this demo. Generated teacher voice/video will connect through the production media service.</small><p>{lesson.introduction}</p><ol>{lesson.explanation_steps.map(step=><li key={step}>{step}</li>)}</ol><div className="example"><b>Worked example</b><p>{lesson.example}</p></div><h3>Key points</h3><ul>{lesson.key_points.map(point=><li key={point}>{point}</li>)}</ul><div className="check"><b>Quick check</b><p>{lesson.check_question}</p></div><button className="practiceButton" type="button" onClick={startPractice}>Generate 15 practice questions</button></article>}</aside>
    </div></section>
    {questions.length > 0 && <section className="practiceArea shell" ref={practiceRef}><div className="practiceHeader"><div><p className="eyebrow">Adaptive practice</p><h2>15 unique questions</h2><p>One retry is allowed. After the second incorrect attempt, Vedha reveals and explains the answer.</p></div><div className="progressRing"><b>{completed}</b><span>/ 15 complete</span></div></div><div className="questionGrid">{questions.map((q,index)=>{const result=attempts[q.id];return <article className={`questionCard ${result?.state ?? "idle"}`} key={q.id}><div><span className={`level ${q.difficulty.toLowerCase()}`}>{q.difficulty}</span><small>Question {index+1} of 15</small></div><h3>{q.prompt}</h3><div className="answerRow"><input aria-label={`Answer for question ${index+1}`} value={answers[q.id] ?? ""} disabled={result?.state === "correct" || result?.state === "revealed"} onChange={e=>setAnswers(a=>({...a,[q.id]:e.target.value}))} placeholder="Type your answer"/><button type="button" onClick={()=>check(q)}>Check</button></div>{result?.feedback && <p className="feedback">{result.feedback}{result.state === "revealed" && <strong>Answer: {q.answer}</strong>}</p>}</article>})}</div></section>}
    {visualOpen && lesson && <div className="visualModal" role="dialog" aria-modal="true" aria-label="Visual lesson"><div className="visualPlayer"><button className="closeVisual" onClick={()=>setVisualOpen(false)} aria-label="Close visual lesson">×</button><span className="visualLabel">GUIDED VISUAL · {visualStep+1} / {lesson.explanation_steps.length}</span><div className="visualScene"><div className="conceptOrb">{visualStep+1}</div><h2>{lesson.title}</h2><p>{lesson.explanation_steps[visualStep]}</p></div><div className="visualControls"><button disabled={visualStep===0} onClick={()=>setVisualStep(s=>s-1)}>← Previous</button><button onClick={()=>visualStep < lesson.explanation_steps.length-1 ? setVisualStep(s=>s+1) : setVisualOpen(false)}>{visualStep < lesson.explanation_steps.length-1 ? "Next →" : "Finish"}</button></div><small>This is an animated concept walkthrough, not a generated teacher video.</small></div></div>}
  </main>;
}
