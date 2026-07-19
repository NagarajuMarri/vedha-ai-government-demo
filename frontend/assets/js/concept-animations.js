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
      durationSeconds: 120,
      steps: {
        en: [
          "This pizza is one complete whole. Nothing has been cut or removed yet.",
          "To share it fairly among four learners, first make one straight vertical cut through the centre.",
          "Now make a second straight cut across the centre. The pizza is divided into four pieces.",
          "Check the pieces carefully. All four pieces have the same size, so they are four equal parts.",
          "Each single piece is one out of four equal parts. We write one-fourth.",
          "Now select three equal pieces. Three of the four pieces are highlighted.",
          "We write the selected amount as three-fourths. Three is the numerator because three pieces are selected.",
          "Four is the denominator because the whole pizza has four equal pieces. Therefore the highlighted fraction is three-fourths.",
        ],
        te: [
          "ఈ పిజ్జా ఒక పూర్తి మొత్తం. ఇప్పటివరకు దీనిని కోయలేదు, ఏ భాగాన్నీ తీసుకోలేదు.",
          "నలుగురికి సమానంగా పంచడానికి, ముందుగా మధ్యలో నిలువుగా ఒక కోత పెట్టాలి.",
          "ఇప్పుడు మధ్యలో అడ్డంగా రెండవ కోత పెట్టాలి. పిజ్జా నాలుగు ముక్కలుగా విభజించబడింది.",
          "నాలుగు ముక్కలను జాగ్రత్తగా చూడండి. అన్నీ ఒకే పరిమాణంలో ఉన్నాయి కాబట్టి ఇవి నాలుగు సమాన భాగాలు.",
          "ఒక్క ముక్క నాలుగు సమాన భాగాలలో ఒకటి. దీనిని ఒక నాలుగవ వంతు అని రాస్తాము.",
          "ఇప్పుడు మూడు సమాన ముక్కలను ఎంచుకుందాం. నాలుగు ముక్కల్లో మూడు రంగుతో చూపబడుతున్నాయి.",
          "ఎంచుకున్న భాగాన్ని మూడు నాలుగవ వంతులు అని రాస్తాము. మూడు ముక్కలు ఎంచుకున్నందువల్ల మూడు లవం.",
          "మొత్తం పిజ్జాలో నాలుగు సమాన ముక్కలు ఉన్నందువల్ల నాలుగు హారం. కాబట్టి రంగుతో చూపిన భిన్నం మూడు నాలుగవ వంతులు.",
        ],
      },
    },
    Geometry: {
      title: { en: "Geometry: understanding a triangle", te: "జ్యామితి: త్రిభుజాన్ని అర్థం చేసుకుందాం" },
      durationSeconds: 105,
      steps: {
        en: [
          "Geometry studies shapes, sizes, positions, and the relationships between them. We will use a triangle to understand these ideas.",
          "A point marks an exact position. Joining two points creates a line segment with a measurable length.",
          "Three line segments joined end to end form this closed shape called a triangle.",
          "The joining points are vertices. A triangle has three vertices, labelled A, B, and C.",
          "The opening formed where two sides meet is an interior angle. This triangle has three interior angles.",
          "An important triangle rule says that all three interior angles always add up to one hundred and eighty degrees.",
          "Here two angles measure fifty and sixty degrees. Add them first: fifty plus sixty equals one hundred and ten degrees.",
          "Subtract one hundred and ten from one hundred and eighty. The missing angle is seventy degrees, and all three now total one hundred and eighty.",
        ],
        te: [
          "ఆకారాలు, పరిమాణాలు, స్థానాలు, వాటి మధ్య సంబంధాలను అధ్యయనం చేసే గణిత విభాగాన్ని జ్యామితి అంటారు. త్రిభుజం ద్వారా ఈ భావనలను తెలుసుకుందాం.",
          "బిందువు ఒక ఖచ్చితమైన స్థానాన్ని సూచిస్తుంది. రెండు బిందువులను కలిపితే కొలవగల పొడవు ఉన్న రేఖాఖండం ఏర్పడుతుంది.",
          "మూడు రేఖాఖండాలను చివరల వద్ద కలిపితే త్రిభుజం అనే మూసిన ఆకారం ఏర్పడుతుంది.",
          "రేఖాఖండాలు కలిసే బిందువులను శీర్షాలు అంటారు. త్రిభుజానికి ఏ, బీ, సీ అనే మూడు శీర్షాలు ఉన్నాయి.",
          "రెండు భుజాలు కలిసే చోట ఏర్పడే విస్తారాన్ని అంతర్గత కోణం అంటారు. త్రిభుజానికి మూడు అంతర్గత కోణాలు ఉంటాయి.",
          "ప్రతి త్రిభుజంలోని మూడు అంతర్గత కోణాల మొత్తం ఎల్లప్పుడూ నూట ఎనభై డిగ్రీలు.",
          "ఇక్కడ రెండు కోణాలు యాభై, అరవై డిగ్రీలు. ముందుగా వాటిని కలిపితే నూట పది డిగ్రీలు.",
          "నూట ఎనభై నుండి నూట పదిని తీసివేస్తే మిగిలిన కోణం డెబ్బై డిగ్రీలు. మూడు కోణాల మొత్తం నూట ఎనభై అవుతుంది.",
        ],
      },
    },
    "Water Cycle": {
      title: { en: "The continuous water cycle", te: "నిరంతర నీటి చక్రం" },
      durationSeconds: 125,
      steps: {
        en: [
          "The water cycle is the continuous movement of water between Earth's surface and the atmosphere. It has no fixed beginning or end.",
          "Most water is stored in oceans, while lakes, rivers, soil, plants, ice, and groundwater hold smaller amounts.",
          "Energy from the Sun heats surface water. Faster-moving water molecules escape into the air as invisible water vapour.",
          "This change from liquid water to water vapour is evaporation. Plants also release water vapour through transpiration.",
          "As moist air rises, it becomes cooler. Water vapour changes into tiny liquid droplets around dust particles.",
          "This cooling process is condensation. Millions of tiny droplets gather to form visible clouds.",
          "When droplets combine and become too heavy for the cloud, water falls as rain, snow, or hail. This is precipitation.",
          "Some water flows over land into streams and rivers, while some enters the soil and becomes groundwater.",
          "Collected water eventually returns to lakes and oceans. The Sun heats it again, so the water cycle continuously repeats.",
        ],
        te: [
          "భూమి ఉపరితలం మరియు వాతావరణం మధ్య నీరు నిరంతరం ప్రయాణించే ప్రక్రియను నీటి చక్రం అంటారు. దీనికి ఒక స్థిరమైన ఆరంభం లేదా ముగింపు ఉండదు.",
          "ఎక్కువ నీరు సముద్రాల్లో ఉంటుంది. సరస్సులు, నదులు, నేల, మొక్కలు, మంచు, భూగర్భ జలాల్లో కూడా నీరు నిల్వ ఉంటుంది.",
          "సూర్యుడి శక్తి ఉపరితల నీటిని వేడిచేస్తుంది. వేగంగా కదిలే నీటి అణువులు కనిపించని నీటి ఆవిరిగా గాలిలోకి వెళతాయి.",
          "ద్రవ నీరు ఆవిరిగా మారడాన్ని ఆవిరీకరణ అంటారు. మొక్కలు కూడా బాష్పోత్సేకం ద్వారా నీటి ఆవిరిని విడుదల చేస్తాయి.",
          "తేమగల గాలి పైకి వెళ్లినప్పుడు చల్లబడుతుంది. నీటి ఆవిరి ధూళి కణాల చుట్టూ చిన్న నీటి బిందువులుగా మారుతుంది.",
          "ఈ చల్లబడే ప్రక్రియను సంఘననం అంటారు. లక్షల చిన్న బిందువులు కలిసి కనిపించే మేఘాలను ఏర్పరుస్తాయి.",
          "బిందువులు కలసి బరువెక్కినప్పుడు వర్షం, మంచు లేదా వడగళ్ల రూపంలో భూమికి పడతాయి. దీనిని వర్షపాతం అంటారు.",
          "కొంత నీరు నేలపై ప్రవహించి వాగులు, నదుల్లో చేరుతుంది. మరికొంత నేలలోకి ఇంకి భూగర్భ జలంగా మారుతుంది.",
          "సేకరించిన నీరు చివరకు సరస్సులు, సముద్రాల్లో చేరుతుంది. సూర్యుడు మళ్లీ వేడిచేయడంతో నీటి చక్రం నిరంతరం కొనసాగుతుంది.",
        ],
      },
    },
    "Solar System": {
      title: { en: "Our Solar System", te: "మన సౌర కుటుంబం" },
      durationSeconds: 125,
      steps: {
        en: [
          "The Solar System contains the Sun and every object held by its gravity, including planets, moons, dwarf planets, asteroids, and comets.",
          "The Sun is a star at the centre. It contains most of the Solar System's mass and supplies the light and heat needed for life on Earth.",
          "The four inner planets are Mercury, Venus, Earth, and Mars. They are smaller, rocky planets located closer to the Sun.",
          "The four outer planets are Jupiter, Saturn, Uranus, and Neptune. They are much larger and are made mainly of gases or icy materials.",
          "Every planet travels around the Sun along a curved path called an orbit. Gravity keeps planets from moving away into space.",
          "Earth also rotates on an imaginary axis. One complete rotation takes about twenty-four hours and produces day and night.",
          "Earth revolves around the Sun while rotating. One complete revolution takes about three hundred and sixty-five days, which forms a year.",
          "Earth's Moon revolves around Earth. Other planets also have moons, while Saturn is especially known for its broad ring system.",
          "The Solar System is only one small part of the Milky Way galaxy, which contains billions of stars and many other planetary systems.",
        ],
        te: [
          "సూర్యుడు, అతని గురుత్వాకర్షణ వల్ల బంధించబడిన గ్రహాలు, ఉపగ్రహాలు, మరుగుజ్జు గ్రహాలు, గ్రహశకలాలు, తోకచుక్కలు కలిసి సౌర కుటుంబాన్ని ఏర్పరుస్తాయి.",
          "సూర్యుడు మధ్యలో ఉన్న ఒక నక్షత్రం. సౌర కుటుంబంలోని ఎక్కువ ద్రవ్యరాశి సూర్యుడిలోనే ఉంది. భూమిపై జీవానికి అవసరమైన కాంతి, వేడిని అందిస్తాడు.",
          "బుధుడు, శుక్రుడు, భూమి, అంగారకుడు అంతర్గత గ్రహాలు. ఇవి సూర్యుడికి దగ్గరగా ఉన్న చిన్న రాతి గ్రహాలు.",
          "గురుడు, శని, యురేనస్, నెప్ట్యూన్ బాహ్య గ్రహాలు. ఇవి చాలా పెద్దవి; ప్రధానంగా వాయువులు లేదా మంచు పదార్థాలతో ఏర్పడ్డాయి.",
          "ప్రతి గ్రహం కక్ష్య అనే వక్ర మార్గంలో సూర్యుని చుట్టూ తిరుగుతుంది. గురుత్వాకర్షణ గ్రహాలు అంతరిక్షంలోకి దూరంగా వెళ్లకుండా ఉంచుతుంది.",
          "భూమి ఒక ఊహాత్మక అక్షంపై కూడా తిరుగుతుంది. ఒకసారి తిరగడానికి సుమారు ఇరవై నాలుగు గంటలు పడుతుంది; దీని వల్ల పగలు, రాత్రి ఏర్పడతాయి.",
          "భూమి తన అక్షంపై తిరుగుతూ సూర్యుని చుట్టూ పరిభ్రమిస్తుంది. ఒక పరిభ్రమణానికి సుమారు మూడు వందల అరవై ఐదు రోజులు పడుతుంది; దీనినే ఒక సంవత్సరం అంటాము.",
          "చంద్రుడు భూమి చుట్టూ తిరుగుతాడు. ఇతర గ్రహాలకు కూడా ఉపగ్రహాలు ఉన్నాయి. శని తన విస్తారమైన వలయాలకు ప్రసిద్ధి.",
          "మన సౌర కుటుంబం పాలపుంత అనే నక్షత్ర వీధిలోని చిన్న భాగం మాత్రమే. పాలపుంతలో కోట్లాది నక్షత్రాలు, అనేక గ్రహ వ్యవస్థలు ఉన్నాయి.",
        ],
      },
    },
    Decimals: {
      title: { en: "Decimals and place value", te: "దశాంశాలు మరియు స్థాన విలువ" },
      durationSeconds: 100,
      steps: { en: ["A decimal shows a whole and parts smaller than one.", "Read digits by their place value.", "Tenths come immediately after the decimal point.", "Hundredths come in the next place."], te: ["దశాంశం పూర్ణ సంఖ్యతో పాటు ఒకటి కంటే చిన్న భాగాలను చూపుతుంది.", "ప్రతి అంకెను దాని స్థాన విలువ ఆధారంగా చదవాలి.", "దశాంశ బిందువు తర్వాత మొదటి స్థానం పదవ వంతులు.", "తర్వాతి స్థానం నూరవ వంతులు."] },
    },
    Photosynthesis: {
      title: { en: "Photosynthesis", te: "కిరణజన్య సంయోగక్రియ" },
      durationSeconds: 120,
      steps: { en: ["Plants use sunlight to make food.", "Roots absorb water.", "Leaves take in carbon dioxide.", "Glucose is made and oxygen is released."], te: ["మొక్కలు సూర్యకాంతితో ఆహారం తయారు చేసుకుంటాయి.", "వేర్లు నీటిని గ్రహిస్తాయి.", "ఆకులు కార్బన్ డయాక్సైడ్ తీసుకుంటాయి.", "గ్లూకోజ్ తయారై ఆక్సిజన్ విడుదలవుతుంది."] },
    },
    Grammar: {
      title: { en: "English Grammar", te: "ఆంగ్ల వ్యాకరణం" },
      durationSeconds: 100,
      steps: { en: ["A sentence expresses a complete thought.", "The subject tells who or what.", "The verb shows action or state.", "Correct order and punctuation make meaning clear."], te: ["వాక్యం సంపూర్ణ భావాన్ని తెలియజేస్తుంది.", "కర్త ఎవరు లేదా ఏమిటో చెబుతుంది.", "క్రియ చర్య లేదా స్థితిని చూపుతుంది.", "సరైన పదక్రమం, విరామచిహ్నాలు భావాన్ని స్పష్టం చేస్తాయి."] },
    },
    "Telugu Grammar": {
      title: { en: "Telugu Grammar", te: "తెలుగు వ్యాకరణం" },
      durationSeconds: 100,
      steps: { en: ["A Telugu sentence joins meaningful word forms.", "Identify the subject.", "Identify the object.", "The verb commonly appears at the end."], te: ["తెలుగు వాక్యం అర్థవంతమైన పదరూపాలను కలుపుతుంది.", "ముందుగా కర్తను గుర్తించాలి.", "తర్వాత కర్మను గుర్తించాలి.", "క్రియ సాధారణంగా వాక్యం చివర ఉంటుంది."] },
    },
    "Indian Constitution": {
      title: { en: "Indian Constitution", te: "భారత రాజ్యాంగం" },
      durationSeconds: 130,
      steps: { en: ["The Constitution is India's supreme law.", "It establishes institutions and their powers.", "It protects Fundamental Rights.", "It also explains duties and democratic values."], te: ["రాజ్యాంగం భారతదేశ అత్యున్నత చట్టం.", "ఇది ప్రభుత్వ సంస్థలు, వాటి అధికారాలను ఏర్పాటు చేస్తుంది.", "ఇది ప్రాథమిక హక్కులను రక్షిస్తుంది.", "బాధ్యతలు, ప్రజాస్వామ్య విలువలను వివరిస్తుంది."] },
    },
    "Indian Freedom Movement": {
      title: { en: "Indian Freedom Movement", te: "భారత స్వాతంత్ర్య ఉద్యమం" },
      durationSeconds: 150,
      steps: { en: ["Colonial rule created political and economic injustice.", "Resistance grew across regions.", "Mass movements united people.", "India became independent in 1947."], te: ["వలస పాలన రాజకీయ, ఆర్థిక అన్యాయాన్ని సృష్టించింది.", "వివిధ ప్రాంతాల్లో ప్రతిఘటన పెరిగింది.", "ప్రజా ఉద్యమాలు దేశాన్ని ఏకం చేశాయి.", "1947లో భారతదేశం స్వాతంత్ర్యం పొందింది."] },
    },
    "Andhra Pradesh Geography": {
      title: { en: "Andhra Pradesh Geography", te: "ఆంధ్రప్రదేశ్ భూగోళ శాస్త్రం" },
      durationSeconds: 125,
      steps: { en: ["Andhra Pradesh has coastal plains and uplands.", "The Eastern Ghats cross the state.", "Krishna and Godavari support farming.", "The Bay of Bengal shapes climate and livelihoods."], te: ["ఆంధ్రప్రదేశ్‌లో తీర మైదానాలు, ఎత్తైన ప్రాంతాలు ఉన్నాయి.", "తూర్పు కనుమలు రాష్ట్రంలో విస్తరించాయి.", "కృష్ణా, గోదావరి నదులు వ్యవసాయానికి తోడ్పడతాయి.", "బంగాళాఖాతం వాతావరణం, జీవనోపాధులను ప్రభావితం చేస్తుంది."] },
    },
    "Local Government": {
      title: { en: "Local Government", te: "స్థానిక ప్రభుత్వం" },
      durationSeconds: 110,
      steps: { en: ["Local government serves people close to home.", "Gram Panchayats serve villages.", "Municipal bodies serve towns and cities.", "Elected representatives manage local services."], te: ["స్థానిక ప్రభుత్వం ప్రజలకు సమీపంగా సేవలందిస్తుంది.", "గ్రామ పంచాయతీలు గ్రామాలకు సేవలందిస్తాయి.", "పురపాలక సంస్థలు పట్టణాలు, నగరాలకు సేవలందిస్తాయి.", "ఎన్నికైన ప్రతినిధులు స్థానిక సేవలను నిర్వహిస్తారు."] },
    },
    "Climate and Natural Resources": {
      title: { en: "Climate and Natural Resources", te: "వాతావరణం మరియు సహజ వనరులు" },
      durationSeconds: 125,
      steps: { en: ["Climate shapes rainfall and temperature patterns.", "Water, soil, forests, and minerals are natural resources.", "People depend on resources for life and livelihoods.", "Conservation protects resources for future generations."], te: ["వాతావరణం వర్షపాతం, ఉష్ణోగ్రత నమూనాలను నిర్ణయిస్తుంది.", "నీరు, నేల, అడవులు, ఖనిజాలు సహజ వనరులు.", "జీవితం, జీవనోపాధులకు ప్రజలు వనరులపై ఆధారపడతారు.", "సంరక్షణ భవిష్యత్ తరాలకు వనరులను కాపాడుతుంది."] },
    },
  };

  const state = { lesson: null, concept: null, profile: "english_medium", language: "en", index: 0, playing: false, timer: null, stepStartedAt: 0 };
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
        part.append(node("piece-number", String(index + 1)));
        whole.append(part);
      }
      whole.append(
        node("pizza-cut cut-vertical"),
        node("pizza-cut cut-horizontal"),
        node("fraction-label", "3/4"),
      );
      plate.append(whole);
      table.append(
        plate,
        node("fraction-story story-whole", state.language === "te" ? "1 పూర్తి మొత్తం" : "1 complete whole"),
        node("fraction-story story-equal", state.language === "te" ? "4 సమాన భాగాలు" : "4 equal parts"),
        node("fraction-story story-selected", state.language === "te" ? "3 భాగాలు ఎంచుకున్నాం" : "3 parts selected"),
        node("fraction-story story-result", "3/4"),
      );
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
    } else if (concept === "Decimals") {
      const board = node("decimal-scene");
      board.append(
        node("decimal-number", "2.35"),
        node("decimal-point-marker", "●"),
        node("place-card ones-card", state.language === "te" ? "ఒకట్లు · 2" : "ONES · 2"),
        node("place-card tenths-card", state.language === "te" ? "పదవ వంతులు · 3" : "TENTHS · 3"),
        node("place-card hundredths-card", state.language === "te" ? "నూరవ వంతులు · 5" : "HUNDREDTHS · 5"),
      );
      stage.append(board);
    } else if (concept === "Photosynthesis") {
      const scene = node("plant-scene");
      scene.append(
        node("plant-sun", "☀"),
        node("plant-ground"),
        node("plant-stem"),
        node("plant-leaf leaf-left"),
        node("plant-leaf leaf-right"),
        node("plant-roots"),
        node("plant-flow water-flow", state.language === "te" ? "నీరు ↑" : "WATER ↑"),
        node("plant-flow carbon-flow", "CO₂ →"),
        node("plant-flow oxygen-flow", "O₂ ↑"),
        node("plant-food", state.language === "te" ? "ఆహారం" : "GLUCOSE"),
      );
      stage.append(scene);
    } else if (concept === "Grammar" || concept === "Telugu Grammar") {
      const telugu = concept === "Telugu Grammar";
      const sentence = telugu ? ["రాము", "పుస్తకం", "చదివాడు"] : ["Ravi", "reads", "a book"];
      const scene = node("grammar-scene");
      scene.append(node("grammar-heading", telugu ? "కర్త + కర్మ + క్రియ" : "SUBJECT + VERB + OBJECT"));
      const row = node("sentence-builder");
      sentence.forEach((word, index) => {
        const token = node(`sentence-token token-${index + 1}`, word);
        token.append(node("token-role", telugu ? ["కర్త", "కర్మ", "క్రియ"][index] : ["SUBJECT", "VERB", "OBJECT"][index]));
        row.append(token);
      });
      scene.append(row, node("sentence-result", sentence.join(" ")));
      stage.append(scene);
    } else if (concept === "Indian Constitution") {
      const scene = node("constitution-scene");
      const book = node("constitution-book");
      book.append(node("book-emblem", "☸"), node("book-title", state.language === "te" ? "భారత రాజ్యాంగం" : "CONSTITUTION OF INDIA"));
      scene.append(book, node("civic-pillar rights-pillar", state.language === "te" ? "హక్కులు" : "RIGHTS"), node("civic-pillar duties-pillar", state.language === "te" ? "బాధ్యతలు" : "DUTIES"), node("civic-pillar democracy-pillar", state.language === "te" ? "ప్రజాస్వామ్యం" : "DEMOCRACY"));
      stage.append(scene);
    } else if (concept === "Indian Freedom Movement") {
      const scene = node("freedom-scene");
      const timeline = node("freedom-timeline");
      [["1857", "Resistance"], ["1920", "Non-Cooperation"], ["1930", "Salt March"], ["1942", "Quit India"], ["1947", "Freedom"]].forEach(([year, label], index) => {
        const event = node(`freedom-event event-${index + 1}`);
        event.append(node("event-year", year), node("event-label", label));
        timeline.append(event);
      });
      scene.append(node("freedom-flag", "🇮🇳"), timeline);
      stage.append(scene);
    } else if (concept === "Andhra Pradesh Geography") {
      const scene = node("ap-scene");
      scene.append(node("ap-map-shape"), node("ap-coast"), node("ap-river krishna-river", "కృష్ణా"), node("ap-river godavari-river", "గోదావరి"), node("ap-ghats", state.language === "te" ? "తూర్పు కనుమలు" : "EASTERN GHATS"));
      stage.append(scene);
    } else if (concept === "Local Government") {
      const scene = node("local-government-scene");
      scene.append(node("village-homes", "⌂  ⌂  ⌂"), node("panchayat-building", state.language === "te" ? "గ్రామ పంచాయతి" : "GRAM PANCHAYAT"), node("service service-water", "💧"), node("service service-road", "═"), node("service service-light", "☀"));
      stage.append(scene);
    } else if (concept === "Climate and Natural Resources") {
      const scene = node("resources-scene");
      scene.append(node("resource-earth", "🌍"), node("resource-card resource-water", state.language === "te" ? "నీరు" : "WATER"), node("resource-card resource-soil", state.language === "te" ? "నేల" : "SOIL"), node("resource-card resource-forest", state.language === "te" ? "అడవులు" : "FORESTS"), node("resource-card resource-mineral", state.language === "te" ? "ఖనిజాలు" : "MINERALS"), node("conservation-ring", state.language === "te" ? "సంరక్షణ" : "CONSERVE"));
      stage.append(scene);
    }
  }

  function setStep(index) {
    const steps = state.lesson.steps[state.language];
    state.index = Math.max(0, Math.min(index, steps.length - 1));
    const visualStep = state.concept === "Fractions"
      ? state.index + 1
      : Math.min(4, Math.ceil(((state.index + 1) / steps.length) * 4));
    byId("animation-stage").dataset.step = String(visualStep);
    byId("animation-caption").textContent = steps[state.index];
    byId("animation-step").textContent = `${state.index + 1} / ${steps.length}`;
    byId("animation-progress-fill").style.width = `${((state.index + 1) / steps.length) * 100}%`;
    byId("animation-progress").setAttribute("aria-valuenow", String(state.index + 1));
    byId("animation-progress").setAttribute("aria-valuemax", String(steps.length));
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

  function scheduleAdvanceAfterNarration() {
    if (!state.playing) return;
    state.timer = window.setTimeout(advanceAfterNarration, 650);
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
    state.stepStartedAt = Date.now();
    const spoken = await window.VedhaVoice?.speakText(caption, state.profile, {
      onEnd: scheduleAdvanceAfterNarration,
      onUnavailable: () => {
        byId("animation-status").textContent = state.language === "te"
          ? "తెలుగు వాయిస్ అందుబాటులో లేదు. దృశ్యం, సమకాలిక వాక్యంతో కొనసాగుతోంది."
          : "Narration is unavailable. Continuing with synchronized captions.";
      },
    });
    if (!spoken && state.playing) {
      state.timer = window.setTimeout(advanceAfterNarration, Math.max(4500, caption.length * 65));
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

  function buildFullLessonNarration(generatedLesson) {
    if (!generatedLesson) return [];
    return [
      generatedLesson.introduction,
      ...generatedLesson.explanation_steps,
      generatedLesson.example,
      ...generatedLesson.key_points,
      generatedLesson.check_question,
    ].map((text) => String(text || "").trim()).filter(Boolean);
  }

  function estimateNarrationSeconds(steps) {
    const wordCount = steps.join(" ").split(/\s+/).filter(Boolean).length;
    return Math.max(60, Math.min(300, Math.ceil(wordCount / 1.8)));
  }

  function prepare(concept, profile, generatedLesson) {
    state.concept = concept;
    state.profile = profile;
    state.language = profiles[profile] || "en";
    const template = lessons[concept] || null;
    const fullNarration = buildFullLessonNarration(generatedLesson);
    state.lesson = template && fullNarration.length
      ? {
          ...template,
          title: { en: generatedLesson.title, te: generatedLesson.title },
          steps: { en: fullNarration, te: fullNarration },
          durationSeconds: estimateNarrationSeconds(fullNarration),
        }
      : template;
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
    const minutes = Math.ceil(state.lesson.durationSeconds / 60);
    byId("animation-duration").textContent = state.language === "te"
      ? `సుమారు ${minutes} నిమిషాలు`
      : `About ${minutes} min`;
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
