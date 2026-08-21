(() => {
  "use strict";
  const cms = window.GUIDE_CMS;
  if (!cms) throw new Error("No se cargó data/content.js");
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[char]));
  const normalize = value => String(value || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  const iconMap = {coffee:"☕",milk:"◒",steam:"≋",pour:"↘",pump:"●",ice:"◇",blend:"↻",finish:"✓",clean:"✦",measure:"▤",shake:"↕",check:"✓",timer:"◷"};
  const categoryCopy = {
    Bebidas: ["Bebidas CORE", "Practica calientes, heladas, Frappuccino, Refreshers y proteína."],
    Procesos: ["Bases CORE", "Domina VSC, leche y Cold Foam de proteína, y otras bases."],
    Alimentos: ["Alimentos", "Aprende preensamble, ensamble, conservación y entrega."],
  };
  const state = {view:"home",category:"",content:null,selections:{},selectorIndex:0,route:"",step:0,filter:"Todos",subfilter:"Todas",query:"",visible:12,timer:null,deferredInstall:null};

  function announce(message) { $("statusRegion").textContent = message; }
  function saveProgress() {
    if (!state.content || !state.route) return;
    sessionStorage.setItem("guia-core-progress", JSON.stringify({contentId:state.content.id,selections:state.selections,route:state.route,step:state.step}));
    updateResume();
  }
  function updateResume() {
    const saved = JSON.parse(sessionStorage.getItem("guia-core-progress") || "null");
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
    const hash = view === "training" ? "#practicar" : view === "search" ? "#biblioteca" : "#inicio";
    if (options.history !== false && location.hash !== hash) history.pushState({view}, "", hash);
    announce(view === "home" ? "Inicio" : view === "training" ? "Práctica guiada" : "Biblioteca CORE");
    window.scrollTo({top:0,behavior:"smooth"});
  }
  function trail() {
    const parts = [];
    if (state.category) parts.push(state.category);
    if (state.content) parts.push(state.content.name);
    Object.entries(state.selections).forEach(([key,value]) => {
      const selector = state.content?.selectors.find(item => item.id === key);
      parts.push(`${selector?.label}: ${cms.labels[value] || value}`);
    });
    $("selectionTrail").innerHTML = parts.map((part,index) => `<span>${index + 1}</span><b>${esc(part)}</b>`).join("");
  }
  function setTrainingHeader(title, intro) { $("trainingHeading").textContent=title;$("trainingIntro").textContent=intro;trail(); }
  function resetTraining() {
    Object.assign(state,{category:"",content:null,selections:{},selectorIndex:0,route:"",step:0});
    setTrainingHeader("Elige un área","Comienza por el tipo de preparación.");
    $("trainingStage").innerHTML = `<div class="area-grid">${Object.entries(categoryCopy).map(([category,copy]) => `<button class="area-card" data-category="${category}" type="button"><span>${category === "Bebidas" ? "☕" : category === "Procesos" ? "↻" : "▱"}</span><b>${category}</b><small>${esc(copy[1])}</small><i>Continuar →</i></button>`).join("")}</div>`;
    document.querySelectorAll("[data-category]").forEach(button => button.onclick=()=>selectCategory(button.dataset.category));
  }
  function selectCategory(category) {
    state.category=category;setTrainingHeader(...categoryCopy[category]);
    const contents=cms.contents.filter(item=>item.category===category).sort((a,b)=>a.subcategory.localeCompare(b.subcategory,"es")||a.name.localeCompare(b.name,"es"));
    const groups=contents.reduce((acc,item)=>((acc[item.subcategory] ||= []).push(item),acc),{});
    $("trainingStage").innerHTML=`<button class="back-link" id="changeArea" type="button">← Cambiar área</button>${Object.entries(groups).map(([group,items])=>`<section class="content-group"><header><h2>${esc(group)}</h2><span>${items.length}</span></header><div class="training-card-grid">${items.map(item=>`<button class="training-card" data-content="${item.id}" type="button"><img loading="lazy" src="${item.productImage}" alt=""><span><small>${esc(item.subcategory)}</small><b>${esc(item.name)}</b><em>${esc(item.description)}</em><i>Practicar →</i></span></button>`).join("")}</div></section>`).join("")}`;
    $("changeArea").onclick=resetTraining;document.querySelectorAll("[data-content]").forEach(button=>button.onclick=()=>selectContent(button.dataset.content));
  }
  function selectContent(id) {
    state.content=cms.contents.find(item=>item.id===id);state.selections={};state.selectorIndex=0;
    if(!state.content.selectors.length){state.route=state.content.routes.default;return startRoute();}renderSelector();
  }
  function renderSelector() {
    const selector=state.content.selectors[state.selectorIndex];
    setTrainingHeader(`Elige ${selector.label.toLowerCase()}`,`Sólo se muestran opciones disponibles para ${state.content.name}.`);
    $("trainingStage").innerHTML=`<div class="config-layout"><div class="config-product"><img src="${state.content.productImage}" alt="${esc(state.content.name)}"><small>${esc(state.content.subcategory)}</small><h2>${esc(state.content.name)}</h2></div><div class="option-panel"><span class="step-kicker">CONFIGURA ANTES DE INICIAR</span><h2>${esc(selector.label)}</h2><p>La cantidad se resaltará de acuerdo con esta selección.</p><div class="option-grid">${selector.options.map(option=>`<button data-option="${option}" type="button"><b>${esc(cms.labels[option]||option)}</b><span>→</span></button>`).join("")}</div></div></div>`;
    document.querySelectorAll("[data-option]").forEach(button=>button.onclick=()=>{state.selections[selector.id]=button.dataset.option;state.selectorIndex++;state.selectorIndex<state.content.selectors.length?renderSelector():resolveRoute();});
  }
  function resolveRoute() {
    const key=state.content.selectors.map(selector=>`${selector.id}=${state.selections[selector.id]}`).join("|");state.route=state.content.routes[key];
    if(!state.route)throw new Error(`Ruta no encontrada: ${key}`);startRoute();
  }
  function routeSteps(){return cms.steps.filter(step=>step.route===state.route).sort((a,b)=>a.order-b.order);}
  function valueFor(step){
    const entries=Object.fromEntries(String(step.values||"").split("|").filter(Boolean).map(pair=>{const at=pair.indexOf("=");return[pair.slice(0,at),pair.slice(at+1)];}));
    const selected=state.selections.size||state.selections.batch;return entries[selected]||entries.TODOS||"";
  }
  function startRoute(){state.step=0;saveProgress();setTrainingHeader(state.content.name,"Observa, ejecuta y valida antes de avanzar.");renderRunner();}
  function renderRunner(){
    const steps=routeSteps(),current=steps[state.step],progress=Math.round(((state.step+1)/steps.length)*100),visual=current.media||state.content.productImage;
    $("trainingStage").innerHTML=`<div class="runner"><aside class="runner-visual"><span>${current.media?"TÉCNICA CORE":"RESULTADO ESPERADO"}</span><div class="visual-frame"><img src="${visual}" alt="${esc(current.media?current.title:state.content.name)}"></div><h2>${esc(state.content.name)}</h2><div class="visual-actions"><button id="openRecipe" type="button">Ver ficha completa</button><button id="openRules" type="button">Equipo y control</button></div></aside><section class="runner-main"><div class="progress-meta"><b>Paso ${state.step+1} de ${steps.length}</b><span>${progress}%</span></div><div class="progress-line"><span style="width:${progress}%"></span></div><div class="milestones">${steps.map((item,index)=>`<button class="${index<state.step?"done":index===state.step?"active":""}" data-jump="${index}" type="button" aria-label="Ir al paso ${index+1}"><i>${index<state.step?"✓":index+1}</i><b>${esc(item.stage)}</b></button>`).join("")}</div><article class="step-card"><div class="step-top"><span class="step-icon">${iconMap[current.icon]||"•"}</span><span class="step-kicker">${esc(current.stage)}</span></div><h2>${esc(current.title)}</h2><p>${esc(current.detail)}</p>${valueFor(current)?`<div class="measure"><span>${esc(Object.values(state.selections).map(value=>cms.labels[value]||value).join(" · ")||"CANTIDAD CLAVE")}</span><strong>${esc(valueFor(current))}</strong></div>`:""}${current.timer?`<button class="timer-button" id="timerButton" data-seconds="${current.timer}" type="button">◷ Iniciar temporizador</button>`:""}</article><details class="reference-dock"><summary>Comparar con la ficha de receta</summary><img src="${state.content.referenceImage}" alt="Ficha de ${esc(state.content.name)}"></details><div class="runner-actions"><button id="prevStep" type="button" ${state.step===0?"disabled":""}>← Anterior</button><button class="primary-button" id="nextStep" type="button">${state.step===steps.length-1?"Completar ✓":"Siguiente →"}</button></div></section></div>`;
    $("prevStep").onclick=()=>{if(state.step>0){state.step--;saveProgress();renderRunner();}};$("nextStep").onclick=()=>{if(state.step<steps.length-1){state.step++;saveProgress();renderRunner();}else renderDone();};$("openRecipe").onclick=()=>openReference(state.content.id);$("openRules").onclick=renderRules;document.querySelectorAll("[data-jump]").forEach(button=>button.onclick=()=>{state.step=Number(button.dataset.jump);saveProgress();renderRunner();});if($("timerButton"))$("timerButton").onclick=startTimer;
  }
  function renderRules(){
    $("trainingStage").innerHTML=`<div class="rules-panel"><button class="back-link" id="backToStep" type="button">← Volver al paso</button><section><span class="eyebrow">ANTES DE COMENZAR</span><h2>Equipo</h2><ul>${state.content.equipment.map(item=>`<li>${esc(item)}</li>`).join("")}</ul><h2>Puntos de control</h2><ul>${state.content.rules.map(item=>`<li>${esc(item)}</li>`).join("")}</ul></section><img src="${state.content.referenceImage}" alt="Ficha de referencia"></div>`;$("backToStep").onclick=renderRunner;
  }
  function startTimer(event){let remaining=Number(event.currentTarget.dataset.seconds);clearInterval(state.timer);const button=event.currentTarget;const tick=()=>{const h=Math.floor(remaining/3600),m=Math.floor((remaining%3600)/60),s=remaining%60;button.textContent=`◷ ${h?`${h}:`:""}${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;if(remaining--<=0){clearInterval(state.timer);button.textContent="✓ Tiempo completado";}};tick();state.timer=setInterval(tick,1000);}
  function renderDone(){sessionStorage.removeItem("guia-core-progress");updateResume();$("trainingStage").innerHTML=`<div class="done-card"><span>✓</span><small>PRÁCTICA COMPLETA</small><h2>${esc(state.content.name)}</h2><p>Repasaste ${routeSteps().length} pasos con apoyo de la ficha original.</p><div><button id="repeatTraining" type="button">Repetir</button><button class="primary-button" id="newTraining" type="button">Elegir otra</button></div></div>`;$("repeatTraining").onclick=startRoute;$("newTraining").onclick=resetTraining;}
  function renderSearch(){
    const categories=["Todos",...new Set(cms.catalog.map(item=>item.category))];
    $("filterRow").innerHTML=categories.map(category=>`<button class="${state.filter===category?"active":""}" data-filter="${category}" type="button">${category}<small>${category==="Todos"?cms.catalog.length:cms.catalog.filter(item=>item.category===category).length}</small></button>`).join("");document.querySelectorAll("[data-filter]").forEach(button=>button.onclick=()=>{state.filter=button.dataset.filter;state.subfilter="Todas";state.visible=12;renderSearch();});
    const subcategories=state.filter==="Todos"?[...new Set(cms.catalog.map(item=>item.subcategory))]:[...new Set(cms.catalog.filter(item=>item.category===state.filter).map(item=>item.subcategory))];$("subfilterRow").innerHTML=["Todas",...subcategories].map(value=>`<button class="${state.subfilter===value?"active":""}" data-subfilter="${esc(value)}" type="button">${esc(value)}</button>`).join("");document.querySelectorAll("[data-subfilter]").forEach(button=>button.onclick=()=>{state.subfilter=button.dataset.subfilter;state.visible=12;renderSearch();});
    const terms=normalize(state.query).split(" ").filter(Boolean);const filtered=cms.catalog.filter(item=>(state.filter==="Todos"||item.category===state.filter)&&(state.subfilter==="Todas"||item.subcategory===state.subfilter)&&terms.every(term=>normalize(`${item.name} ${item.category} ${item.subcategory}`).includes(term))).sort((a,b)=>a.name.localeCompare(b.name,"es"));
    $("clearSearch").hidden=!state.query;$("resultCount").textContent=`${filtered.length} ${filtered.length===1?"receta":"recetas"}`;$("recipeGrid").innerHTML=filtered.slice(0,state.visible).map(item=>`<article class="recipe-card"><div class="product-frame"><img loading="lazy" decoding="async" src="${item.productImage}" alt="${esc(item.name)}"></div><div class="recipe-copy"><small>${esc(item.subcategory)}</small><h2>${esc(item.name)}</h2><div class="recipe-actions"><button class="mini-primary" data-practice="${item.id}" type="button">Practicar</button><button class="text-button" data-reference="${item.id}" type="button">Ver ficha</button></div></div></article>`).join("")||`<div class="empty-state"><span>⌕</span><h2>Sin coincidencias</h2><p>Prueba con otra palabra o categoría.</p></div>`;$("showMore").hidden=state.visible>=filtered.length;document.querySelectorAll("[data-reference]").forEach(button=>button.onclick=()=>openReference(button.dataset.reference));document.querySelectorAll("[data-practice]").forEach(button=>button.onclick=()=>launchTraining(button.dataset.practice));announce(`${filtered.length} resultados`);
  }
  function launchTraining(id){showView("training",{reset:false});selectContent(id);}
  function openReference(id){const item=cms.catalog.find(entry=>entry.id===id);if(!item)return;$("dialogProduct").src=item.productImage;$("dialogProduct").alt=item.name;$("dialogReference").src=item.referenceImage;$("dialogTitle").textContent=item.name;$("dialogCategory").textContent=`${item.category} · ${item.subcategory}`;const content=cms.contents.find(entry=>entry.id===item.id);$("dialogTrain").hidden=!content;$("dialogTrain").onclick=()=>{$("referenceDialog").close();launchTraining(content.id);};$("referenceDialog").showModal();}
  function resumeTraining(){const saved=JSON.parse(sessionStorage.getItem("guia-core-progress")||"null"),content=saved&&cms.contents.find(item=>item.id===saved.contentId);if(!content)return;state.content=content;state.category=content.category;state.selections=saved.selections||{};state.route=saved.route;state.step=Math.min(Number(saved.step||0),Math.max(0,cms.steps.filter(item=>item.route===saved.route).length-1));showView("training",{reset:false});setTrainingHeader(content.name,"Continuaste tu práctica guardada.");renderRunner();}
  function setupInstall(){const standalone=matchMedia("(display-mode: standalone)").matches||navigator.standalone===true,ios=/iphone|ipad|ipod/i.test(navigator.userAgent);$("installApp").textContent=standalone?"Instalada":"Instalar";addEventListener("beforeinstallprompt",event=>{event.preventDefault();state.deferredInstall=event;});$("installApp").onclick=async()=>{if(standalone)return announce("La guía ya está instalada");if(state.deferredInstall){await state.deferredInstall.prompt();state.deferredInstall=null;return;}$("installGuide").innerHTML=ios?"<ol><li>Toca Compartir en Safari.</li><li>Elige Agregar a inicio.</li></ol>":"<p>Abre el menú del navegador y selecciona Instalar aplicación o Agregar a pantalla principal.</p>";$("installDialog").showModal();};$("confirmInstall").onclick=()=>$("installDialog").close();}

  document.querySelectorAll("[data-view]").forEach(button=>button.onclick=()=>showView(button.dataset.view));document.querySelectorAll("[data-close]").forEach(button=>button.onclick=()=>$(button.dataset.close).close());$("homeButton").onclick=()=>showView("home");$("recipeSearch").oninput=event=>{state.query=event.target.value;state.visible=12;renderSearch();};$("clearSearch").onclick=()=>{state.query="";$("recipeSearch").value="";renderSearch();};$("showMore").onclick=()=>{state.visible+=12;renderSearch();};$("resumeTraining").onclick=resumeTraining;$("homeBeverageCount").textContent=cms.contents.filter(item=>item.category!=="Alimentos").length;$("homeFoodCount").textContent=cms.contents.filter(item=>item.category==="Alimentos").length;addEventListener("popstate",()=>showView(location.hash==="#practicar"?"training":location.hash==="#biblioteca"?"search":"home",{history:false}));if("serviceWorker" in navigator)addEventListener("load",()=>navigator.serviceWorker.register("sw.js").catch(()=>{}));updateResume();setupInstall();showView(location.hash==="#practicar"?"training":location.hash==="#biblioteca"?"search":"home",{history:false});
})();
