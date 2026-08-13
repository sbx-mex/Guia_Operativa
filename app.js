(() => {
  const cms = window.RECIPE_CMS;
  const $ = id => document.getElementById(id);
  const state = { size: "", recipe: null, variant: null, step: 0 };
  const screens = ["size","recipe","variant","steps","done"];

  function show(name){
    screens.forEach(screen=>{const element=$(`${screen}Screen`);element.hidden=screen!==name;element.classList.toggle("active",screen===name);});
    const stageIndex={size:0,recipe:1,variant:2,steps:3,done:4}[name];
    document.querySelectorAll(".progress span").forEach((item,index)=>{item.classList.toggle("active",index===stageIndex);item.classList.toggle("done",index<stageIndex);});
    renderSelection();window.scrollTo({top:0,behavior:"smooth"});
  }
  function renderSelection(){
    const parts=[];
    if(state.size)parts.push(`Tamaño · ${cms.sizes.find(size=>size.id===state.size)?.label}`);
    if(state.recipe)parts.push(state.recipe.name);
    if(state.variant)parts.push(`Versión · ${state.variant.label}`);
    $("selection").innerHTML=parts.map(part=>`<span>${part}</span>`).join("");
  }
  function renderSizes(){
    $("sizeCards").innerHTML=cms.sizes.map(size=>`<button class="choice-card" data-size="${size.id}" type="button"><div class="cup ${size.id.toLowerCase()}">${size.short}</div><h3>${size.label}</h3><p>Ver cantidades para ${size.label}</p></button>`).join("");
    $("sizeCards").querySelectorAll("[data-size]").forEach(button=>button.addEventListener("click",()=>{state.size=button.dataset.size;show("recipe");}));
  }
  function renderRecipes(){
    $("recipeCards").innerHTML=cms.recipes.map(recipe=>`<button class="recipe-card" data-recipe="${recipe.id}" type="button"><div class="image" style="background-image:url('${recipe.image}')"></div><div class="copy"><span class="eyebrow">Frappuccino</span><h3>${recipe.name}</h3><p>${recipe.description}</p><span class="go">Abrir receta →</span></div></button>`).join("");
    $("recipeCards").querySelectorAll("[data-recipe]").forEach(button=>button.addEventListener("click",()=>selectRecipe(button.dataset.recipe)));
  }
  function selectRecipe(id){
    state.recipe=cms.recipes.find(recipe=>recipe.id===id);state.variant=null;state.step=0;
    if(state.recipe.askVariant){renderVariants();show("variant");}else{state.variant=state.recipe.variants[0];renderSteps();show("steps");}
  }
  function renderVariants(){
    $("variantImage").style.backgroundImage=`url('${state.recipe.image}')`;
    $("variantTitle").textContent=`${state.recipe.name}: ¿Café o Cream?`;
    $("variantCards").innerHTML=state.recipe.variants.map(variant=>`<button class="variant-button" data-variant="${variant.id}" type="button"><span><b>${variant.label}</b><small>${variant.note}</small></span><span>→</span></button>`).join("");
    $("variantCards").querySelectorAll("[data-variant]").forEach(button=>button.addEventListener("click",()=>{state.variant=state.recipe.variants.find(variant=>variant.id===button.dataset.variant);state.step=0;renderSteps();show("steps");}));
  }
  function renderSteps(){
    $("recipeHero").style.backgroundImage=`url('${state.recipe.image}')`;
    $("stepsTitle").textContent=state.recipe.name;
    $("recipeDescription").textContent=state.recipe.description;
    $("recipeMeta").textContent=`${cms.sizes.find(size=>size.id===state.size).label} · ${state.variant.label}`;
    const steps=state.variant.steps;
    $("stepList").innerHTML=steps.map((step,index)=>`<button type="button" data-step="${index}"><b>${index+1}</b><span>${step.title}</span></button>`).join("");
    $("stepList").querySelectorAll("[data-step]").forEach(button=>button.addEventListener("click",()=>{state.step=Number(button.dataset.step);renderCurrentStep();}));
    renderCurrentStep();
  }
  function renderCurrentStep(){
    const steps=state.variant.steps,step=steps[state.step],sizeLabel=cms.sizes.find(size=>size.id===state.size).label;
    $("stepCounter").textContent=`${state.step+1} de ${steps.length}`;
    $("stepCard").innerHTML=`<div class="step-icon">${step.icon}</div><div class="step-content"><span class="step-number">Paso ${state.step+1} · ${sizeLabel}</span><h3>${step.title}</h3><p>${step.detail}</p><div class="measure"><span>${sizeLabel}</span><strong>${step.values[state.size]}</strong></div>${state.recipe.id==="FRAP_CAJETA"&&state.variant.id==="CREAM"&&state.step===0?'<div class="cream-note">✓ Roast omitido: la versión Cream comienza aquí, con leche.</div>':''}</div>`;
    document.querySelectorAll("[data-step]").forEach((button,index)=>{button.classList.toggle("active",index===state.step);button.classList.toggle("done",index<state.step);});
    $("prevStep").disabled=state.step===0;
    $("nextStep").textContent=state.step===steps.length-1?"Finalizar bebida":"Siguiente paso";
  }
  function next(){
    if(state.step<state.variant.steps.length-1){state.step++;renderCurrentStep();return;}
    $("doneSummary").textContent=`${state.recipe.name} · ${state.variant.label} · ${cms.sizes.find(size=>size.id===state.size).label}`;show("done");
  }
  function restart(){state.size="";state.recipe=null;state.variant=null;state.step=0;show("size");}

  renderSizes();renderRecipes();
  document.querySelectorAll("[data-back]").forEach(button=>button.addEventListener("click",()=>show(button.dataset.back)));
  $("prevStep").addEventListener("click",()=>{if(state.step>0){state.step--;renderCurrentStep();}});
  $("nextStep").addEventListener("click",next);
  $("restart").addEventListener("click",restart);$("restartTop").addEventListener("click",restart);
  show("size");
})();
