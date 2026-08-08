const portals = [
  { key: "01", title: "Student App", telugu: "విద్యార్థి యాప్", detail: "Learn in English or Telugu with an AI tutor, voice, visuals and adaptive practice.", tone: "student", href: "/student" },
  { key: "02", title: "Parent Portal", telugu: "తల్లిదండ్రుల పోర్టల్", detail: "See progress, strengths, attention areas and practical support recommendations.", tone: "parent" },
  { key: "03", title: "Teacher Portal", telugu: "ఉపాధ్యాయ పోర్టల్", detail: "Find learning gaps, review concept performance and assign focused remediation.", tone: "teacher" },
  { key: "04", title: "Government Dashboard", telugu: "ప్రభుత్వ డ్యాష్‌బోర్డ్", detail: "Explore privacy-conscious, aggregated education indicators and district insights.", tone: "government" },
];

const journey = [
  ["Ask", "A learner asks in English or Telugu by text or voice."],
  ["Understand", "Vedha teaches the concept step by step with age-appropriate examples."],
  ["Practise", "Exactly 15 questions: 5 easy, 5 medium and 5 hard."],
  ["Improve", "Mistakes become corrective guidance, not just a final answer."],
];

export default function Home() {
  return (
    <main>
      <header className="nav shell">
        <a className="brand" href="#top" aria-label="Vedha AI home">
          <span className="brandMark" aria-hidden="true">V</span>
          <span>Vedha <em>AI</em></span>
        </a>
        <nav aria-label="Main navigation">
          <a href="#platform">Platform</a>
          <a href="#journey">How it works</a>
          <a href="#roadmap">Roadmap</a>
        </nav>
        <a className="navCta" href="#platform">Explore the demo</a>
      </header>

      <section id="top" className="hero shell">
        <div className="heroCopy">
          <p className="eyebrow"><span /> AI-powered learning for every student</p>
          <h1>Every learner deserves a teacher who <strong>understands them.</strong></h1>
          <p className="lede">Vedha turns every question into a clear lesson, meaningful practice and personal guidance—in English and Telugu.</p>
          <p className="telugu" lang="te">ప్రతి విద్యార్థి తన భాషలో, తన వేగంతో నేర్చుకునే వ్యక్తిగత AI విద్యా సహాయకుడు.</p>
          <div className="actions">
            <a className="primary" href="#platform">Experience Vedha <span>→</span></a>
            <span className="trust">Responsible AI · Bilingual · Accessible</span>
          </div>
        </div>
        <div className="heroVisual" aria-label="Personalized AI learning illustration">
          <div className="orb orbOne" /><div className="orb orbTwo" />
          <div className="book">
            <span className="sun" /><div className="pages"><i /><i /><i /></div>
            <b>VEDHA</b><small>LEARN · PRACTISE · GROW</small>
          </div>
          <span className="chip chipOne">Adaptive lessons</span>
          <span className="chip chipTwo">English + తెలుగు</span>
          <span className="chip chipThree">Voice & visuals</span>
        </div>
      </section>

      <section className="metrics">
        <div className="shell metricGrid">
          <div><b>Classes 1–12</b><span>One learning platform</span></div>
          <div><b>2 languages</b><span>English and Telugu</span></div>
          <div><b>15 questions</b><span>5 easy · 5 medium · 5 hard</span></div>
          <div><b>4 experiences</b><span>One connected ecosystem</span></div>
        </div>
      </section>

      <section id="platform" className="section shell">
        <div className="sectionHead"><div><p className="eyebrow">One connected platform</p><h2>Support at every level of learning.</h2></div><p>Built for independent students and the people who help them succeed—with clear privacy boundaries for every role.</p></div>
        <div className="portalGrid">
          {portals.map((portal) => <article className={`portal ${portal.tone}`} key={portal.title}><span className="number">{portal.key}</span><div className="portalIcon" aria-hidden="true">{portal.title[0]}</div><h3>{portal.title}</h3><p className="portalTelugu" lang="te">{portal.telugu}</p><p>{portal.detail}</p>{portal.href ? <a className="learn" href={portal.href}>Open Student App <b>→</b></a> : <span className="learn">Included in the unified platform <b>→</b></span>}</article>)}
        </div>
      </section>

      <section id="journey" className="journey">
        <div className="shell journeyGrid">
          <div className="journeyIntro"><p className="eyebrow light">Independent learning journey</p><h2>From “I don’t understand” to “I can do it.”</h2><p>The tutor teaches before testing and adapts when a learner makes a mistake.</p><div className="languagePill">తెలుగులో కూడా పూర్తిగా అందుబాటులో ఉంది</div></div>
          <ol>{journey.map(([title, detail], index) => <li key={title}><span>{index + 1}</span><div><h3>{title}</h3><p>{detail}</p></div></li>)}</ol>
        </div>
      </section>

      <section id="roadmap" className="section shell roadmap">
        <div><p className="eyebrow">Built to evolve</p><h2>Demo today. Commercial platform tomorrow.</h2><p>The product is being organized around versioned APIs and reusable React components, so student, teacher, parent, subscription, admin and new AI capabilities can be released in controlled versions.</p></div>
        <div className="roadmapCard"><span>Deployment path</span><b>GPT Site</b><i>→</i><b>Azure commercial product</b><small>React + TypeScript frontend · FastAPI backend · managed cloud services</small></div>
      </section>

      <footer><div className="shell"><div className="brand"><span className="brandMark">V</span><span>Vedha <em>AI</em></span></div><p>Education that understands every learner.</p><span>Government demonstration · Synthetic data only</span></div></footer>
    </main>
  );
}
