(() => {
  const $ = id => document.getElementById(id);
  const KEY = "guia-objectives-v1";
  let model = normalize(loadLocal() || window.OBJECTIVES_TEMPLATE);
  let wired = false;

  function clone(value) { return JSON.parse(JSON.stringify(value)); }
  function text(value) { return String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[char]); }
  function number(value) { const parsed = Number(value); return Number.isFinite(parsed) && parsed >= 0 ? Math.round(parsed) : 0; }
  function normalize(source) {
    const base = clone(source || window.OBJECTIVES_TEMPLATE);
    base.schemaVersion = 1;
    base.store ||= {ceco:"", name:""}; base.values ||= {};
    base.days.forEach(day => { base.values[day.id] ||= {}; base.products.forEach(product => { base.values[day.id][product.id] ||= {goal:0, actual:0}; }); });
    return base;
  }
  function loadLocal() { try { return JSON.parse(localStorage.getItem(KEY)); } catch { return null; } }
  function save() { localStorage.setItem(KEY, JSON.stringify(model)); }
  function total(productId, field) { return model.days.reduce((sum, day) => sum + number(model.values[day.id][productId][field]), 0); }
  function progress(actual, goal) { return goal ? Math.round(actual / goal * 100) : 0; }
  function timestamp() { return new Intl.DateTimeFormat("es-MX", {dateStyle:"long", timeStyle:"short", timeZone:model.campaign.timezone}).format(new Date()); }

  function summaryMarkup() {
    return model.products.map(product => {
      const goal = total(product.id, "goal"), actual = total(product.id, "actual"), pct = progress(actual, goal);
      return `<article style="--accent:${product.accent}"><img src="${text(product.image)}" alt="" style="object-position:${text(product.focus || "center")}"><div><small>${text(product.note)}</small><h2>${text(product.name)}</h2><div class="summary-metrics"><span><b>${goal}</b>Meta</span><span><b>${actual}</b>Real</span><span><b>${pct}%</b>Avance</span></div><div class="goal-bar"><i style="width:${Math.min(pct,100)}%"></i></div></div></article>`;
    }).join("");
  }
  function daysMarkup() {
    return model.days.map((day, dayIndex) => `<section class="objective-day"><header><span>${dayIndex + 1}</span><div><small>${dayIndex === 0 ? "ANTICIPA" : "ACTUALIZA"}</small><h2>${text(day.label)}</h2></div></header><div class="day-products">${model.products.map(product => {
      const value = model.values[day.id][product.id];
      return `<article><div class="day-product-name"><i style="background:${product.accent}"></i><b>${text(product.name)}</b></div><label><span>Objetivo</span><input type="number" min="0" step="1" inputmode="numeric" value="${number(value.goal) || ""}" placeholder="0" data-day="${day.id}" data-product="${product.id}" data-field="goal"></label><label><span>Real vendido</span><input type="number" min="0" step="1" inputmode="numeric" value="${number(value.actual) || ""}" placeholder="0" data-day="${day.id}" data-product="${product.id}" data-field="actual"></label><div class="day-progress"><b>${progress(number(value.actual),number(value.goal))}%</b><small>avance</small></div></article>`;
    }).join("")}</div></section>`).join("");
  }
  function render() {
    if (!$("objectiveDays")) return;
    $("objectiveCeco").value = model.store.ceco || ""; $("objectiveStore").value = model.store.name || "";
    $("objectiveSummary").innerHTML = summaryMarkup(); $("objectiveDays").innerHTML = daysMarkup();
    $("objectiveDays").querySelectorAll("input").forEach(input => input.addEventListener("input", event => {
      const {day, product, field} = event.currentTarget.dataset;
      model.values[day][product][field] = number(event.currentTarget.value); save(); render();
    }));
  }
  function validate(source) {
    if (!source || source.schemaVersion !== 1 || !Array.isArray(source.products) || !Array.isArray(source.days)) throw new Error("El JSON no corresponde al tablero de objetivos.");
    if (!source.products.length || !source.days.length) throw new Error("El JSON debe incluir productos y días.");
    const ids = source.products.map(item => item.id); if (new Set(ids).size !== ids.length) throw new Error("Hay productos duplicados en el JSON.");
    return normalize(source);
  }
  function download(name, body, type) {
    const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([body], {type})); link.download = name; link.click(); setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  }
  function reportMarkup() {
    const headers = model.days.map(day => `<th colspan="3">${text(day.label)}</th>`).join("");
    const subheaders = model.days.map(() => "<th>Objetivo</th><th>Real</th><th>Avance</th>").join("");
    const rows = model.products.map(product => `<tr><th><span style="color:${product.accent}">${text(product.name)}</span><small>${text(product.note)}</small></th>${model.days.map(day => { const v=model.values[day.id][product.id]; return `<td>${number(v.goal)}</td><td>${number(v.actual)}</td><td>${progress(number(v.actual),number(v.goal))}%</td>`; }).join("")}<td>${total(product.id,"goal")}</td><td>${total(product.id,"actual")}</td><td>${progress(total(product.id,"actual"),total(product.id,"goal"))}%</td></tr>`).join("");
    return `<div class="print-cover"><span>DASH DE VENTAS</span><h1>Logro de objetivos</h1><p>${text(model.campaign.name)}</p><div><b>${text(model.store.name || "Tienda sin nombre")}</b><small>${model.store.ceco ? `CeCo ${text(model.store.ceco)} · ` : ""}Actualizado ${text(timestamp())}</small></div></div><div class="print-summary">${summaryMarkup()}</div><table><thead><tr><th rowspan="2">Producto</th>${headers}<th colspan="3">Total campaña</th></tr><tr>${subheaders}<th>Objetivo</th><th>Real</th><th>Avance</th></tr></thead><tbody>${rows}</tbody></table><footer>Preparar · practicar · medir · compartir</footer>`;
  }
  function printReport() {
    if (!model.store.name.trim()) { $("objectiveStore").focus(); alert("Escribe el nombre de la tienda antes de exportar."); return; }
    $("objectivePrintReport").innerHTML = reportMarkup(); document.body.classList.add("printing-objectives");
    const done = () => document.body.classList.remove("printing-objectives"); window.addEventListener("afterprint", done, {once:true}); window.print(); setTimeout(done, 2000);
  }
  async function share() {
    const message = `${model.campaign.name}\n${model.store.name || "Tienda"}\nUnicorn: ${total("unicorn","actual")}/${total("unicorn","goal")} (${progress(total("unicorn","actual"),total("unicorn","goal"))}%)\nCake Pop: ${total("cake-pop","actual")}/${total("cake-pop","goal")} (${progress(total("cake-pop","actual"),total("cake-pop","goal"))}%)\nActualizado: ${timestamp()}`;
    if (navigator.share) { try { await navigator.share({title:"Avance Unicorn", text:message}); return; } catch (error) { if (error.name === "AbortError") return; } }
    await navigator.clipboard.writeText(message); alert("Resumen copiado. Abre Workvivo y pégalo en tu publicación.");
  }
  function wire() {
    if (wired) return; wired = true;
    $("objectiveCeco").addEventListener("input", event => { model.store.ceco=event.target.value.trim(); save(); });
    $("objectiveStore").addEventListener("input", event => { model.store.name=event.target.value.trim(); save(); });
    $("loadObjectivesJson").onclick = () => $("objectivesJsonFile").click();
    $("objectivesJsonFile").onchange = async event => { try { model=validate(JSON.parse(await event.target.files[0].text())); save(); render(); alert("Objetivos cargados correctamente."); } catch(error) { alert(error.message); } finally { event.target.value=""; } };
    $("downloadObjectivesJson").onclick = () => download(`objetivos-${model.store.ceco || "tienda"}.json`, JSON.stringify({...model, exportedAt:new Date().toISOString()}, null, 2), "application/json");
    $("resetObjectives").onclick = () => { if (confirm("¿Limpiar metas y reales capturados en este dispositivo?")) { model=normalize(window.OBJECTIVES_TEMPLATE); save(); render(); } };
    $("printObjectives").onclick = printReport; $("shareObjectives").onclick = share;
  }
  window.Objectives = {render(){ wire(); render(); }};
})();
