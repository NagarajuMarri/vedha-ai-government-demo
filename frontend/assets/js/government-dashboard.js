"use strict";
(function initializeGovernmentDashboard(document) {
  const baseDistricts = {
    statewide:{label:"Andhra Pradesh",learners:128460,lessons:486920,practice:72,mastery:68,telugu:61,improvement:14,subjects:{Mathematics:71,Science:69,English:62,Telugu:76,"Social Studies":66}},
    visakhapatnam:{label:"Visakhapatnam",learners:24180,lessons:92640,practice:76,mastery:72,telugu:54,improvement:16,subjects:{Mathematics:75,Science:73,English:68,Telugu:77,"Social Studies":69}},
    guntur:{label:"Guntur",learners:22640,lessons:86410,practice:73,mastery:69,telugu:59,improvement:15,subjects:{Mathematics:72,Science:70,English:63,Telugu:76,"Social Studies":67}},
    kurnool:{label:"Kurnool",learners:19870,lessons:71820,practice:66,mastery:61,telugu:72,improvement:11,subjects:{Mathematics:64,Science:62,English:54,Telugu:71,"Social Studies":59}},
    tirupati:{label:"Tirupati",learners:17620,lessons:68450,practice:74,mastery:70,telugu:57,improvement:15,subjects:{Mathematics:73,Science:72,English:65,Telugu:75,"Social Studies":67}},
    east_godavari:{label:"East Godavari",learners:21750,lessons:83210,practice:70,mastery:67,telugu:68,improvement:13,subjects:{Mathematics:69,Science:68,English:59,Telugu:78,"Social Studies":64}}
  };
  const hierarchy={
    visakhapatnam:{gajuwaka:{label:"Gajuwaka",schools:{zphs_gajuwaka:"Vedha Demo ZPHS Gajuwaka",mpups_pedagantyada:"Vedha Demo MPUPS Pedagantyada"}},bheemunipatnam:{label:"Bheemunipatnam",schools:{zphs_bheemili:"Vedha Demo ZPHS Bheemili",mpups_kapuluppada:"Vedha Demo MPUPS Kapuluppada"}}},
    guntur:{tenali:{label:"Tenali",schools:{zphs_tenali:"Vedha Demo ZPHS Tenali",mpups_kollipara:"Vedha Demo MPUPS Kollipara"}},mangalagiri:{label:"Mangalagiri",schools:{zphs_mangalagiri:"Vedha Demo ZPHS Mangalagiri",mpups_tadepalli:"Vedha Demo MPUPS Tadepalli"}}},
    kurnool:{adoni:{label:"Adoni",schools:{zphs_adoni:"Vedha Demo ZPHS Adoni",mpups_pedda_tumbalam:"Vedha Demo MPUPS Pedda Tumbalam"}},nandyal:{label:"Nandyal",schools:{zphs_nandyal:"Vedha Demo ZPHS Nandyal",mpups_panyam:"Vedha Demo MPUPS Panyam"}}},
    tirupati:{chandragiri:{label:"Chandragiri",schools:{zphs_chandragiri:"Vedha Demo ZPHS Chandragiri",mpups_pakala:"Vedha Demo MPUPS Pakala"}},srikalahasti:{label:"Srikalahasti",schools:{zphs_srikalahasti:"Vedha Demo ZPHS Srikalahasti",mpups_renigunta:"Vedha Demo MPUPS Renigunta"}}},
    east_godavari:{rajamahendravaram:{label:"Rajamahendravaram",schools:{zphs_rajahmundry:"Vedha Demo ZPHS Rajamahendravaram",mpups_kadiyam:"Vedha Demo MPUPS Kadiyam"}},kovvur:{label:"Kovvur",schools:{zphs_kovvur:"Vedha Demo ZPHS Kovvur",mpups_nidadavole:"Vedha Demo MPUPS Nidadavole"}}}
  };
  const districtComparison=[["Visakhapatnam",72],["Tirupati",70],["Guntur",69],["East Godavari",67],["Kurnool",61]];
  const subjectAliases={mathematics:"Mathematics",maths:"Mathematics","గణితం":"Mathematics",science:"Science","సైన్స్":"Science","విజ్ఞాన శాస్త్రం":"Science",english:"English","ఆంగ్లం":"English",telugu:"Telugu","తెలుగు":"Telugu","social studies":"Social Studies",social:"Social Studies","సాంఘిక శాస్త్రం":"Social Studies"};
  const districtAliases={"andhra pradesh":"statewide","ఆంధ్రప్రదేశ్":"statewide",visakhapatnam:"visakhapatnam","విశాఖపట్నం":"visakhapatnam",guntur:"guntur","గుంటూరు":"guntur",kurnool:"kurnool","కర్నూలు":"kurnool",tirupati:"tirupati","తిరుపతి":"tirupati","east godavari":"east_godavari","తూర్పు గోదావరి":"east_godavari"};
  const byId=id=>document.getElementById(id);
  const formatNumber=value=>new Intl.NumberFormat("en-IN").format(value);
  const clamp=value=>Math.max(0,Math.min(100,Math.round(value)));
  function option(value,text){return Object.assign(document.createElement("option"),{value,textContent:text});}
  function populateMandals(){
    const district=byId("district-filter").value,select=byId("mandal-filter");select.replaceChildren(option("all","All mandals"));
    if(district==="statewide"){select.disabled=true;byId("school-filter").replaceChildren(option("all","All schools"));byId("school-filter").disabled=true;return;}
    Object.entries(hierarchy[district]||{}).forEach(([key,item])=>select.append(option(key,item.label)));select.disabled=false;populateSchools();
  }
  function populateSchools(){
    const district=byId("district-filter").value,mandal=byId("mandal-filter").value,select=byId("school-filter");select.replaceChildren(option("all","All schools"));
    if(district==="statewide"||mandal==="all"){select.disabled=true;return;}
    Object.entries(hierarchy[district]?.[mandal]?.schools||{}).forEach(([key,label])=>select.append(option(key,label)));select.disabled=false;
  }
  function selectedScope(){
    const districtKey=byId("district-filter").value,mandalKey=byId("mandal-filter").value,schoolKey=byId("school-filter").value,subject=byId("subject-filter").value,classBand=byId("class-filter").value;
    const base=baseDistricts[districtKey],mandal=hierarchy[districtKey]?.[mandalKey],schoolLabel=mandal?.schools?.[schoolKey];
    const mandalIndex=mandal?Object.keys(hierarchy[districtKey]).indexOf(mandalKey):0,schoolIndex=schoolLabel?Object.keys(mandal.schools).indexOf(schoolKey):0;
    const level=schoolLabel?"school":mandal?"mandal":districtKey==="statewide"?"state":"district";
    const factor=level==="mandal"?.48:level==="school"?.19:1;
    const classFactor=classBand==="middle"?.58:classBand==="secondary"?.42:1;
    const shift=level==="mandal"?(mandalIndex===0?2:-2):level==="school"?(schoolIndex===0?3:-3):0;
    const subjects=Object.fromEntries(Object.entries(base.subjects).map(([name,score])=>[name,clamp(score+shift)]));
    const mastery=subject==="all"?clamp(base.mastery+shift):subjects[subject];
    const label=schoolLabel||mandal?.label||base.label;
    const trail=[base.label,mandal?.label,schoolLabel].filter(Boolean);
    return {districtKey,mandalKey,schoolKey,subject,classBand,level,label,trail,learners:Math.max(40,Math.round(base.learners*factor*classFactor)),lessons:Math.round(base.lessons*factor*classFactor),practice:clamp(base.practice+shift),mastery,telugu:clamp(base.telugu+(level==="school"?1:0)),improvement:clamp(base.improvement+(shift>0?1:0)),subjects};
  }
  function renderMetric(id,value,suffix=""){byId(id).textContent=`${value}${suffix}`;}
  function createBar(label,value,accent="teal"){const row=document.createElement("div"),heading=document.createElement("div"),name=document.createElement("span"),score=document.createElement("strong"),track=document.createElement("div"),fill=document.createElement("span");row.className="dashboard-bar-row";name.textContent=label;score.textContent=value+"%";heading.append(name,score);track.className="dashboard-bar-track";fill.className=`dashboard-bar-fill ${accent}`;fill.style.width=value+"%";track.append(fill);row.append(heading,track);return row;}
  function comparisonRows(scope){
    if(scope.level==="state")return districtComparison;
    const district=baseDistricts[scope.districtKey];
    if(scope.level==="district")return [[district.label,scope.mastery],["State average",baseDistricts.statewide.mastery]];
    if(scope.level==="mandal")return Object.entries(hierarchy[scope.districtKey]).map(([key,item],index)=>[item.label,clamp(district.mastery+(index===0?2:-2))]);
    const schools=hierarchy[scope.districtKey][scope.mandalKey].schools;
    return Object.entries(schools).map(([key,label],index)=>[label,clamp(district.mastery+(index===0?3:-3))]);
  }
  function renderDashboard(){
    const scope=selectedScope();byId("dashboard-scope").textContent=scope.trail.join(" › ")+(scope.subject==="all"?"":" · "+scope.subject);
    renderMetric("metric-learners",formatNumber(scope.learners));renderMetric("metric-lessons",formatNumber(scope.lessons));renderMetric("metric-practice",scope.practice,"%");renderMetric("metric-mastery",scope.mastery,"%");renderMetric("metric-telugu",scope.telugu,"%");renderMetric("metric-improvement","+"+scope.improvement,"%");
    const subjectRows=scope.subject==="all"?Object.entries(scope.subjects):[[scope.subject,scope.subjects[scope.subject]]];
    byId("subject-performance").replaceChildren(...subjectRows.map(([name,score],index)=>createBar(name,score,name==="Telugu"?"gold":"teal")));
    byId("comparison-title").textContent=scope.level==="state"?"District comparison":scope.level==="district"?"District vs state":scope.level==="mandal"?"Mandal comparison":"School comparison";
    byId("district-performance").replaceChildren(...comparisonRows(scope).map(([name,score],index)=>createBar(name,score,index===0?"navy":"teal")));
    byId("filter-announcement").textContent=`Dashboard updated for ${scope.trail.join(", ")}${scope.subject==="all"?"":" and "+scope.subject}. All figures are synthetic aggregate demonstration data.`;
    return scope;
  }
  function findVoiceSelections(query){
    const districtMatch=Object.entries(districtAliases).find(([alias])=>query.includes(alias));
    let districtKey=districtMatch?.[1]||byId("district-filter").value;
    let mandalKey="all",schoolKey="all";
    Object.entries(hierarchy).some(([dKey,mandals])=>Object.entries(mandals).some(([mKey,m])=>{
      if(query.includes(m.label.toLowerCase())){districtKey=dKey;mandalKey=mKey;return true;}
      return Object.entries(m.schools).some(([sKey,label])=>{if(query.includes(label.toLowerCase())||query.includes(label.replace("Vedha Demo ","").toLowerCase())){districtKey=dKey;mandalKey=mKey;schoolKey=sKey;return true;}return false;});
    }));
    const subjectMatch=Object.entries(subjectAliases).find(([alias])=>query.includes(alias));
    return {districtKey,mandalKey,schoolKey,subject:subjectMatch?.[1]||"all",matched:Boolean(districtMatch||mandalKey!=="all"||schoolKey!=="all"||subjectMatch)};
  }
  function applyVoiceQuery(event){
    event.preventDefault();const query=byId("government-voice-query").value.trim().toLowerCase(),profile=byId("government-voice-language").value,found=findVoiceSelections(query);
    if(!found.matched){byId("government-voice-status").hidden=false;byId("government-voice-status").textContent=profile==="pure_telugu"?"జిల్లా, మండలం, పాఠశాల లేదా విషయాన్ని పేర్కొనండి.":"Mention a supported district, mandal, demo school or subject.";byId("government-answer").hidden=true;return;}
    byId("district-filter").value=found.districtKey;populateMandals();byId("mandal-filter").value=found.mandalKey;populateSchools();byId("school-filter").value=found.schoolKey;byId("subject-filter").value=found.subject;
    const scope=renderDashboard(),place=scope.trail.join(" › "),subject=scope.subject==="all"?"all subjects":scope.subject;
    const insight=profile==="pure_telugu"?`${place} పరిధిలో ${formatNumber(scope.learners)} మంది విద్యార్థుల సమగ్ర సూచికలు చూపుతున్నాం. ${subject} భావనల పట్టు ${scope.mastery} శాతం, అభ్యాస పూర్తి ${scope.practice} శాతం. వ్యక్తిగత విద్యార్థి వివరాలు చూపబడవు.`:profile==="telugu_assisted_english"?`${place} scopeలో ${formatNumber(scope.learners)} learners aggregate indicators చూపుతున్నాం. ${subject} mastery ${scope.mastery}%, practice completion ${scope.practice}%. Individual student data చూపబడదు.`:`${place} shows aggregate indicators for ${formatNumber(scope.learners)} learners. ${subject} mastery is ${scope.mastery}% and practice completion is ${scope.practice}%. No individual student data is shown.`;
    byId("government-voice-status").hidden=false;byId("government-voice-status").textContent=profile==="pure_telugu"?"అభ్యర్థన వర్తింపజేయబడింది.":"Request applied.";byId("government-answer-text").textContent=insight;byId("government-answer").hidden=false;byId("government-answer").scrollIntoView({behavior:"smooth",block:"center"});
  }
  byId("government-voice-form").addEventListener("submit",applyVoiceQuery);
  byId("district-filter").addEventListener("change",()=>{populateMandals();renderDashboard();});
  byId("mandal-filter").addEventListener("change",()=>{populateSchools();renderDashboard();});
  ["school-filter","subject-filter","class-filter"].forEach(id=>byId(id).addEventListener("change",renderDashboard));
  byId("government-voice-language").addEventListener("change",()=>{document.documentElement.lang=byId("government-voice-language").value==="english_medium"?"en":"te";byId("government-answer").hidden=true;});
  populateMandals();renderDashboard();
})(document);