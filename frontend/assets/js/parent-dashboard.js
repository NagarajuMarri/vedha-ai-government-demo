"use strict";

(function initializeParentDashboard(document) {
  const children = {
    ananya: {
      name: "Ananya", className: "Class 9", board: "AP State Board", avatar: "A",
      lessons: 8, practice: 76, streak: 5, growth: 12,
      reports: { weekly: { lessons: 8, practice: 76, streak: 5, growth: 12 }, monthly: { lessons: 29, practice: 73, streak: 18, growth: 21 } },
      subjectCompletion: [["Mathematics", 78], ["Science", 72], ["English", 64], ["Telugu", 81], ["Social Studies", 69]],
      exam: { title: "Term Examination Preparation", date: "Exam starts 18 August 2026", completion: 68, completed: ["Fractions and Decimals", "Solar System and Water Cycle", "Indian Constitution"], remaining: ["Geometry revision", "English grammar practice", "AP Geography map work"], next: "20 July: Geometry angles revision · 30 minutes" },
      strengths: [["Mathematics · Fractions", 88], ["Science · Solar System", 82], ["Telugu", 79]],
      attention: [["Geometry", 58, "Review angles and triangle rules"], ["English grammar", 63, "Practise subject–verb agreement"]],
      activity: [["Today", "Completed a fractions lesson and 5 practice questions"], ["Yesterday", "Improved Solar System practice from 65% to 82%"], ["Friday", "Asked Vedha for a Telugu explanation of geometry"]],
      recommendations: ["Use a chapati or fruit to practise equal fractions for 10 minutes.", "Ask Ananya to explain one triangle rule in her own words.", "Celebrate the five-day learning streak before choosing the next goal."],
    },
    arjun: {
      name: "Arjun", className: "Class 6", board: "AP State Board", avatar: "A",
      lessons: 6, practice: 71, streak: 3, growth: 9,
      reports: { weekly: { lessons: 6, practice: 71, streak: 3, growth: 9 }, monthly: { lessons: 22, practice: 69, streak: 12, growth: 16 } },
      subjectCompletion: [["Mathematics", 66], ["Science", 84], ["English", 62], ["Telugu", 70], ["Social Studies", 73]],
      exam: { title: "Unit Test Preparation", date: "Exam starts 12 August 2026", completion: 61, completed: ["Water Cycle", "Decimals", "Local Government"], remaining: ["Equivalent fractions", "Telugu grammar", "Climate and resources"], next: "20 July: Equivalent fractions with visual examples · 25 minutes" },
      strengths: [["Science · Water Cycle", 86], ["Mathematics · Decimals", 78], ["Social Studies", 74]],
      attention: [["Fractions", 56, "Practise equivalent fractions"], ["Telugu grammar", 61, "Review subject, object and verb"]],
      activity: [["Today", "Completed a narrated Water Cycle animation"], ["Yesterday", "Answered decimal questions using voice"], ["Saturday", "Retried two fraction questions with corrective guidance"]],
      recommendations: ["Draw the water cycle together and ask Arjun to label each stage.", "Compare prices at home to practise decimals.", "Use one short Telugu sentence to identify subject, object and verb."],
    },
  };

  const copy = {
    english_medium: {
      heading: "See progress. Support with confidence.", intro: "A clear weekly view of your linked child’s learning, strengths and next support steps.",
      week: "This week", lessons: "Lessons completed", practice: "Practice accuracy", streak: "Learning streak", growth: "Weekly improvement",
      strengthsEyebrow: "What is going well", strengths: "Strengths", attentionEyebrow: "Where support helps", attention: "Attention areas",
      activityEyebrow: "Recent learning", activity: "Activity", recommendationEyebrow: "Try this at home", recommendations: "Support recommendations",
      voiceTitle: "Ask Vedha about your child", voiceHelp: "Try “Where does my child need help?” or “What should we practise today?”",
      placeholder: "Speak or type your question", ask: "Ask Vedha",
      subjectEyebrow: "Syllabus progress", subjectTitle: "Subject-wise completion", examEyebrow: "Upcoming assessment",
      completed: "Completed", remaining: "Still to prepare", nextStep: "Next preparation step", planCompleted: "Plan completed",
      weekly: "This week", monthly: "This month", days: "days",
    },
    pure_telugu: {
      heading: "ప్రగతిని చూడండి. నమ్మకంగా సహాయం చేయండి.", intro: "మీ బిడ్డ అభ్యాసం, బలాలు, సహాయం అవసరమైన అంశాల వారపు సంక్షిప్త సమాచారం.",
      week: "ఈ వారం", lessons: "పూర్తి చేసిన పాఠాలు", practice: "అభ్యాస ఖచ్చితత్వం", streak: "అభ్యాస పరంపర", growth: "వారపు మెరుగుదల",
      strengthsEyebrow: "బాగా నేర్చుకుంటున్నవి", strengths: "బలాలు", attentionEyebrow: "సహాయం అవసరమైనవి", attention: "శ్రద్ధ అవసరమైన అంశాలు",
      activityEyebrow: "ఇటీవలి అభ్యాసం", activity: "కార్యకలాపాలు", recommendationEyebrow: "ఇంట్లో ప్రయత్నించండి", recommendations: "సహాయ సూచనలు",
      voiceTitle: "మీ బిడ్డ గురించి వేదను అడగండి", voiceHelp: "“నా బిడ్డకు ఎక్కడ సహాయం అవసరం?” లేదా “ఈ రోజు ఏమి అభ్యసించాలి?” అని అడగండి.",
      placeholder: "మీ ప్రశ్నను చెప్పండి లేదా టైప్ చేయండి", ask: "వేదను అడగండి",
      subjectEyebrow: "పాఠ్యాంశ ప్రగతి", subjectTitle: "సబ్జెక్టుల వారీగా పూర్తి", examEyebrow: "రాబోయే పరీక్ష",
      completed: "పూర్తయినవి", remaining: "ఇంకా సిద్ధం కావాల్సినవి", nextStep: "తదుపరి సిద్ధత దశ", planCompleted: "ప్రణాళిక పూర్తయింది",
      weekly: "ఈ వారం", monthly: "ఈ నెల", days: "రోజులు",
    },
    telugu_assisted_english: {
      heading: "Progress చూడండి. Confidenceతో support చేయండి.", intro: "మీ child learning, strengths, attention areas మరియు next support steps యొక్క clear report.",
      week: "ఈ వారం", lessons: "Lessons completed", practice: "Practice accuracy", streak: "Learning streak", growth: "Improvement",
      strengthsEyebrow: "బాగా నేర్చుకుంటున్నవి", strengths: "Strengths", attentionEyebrow: "Support అవసరమైనవి", attention: "Attention areas",
      activityEyebrow: "Recent learning", activity: "Activity", recommendationEyebrow: "ఇంట్లో try చేయండి", recommendations: "Support recommendations",
      voiceTitle: "మీ child గురించి Vedhaను అడగండి", voiceHelp: "“నా childకు ఎక్కడ help అవసరం?” లేదా “ఈ రోజు ఏమి practise చేయాలి?” అని అడగండి.",
      placeholder: "మీ questionను చెప్పండి లేదా type చేయండి", ask: "Vedhaను అడగండి",
      subjectEyebrow: "Syllabus progress", subjectTitle: "Subject-wise completion", examEyebrow: "Upcoming exam",
      completed: "Completed topics", remaining: "Prepare చేయాల్సినవి", nextStep: "Next preparation step", planCompleted: "Plan completed",
      weekly: "ఈ వారం", monthly: "ఈ నెల", days: "days",
    },
  };

  const translations = {

    pure_telugu: {
      "Class 9": "9వ తరగతి", "Class 6": "6వ తరగతి", "AP State Board": "ఆంధ్రప్రదేశ్ రాష్ట్ర విద్యా మండలి",
      "Mathematics": "గణితం", "Science": "విజ్ఞాన శాస్త్రం", "English": "ఆంగ్లం", "Telugu": "తెలుగు", "Social Studies": "సాంఘిక శాస్త్రం",
      "Term Examination Preparation": "టర్మ్ పరీక్ష సిద్ధత", "Unit Test Preparation": "యూనిట్ పరీక్ష సిద్ధత",
      "Exam starts 18 August 2026": "పరీక్ష 18 ఆగస్టు 2026న ప్రారంభమవుతుంది", "Exam starts 12 August 2026": "పరీక్ష 12 ఆగస్టు 2026న ప్రారంభమవుతుంది",
      "Fractions and Decimals": "భిన్నాలు మరియు దశాంశాలు", "Solar System and Water Cycle": "సౌర కుటుంబం మరియు నీటి చక్రం", "Indian Constitution": "భారత రాజ్యాంగం",
      "Geometry revision": "జ్యామితి పునశ్చరణ", "English grammar practice": "ఆంగ్ల వ్యాకరణ అభ్యాసం", "AP Geography map work": "ఆంధ్రప్రదేశ్ భౌగోళిక పటాల అభ్యాసం",
      "20 July: Geometry angles revision · 30 minutes": "20 జూలై: జ్యామితిలో కోణాల పునశ్చరణ · 30 నిమిషాలు",
      "Water Cycle": "నీటి చక్రం", "Decimals": "దశాంశాలు", "Local Government": "స్థానిక ప్రభుత్వం", "Equivalent fractions": "సమాన భిన్నాలు",
      "Telugu grammar": "తెలుగు వ్యాకరణం", "Climate and resources": "వాతావరణం మరియు వనరులు",
      "20 July: Equivalent fractions with visual examples · 25 minutes": "20 జూలై: బొమ్మల ఉదాహరణలతో సమాన భిన్నాలు · 25 నిమిషాలు",
      "Mathematics · Fractions": "గణితం · భిన్నాలు", "Science · Solar System": "విజ్ఞాన శాస్త్రం · సౌర కుటుంబం",
      "Geometry": "జ్యామితి", "English grammar": "ఆంగ్ల వ్యాకరణం", "Review angles and triangle rules": "కోణాలు, త్రిభుజ నియమాలను పునశ్చరణ చేయండి",
      "Practise subject–verb agreement": "కర్త–క్రియ అన్వయాన్ని అభ్యసించండి", "Science · Water Cycle": "విజ్ఞాన శాస్త్రం · నీటి చక్రం",
      "Mathematics · Decimals": "గణితం · దశాంశాలు", "Fractions": "భిన్నాలు", "Practise equivalent fractions": "సమాన భిన్నాలను అభ్యసించండి",
      "Review subject, object and verb": "కర్త, కర్మ, క్రియలను పునశ్చరణ చేయండి",
      "Today": "ఈ రోజు", "Yesterday": "నిన్న", "Friday": "శుక్రవారం", "Saturday": "శనివారం",
      "Completed a fractions lesson and 5 practice questions": "భిన్నాల పాఠం మరియు 5 అభ్యాస ప్రశ్నలను పూర్తి చేశారు",
      "Improved Solar System practice from 65% to 82%": "సౌర కుటుంబ అభ్యాస ఫలితాన్ని 65% నుంచి 82%కు మెరుగుపరిచారు",
      "Asked Vedha for a Telugu explanation of geometry": "జ్యామితిని తెలుగులో వివరించమని వేదను అడిగారు",
      "Completed a narrated Water Cycle animation": "వివరణతో కూడిన నీటి చక్రం యానిమేషన్ పూర్తి చేశారు",
      "Answered decimal questions using voice": "దశాంశ ప్రశ్నలకు స్వరంతో సమాధానమిచ్చారు",
      "Retried two fraction questions with corrective guidance": "సరిదిద్దే మార్గదర్శకంతో రెండు భిన్నాల ప్రశ్నలను మళ్లీ ప్రయత్నించారు",
      "Use a chapati or fruit to practise equal fractions for 10 minutes.": "చపాతీ లేదా పండుతో 10 నిమిషాలు సమాన భిన్నాలను అభ్యసించండి.",
      "Ask Ananya to explain one triangle rule in her own words.": "ఒక త్రిభుజ నియమాన్ని తన మాటల్లో వివరించమని అనన్యను అడగండి.",
      "Celebrate the five-day learning streak before choosing the next goal.": "తదుపరి లక్ష్యాన్ని ఎంచుకునే ముందు ఐదు రోజుల అభ్యాస పరంపరను అభినందించండి.",
      "Draw the water cycle together and ask Arjun to label each stage.": "నీటి చక్రాన్ని కలిసి గీసి, ప్రతి దశకు పేరు రాయమని అర్జున్‌ను అడగండి.",
      "Compare prices at home to practise decimals.": "దశాంశాల అభ్యాసానికి ఇంట్లో ధరలను పోల్చండి.",
      "Use one short Telugu sentence to identify subject, object and verb.": "ఒక చిన్న తెలుగు వాక్యంలో కర్త, కర్మ, క్రియలను గుర్తించండి."
    },
    telugu_assisted_english: {
      "Class 9": "Class 9", "Class 6": "Class 6", "AP State Board": "AP State Board",
      "Mathematics": "Mathematics", "Science": "Science", "English": "English", "Telugu": "Telugu", "Social Studies": "Social Studies",
      "Term Examination Preparation": "Term Exam preparation", "Unit Test Preparation": "Unit Test preparation",
      "Exam starts 18 August 2026": "Exam 18 August 2026న start అవుతుంది", "Exam starts 12 August 2026": "Exam 12 August 2026న start అవుతుంది",
      "Fractions and Decimals": "Fractions మరియు Decimals", "Solar System and Water Cycle": "Solar System మరియు Water Cycle", "Indian Constitution": "Indian Constitution",
      "Geometry revision": "Geometry revision", "English grammar practice": "English grammar practice", "AP Geography map work": "AP Geography map work",
      "20 July: Geometry angles revision · 30 minutes": "20 July: Geometry angles revision · 30 minutes",
      "Water Cycle": "Water Cycle", "Decimals": "Decimals", "Local Government": "Local Government", "Equivalent fractions": "Equivalent fractions",
      "Telugu grammar": "Telugu grammar", "Climate and resources": "Climate and resources",
      "20 July: Equivalent fractions with visual examples · 25 minutes": "20 July: visual examplesతో Equivalent fractions · 25 minutes",
      "Mathematics · Fractions": "Mathematics · Fractions", "Science · Solar System": "Science · Solar System", "Geometry": "Geometry",
      "English grammar": "English grammar", "Review angles and triangle rules": "Angles మరియు triangle rulesను review చేయండి",
      "Practise subject–verb agreement": "Subject–verb agreementను practise చేయండి", "Science · Water Cycle": "Science · Water Cycle",
      "Mathematics · Decimals": "Mathematics · Decimals", "Fractions": "Fractions", "Practise equivalent fractions": "Equivalent fractionsను practise చేయండి",
      "Review subject, object and verb": "Subject, object, verbను review చేయండి",
      "Today": "Today", "Yesterday": "Yesterday", "Friday": "Friday", "Saturday": "Saturday",
      "Completed a fractions lesson and 5 practice questions": "Fractions lesson మరియు 5 practice questions complete చేశారు",
      "Improved Solar System practice from 65% to 82%": "Solar System practiceను 65% నుంచి 82%కు improve చేశారు",
      "Asked Vedha for a Telugu explanation of geometry": "Geometryని Teluguలో explain చేయమని Vedhaను అడిగారు",
      "Completed a narrated Water Cycle animation": "Narrationతో Water Cycle animation complete చేశారు",
      "Answered decimal questions using voice": "Decimal questionsకు voiceతో answers ఇచ్చారు",
      "Retried two fraction questions with corrective guidance": "Corrective guidanceతో రెండు fraction questionsను retry చేశారు",
      "Use a chapati or fruit to practise equal fractions for 10 minutes.": "Chapati లేదా fruitతో 10 minutes equal fractions practise చేయండి.",
      "Ask Ananya to explain one triangle rule in her own words.": "ఒక triangle ruleను own wordsలో explain చేయమని Ananyaను అడగండి.",
      "Celebrate the five-day learning streak before choosing the next goal.": "Next goal ఎంచుకునే ముందు five-day learning streakను celebrate చేయండి.",
      "Draw the water cycle together and ask Arjun to label each stage.": "Water Cycleను కలిసి draw చేసి ప్రతి stageకు label పెట్టమని Arjunను అడగండి.",
      "Compare prices at home to practise decimals.": "Decimals practise చేయడానికి ఇంట్లో prices compare చేయండి.",
      "Use one short Telugu sentence to identify subject, object and verb.": "ఒక short Telugu sentenceలో subject, object, verb identify చేయండి."
    }
  };

  function translate(text, profile) {
    return translations[profile]?.[text] || text;
  }

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
    const period = byId("report-period").value;
    const report = child.reports[period];
    document.documentElement.lang = language === "english_medium" ? "en" : "te";
    const staticLabels = {
      "synthetic-label": language === "pure_telugu" ? "కల్పిత ప్రదర్శన సమాచారం" : language === "telugu_assisted_english" ? "Synthetic demo data" : "Synthetic demonstration data",
      "gateway-label": language === "pure_telugu" ? "ముఖ్య పుట" : language === "telugu_assisted_english" ? "Interface gateway" : "Interface gateway",
      "language-label": language === "pure_telugu" ? "భాష" : "Language",
      "report-label": language === "pure_telugu" ? "నివేదిక" : "Report",
      "child-label": language === "pure_telugu" ? "అనుసంధానించిన బిడ్డ" : language === "telugu_assisted_english" ? "Linked child" : "Linked child",
      "privacy-title": language === "pure_telugu" ? "నియంత్రిత ప్రదర్శన:" : language === "telugu_assisted_english" ? "Controlled demo:" : "Controlled demo:",
      "privacy-text": language === "pure_telugu" ? "ఇక్కడ చూపిన పిల్లలు, కార్యకలాపాలు, మార్కులు అన్నీ కల్పితమైనవి. నిజమైన వ్యవస్థలో తల్లిదండ్రులు అనుసంధానించిన పిల్లలను మాత్రమే చూడగలరు." : language === "telugu_assisted_english" ? "ఇక్కడ చూపిన children, activities, scores అన్నీ fictional demo data. Productionలో explicitly linked children మాత్రమే కనిపిస్తారు." : "All children, activities and scores shown here are fictional. A production parent would only see explicitly linked children."
    };
    Object.entries(staticLabels).forEach(([id, text]) => { byId(id).textContent = text; });
    const reportSelect = byId("report-period");
    reportSelect.options[0].textContent = language === "pure_telugu" ? "వారపు నివేదిక" : language === "telugu_assisted_english" ? "Weekly report" : "Weekly report";
    reportSelect.options[1].textContent = language === "pure_telugu" ? "నెలవారీ నివేదిక" : language === "telugu_assisted_english" ? "Monthly report" : "Monthly report";
    byId("parent-heading").textContent = labels.heading; byId("parent-intro").textContent = labels.intro;
    byId("week-label").textContent = labels[period]; byId("child-name").textContent = child.name;
    byId("child-context").textContent = `${translate(child.className, language)} · ${translate(child.board, language)}`; byId("child-avatar").textContent = child.avatar;
    byId("metric-lessons").textContent = String(report.lessons); byId("metric-practice").textContent = `${report.practice}%`;
    byId("metric-streak").textContent = `${report.streak} ${labels.days}`; byId("metric-growth").textContent = `+${report.growth}%`;
    ["lessons","practice","streak","growth"].forEach((key) => { byId(`metric-${key}-label`).textContent = labels[key]; });
    [["strengths-eyebrow","strengthsEyebrow"],["strengths-title","strengths"],["attention-eyebrow","attentionEyebrow"],["attention-title","attention"],["activity-eyebrow","activityEyebrow"],["activity-title","activity"],["recommendation-eyebrow","recommendationEyebrow"],["recommendation-title","recommendations"],["parent-voice-title","voiceTitle"],["parent-voice-help","voiceHelp"]].forEach(([id,key]) => { byId(id).textContent = labels[key]; });
    byId("parent-voice-query").placeholder = labels.placeholder; byId("parent-ask").textContent = labels.ask;
    byId("subject-eyebrow").textContent = labels.subjectEyebrow;
    byId("subject-title").textContent = labels.subjectTitle;
    byId("exam-eyebrow").textContent = labels.examEyebrow;
    byId("completed-title").textContent = labels.completed;
    byId("remaining-title").textContent = labels.remaining;
    byId("next-step-title").textContent = labels.nextStep;
    byId("exam-ready-label").textContent = labels.planCompleted;
    const overall = Math.round(child.subjectCompletion.reduce((sum, [, score]) => sum + score, 0) / child.subjectCompletion.length);
    byId("overall-completion").textContent = `${overall}%`;
    byId("subject-completion-list").replaceChildren(...child.subjectCompletion.map(([label, score]) => progressRow([translate(label, language), score])));
    byId("exam-title").textContent = translate(child.exam.title, language);
    byId("exam-date").textContent = translate(child.exam.date, language);
    byId("exam-completion").textContent = `${child.exam.completion}%`;
    byId("exam-progress-fill").style.width = `${child.exam.completion}%`;
    const examTrack = document.querySelector(".exam-progress-track");
    examTrack.setAttribute("aria-valuenow", String(child.exam.completion));
    byId("exam-ring").style.setProperty("--exam-progress", `${child.exam.completion * 3.6}deg`);
    byId("exam-completed-list").replaceChildren(...child.exam.completed.map((text) => Object.assign(document.createElement("li"), { textContent: translate(text, language) })));
    byId("exam-remaining-list").replaceChildren(...child.exam.remaining.map((text) => Object.assign(document.createElement("li"), { textContent: translate(text, language) })));
    byId("exam-next-step").textContent = translate(child.exam.next, language);
    byId("strengths-list").replaceChildren(...child.strengths.map(([label, score]) => progressRow([translate(label, language), score])));
    byId("attention-list").replaceChildren(...child.attention.map(([topic,score,next]) => {
      const item=document.createElement("article"); const title=document.createElement("strong"); const detail=document.createElement("p");
      title.textContent=`${translate(topic, language)} · ${score}%`; detail.textContent=translate(next, language); item.append(title,detail); return item;
    }));
    byId("activity-list").replaceChildren(...child.activity.map(([when,activity]) => { const li=document.createElement("li");const time=document.createElement("strong");const text=document.createElement("span");time.textContent=translate(when, language);text.textContent=translate(activity, language);li.append(time,text);return li; }));
    byId("recommendation-list").replaceChildren(...child.recommendations.map((recommendation,index) => { const item=document.createElement("article");item.append(Object.assign(document.createElement("span"),{textContent:String(index+1)}),Object.assign(document.createElement("p"),{textContent:translate(recommendation, language)}));return item; }));
    byId("parent-answer").hidden = true;
  }

  function answerQuery(event) {
    event.preventDefault();
    const query=byId("parent-voice-query").value.trim().toLowerCase();
    const child=children[byId("child-selector").value];
    const profile=byId("parent-language").value;
    const topic=translate(child.strengths[0][0], profile);
    const examTitle=translate(child.exam.title, profile);
    const next=translate(child.exam.next, profile);
    const attention=translate(child.attention[0][0], profile);
    const action=translate(child.attention[0][2], profile);
    const recommendation=translate(child.recommendations[0], profile);
    let answer;
    if (/strength|good|బలం|బాగా/.test(query)) {
      if (profile === "pure_telugu") answer=`${child.name} ప్రస్తుతం ${topic}లో బలంగా ఉన్నారు. ఖచ్చితత్వం ${child.strengths[0][1]} శాతం.`;
      else if (profile === "telugu_assisted_english") answer=`${child.name} ప్రస్తుతం ${topic}లో strongగా ఉన్నారు. Accuracy ${child.strengths[0][1]}%.`;
      else answer=`${child.name}'s strongest current area is ${topic} at ${child.strengths[0][1]}% accuracy.`;
    } else if (/exam|preparation|complete|పరీక్ష|సిద్ధత|పూర్తి/.test(query)) {
      if (profile === "pure_telugu") answer=`${examTitle} ప్రణాళిక ${child.exam.completion} శాతం పూర్తయింది. తదుపరి దశ: ${next}.`;
      else if (profile === "telugu_assisted_english") answer=`${examTitle} plan ${child.exam.completion}% complete అయింది. Next step: ${next}.`;
      else answer=`${examTitle} is ${child.exam.completion}% complete. Next step: ${next}.`;
    } else if (/help|support|attention|weak|సహాయం|శ్రద్ధ/.test(query)) {
      if (profile === "pure_telugu") answer=`${attention}లో సహాయం అవసరం. తదుపరి చర్య: ${action}.`;
      else if (profile === "telugu_assisted_english") answer=`${attention}లో support అవసరం. Recommended next step: ${action}.`;
      else answer=`The priority support area is ${attention}. Recommended next step: ${action}.`;
    } else {
      answer = profile === "pure_telugu" ? `ఈ రోజు సూచన: ${recommendation}` : profile === "telugu_assisted_english" ? `Today's support suggestion: ${recommendation}` : `Today's suggested support: ${recommendation}`;
    }
    byId("parent-answer-text").textContent=answer; byId("parent-answer").hidden=false;
    byId("parent-answer").scrollIntoView({behavior:"smooth",block:"center"});
  }

  byId("child-selector").addEventListener("change",render);
  byId("parent-language").addEventListener("change",render);
  byId("report-period").addEventListener("change",render);
  byId("parent-voice-form").addEventListener("submit",answerQuery);
  render();
})(document);
