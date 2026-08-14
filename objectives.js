(() => {
  const $ = id => document.getElementById(id);
  const KEY = "guia-objectives-v3";
  const template = window.OBJECTIVES_TEMPLATE;
  let selectedCeco = "";
  let captures = loadLocal();
  let wired = false;

  function esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[character]);
  }
  function num(value) {
    const parsed = Number(value);
    return Number.isFinite(parsed) && parsed >= 0 ? Math.round(parsed) : 0;
  }
  function loadLocal() {
    try {
      const saved = JSON.parse(localStorage.getItem(KEY)) || {};
      selectedCeco = String(saved.selectedCeco || "");
      return saved.captures || {};
    } catch {
      return {};
    }
  }
  function save() {
    localStorage.setItem(KEY, JSON.stringify({selectedCeco, captures}));
  }
  function currentStore() {
    return template.stores.find(store => store.ceco === selectedCeco) || null;
  }
  function entry(store, dayId, productId) {
    const actual = num(captures[store.ceco]?.[dayId]?.[productId]);
    return {goal: num(store.goals[dayId][productId]), actual};
  }
  function total(store, productId, field) {
    return template.days.reduce((sum, day) => sum + entry(store, day.id, productId)[field], 0);
  }
  function pct(actual, goal) {
    return goal ? Math.round(actual / goal * 100) : 0;
  }
  function status(actual, goal) {
    if (!actual) return "Pendiente";
    return pct(actual, goal) >= 100 ? "Meta lograda" : "En avance";
  }
  function stamp() {
    return new Intl.DateTimeFormat("es-MX", {dateStyle:"long", timeStyle:"short", timeZone:template.campaign.timezone}).format(new Date());
  }
  function reportFileName(store) {
    const safe = store.name.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/gi, "_").replace(/^_|_$/g, "");
    return `${store.ceco}_${safe}_Avance_Unicorn`;
  }
  function productVisual(product) {
    if (product.image) return `<img src="${esc(product.image)}" alt="">`;
    return `<span class="objective-kpi-icon" aria-hidden="true">${esc(product.icon || "◎")}</span>`;
  }
  function storeOptions() {
    return template.stores.map(store => `<option value="${esc(store.ceco)}">${esc(store.ceco)} · ${esc(store.name)}</option>`).join("");
  }
  function summary(store) {
    return template.products.map(product => {
      const goal = total(store, product.id, "goal");
      const actual = total(store, product.id, "actual");
      const reach = pct(actual, goal);
      return `<article style="--accent:${product.accent}">${productVisual(product)}<div><small>${esc(product.note)}</small><h2>${esc(product.name)}</h2><div class="summary-metrics"><span><b>${goal}</b>Objetivo</span><span><b>${actual}</b>Real</span><span><b>${reach}%</b>Alcance</span></div><div class="goal-bar"><i style="width:${Math.min(reach,100)}%"></i></div></div></article>`;
    }).join("");
  }
  function dayReach(store, dayId) {
    const completed = template.products.filter(product => {
      const value = entry(store, dayId, product.id);
      return value.goal > 0 && value.actual >= value.goal;
    }).length;
    return `${completed} de ${template.products.length} objetivos logrados`;
  }
  function days(store) {
    return template.days.map((day, index) => `<section class="objective-day" id="objective-${day.id}"><header><span>${index + 1}</span><div><small>CAPTURA DEL DÍA</small><h2>${esc(day.label)}</h2></div><strong>${dayReach(store, day.id)}</strong></header><div class="day-products">${template.products.map(product => {
      const value = entry(store, day.id, product.id);
      const reach = pct(value.actual, value.goal);
      return `<article><div class="day-product-name">${productVisual(product)}<i style="background:${product.accent}"></i><span><b>${esc(product.name)}</b><small>${esc(product.unit)}</small></span></div><label class="goal-field"><span>Objetivo del día</span><output>${value.goal}</output></label><label><span>Real del día</span><input aria-label="Real ${esc(product.name)} ${esc(day.label)}" type="number" min="0" inputmode="numeric" value="${value.actual || ""}" placeholder="0" data-day="${day.id}" data-product="${product.id}"></label><div class="day-progress"><b>${reach}%</b><small>${status(value.actual, value.goal)}</small></div></article>`;
    }).join("")}</div></section>`).join("");
  }
  function jump(store) {
    return template.days.map((day, index) => `<button type="button" data-target="objective-${day.id}"><span>${index + 1}</span><b>${esc(day.label.split(" de ")[0])}</b><small>${esc(dayReach(store, day.id))}</small></button>`).join("");
  }
  function render() {
    if (!$("objectiveDays")) return;
    const store = currentStore();
    $("objectiveStore").value = store?.ceco || "";
    $("objectiveEmpty").hidden = Boolean(store);
    $("objectiveWorkspace").hidden = !store;
    $("printObjectives").disabled = !store;
    $("downloadObjectivePdf").hidden = !store;
    $("objectiveStoreMeta").innerHTML = store ? `<small>CC seleccionado</small><b>${esc(store.ceco)}</b><span>${esc(store.name)}</span>` : "<small>CC</small><b>—</b>";
    if (!store) return;
    $("downloadObjectivePdf").href = store.objectivePdf;
    $("downloadObjectivePdf").download = `${store.ceco}_${store.name}_Objetivos_Unicorn.pdf`;
    $("objectiveSummary").innerHTML = summary(store);
    $("objectiveDayJump").innerHTML = jump(store);
    $("objectiveDays").innerHTML = days(store);
    $("objectiveDayJump").querySelectorAll("button").forEach(button => button.onclick = () => document.getElementById(button.dataset.target).scrollIntoView({behavior:"smooth", block:"start"}));
    $("objectiveDays").querySelectorAll("input").forEach(input => input.addEventListener("input", event => {
      const {day, product} = event.currentTarget.dataset;
      captures[store.ceco] ||= {};
      captures[store.ceco][day] ||= {};
      captures[store.ceco][day][product] = num(event.currentTarget.value);
      save();
      render();
      const next = document.querySelector(`[data-day="${day}"][data-product="${product}"]`);
      next?.focus();
    }));
  }
  function report(store) {
    const heads = template.days.map(day => `<th colspan="3">${esc(day.label)}</th>`).join("");
    const subs = template.days.map(() => "<th>Objetivo</th><th>Real</th><th>Alcance</th>").join("");
    const rows = template.products.map(product => `<tr><th><span style="color:${product.accent}">${esc(product.name)}</span><small>${esc(product.note)}</small></th>${template.days.map(day => {const value=entry(store,day.id,product.id);return `<td>${value.goal}</td><td>${value.actual}</td><td>${pct(value.actual,value.goal)}%</td>`;}).join("")}<td>${total(store,product.id,"goal")}</td><td>${total(store,product.id,"actual")}</td><td>${pct(total(store,product.id,"actual"),total(store,product.id,"goal"))}%</td></tr>`).join("");
    return `<div class="print-cover"><span>JUNTÉMONOS MÁS · PREPARÉMONOS MÁS</span><h1>Objetivos y avance</h1><p>15, 16 y 17 de agosto</p><div><b>${esc(store.name)} · CC ${esc(store.ceco)}</b><small>Voz de Operaciones · ${esc(template.campaign.operationsUpdate)} · Exportado ${esc(stamp())}</small></div></div><div class="print-summary">${summary(store)}</div><table><thead><tr><th rowspan="2">Indicador</th>${heads}<th colspan="3">Acumulado</th></tr><tr>${subs}<th>Objetivo</th><th>Real</th><th>Alcance</th></tr></thead><tbody>${rows}</tbody></table><footer>Diseñado: Jorge Alcantar Aguiar &amp; Enrique César Flores</footer>`;
  }
  function printReport() {
    const store = currentStore();
    if (!store) return;
    $("objectivePrintReport").innerHTML = report(store);
    document.body.classList.add("printing-objectives");
    const originalTitle = document.title;
    document.title = reportFileName(store);
    const done = () => {document.body.classList.remove("printing-objectives"); document.title = originalTitle;};
    window.addEventListener("afterprint", done, {once:true});
    window.print();
    setTimeout(done, 2000);
  }
  function wire() {
    if (wired) return;
    wired = true;
    $("objectiveStore").insertAdjacentHTML("beforeend", storeOptions());
    $("objectiveStore").addEventListener("change", event => {selectedCeco = event.target.value; save(); render();});
    $("printObjectives").onclick = printReport;
  }
  window.Objectives = {render() {wire(); render();}};
})();
