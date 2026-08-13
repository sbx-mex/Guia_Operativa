(() => {
  const cms = window.TRAINING_CMS;
  const $ = id => document.getElementById(id);
  const state = {
    view: "home", category: "", content: null, selections: {}, selectorIndex: 0,
    route: "", step: 0, filter: "Todos", subfilter: "Todas", query: "", visible: 6, timer: null,
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
    const hash = view === "training" ? "#capacitar" : view === "search" ? "#recetario" : "#inicio";
    if (options.history !== false && location.hash !== hash) history.pushState({view}, "", hash);
    announce(view === "home" ? "Inicio" : view === "training" ? "Capacitación" : "Buscador de recetas");
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
    const contents = cms.contents.filter(item => item.category === category);
    $("trainingStage").innerHTML = `<button class="back-link inline" id="changeArea" type="button">← Cambiar área</button>
      <div class="training-card-grid">${contents.map(item => `<button class="training-card" data-content="${item.id}" type="button"><img src="${item.productImage}" alt="${item.name}"><span><small>${item.subcategory}</small><b>${item.name}</b><em>${item.description}</em><i>Practicar →</i></span></button>`).join("")}</div>`;
    $("changeArea").addEventListener("click", resetTraining);
    document.querySelectorAll("[data-content]").forEach(button => button.addEventListener("click", () => selectContent(button.dataset.content)));
  }
  function selectContent(id) {
    state.content = cms.contents.find(item => item.id === id);
    state.selections = {}; state.selectorIndex = 0;
    if (!state.content.selectors.length) { state.route = state.content.routes.default; startRoute(); return; }
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
    $("trainingStage").innerHTML = `<div class="done-card"><span>✓</span><small>CAPACITACIÓN COMPLETA</small><h2>${state.content.name}</h2><p>Repasaste ${routeSteps().length} pasos operativos.</p><div><button id="repeatTraining" type="button">Repetir</button><button class="primary-button" id="newTraining" type="button">Nueva capacitación</button></div></div>`;
    $("repeatTraining").addEventListener("click", startRoute);
    $("newTraining").addEventListener("click", resetTraining);
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
    document.querySelectorAll("[data-train]").forEach(button => button.addEventListener("click", () => { showView("training"); selectContent(button.dataset.train); }));
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
  $("resumeTraining").addEventListener("click", resumeTraining);
  document.addEventListener("keydown", event => {
    if (event.key === "/" && state.view === "search" && document.activeElement !== $("recipeSearch")) { event.preventDefault(); $("recipeSearch").focus(); }
  });
  document.addEventListener("error", event => {
    if (event.target.tagName !== "IMG") return;
    event.target.hidden = true; event.target.parentElement?.classList.add("image-unavailable");
  }, true);
  window.addEventListener("popstate", () => {
    const view = location.hash === "#capacitar" ? "training" : location.hash === "#recetario" ? "search" : "home";
    showView(view, {history: false, reset: view === "training" && !state.content});
  });
  $("catalogCount").textContent = cms.meta.catalogItems;
  $("moduleCount").textContent = cms.meta.trainingModules;
  updateResume();
  const initialView = location.hash === "#capacitar" ? "training" : location.hash === "#recetario" ? "search" : "home";
  showView(initialView, {history: false});
  if ("serviceWorker" in navigator && location.protocol.startsWith("http")) navigator.serviceWorker.register("sw.js");
})();
