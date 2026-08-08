"use client";

import { FormEvent, useMemo, useState } from "react";

type Profile = "english_medium" | "telugu_medium";
type Setup = { student_name: string; class_level: number; subject: string; concept: string; learning_profile: Profile };
type Lesson = { title: string; introduction: string; explanation_steps: string[]; example: string; key_points: string[]; check_question: string; source: string };

const concepts: Record<string, string[]> = {
  Mathematics: ["Addition", "Fractions", "Linear Equations", "Geometry"],
  Science: ["Plants", "Force and Motion", "Electricity", "Human Body"],
  English: ["Nouns", "Tenses", "Reading Comprehension", "Writing"],
  Telugu: ["అక్షరాలు", "వ్యాకరణం", "పఠనం", "రచన"],
  "Social Studies": ["Our Community", "Indian Constitution", "Rivers of India", "Freedom Movement"],
};

function sampleLesson(setup: Setup): Lesson {
  if (setup.learning_profile === "telugu_medium") return {
    title: `${setup.concept} — సులభంగా నేర్చుకుందాం`,
    introduction: `${setup.concept} అనే అంశాన్ని రోజువారీ జీవితంలోని ఉదాహరణలతో దశలవారీగా అర్థం చేసుకుందాం.`,
    explanation_steps: ["ముందుగా ముఖ్యమైన భావాన్ని గుర్తించండి.", "ఒక సులభమైన ఉదాహరణను పరిశీలించండి.", "ప్రతి దశ ఎందుకు పనిచేస్తుందో గమనించండి."],
    example: `ఉదాహరణ: ${setup.concept} ను మీ ఇంటి లేదా పాఠశాల అనుభవంతో పోల్చి చూడండి.`,
    key_points: ["భావాన్ని అర్థం చేసుకోండి", "దశలను క్రమంగా అనుసరించండి", "సమాధానాన్ని మరోసారి తనిఖీ చేయండి"],
    check_question: `మీ మాటల్లో ${setup.concept} అంటే ఏమిటో చెప్పగలరా?`, source: "guided_demo",
  };
  return {
    title: `${setup.concept} — learn it step by step`,
    introduction: `Let us understand ${setup.concept} through a clear, age-appropriate example.`,
    explanation_steps: ["Identify the main idea.", "Work through one simple example.", "Explain why each step works."],
    example: `Example: connect ${setup.concept} to something you see at home or school.`,
    key_points: ["Understand the idea", "Follow the steps in order", "Check your result"],
    check_question: `Can you explain ${setup.concept} in your own words?`, source: "guided_demo",
  };
}

export default function StudentPage() {
  const [subject, setSubject] = useState("Mathematics");
  const [profile, setProfile] = useState<Profile>("telugu_medium");
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [loading, setLoading] = useState(false);
  const [notice, setNotice] = useState("");
  const availableConcepts = useMemo(() => concepts[subject] ?? [], [subject]);

  async function begin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setLoading(true); setNotice("");
    const data = new FormData(event.currentTarget);
    const setup: Setup = { student_name: String(data.get("student_name")), class_level: Number(data.get("class_level")), subject, concept: String(data.get("concept")), learning_profile: profile };
    const apiBase = process.env.NEXT_PUBLIC_VEDHA_API_BASE_URL?.replace(/\/$/, "");
    if (apiBase) {
      try {
        const response = await fetch(`${apiBase}/api/v1/lessons/explain`, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(setup) });
        if (!response.ok) throw new Error("request_failed");
        setLesson(await response.json() as Lesson); setNotice("Live Vedha tutor response");
      } catch { setLesson(sampleLesson(setup)); setNotice("The live tutor is temporarily unavailable. Showing the guided demo lesson."); }
    } else { setLesson(sampleLesson(setup)); setNotice("Guided demo mode. This screen connects to FastAPI when the API address is configured."); }
    setLoading(false);
  }

  return <main className="studentStudio">
    <header className="studentNav shell"><a className="brand" href="/"><span className="brandMark">V</span><span>Vedha <em>AI</em></span></a><span className="studioBadge"><i /> Student Learning Studio</span></header>
    <section className="studentShell shell">
      <div className="steps" aria-label="Learning journey"><b className="active">1 <span>Choose</span></b><i/><b>2 <span>Learn</span></b><i/><b>3 <span>Practise</span></b><i/><b>4 <span>Improve</span></b></div>
      <div className="studioGrid">
        <section className="setupCard">
          <p className="eyebrow">Your learning, your way</p><h1>What shall we discover today?</h1><p>Choose your class, subject and language. Vedha shapes the explanation around you.</p>
          <form onSubmit={begin}>
            <label>Student name<input name="student_name" minLength={2} maxLength={80} required placeholder="Enter your name" /></label>
            <div className="formRow"><label>Class<select name="class_level" defaultValue="6">{Array.from({length:12},(_,i)=><option key={i+1} value={i+1}>Class {i+1}</option>)}</select></label><label>Subject<select value={subject} onChange={e=>setSubject(e.target.value)}>{Object.keys(concepts).map(item=><option key={item}>{item}</option>)}</select></label></div>
            <label>Concept<select name="concept" key={subject}>{availableConcepts.map(item=><option key={item}>{item}</option>)}</select></label>
            <fieldset><legend>Learning profile</legend><label><input type="radio" checked={profile==="english_medium"} onChange={()=>setProfile("english_medium")}/> English Medium</label><label><input type="radio" checked={profile==="telugu_medium"} onChange={()=>setProfile("telugu_medium")}/> తెలుగు Medium</label></fieldset>
            <button disabled={loading}>{loading ? "Preparing your lesson…" : "Start learning →"}</button>
          </form>
        </section>
        <aside className="tutorCard" aria-live="polite">
          {!lesson ? <div className="emptyLesson"><span>✦</span><h2>Your personal lesson will appear here.</h2><p>Vedha teaches the concept first, then prepares exactly 15 practice questions.</p><div className="practiceSplit"><b>5<small>Easy</small></b><b>5<small>Medium</small></b><b>5<small>Hard</small></b></div></div> : <article className="lesson"><span className="modeNote">{notice}</span><h2>{lesson.title}</h2><p>{lesson.introduction}</p><ol>{lesson.explanation_steps.map(step=><li key={step}>{step}</li>)}</ol><div className="example"><b>Worked example</b><p>{lesson.example}</p></div><h3>Key points</h3><ul>{lesson.key_points.map(point=><li key={point}>{point}</li>)}</ul><div className="check"><b>Quick check</b><p>{lesson.check_question}</p></div><button className="practiceButton" type="button">Generate 15 practice questions</button></article>}
        </aside>
      </div>
    </section>
  </main>;
}
