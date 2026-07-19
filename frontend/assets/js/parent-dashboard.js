"use strict";

(function initializeParentDashboard(document) {
  const children = {
    ananya: {
      name: "Ananya", className: "Class 9", board: "AP State Board", avatar: "A",
      lessons: 8, practice: 76, streak: 5, growth: 12,
      strengths: [["Mathematics · Fractions", 88], ["Science · Solar System", 82], ["Telugu", 79]],
      attention: [["Geometry", 58, "Review angles and triangle rules"], ["English grammar", 63, "Practise subject–verb agreement"]],
      activity: [["Today", "Completed a fractions lesson and 5 practice questions"], ["Yesterday", "Improved Solar System practice from 65% to 82%"], ["Friday", "Asked Vedha for a Telugu explanation of geometry"]],
      recommendations: ["Use a chapati or fruit to practise equal fractions for 10 minutes.", "Ask Ananya to explain one triangle rule in her own words.", "Celebrate the five-day learning streak before choosing the next goal."],
    },
    arjun: {
      name: "Arjun", className: "Class 6", board: "AP State Board", avatar: "A",
      lessons: 6, practice: 71, streak: 3, growth: 9,
      strengths: [["Science · Water Cycle", 86], ["Mathematics · Decimals", 78], ["Social Studies", 74]],
      attention: [["Fractions", 56, "Practise equivalent fractions"], ["Telugu grammar", 61, "Review subject, object and verb"]],
      activity: [["Today", "Completed a narrated Water Cycle animation"], ["Yesterday", "Answered decimal questions using voice"], ["Saturday", "Retried two fraction questions with corrective guidance"]],
      recommendations: ["Draw the water cycle together and ask Arjun to label each stage.", "Compare prices at home to practise decimals.", "Use one short Telugu sentence to identify subject, object and verb."],
    },
  };

  const copy = {
    english: {
      heading: "See progress. Support with confidence.", intro: "A clear weekly view of your linked child’s learning, strengths and next support steps.",
      week: "This week", lessons: "Lessons completed", practice: "Practice accuracy", streak: "Learning streak", growth: "Weekly improvement",
      strengthsEyebrow: "What is going well", strengths: "Strengths", attentionEyebrow: "Where support helps", attention: "Attention areas",
      activityEyebrow: "Recent learning", activity: "Activity", recommendationEyebrow: "Try this at home", recommendations: "Support recommendations",
      voiceTitle: "Ask Vedha about your child", voiceHelp: "Try “Where does my child need help?” or “What should we practise today?”",
      placeholder: "Speak or type your question", ask: "Ask Vedha",
    },
    telugu: {
      heading: "ప్రగతిని చూడండి. నమ్మకంగా సహాయం చేయండి.", intro: "మీ బిడ్డ అభ్యాసం, బలాలు, సహాయం అవసరమైన అంశాల వారపు సంక్షిప్త సమాచారం.",
      week: "ఈ వారం", lessons: "పూర్తి చేసిన పాఠాలు", practice: "అభ్యాస ఖచ్చితత్వం", streak: "అభ్యాస పరంపర", growth: "వారపు మెరుగుదల",
      strengthsEyebrow: "బాగా నేర్చుకుంటున్నవి", strengths: "బలాలు", attentionEyebrow: "సహాయం అవసరమైనవి", attention: "శ్రద్ధ అవసరమైన అంశాలు",
      activityEyebrow: "ఇటీవలి అభ్యాసం", activity: "కార్యకలాపాలు", recommendationEyebrow: "ఇంట్లో ప్రయత్నించండి", recommendations: "సహాయ సూచనలు",
      voiceTitle: "మీ బిడ్డ గురించి వేదను అడగండి", voiceHelp: "“నా బిడ్డకు ఎక్కడ సహాయం అవసరం?” లేదా “ఈ రోజు ఏమి అభ్యసించాలి?” అని అడగండి.",
      placeholder: "మీ ప్రశ్నను చెప్పండి లేదా టైప్ చేయండి", ask: "వేదను అడగండి",
    },
  };

  const byId = (id) => document.getElementById(id);

  function progressRow([label, score]) {
    const row = document.createElement("div");
    row.className = "parent-progress-row";
    const heading = document.createElement("div");
    const name = document.createElement("span");
    const value = document.createElement("strong");
    const track = document.createElement("div");
    const fill = document.createElement("span");
    name.textContent = label; value.textContent = `${score}%`;
    heading.append(name, value); track.append(fill); fill.style.width = `${score}%`;
    row.append(heading, track); return row;
  }

  function render() {
    const child = children[byId("child-selector").value];
    const language = byId("parent-language").value;
    const labels = copy[language];
    document.documentElement.lang = language === "telugu" ? "te" : "en";
    byId("parent-heading").textContent = labels.heading; byId("parent-intro").textContent = labels.intro;
    byId("week-label").textContent = labels.week; byId("child-name").textContent = child.name;
    byId("child-context").textContent = `${child.className} · ${child.board}`; byId("child-avatar").textContent = child.avatar;
    byId("metric-lessons").textContent = String(child.lessons); byId("metric-practice").textContent = `${child.practice}%`;
    byId("metric-streak").textContent = `${child.streak} days`; byId("metric-growth").textContent = `+${child.growth}%`;
    ["lessons","practice","streak","growth"].forEach((key) => { byId(`metric-${key}-label`).textContent = labels[key]; });
    [["strengths-eyebrow","strengthsEyebrow"],["strengths-title","strengths"],["attention-eyebrow","attentionEyebrow"],["attention-title","attention"],["activity-eyebrow","activityEyebrow"],["activity-title","activity"],["recommendation-eyebrow","recommendationEyebrow"],["recommendation-title","recommendations"],["parent-voice-title","voiceTitle"],["parent-voice-help","voiceHelp"]].forEach(([id,key]) => { byId(id).textContent = labels[key]; });
    byId("parent-voice-query").placeholder = labels.placeholder; byId("parent-ask").textContent = labels.ask;
    byId("strengths-list").replaceChildren(...child.strengths.map(progressRow));
    byId("attention-list").replaceChildren(...child.attention.map(([topic,score,next]) => {
      const item=document.createElement("article"); const title=document.createElement("strong"); const detail=document.createElement("p");
      title.textContent=`${topic} · ${score}%`; detail.textContent=next; item.append(title,detail); return item;
    }));
    byId("activity-list").replaceChildren(...child.activity.map(([when,activity]) => { const li=document.createElement("li");const time=document.createElement("strong");const text=document.createElement("span");time.textContent=when;text.textContent=activity;li.append(time,text);return li; }));
    byId("recommendation-list").replaceChildren(...child.recommendations.map((recommendation,index) => { const item=document.createElement("article");item.append(Object.assign(document.createElement("span"),{textContent:String(index+1)}),Object.assign(document.createElement("p"),{textContent:recommendation}));return item; }));
    byId("parent-answer").hidden = true;
  }

  function answerQuery(event) {
    event.preventDefault();
    const query=byId("parent-voice-query").value.trim().toLowerCase();
    const child=children[byId("child-selector").value]; const telugu=byId("parent-language").value==="telugu";
    let answer;
    if (/strength|good|బలం|బాగా/.test(query)) answer=telugu ? `${child.name} ప్రస్తుతం ${child.strengths[0][0]}లో బలంగా ఉన్నారు. ఖచ్చితత్వం ${child.strengths[0][1]} శాతం.` : `${child.name}'s strongest current area is ${child.strengths[0][0]} at ${child.strengths[0][1]}% accuracy.`;
    else if (/help|support|attention|weak|సహాయం|శ్రద్ధ/.test(query)) answer=telugu ? `${child.attention[0][0]}లో సహాయం అవసరం. తదుపరి చర్య: ${child.attention[0][2]}.` : `The priority support area is ${child.attention[0][0]}. Recommended next step: ${child.attention[0][2]}.`;
    else answer=telugu ? `ఈ రోజు సూచన: ${child.recommendations[0]}` : `Today's suggested support: ${child.recommendations[0]}`;
    byId("parent-answer-text").textContent=answer; byId("parent-answer").hidden=false;
    byId("parent-answer").scrollIntoView({behavior:"smooth",block:"center"});
  }

  byId("child-selector").addEventListener("change",render);
  byId("parent-language").addEventListener("change",render);
  byId("parent-voice-form").addEventListener("submit",answerQuery);
  render();
})(document);
