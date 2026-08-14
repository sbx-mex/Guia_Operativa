(() => {
  const cms = window.TRAINING_CMS;
  const $ = id => document.getElementById(id);
  const state = {
    view: "home", category: "", content: null, selections: {}, selectorIndex: 0,
    route: "", step: 0, filter: "Todos", subfilter: "Todas", query: "", visible: 6, timer: null,
    deferredInstall: null, evaluationIndex: 0, evaluationScore: 0, evaluatedPartner: "", evaluationPhoto: "",
  };
  const iconMap = {
    coffee: "☕", milk: "🥛", pour: "↘", ice: "❄", bottle: "▤", blend: "◎",
    check: "✓", sauce: "◒", grind: "◉", filter: "▽", water: "◌", tie: "⌁",
    timer: "◷", store: "▣", freeze: "❄", tray: "▱", layout: "▦", oven: "♨",
    heat: "⌁", serve: "✓",
  };
  const categoryCopy = {
    Bebidas: ["Bebidas", "Elige una bebida para practicar su secuencia."],
    Procesos: ["Procesos", "Practica preparación, almacenamiento y controles críticos."],
    Alimentos: ["Alimentos", "Sigue ensamble y horneo sin perder parámetros."],
  };
  const campaignResourceCopy = [
    {title: "Checklist operativo", description: "Valida personal, insumos, layout y seguimiento antes de abrir."},
    {title: "Buenas prácticas", description: "Confirma Grande, vida útil de 24 h, smallwares y una bebida por licuadora."},
    {title: "¡Participa en el concurso!", description: "Informativo importante: revisa la dinámica, reúne a tu equipo y confirma cómo participar.", priority: true},
  ];
  const unicornQuiz = [
    {question: "¿En qué tamaño se prepara Unicorn Frappuccino?", options: ["Alto", "Grande", "Venti"], answer: "Grande", note: "Unicorn se ofrece únicamente en tamaño Grande."},
    {question: "¿Cuál es la vida útil de Salsa Azul Drizzle?", options: ["12 horas", "24 horas", "48 horas"], answer: "24 horas", note: "Etiqueta la Salsa Azul con vida útil de 24 horas."},
    {question: "¿Qué dosificador se usa para el mocha blanco de Salsa Azul?", options: ["Pump espresso", "Pump CBS", "Cuchara"], answer: "Pump CBS", note: "Los 6 y 8 pumps indicados son pumps CBS."},
    {question: "¿Cuántas bebidas Unicorn se preparan a la vez en la licuadora?", options: ["1 bebida", "2 bebidas", "3 bebidas"], answer: "1 bebida", note: "Prepara una sola bebida por ciclo de licuadora."},
    {question: "¿Qué debes dominar antes del servicio?", options: ["Sólo el concurso", "Salsa Azul y Unicorn", "Sólo etiquetado"], answer: "Salsa Azul y Unicorn", note: "Practica primero Salsa Azul y después la bebida completa."},
  ];

  function localDate(timezone) {
    return new Intl.DateTimeFormat("en-CA", {timeZone: timezone, year: "numeric", month: "2-digit", day: "2-digit"}).format(new Date());
  }
  function activeCampaign() {
    return (cms.meta.campaigns || []).find(item => {
      const today = localDate(item.timezone || "America/Mexico_City");
      return today >= item.start && today <= item.end;
    });
  }
  function launchTraining(id) {
    showView("training");
    selectContent(id);
  }
  function configureCampaign() {
    const campaign = activeCampaign();
    if (!campaign) return;
    const primary = cms.contents.find(item => item.id === campaign.primary);
    const secondary = cms.contents.find(item => item.id === campaign.secondary);
    if (!primary || !secondary) return;
    $("campaignSpotlight").hidden = false;
    $("campaignSpotlightImage").src = primary.productImage;
    $("campaignSpotlightImage").alt = primary.name;
    $("campaignSpotlightTitle").textContent = campaign.title;
    $("campaignTitle").textContent = campaign.title;
    $("campaignSubtitle").textContent = campaign.subtitle;
    $("campaignHero").src = primary.productImage;
    const campaignVideo = $("campaignVideo");
    const campaignHero = $("campaignHero");
    campaignVideo.hidden = false;
    campaignHero.hidden = true;
    const practice = (id, dialog = false) => {
      if (dialog) {
        campaignVideo.pause();
        $("campaignDialog").close();
      }
      launchTraining(id);
    };
    $("campaignPrimary").onclick = () => practice(primary.id);
    $("campaignSecondary").onclick = () => practice(secondary.id);
    $("campaignDialogPrimary").onclick = () => practice(primary.id, true);
    $("campaignDialogSecondary").onclick = () => practice(secondary.id, true);
    $("campaignResources").innerHTML = campaign.resources.map((resource, index) => {const copy=campaignResourceCopy[index]||{title:`Material ${index+1}`,description:"Consulta el material de apoyo."};return `<button class="${copy.priority?"campaign-resource-priority":""}" type="button" data-campaign-resource="${index}"><img src="${resource}" alt=""><span>${copy.title}</span><small>${copy.description}</small></button>`;}).join("");
    const selectResource = (index, showResource = true) => {
      const context = campaignResourceCopy[index] || {title:`Material ${index+1}`,description:"Consulta el material de apoyo."};
      if (showResource) {
        campaignVideo.pause();
        campaignVideo.hidden = true;
        campaignHero.hidden = false;
        campaignHero.src = campaign.resources[index];
        campaignHero.alt = context.title;
      }
      $("campaignResourceContext").innerHTML = `<b>${context.title}</b><span>${context.description}</span>`;
      document.querySelectorAll("[data-campaign-resource]").forEach(button => button.classList.toggle("active", Number(button.dataset.campaignResource) === index));
    };
    document.querySelectorAll("[data-campaign-resource]").forEach(button => button.addEventListener("click", () => selectResource(Number(button.dataset.campaignResource))));
    selectResource(0, false);
    $("toggleCampaignVideo").onclick = () => {
      if (campaignVideo.hidden) {
        campaignHero.hidden = true; campaignVideo.hidden = false; campaignVideo.play();
      } else if (campaignVideo.paused) campaignVideo.play(); else campaignVideo.pause();
      $("toggleCampaignVideo").textContent = campaignVideo.paused ? "Reproducir animación" : "Pausar animación";
    };
    campaignVideo.addEventListener("play", () => $("toggleCampaignVideo").textContent = "Pausar animación");
    campaignVideo.addEventListener("pause", () => $("toggleCampaignVideo").textContent = "Reproducir animación");
    $("campaignEvaluate").onclick = () => { campaignVideo.pause(); $("campaignDialog").close(); openEvaluation(); };
    $("campaignEvaluateHome").onclick = openEvaluation;
    $("closeCampaign").onclick = () => { sessionStorage.setItem(`campaign-${campaign.id}`, "closed"); campaignVideo.pause(); $("campaignDialog").close(); };
    if (!sessionStorage.getItem(`campaign-${campaign.id}`)) {
      $("campaignDialog").showModal();
      if (!matchMedia("(prefers-reduced-motion: reduce)").matches) campaignVideo.play().catch(() => {}); else campaignVideo.pause();
    }
  }

  function setupPdfViewer() {
    const dialog = $("pdfDialog");
    const frame = $("pdfFrame");
    const open = (url, title = "Vista previa PDF", downloadName = "documento.pdf") => {
      frame.src = url;
      $("pdfDialogTitle").textContent = title;
      $("openPdfExternal").href = url;
      $("downloadPdfTarget").href = url;
      $("downloadPdfTarget").download = downloadName;
      if (!dialog.open) dialog.showModal();
    };
    window.PdfViewer = {open};
    document.querySelectorAll(".pdf-preview-link").forEach(link => link.addEventListener("click", event => {
      event.preventDefault();
      open(link.href, link.dataset.pdfTitle || link.textContent.trim(), link.href.split("/").pop() || "documento.pdf");
    }));
    $("closePdfDialog").onclick = () => dialog.close();
    dialog.addEventListener("close", () => { frame.src = "about:blank"; });
  }

  function normalize(value) {
    return String(value || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  }
  function announce(message) { $("statusRegion").textContent = message; }
  function saveProgress() {
    if (!state.content || !state.route) return;
    sessionStorage.setItem("guia-progress", JSON.stringify({contentId: state.content.id, selections: state.selections, route: state.route, step: state.step}));
    updateResume();
  }
  function updateResume() {
    const saved = JSON.parse(sessionStorage.getItem("guia-progress") || "null");
    const content = saved && cms.contents.find(item => item.id === saved.contentId);
    $("resumeTraining").hidden = !content;
    if (content) $("resumeLabel").textContent = `${content.name} · paso ${Number(saved.step || 0) + 1}`;
  }
  function showView(view, options = {}) {
    state.view = view;
    document.querySelectorAll(".view").forEach(node => node.classList.toggle("active", node.id === `${view}View`));
    document.querySelectorAll(".nav-button").forEach(node => node.classList.toggle("active", node.dataset.view === view));
    if (view === "training" && options.reset !== false) resetTraining();
    if (view === "search") renderSearch();
    if (view === "objectives") window.Objectives?.render();
    const hash = view === "training" ? "#capacitar" : view === "search" ? "#recetario" : view === "objectives" ? "#objetivos" : "#inicio";
    if (options.history !== false && location.hash !== hash) history.pushState({view}, "", hash);
    announce(view === "home" ? "Inicio" : view === "training" ? "Capacitación" : view === "search" ? "Buscador de recetas" : "Objetivos y avance");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  function trail() {
    const parts = [];
    if (state.category) parts.push(state.category);
    if (state.content) parts.push(state.content.name);
    Object.entries(state.selections).forEach(([key, value]) => {
      const selector = state.content?.selectors.find(item => item.id === key);
      parts.push(`${selector?.label}: ${cms.labels[value] || value}`);
    });
    $("selectionTrail").innerHTML = parts.map((part, index) => `<span>${index + 1}</span><b>${part}</b>`).join("");
  }
  function setTrainingHeader(title, intro) {
    $("trainingHeading").textContent = title;
    $("trainingIntro").textContent = intro;
    trail();
  }
  function resetTraining() {
    state.category = ""; state.content = null; state.selections = {}; state.selectorIndex = 0; state.route = ""; state.step = 0;
    setTrainingHeader("Elige un área", "Comienza por el tipo de preparación.");
    $("trainingStage").innerHTML = `<div class="area-grid">
      ${Object.keys(categoryCopy).map(category => `<button class="area-card" data-category="${category}" type="button"><span>${category === "Bebidas" ? "◒" : category === "Procesos" ? "⟳" : "♨"}</span><b>${category}</b><small>${categoryCopy[category][1]}</small><i>Continuar →</i></button>`).join("")}
    </div>`;
    document.querySelectorAll("[data-category]").forEach(button => button.addEventListener("click", () => selectCategory(button.dataset.category)));
  }
  function selectCategory(category) {
    state.category = category;
    const [title, intro] = categoryCopy[category];
    setTrainingHeader(title, intro);
    const contents = cms.contents.filter(item => item.category === category).sort((a, b) => {
      const priority = value => value.subcategory.includes("prioridad") ? 0 : value.subcategory.includes("temporada") ? 1 : 2;
      return priority(a) - priority(b) || a.name.localeCompare(b.name, "es");
    });
    $("trainingStage").innerHTML = `<button class="back-link inline" id="changeArea" type="button">← Cambiar área</button>
      <div class="training-card-grid">${contents.map(item => `<button class="training-card" data-content="${item.id}" type="button"><img src="${item.productImage}" alt="${item.name}"><span><small>${item.subcategory}</small><b>${item.name}</b><em>${item.description}</em><i>Practicar →</i></span></button>`).join("")}</div>`;
    $("changeArea").addEventListener("click", resetTraining);
    document.querySelectorAll("[data-content]").forEach(button => button.addEventListener("click", () => selectContent(button.dataset.content)));
  }
  function selectContent(id) {
    state.content = cms.contents.find(item => item.id === id);
    state.selections = {}; state.selectorIndex = 0;
    if (!state.content.selectors.length) { state.route = state.content.routes.default; startRoute(); return; }
    if (state.content.selectors.length === 1 && state.content.selectors[0].options.length === 1) {
      const selector = state.content.selectors[0];
      state.selections[selector.id] = selector.options[0];
      resolveRoute();
      return;
    }
    renderSelector();
  }
  function renderSelector() {
    const selector = state.content.selectors[state.selectorIndex];
    setTrainingHeader(`Elige ${selector.label.toLowerCase()}`, `Configura ${state.content.name} antes de comenzar.`);
    $("trainingStage").innerHTML = `<div class="config-layout"><div class="config-product"><img src="${state.content.productImage}" alt="${state.content.name}"><small>${state.content.subcategory}</small><h2>${state.content.name}</h2></div><div class="option-panel"><span class="step-kicker">${state.selectorIndex + 1} de ${state.content.selectors.length}</span><h2>${selector.label}</h2><div class="option-grid">${selector.options.map(option => `<button data-option="${option}" type="button"><b>${cms.labels[option] || option}</b><span>→</span></button>`).join("")}</div></div></div>`;
    document.querySelectorAll("[data-option]").forEach(button => button.addEventListener("click", () => {
      state.selections[selector.id] = button.dataset.option;
      state.selectorIndex += 1;
      if (state.selectorIndex < state.content.selectors.length) renderSelector(); else resolveRoute();
    }));
  }
  function resolveRoute() {
    const key = state.content.selectors.map(selector => `${selector.id}=${state.selections[selector.id]}`).join("|");
    state.route = state.content.routes[key];
    if (!state.route) throw new Error(`Ruta no encontrada: ${key}`);
    startRoute();
  }
  function routeSteps() { return cms.steps.filter(step => step.route === state.route).sort((a, b) => a.order - b.order); }
  function valueFor(step) {
    const entries = Object.fromEntries(String(step.values || "").split("|").filter(Boolean).map(pair => pair.split("=")));
    const primary = state.selections.size || state.selections.batch;
    return entries[primary] || entries.TODOS || "";
  }
  function startRoute() {
    state.step = 0; saveProgress();
    setTrainingHeader(state.content.name, "Avanza a tu ritmo. La guía conserva el contexto de cada paso.");
    renderRunner();
  }
  function renderRunner() {
    const steps = routeSteps();
    const step = steps[state.step];
    const progress = Math.round(((state.step + 1) / steps.length) * 100);
    const milestones = steps.map((item, index) => `<span class="${index < state.step ? "done" : index === state.step ? "active" : ""}"><i>${index < state.step ? "✓" : index + 1}</i><b>${item.stage}</b></span>`).join("");
    $("trainingStage").innerHTML = `<div class="runner">
      <aside class="runner-visual"><img src="${state.content.productImage}" alt="${state.content.name}"><small>Resultado esperado</small><h2>${state.content.name}</h2><button id="openRules" type="button">Equipo y normas</button></aside>
      <section class="runner-main">
        <div class="progress-line"><span style="width:${progress}%"></span></div>
        <div class="milestones">${milestones}</div>
        <article class="step-card">
          <div class="step-top"><span class="step-icon">${iconMap[step.icon] || "•"}</span><span class="step-kicker">Paso ${state.step + 1} de ${steps.length}</span></div>
          <h2>${step.title}</h2><p>${step.detail}</p>
          ${valueFor(step) ? `<div class="measure"><span>${Object.values(state.selections).map(value => cms.labels[value] || value).join(" · ") || "Indicador"}</span><strong>${valueFor(step)}</strong></div>` : ""}
          ${step.timer ? `<button class="timer-button" id="timerButton" data-seconds="${step.timer}" type="button">◷ Iniciar temporizador</button>` : ""}
        </article>
        <div class="runner-actions"><button id="prevStep" type="button" ${state.step === 0 ? "disabled" : ""}>← Anterior</button><button class="primary-button" id="nextStep" type="button">${state.step === steps.length - 1 ? "Completar" : "Siguiente →"}</button></div>
      </section>
    </div>`;
    $("prevStep").addEventListener("click", () => { if (state.step > 0) { state.step--; saveProgress(); renderRunner(); } });
    $("nextStep").addEventListener("click", () => { if (state.step < steps.length - 1) { state.step++; saveProgress(); renderRunner(); } else renderDone(); });
    $("openRules").addEventListener("click", renderRules);
    if ($("timerButton")) $("timerButton").addEventListener("click", startTimer);
  }
  function renderRules() {
    const markup = `<div class="rules-panel"><button class="back-link" id="backToStep" type="button">← Volver al paso</button><div><span class="eyebrow">ANTES DE COMENZAR</span><h2>Equipo</h2><ul>${state.content.equipment.map(item => `<li>${item}</li>`).join("")}</ul><h2>Normas</h2><ul>${state.content.rules.map(item => `<li>${item}</li>`).join("")}</ul></div><img src="${state.content.referenceImage}" alt="Ficha de referencia"></div>`;
    $("trainingStage").innerHTML = markup;
    $("backToStep").addEventListener("click", renderRunner);
  }
  function startTimer(event) {
    let remaining = Number(event.currentTarget.dataset.seconds);
    clearInterval(state.timer);
    const button = event.currentTarget;
    const tick = () => {
      const hours = Math.floor(remaining / 3600), minutes = Math.floor((remaining % 3600) / 60), seconds = remaining % 60;
      button.textContent = `◷ ${hours ? `${hours}:` : ""}${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
      if (remaining <= 0) { clearInterval(state.timer); button.textContent = "✓ Tiempo completado"; return; }
      remaining--;
    };
    tick(); state.timer = setInterval(tick, 1000);
  }
  function renderDone() {
    sessionStorage.removeItem("guia-progress"); updateResume();
    const evaluate = state.content.id === "unicorn-frappuccino" || state.content.id === "salsa-azul-drizzle";
    $("trainingStage").innerHTML = `<div class="done-card"><span>✓</span><small>CAPACITACIÓN COMPLETA</small><h2>${state.content.name}</h2><p>Repasaste ${routeSteps().length} pasos operativos.</p><div><button id="repeatTraining" type="button">Repetir</button>${evaluate ? '<button id="evaluateTraining" type="button">Evaluar preparación</button>' : ""}<button class="primary-button" id="newTraining" type="button">Nueva capacitación</button></div></div>`;
    $("repeatTraining").addEventListener("click", startRoute);
    $("newTraining").addEventListener("click", resetTraining);
    if ($("evaluateTraining")) $("evaluateTraining").addEventListener("click", openEvaluation);
  }

  function openEvaluation() {
    state.evaluationIndex = 0; state.evaluationScore = 0; state.evaluationPhoto = "";
    state.evaluatedPartner = localStorage.getItem("evaluated-partner") || "";
    renderEvaluationStart();
    $("evaluationDialog").showModal();
  }
  function renderEvaluationStart() {
    $("evaluationProgress").textContent = "Comenzar";
    $("evaluationStage").innerHTML = `<div class="evaluation-start"><span class="eyebrow">PASO 1</span><h2>¿A quién vas a evaluar?</h2><p>Escribe únicamente el nombre del Partner.</p><label><span>Nombre del Partner</span><input id="evaluationPartnerInput" maxlength="80" autocomplete="name" value="${state.evaluatedPartner.replace(/[&<>'"]/g,"")}" placeholder="Ej. Enrique"></label><button class="primary-button" id="startEvaluation" type="button">Comenzar cuestionario</button></div>`;
    $("startEvaluation").onclick = () => { const name=$("evaluationPartnerInput").value.trim(); if(!name){$("evaluationPartnerInput").focus();return;} state.evaluatedPartner=name;localStorage.setItem("evaluated-partner",name);renderEvaluation(); };
    $("evaluationPartnerInput").focus();
  }
  function renderEvaluation() {
    const item = unicornQuiz[state.evaluationIndex];
    if (!item) {
      const passed = state.evaluationScore >= 4;
      localStorage.setItem("unicorn-evaluation", JSON.stringify({score: state.evaluationScore, total: unicornQuiz.length, date: localDate("America/Mexico_City")}));
      $("evaluationProgress").textContent = "Resultado";
      const partner = state.evaluatedPartner || "Partner";
      const evaluatedAt = new Intl.DateTimeFormat("es-MX", {dateStyle:"long", timeStyle:"short", timeZone:"America/Mexico_City"}).format(new Date());
      localStorage.setItem("evaluated-partner", partner);
      $("evaluationStage").innerHTML = `<div class="evaluation-result"><span>${passed ? "✓" : "↻"}</span><small>${partner.toUpperCase()}</small><h2>${state.evaluationScore} de ${unicornQuiz.length}</h2><p>${passed ? "Cuestionario completo. Ahora registra la práctica." : "Repasa la receta y registra la práctica."}</p><time>${evaluatedAt}</time><div class="practice-capture"><input id="evaluationPhoto" type="file" accept="image/*" capture="environment" hidden><button class="camera-button" id="takePracticePhoto" type="button"><b>◎ Tomar foto de práctica</b><small>Abre la cámara del dispositivo</small></button><img id="evaluationPhotoPreview" alt="Evidencia de práctica" hidden></div><div><button id="retryEvaluation" type="button">Repetir</button><button class="primary-button" id="finishEvaluation" type="button">Finalizar</button></div></div>`;
      $("retryEvaluation").onclick = () => { state.evaluationIndex = 0; state.evaluationScore = 0; renderEvaluation(); };
      $("takePracticePhoto").onclick = () => $("evaluationPhoto").click();
      $("evaluationPhoto").onchange = event => { const file=event.target.files[0];if(!file)return;if(file.size>8*1024*1024){alert("La foto debe pesar menos de 8 MB.");return;}const reader=new FileReader();reader.onload=()=>{state.evaluationPhoto=reader.result;$("evaluationPhotoPreview").src=reader.result;$("evaluationPhotoPreview").hidden=false;$("takePracticePhoto").querySelector("b").textContent="✓ Foto lista";};reader.readAsDataURL(file);};
      $("finishEvaluation").onclick = () => $("evaluationDialog").close();
      return;
    }
    $("evaluationProgress").textContent = `Pregunta ${state.evaluationIndex + 1} de ${unicornQuiz.length}`;
    $("evaluationStage").innerHTML = `<div class="evaluation-question"><h2>${item.question}</h2><div class="evaluation-options">${item.options.map(option => `<button type="button" data-evaluation-answer="${option}">${option}<span>→</span></button>`).join("")}</div><p id="evaluationFeedback" aria-live="polite"></p><button class="primary-button" id="nextEvaluation" type="button" hidden>${state.evaluationIndex === unicornQuiz.length - 1 ? "Ver resultado" : "Siguiente"}</button></div>`;
    document.querySelectorAll("[data-evaluation-answer]").forEach(button => button.onclick = () => {
      const correct = button.dataset.evaluationAnswer === item.answer;
      if (correct) state.evaluationScore += 1;
      document.querySelectorAll("[data-evaluation-answer]").forEach(option => { option.disabled = true; option.classList.toggle("correct", option.dataset.evaluationAnswer === item.answer); option.classList.toggle("wrong", option === button && !correct); });
      $("evaluationFeedback").textContent = `${correct ? "Correcto. " : "Revisa. "}${item.note}`;
      $("nextEvaluation").hidden = false;
      $("nextEvaluation").focus();
    });
    $("nextEvaluation").onclick = () => { state.evaluationIndex += 1; renderEvaluation(); };
  }

  function setupPwaInstall() {
    const standalone = window.matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;
    const ios = /iphone|ipad|ipod/i.test(navigator.userAgent);
    const updateStatus = () => {
      $("installApp").textContent = standalone ? "App instalada" : "Instalar app";
      $("installApp").classList.toggle("installed", standalone);
    };
    updateStatus();
    window.addEventListener("beforeinstallprompt", event => { event.preventDefault(); state.deferredInstall = event; });
    window.addEventListener("appinstalled", () => { state.deferredInstall = null; $("installDialog").close(); $("installApp").textContent = "App instalada"; $("installApp").classList.add("installed"); announce("Aplicación instalada"); });
    $("installApp").onclick = async () => {
      if (standalone) { announce("La aplicación ya está instalada"); return; }
      if (state.deferredInstall) {
        await state.deferredInstall.prompt();
        state.deferredInstall = null;
        return;
      }
      $("installGuide").innerHTML = ios ? '<ol><li>Toca <b>Compartir</b> en Safari.</li><li>Elige <b>Agregar a inicio</b>.</li><li>Confirma con <b>Agregar</b>.</li></ol>' : '<p>Abre el menú del navegador y selecciona <b>Instalar aplicación</b> o <b>Agregar a pantalla principal</b>.</p>';
      $("confirmInstall").textContent = "Entendido";
      $("confirmInstall").onclick = () => $("installDialog").close();
      $("installDialog").showModal();
    };
  }
  function renderSearch() {
    const categories = ["Todos", ...new Set(cms.catalog.map(item => item.category))];
    $("filterRow").innerHTML = categories.map(category => `<button class="${state.filter === category ? "active" : ""}" data-filter="${category}" type="button">${category}</button>`).join("");
    document.querySelectorAll("[data-filter]").forEach(button => button.addEventListener("click", () => { state.filter = button.dataset.filter; state.subfilter = "Todas"; state.visible = 6; renderSearch(); }));
    const subcategories = state.filter === "Todos" ? [] : [...new Set(cms.catalog.filter(item => item.category === state.filter).map(item => item.subcategory))];
    $("subfilterRow").hidden = subcategories.length < 2;
    $("subfilterRow").innerHTML = ["Todas", ...subcategories].map(value => `<button class="${state.subfilter === value ? "active" : ""}" data-subfilter="${value}" type="button">${value}</button>`).join("");
    document.querySelectorAll("[data-subfilter]").forEach(button => button.addEventListener("click", () => { state.subfilter = button.dataset.subfilter; state.visible = 6; renderSearch(); }));
    const query = normalize(state.query);
    const filtered = cms.catalog.filter(item => (state.filter === "Todos" || item.category === state.filter) && (state.subfilter === "Todas" || item.subcategory === state.subfilter) && (!query || normalize(`${item.name} ${item.category} ${item.subcategory} ${item.search}`).includes(query)));
    $("resultCount").textContent = `${filtered.length} ${filtered.length === 1 ? "receta" : "recetas"}`; announce(`${filtered.length} resultados`);
    $("recipeGrid").innerHTML = filtered.slice(0, state.visible).map(item => `<article class="recipe-card"><div class="product-frame"><img loading="lazy" src="${item.productImage}" alt="${item.name}"></div><div class="recipe-copy"><small>${item.subcategory}</small><h2>${item.name}</h2><div><button class="text-button" data-reference="${item.id}" type="button">Ver receta</button>${cms.contents.some(content => content.name === item.name) ? `<button class="mini-primary" data-train="${cms.contents.find(content => content.name === item.name).id}" type="button">Practicar</button>` : ""}</div></div></article>`).join("") || `<div class="empty-state"><span>⌕</span><h2>Sin coincidencias</h2><p>Prueba con otra palabra o categoría.</p></div>`;
    $("showMore").hidden = state.visible >= filtered.length;
    document.querySelectorAll("[data-reference]").forEach(button => button.addEventListener("click", () => openReference(button.dataset.reference)));
    document.querySelectorAll("[data-train]").forEach(button => button.addEventListener("click", () => launchTraining(button.dataset.train)));
  }
  function openReference(id) {
    const item = cms.catalog.find(entry => entry.id === id);
    $("dialogProduct").src = item.productImage; $("dialogProduct").alt = item.name;
    $("dialogReference").src = item.referenceImage; $("dialogTitle").textContent = item.name;
    $("dialogCategory").textContent = `${item.category} · ${item.subcategory}`;
    const content = cms.contents.find(entry => entry.name === item.name);
    $("dialogTrain").hidden = !content;
    $("dialogTrain").onclick = () => { $("referenceDialog").close(); showView("training"); selectContent(content.id); };
    $("referenceDialog").showModal();
  }

  function resumeTraining() {
    const saved = JSON.parse(sessionStorage.getItem("guia-progress") || "null");
    const content = saved && cms.contents.find(item => item.id === saved.contentId);
    if (!content) return;
    state.content = content; state.category = content.category; state.selections = saved.selections || {};
    state.route = saved.route; state.step = Math.min(Number(saved.step || 0), Math.max(0, cms.steps.filter(item => item.route === saved.route).length - 1));
    showView("training", {reset: false});
    setTrainingHeader(content.name, "Continuaste tu capacitación guardada en este dispositivo."); renderRunner();
  }

  document.querySelectorAll("[data-view]").forEach(button => button.addEventListener("click", () => showView(button.dataset.view)));
  $("homeButton").addEventListener("click", () => showView("home"));
  $("recipeSearch").addEventListener("input", event => { state.query = event.target.value; state.visible = 6; renderSearch(); });
  $("clearSearch").addEventListener("click", () => { state.query = ""; $("recipeSearch").value = ""; renderSearch(); $("recipeSearch").focus(); });
  $("showMore").addEventListener("click", () => { state.visible += 6; renderSearch(); });
  $("closeDialog").addEventListener("click", () => $("referenceDialog").close());
  $("closeEvaluation").addEventListener("click", () => $("evaluationDialog").close());
  $("closeInstall").addEventListener("click", () => $("installDialog").close());
  $("resumeTraining").addEventListener("click", resumeTraining);
  document.addEventListener("keydown", event => {
    if (event.key === "/" && state.view === "search" && document.activeElement !== $("recipeSearch")) { event.preventDefault(); $("recipeSearch").focus(); }
  });
  document.addEventListener("error", event => {
    if (event.target.tagName !== "IMG") return;
    event.target.hidden = true; event.target.parentElement?.classList.add("image-unavailable");
  }, true);
  window.addEventListener("popstate", () => {
    const view = location.hash === "#capacitar" ? "training" : location.hash === "#recetario" ? "search" : location.hash === "#objetivos" ? "objectives" : "home";
    showView(view, {history: false, reset: view === "training" && !state.content});
  });
  $("catalogCount").textContent = cms.meta.catalogItems;
  $("moduleCount").textContent = cms.meta.trainingModules;
  updateResume();
  setupPwaInstall();
  setupPdfViewer();
  configureCampaign();
  const initialView = location.hash === "#capacitar" ? "training" : location.hash === "#recetario" ? "search" : location.hash === "#objetivos" ? "objectives" : "home";
  showView(initialView, {history: false});
  if ("serviceWorker" in navigator && location.protocol.startsWith("http")) navigator.serviceWorker.register("sw.js");
})();
