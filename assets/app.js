const catalog=JSON.parse(document.getElementById('catalog-data').textContent);
const sitePath=pathname=>(document.body.dataset.basePath||'')+pathname;
const key='ao-inquiry-v1';
let selection=[];
try{const stored=JSON.parse(localStorage.getItem(key)||'[]');selection=Array.isArray(stored)?stored.filter(item=>catalog.some(p=>p.id===item.id)).map(item=>({id:item.id,quantity:/^[1-9]\d{0,3}$/.test(String(item.quantity||''))?String(item.quantity):''})):[];}catch{}
const dialog=document.getElementById('inquiry-dialog');
const body=document.getElementById('inquiry-content');
const city=document.getElementById('inquiry-city');
const message=document.getElementById('inquiry-message');
const escapeHtml=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const track=(name,detail={})=>document.dispatchEvent(new CustomEvent('ao:event',{detail:{name,...detail}}));
function save(){try{localStorage.setItem(key,JSON.stringify(selection));}catch{}updateCounters();}
function updateCounters(){document.querySelectorAll('[data-selection-count]').forEach(el=>el.textContent=selection.length);document.querySelectorAll('[data-add-product]').forEach(el=>{const selected=selection.some(i=>i.id===el.dataset.addProduct);el.setAttribute('aria-pressed',String(selected));el.setAttribute('aria-label',`${selected?'Quitar de':'Agregar a'} la consulta: ${catalog.find(p=>p.id===el.dataset.addProduct)?.name||''}`);if(el.classList.contains('add-button'))el.innerHTML=selected?'<span aria-hidden="true">✓</span>':'<span aria-hidden="true">+</span>';else el.textContent=selected?'Agregada a tu consulta':'Agregar a mi consulta';});}
let statusTimer;
function notify(text){const el=document.getElementById('status-message');el.textContent=text;el.hidden=false;clearTimeout(statusTimer);statusTimer=setTimeout(()=>el.hidden=true,3200);}
function toggleProduct(id){if(!catalog.some(p=>p.id===id))throw new Error('Modelo no encontrado');const found=selection.findIndex(i=>i.id===id);if(found>=0){selection.splice(found,1);notify('Prenda retirada de tu consulta');}else{selection.push({id,quantity:''});track('add_to_inquiry',{product_id:id});notify('Prenda agregada a tu consulta');}save();if(dialog.open)renderInquiry();return {selected_ids:selection.map(i=>i.id)};}
function generateMessage(){const lines=['Hola, A&O. Me interesa comprar para mi negocio. Quisiera consultar precio y disponibilidad de:',''];for(const item of selection){const p=catalog.find(p=>p.id===item.id);lines.push(`• ${p.name} (catálogo, pág. ${p.source_page})${item.quantity?` — cantidad orientativa: ${item.quantity} prendas`:''}`);}lines.push('','¿Cómo se arma la docena y cuáles son las condiciones de compra, pago y envío'+(city.value.trim()?` a ${city.value.trim()}`:'')+'?');return lines.join('\n');}
function refreshMessage(){message.value=generateMessage();const url='https://wa.me/59157736466?text='+encodeURIComponent(message.value);const link=document.getElementById('send-inquiry');link.href=url;link.hidden=url.length>7000;document.getElementById('long-message-note').hidden=url.length<=7000;}
function renderInquiry(){const empty=selection.length===0;document.getElementById('inquiry-form').hidden=empty;document.getElementById('inquiry-footer').hidden=empty;body.innerHTML=empty?`<div class="inquiry-empty"><h3>Tu colección empieza aquí.</h3><p>Elige las prendas que te interesan para consultar sus precios y disponibilidad.</p><a class="button primary" href="${sitePath('/coleccion/')}">Explorar colección</a></div>`:selection.map(item=>{const p=catalog.find(p=>p.id===item.id);return `<div class="inquiry-item"><a href="${sitePath('/prendas/'+p.slug+'/')}"><img src="${escapeHtml(p.image)}" alt="${escapeHtml(p.name)}" width="76" height="100"></a><div><h3><a href="${sitePath('/prendas/'+p.slug+'/')}">${escapeHtml(p.name)}</a></h3><p>Catálogo · pág. ${p.source_page}</p><label class="quantity-label">Cantidad orientativa<input type="number" min="1" max="9999" inputmode="numeric" data-quantity="${p.id}" value="${item.quantity}" placeholder="Opcional" aria-label="Cantidad orientativa de ${escapeHtml(p.name)}"></label></div><button class="icon-button" data-remove="${p.id}" aria-label="Quitar ${escapeHtml(p.name)}">×</button></div>`;}).join('');refreshMessage();}
function openInquiry(){renderInquiry();dialog.showModal();document.body.style.overflow='hidden';}
document.querySelectorAll('[data-open-inquiry]').forEach(el=>el.addEventListener('click',openInquiry));
document.querySelectorAll('[data-add-product]').forEach(el=>el.addEventListener('click',()=>toggleProduct(el.dataset.addProduct)));
document.getElementById('close-inquiry').addEventListener('click',()=>dialog.close());
dialog.addEventListener('close',()=>document.body.style.overflow='');
dialog.addEventListener('click',event=>{if(event.target===dialog&&event.clientX<dialog.getBoundingClientRect().left)dialog.close();});
body.addEventListener('click',event=>{const button=event.target.closest('[data-remove]');if(button)toggleProduct(button.dataset.remove);});
body.addEventListener('input',event=>{if(event.target.dataset.quantity){const item=selection.find(i=>i.id===event.target.dataset.quantity);const value=event.target.value;if(value&&!/^[1-9]\d{0,3}$/.test(value)){event.target.setCustomValidity('Indica un número de 1 a 9999.');return;}event.target.setCustomValidity('');item.quantity=value;save();refreshMessage();}});
city.addEventListener('input',refreshMessage);
const validQuantities=()=>{for(const input of body.querySelectorAll('[data-quantity]'))if(!input.checkValidity()){input.reportValidity();return false;}return true;};
document.getElementById('send-inquiry').addEventListener('click',event=>{if(!validQuantities())event.preventDefault();});
async function copyText(value,success){try{await navigator.clipboard.writeText(value);notify(success);return true;}catch{const textarea=document.createElement('textarea');textarea.value=value;textarea.style.cssText='position:fixed;top:20px;left:20px;width:280px;z-index:100';(dialog.open?dialog:document.body).append(textarea);textarea.select();let copied=false;try{copied=document.execCommand('copy');}catch{}if(copied){textarea.remove();notify(success);}else{notify('Selecciona el texto y cópialo con tu teclado.');textarea.addEventListener('blur',()=>textarea.remove(),{once:true});}return copied;}}
document.querySelectorAll('[data-copy-number]').forEach(button=>button.addEventListener('click',()=>copyText('+59157736466','Número copiado')));
document.getElementById('copy-inquiry').addEventListener('click',async()=>{if(validQuantities()&&await copyText(message.value,'Mensaje copiado'))track('copy_inquiry');});
document.querySelectorAll('[data-copy-individual]').forEach(button=>button.addEventListener('click',()=>{const p=catalog.find(p=>p.id===button.dataset.copyIndividual);copyText(`Hola, A&O. Quisiera consultar precio y disponibilidad de ${p.name} (catálogo, pág. ${p.source_page}). ¿Cómo se arma la docena y cuáles son las condiciones de compra y envío?`,'Consulta copiada');}));
const menuButton=document.getElementById('menu-toggle'),menu=document.getElementById('mobile-nav');
menuButton.addEventListener('click',()=>{const open=menuButton.getAttribute('aria-expanded')!=='true';menuButton.setAttribute('aria-expanded',String(open));menuButton.setAttribute('aria-label',open?'Cerrar menú':'Abrir menú');menu.hidden=!open;});
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&!menu.hidden){menu.hidden=true;menuButton.setAttribute('aria-expanded','false');menuButton.setAttribute('aria-label','Abrir menú');menuButton.focus();}});
const search=document.getElementById('catalog-search');
function applySearch(query){if(!search)return;search.value=query;const normal=value=>value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();let count=0;document.querySelectorAll('[data-search-text]').forEach(card=>{const match=normal(card.dataset.searchText).includes(normal(query.trim()));card.hidden=!match;if(match)count++;});document.getElementById('results-count').textContent=`${count} ${count===1?'prenda':'prendas'}`;document.getElementById('empty-results').hidden=count!==0;document.getElementById('active-search').hidden=!query.trim();document.getElementById('search-label').textContent=query.trim();track('filter_apply',{results:count});return{visible_count:count};}
search?.addEventListener('input',event=>applySearch(event.target.value));
document.querySelectorAll('[data-clear-search]').forEach(button=>button.addEventListener('click',()=>{applySearch('');search.focus();}));
document.querySelectorAll('img[data-fallback]').forEach(img=>{const fail=()=>{img.closest('.product-photo,.detail-image')?.classList.add('media-failed');};img.addEventListener('error',fail);if(img.complete&&!img.naturalWidth)fail();});
document.querySelectorAll('a[href^="https://wa.me/"]').forEach(link=>link.addEventListener('click',()=>track('whatsapp_click',{section:link.dataset.section||document.body.dataset.page,product_id:link.dataset.product||undefined})));
updateCounters();
if(document.body.dataset.page==='coleccion')track('view_collection');
if(document.body.dataset.product)track('view_product',{product_id:document.body.dataset.product});
const context=document.modelContext;
setupHeaderCursorZoom();
function setupHeaderCursorZoom(){
 const controls=[...document.querySelectorAll('.nav-right>.nav-link,.nav-right>.selection-button')];
 const allowed=matchMedia('(hover:hover) and (pointer:fine) and (prefers-reduced-motion:no-preference)');
 controls.forEach(el=>el.classList.add('cursor-zoom'));
 let bounds=[],frame=0,pointer=null;
 const measure=()=>{bounds=controls.map(el=>{const r=el.getBoundingClientRect();const width=el.offsetWidth,height=el.offsetHeight;return {el,width,height,left:r.left+r.width/2-width/2,top:r.top+r.height/2-height/2,last:null};});};
 const reset=()=>{cancelAnimationFrame(frame);frame=0;pointer=null;controls.forEach(el=>{el.style.removeProperty('--cursor-scale');el.removeAttribute('data-pointer-pressed');});bounds.forEach(b=>b.last=null);};
 const paint=()=>{frame=0;if(!allowed.matches||!pointer)return;
  for(const b of bounds){if(!b.width||!b.height)continue;
   const dx=Math.max(b.left-pointer.x,0,pointer.x-b.left-b.width),dy=Math.max(b.top-pointer.y,0,pointer.y-b.top-b.height);
   const proximity=Math.max(0,1-Math.hypot(dx,dy)/48);
   const scale=(1+.075*proximity*proximity*(3-2*proximity)).toFixed(4);
   if(b.last!==scale){b.el.style.setProperty('--cursor-scale',scale);b.last=scale;}
  }
 };
 const schedule=()=>{if(!frame)frame=requestAnimationFrame(paint);};
 document.addEventListener('pointermove',event=>{if(!allowed.matches||event.pointerType!=='mouse')return;pointer={x:event.clientX,y:event.clientY};schedule();},{passive:true});
 document.addEventListener('pointerdown',event=>{if(!allowed.matches||event.pointerType!=='mouse')return;const el=event.target.closest('.cursor-zoom');if(el)el.setAttribute('data-pointer-pressed','true');},{passive:true});
 const release=()=>controls.forEach(el=>el.removeAttribute('data-pointer-pressed'));
 document.addEventListener('pointerup',release,{passive:true});document.addEventListener('pointercancel',reset,{passive:true});
 document.documentElement.addEventListener('pointerleave',reset,{passive:true});
 document.addEventListener('keydown',reset);window.addEventListener('blur',reset);window.addEventListener('pagehide',reset);
 document.addEventListener('visibilitychange',()=>{if(document.hidden)reset();});
 const refresh=()=>{measure();if(pointer)schedule();};
 window.addEventListener('resize',refresh,{passive:true});window.addEventListener('scroll',refresh,{passive:true});
 allowed.addEventListener('change',()=>{reset();measure();});document.fonts.ready.then(refresh);measure();
}
if(context?.registerTool){const lifecycle=new AbortController();const register=tool=>{try{Promise.resolve(context.registerTool(tool,{signal:lifecycle.signal})).catch(()=>{});}catch{}};register({name:'read_collection',description:'Leer los modelos reales del catálogo de A&O y la selección actual.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true,untrustedContentHint:true},execute:()=>({products:catalog.map(p=>({id:p.id,name:p.name,category:p.category,source_page:p.source_page,url:sitePath('/prendas/'+p.slug+'/')})),selected_ids:selection.map(i=>i.id)})});register({name:'stage_inquiry_models',description:'Agregar modelos a la selección para consulta. No envía mensajes ni confirma pedidos.',inputSchema:{type:'object',properties:{product_ids:{type:'array',items:{type:'string'},minItems:1,maxItems:14}},required:['product_ids'],additionalProperties:false},annotations:{readOnlyHint:false},execute:input=>{if(!input||!Array.isArray(input.product_ids)||!input.product_ids.length||input.product_ids.length>14||input.product_ids.some(id=>typeof id!=='string'||!catalog.some(p=>p.id===id)))throw new Error('Referencias de prendas no válidas');for(const id of new Set(input.product_ids))if(!selection.some(i=>i.id===id))selection.push({id,quantity:''});save();openInquiry();return{selected_ids:selection.map(i=>i.id),message:message.value,status:'consulta_preparada'};}});window.addEventListener('pagehide',()=>lifecycle.abort(),{once:true});}
