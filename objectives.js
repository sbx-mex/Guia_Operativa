(() => {
  const $ = id => document.getElementById(id);
  const KEY = "guia-objectives-v5";
  const template = window.OBJECTIVES_TEMPLATE;
  const shardCache = new Map();
  let selectedCeco = "";
  let store = null;
  let captures = loadLocal();
  let wired = false;
  let loadingCeco = "";
  let resultItems = [];
  let activeResult = -1;

  function esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[character]);
  }
  function normalize(value) {
    return String(value || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
  }
  function num(value) {
    const parsed = Number(value);
    return Number.isFinite(parsed) && parsed >= 0 ? Math.round(parsed) : 0;
  }
  function loadLocal() {
    try {
      const saved = JSON.parse(localStorage.getItem(KEY) || localStorage.getItem("guia-objectives-v4") || localStorage.getItem("guia-objectives-v3") || "{}") || {};
      selectedCeco = String(saved.selectedCeco || "");
      return saved.captures || {};
    } catch {
      return {};
    }
  }
  function save() {
    localStorage.setItem(KEY, JSON.stringify({selectedCeco, captures}));
  }
  function announce(message) {
    const region = $("statusRegion");
    if (region) region.textContent = message;
  }
  function indexStore(ceco) {
    return template.stores.find(item => item.ceco === ceco) || null;
  }
  async function loadShard(ceco) {
    const prefix = ceco.slice(0, 3);
    if (!shardCache.has(prefix)) {
      const path = template.storeDataPath.replace("{prefix}", prefix);
      shardCache.set(prefix, fetch(path).then(response => {
        if (!response.ok) throw new Error(`No se pudo cargar el paquete ${prefix}`);
        return response.json();
      }));
    }
    const data = await shardCache.get(prefix);
    return data.stores.find(item => item.ceco === ceco) || null;
  }
  async function selectStore(ceco) {
    if (!ceco || loadingCeco === ceco) return;
    selectedCeco = ceco;
    store = null;
    loadingCeco = ceco;
    save();
    renderLoading();
    try {
      const loaded = await loadShard(ceco);
      if (selectedCeco !== ceco) return;
      if (!loaded) throw new Error("Tienda no encontrada");
      store = loaded;
      $("objectiveStoreSearch").value = `${store.ceco} · ${store.name}`;
      announce(`Tienda ${store.name}, CeCo ${store.ceco}, seleccionada`);
      render();
    } catch (error) {
      if (selectedCeco === ceco) {
        selectedCeco = "";
        store = null;
        save();
        renderEmpty("No fue posible cargar la tienda. Revisa tu conexión e intenta de nuevo.");
      }
    } finally {
      if (loadingCeco === ceco) loadingCeco = "";
    }
  }
  function entry(dayId, productId) {
    const actual = template.cuts.reduce((sum, cut) => sum + cutValue(dayId, productId, cut.id), 0);
    return {goal: num(store.goals[dayId][productId]), actual};
  }
  function cutValue(dayId, productId, cutId) {
    const saved = captures[store.ceco]?.[dayId]?.[productId];
    if (saved && typeof saved === "object") return num(saved[cutId]);
    return cutId === template.cuts.at(-1).id ? num(saved) : 0;
  }
  function saveCut(dayId, productId, cutId, value) {
    captures[store.ceco] ||= {};
    captures[store.ceco][dayId] ||= {};
    const previous = captures[store.ceco][dayId][productId];
    const actuals = previous && typeof previous === "object" ? {...previous} : {[template.cuts.at(-1).id]: num(previous)};
    actuals[cutId] = num(value);
    captures[store.ceco][dayId][productId] = actuals;
    save();
  }
  function total(productId, field) {
    return template.days.reduce((sum, day) => sum + entry(day.id, productId)[field], 0);
  }
  function pct(actual, goal) {
    return goal ? Math.round(actual / goal * 100) : 0;
  }
  function reachState(actual, goal) {
    if (goal && actual >= goal) return {key:"achieved", label:"Meta lograda"};
    if (actual > 0) return {key:"progress", label:"En avance"};
    return {key:"pending", label:"Pendiente"};
  }
  function stamp() {
    return new Intl.DateTimeFormat("es-MX", {dateStyle:"long", timeStyle:"short", timeZone:template.campaign.timezone}).format(new Date());
  }
  function safeName(value) {
    return value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/gi, "_").replace(/^_|_$/g, "");
  }
  function reportFileName() {
    return `${store.ceco}_${safeName(store.name)}_Avance_Unicorn`;
  }
  function productVisual(product, print = false) {
    if (product.image) return `<img src="${esc(product.image)}" alt="${print ? esc(product.name) : ""}">`;
    return `<span class="objective-kpi-icon" aria-hidden="true">${esc(product.icon || product.name.charAt(0))}</span>`;
  }
  function findStores(query) {
    const needle = normalize(query.replace("·", " "));
    if (!needle) return [];
    return template.stores.map(item => {
      const name = normalize(item.name);
      const score = item.ceco === needle ? -1 : item.ceco.startsWith(needle) ? 0 : name.startsWith(needle) ? 1 : name.includes(needle) ? 2 : 9;
      return {item, score};
    }).filter(result => result.score < 9).sort((a, b) => a.score - b.score || Number(a.item.ceco) - Number(b.item.ceco)).slice(0, 6).map(result => result.item);
  }
  function updateActiveResult() {
    $("objectiveStoreResults").querySelectorAll("button").forEach((button, index) => {
      const active = index === activeResult;
      button.classList.toggle("active", active);
      button.setAttribute("aria-selected", String(active));
      if (active) button.scrollIntoView({block:"nearest"});
    });
  }
  function renderSearchResults(query = "") {
    if (normalize(query).length < 2) {
      resultItems = [];
      activeResult = -1;
      hideSearchResults();
      return;
    }
    resultItems = findStores(query);
    activeResult = resultItems.length ? 0 : -1;
    const results = $("objectiveStoreResults");
    results.innerHTML = resultItems.length ? resultItems.map((item, index) => `<button type="button" role="option" aria-selected="${index === 0}" data-store-ceco="${item.ceco}"><b>${item.ceco}</b><span>${esc(item.name)}</span><i>Seleccionar →</i></button>`).join("") : `<p>No encontramos esa tienda. Prueba sólo con el CeCo.</p>`;
    results.hidden = false;
    $("objectiveStoreSearch").setAttribute("aria-expanded", "true");
    results.querySelectorAll("button").forEach(button => button.addEventListener("mousedown", event => event.preventDefault()));
    results.querySelectorAll("button").forEach(button => button.addEventListener("click", () => chooseStore(button.dataset.storeCeco)));
  }
  function hideSearchResults() {
    $("objectiveStoreResults").hidden = true;
    $("objectiveStoreSearch").setAttribute("aria-expanded", "false");
  }
  function chooseStore(ceco) {
    hideSearchResults();
    selectStore(ceco);
  }
  function clearStore() {
    selectedCeco = "";
    store = null;
    save();
    $("objectiveStoreSearch").value = "";
    $("objectiveStoreSearch").focus();
    hideSearchResults();
    render();
  }
  function summary(print = false) {
    return template.products.map(product => {
      const goal = total(product.id, "goal");
      const actual = total(product.id, "actual");
      const reach = pct(actual, goal);
      const state = reachState(actual, goal);
      return `<article class="reach-${state.key}" style="--accent:${product.accent}">${productVisual(product, print)}<div><small>${esc(product.note)}</small><h2>${esc(product.name)}</h2><div class="summary-metrics"><span><b>${goal}</b>Objetivo</span><span><b>${actual}</b>Real</span><span class="reach-value"><b>${reach}%</b>${state.label}</span></div><div class="goal-bar"><i style="width:${Math.min(reach,100)}%"></i></div></div></article>`;
    }).join("");
  }
  function dayReach(dayId) {
    const completed = template.products.filter(product => {
      const value = entry(dayId, product.id);
      return value.goal > 0 && value.actual >= value.goal;
    }).length;
    return `${completed} de ${template.products.length} objetivos logrados`;
  }
  function dayReachCompact(dayId) {
    const completed = template.products.filter(product => {
      const value = entry(dayId, product.id);
      return value.goal > 0 && value.actual >= value.goal;
    }).length;
    return `${completed}/${template.products.length} logrados`;
  }
  function days() {
    return template.days.map((day, index) => {
      const goals = template.products.map(product => {
        const value = entry(day.id, product.id);
        const reach = pct(value.actual, value.goal);
        const state = reachState(value.actual, value.goal);
        return `<article class="day-goal reach-${state.key}" style="--accent:${product.accent}">${productVisual(product)}<div><small>${esc(product.name)}</small><b>Meta ${value.goal}</b><span>Real ${value.actual} · ${reach}%</span></div></article>`;
      }).join("");
      const heading = `<div class="shift-grid shift-grid-head"><b>Turno</b>${template.products.map(product => `<b>${esc(product.name)}</b>`).join("")}</div>`;
      const shifts = template.cuts.map(cut => `<div class="shift-grid shift-row"><div><b>${esc(cut.label)}</b><small>${esc(cut.time)}</small></div>${template.products.map(product => `<label><span class="sr-only">Real ${esc(product.name)} ${esc(cut.label)}</span><input aria-label="Real ${esc(product.name)}, ${esc(cut.label)}, ${esc(day.label)}" type="number" min="0" inputmode="numeric" value="${cutValue(day.id, product.id, cut.id) || ""}" placeholder="0" data-day="${day.id}" data-product="${product.id}" data-cut="${cut.id}"></label>`).join("")}</div>`).join("");
      return `<section class="objective-day" id="objective-${day.id}"><header><span>${index + 1}</span><div><small>META DIARIA + PROYECCIÓN</small><h2>${esc(day.label)}</h2></div><div class="objective-day-actions"><strong>${dayReach(day.id)}</strong><button type="button" data-share-day="${day.id}">Compartir día</button></div></header><div class="day-goals" aria-label="Metas y avance del día">${goals}</div><div class="shift-capture"><div class="shift-capture-title"><div><small>LLENADO OPCIONAL</small><b>Proyección por turno</b></div><p>Un renglón por turno. Captura sólo el real; la meta diaria no cambia.</p></div>${heading}${shifts}</div></section>`;
    }).join("");
  }
  function jump() {
    return template.days.map((day, index) => `<button type="button" data-target="objective-${day.id}"><span>${index + 1}</span><b>${esc(day.label.split(" de ")[0])}</b><small>${esc(dayReachCompact(day.id))}</small></button>`).join("");
  }
  function renderLoading() {
    $("objectiveEmpty").hidden = false;
    $("objectiveEmpty").innerHTML = `<span class="objective-loader">◎</span><h2>Cargando objetivos</h2><p>Buscando el paquete del CeCo ${esc(selectedCeco)}…</p>`;
    $("objectiveWorkspace").hidden = true;
  }
  function renderEmpty(message = "Escribe al menos 2 caracteres del CeCo o nombre. Verás máximo 6 resultados, sin listas largas.") {
    $("objectiveEmpty").hidden = false;
    $("objectiveEmpty").innerHTML = `<span>1</span><h2>Coloca tu CeCo arriba</h2><p>${esc(message)}</p><div class="objective-empty-path"><b>CeCo</b><i>→</i><b>Conoce tus objetivos</b><i>→</i><b>Mide tu alcance</b></div>`;
    $("objectiveWorkspace").hidden = true;
  }
  function render() {
    if (!$("objectiveDays")) return;
    if (selectedCeco && (!store || store.ceco !== selectedCeco)) {
      if (loadingCeco !== selectedCeco) selectStore(selectedCeco);
      return;
    }
    const ready = Boolean(store);
    $("objectiveEmpty").hidden = ready;
    $("objectiveWorkspace").hidden = !ready;
    $("printObjectives").disabled = !ready;
    $("shareObjectives").disabled = !ready;
    $("downloadObjectivePdf").hidden = !ready;
    $("previewObjectivePdf").hidden = !ready;
    $("clearObjectiveStore").hidden = !ready;
    $("objectiveStoreMeta").innerHTML = ready ? `<small>CeCo seleccionado</small><b>${store.ceco}</b><span>${esc(store.name)}</span>` : "<small>CeCo seleccionado</small><b>—</b><span>Sin tienda</span>";
    if (!ready) { renderEmpty(); return; }
    $("downloadObjectivePdf").href = store.objectivePdf;
    $("downloadObjectivePdf").download = `${store.ceco}_${safeName(store.name)}_Objetivos_Unicorn.pdf`;
    $("objectiveSummary").innerHTML = summary();
    $("objectiveDayJump").innerHTML = jump();
    $("objectiveDays").innerHTML = days();
    $("objectiveDayJump").querySelectorAll("button").forEach(button => button.onclick = () => document.getElementById(button.dataset.target).scrollIntoView({behavior:"smooth", block:"start"}));
    $("objectiveDays").querySelectorAll("input").forEach(input => input.addEventListener("change", event => {
      const {day, product, cut} = event.currentTarget.dataset;
      saveCut(day, product, cut, event.currentTarget.value);
      render();
      announce(`Proyección de ${cut} actualizada: ${event.currentTarget.value || 0}`);
    }));
    $("objectiveDays").querySelectorAll("[data-share-day]").forEach(button => button.addEventListener("click", () => shareResults(button.dataset.shareDay)));
  }
  function shareText(dayId = "") {
    const daysToShare = dayId ? template.days.filter(day => day.id === dayId) : template.days;
    const lines = [`Impulso Unicorn | ${store.name} | CeCo ${store.ceco}`];
    daysToShare.forEach(day => {
      lines.push(`\n${day.label}`);
      template.products.forEach(product => {
        const value = entry(day.id, product.id);
        const shifts = template.cuts.map(cut => `${cut.label} ${cutValue(day.id, product.id, cut.id)}`).join(" · ");
        lines.push(`${product.name}: ${shifts} | Real ${value.actual} / Meta ${value.goal} (${pct(value.actual, value.goal)}%)`);
      });
    });
    lines.push("\nAl finalizar el turno: mide tu real y comparte.");
    return lines.join("\n");
  }
  async function shareResults(dayId = "") {
    if (!store) return;
    const text = shareText(dayId);
    try {
      if (navigator.share) await navigator.share({title:`Cierre Unicorn | ${store.ceco}`, text});
      else if (navigator.clipboard) { await navigator.clipboard.writeText(text); announce("Resumen copiado. Ya puedes compartirlo."); }
      else window.prompt("Copia este cierre", text);
    } catch (error) {
      if (error.name !== "AbortError") window.prompt("Copia este cierre", text);
    }
  }
  function report() {
    const daily = template.days.map(day => `<tr><th>${esc(day.label)}</th>${template.products.map(product => {const value=entry(day.id,product.id),state=reachState(value.actual,value.goal);return `<td class="reach-cell reach-${state.key}">Meta <b>${value.goal}</b> · Real <b>${value.actual}</b> · <b>${pct(value.actual,value.goal)}%</b></td>`;}).join("")}</tr>`).join("");
    const shifts = template.days.map(day => template.cuts.map((cut, index) => `<tr>${index === 0 ? `<th rowspan="${template.cuts.length}">${esc(day.label)}</th>` : ""}<td><b>${esc(cut.label)}</b><small>${esc(cut.time)}</small></td>${template.products.map(product => `<td>${cutValue(day.id,product.id,cut.id) || ""}</td>`).join("")}</tr>`).join("")).join("");
    return `<div class="print-cover"><span>IMPULSO UNICORN</span><h1>Objetivos y proyección</h1><p>15, 16 y 17 de agosto</p><div><b>${esc(store.name)} | CeCo ${store.ceco}</b><small>Actualización ${esc(template.campaign.operationsUpdate)} | <b>Creado ${esc(stamp())}</b></small></div></div><div class="print-flow"><span><b>1. CONOCE</b>La meta permanece por día</span><span><b>2. PROYECTA</b>Un renglón opcional por turno</span><span><b>3. MIDE</b>Calcula el alcance</span></div><div class="print-summary">${summary(true)}</div><table class="print-daily"><thead><tr><th>Día</th>${template.products.map(product => `<th>${esc(product.name)} · Meta / Real / Alcance</th>`).join("")}</tr></thead><tbody>${daily}</tbody></table><table class="print-shifts"><thead><tr><th>Día</th><th>Turno</th>${template.products.map(product => `<th>Real ${esc(product.name)}</th>`).join("")}</tr></thead><tbody>${shifts}</tbody></table><div class="print-legend"><b>La meta diaria no cambia · La proyección por turno es opcional</b><span class="reach-achieved">Verde: logrado</span><span class="reach-progress">Amarillo: en avance</span><span class="reach-pending">Gris: pendiente</span></div><footer>Puedes exportar sin llenar · Proyecta por turno y comparte el cierre</footer>`;
  }
  function printReport() {
    if (!store) return;
    $("objectivePrintReport").innerHTML = report();
    document.body.classList.add("printing-objectives");
    const originalTitle = document.title;
    document.title = reportFileName();
    const done = () => {document.body.classList.remove("printing-objectives"); document.title = originalTitle;};
    window.addEventListener("afterprint", done, {once:true});
    window.print();
    setTimeout(done, 2000);
  }
  function wire() {
    if (wired) return;
    wired = true;
    const search = $("objectiveStoreSearch");
    search.addEventListener("focus", () => {if (store) search.select(); if (normalize(search.value).length >= 2 && !store) renderSearchResults(search.value);});
    search.addEventListener("input", event => renderSearchResults(event.target.value));
    search.addEventListener("blur", () => setTimeout(hideSearchResults, 120));
    search.addEventListener("keydown", event => {
      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        event.preventDefault();
        if ($("objectiveStoreResults").hidden) renderSearchResults(search.value);
        activeResult = Math.max(0, Math.min(resultItems.length - 1, activeResult + (event.key === "ArrowDown" ? 1 : -1)));
        updateActiveResult();
      } else if (event.key === "Enter" && resultItems[activeResult]) {
        event.preventDefault(); chooseStore(resultItems[activeResult].ceco);
      } else if (event.key === "Escape") hideSearchResults();
    });
    $("clearObjectiveStore").onclick = clearStore;
    $("previewObjectivePdf").onclick = () => {
      if (!store) return;
      const filename = `${store.ceco}_${safeName(store.name)}_Objetivos_Unicorn.pdf`;
      window.PdfViewer?.open(store.objectivePdf, `Objetivos | ${store.ceco} ${store.name}`, filename);
    };
    $("printObjectives").onclick = printReport;
    $("shareObjectives").onclick = () => shareResults();
    if (selectedCeco && indexStore(selectedCeco)) selectStore(selectedCeco); else render();
  }
  window.Objectives = {render() {wire(); render();}};
})();
