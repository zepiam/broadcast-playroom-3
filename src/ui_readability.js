/* App-only text sizing. Pixel font declarations scale once; canvas output stays exact. */
(()=>{'use strict';
const levels={normal:1,large:1.2,xlarge:1.4},docs=new Map();
let mode=localStorage.getItem('bp3_ui_text_size') || 'normal';if(!(mode in levels))mode='normal';
const excluded='#composerCanvasStage,#composerCanvasStage *,#obsCanvasStage,#obsCanvasStage *,#cwcPreviewStage,#cwcPreviewStage *,#chatPreviewBox,#chatPreviewBox *,.chat-body-msg,.chat-body-msg *';
function install(doc){
 if(docs.has(doc))return;const view=doc.defaultView;if(!view || !doc.body)return;
 let disposed=false,pending=null;const dirty=new Set();
 let sheet=doc.head.querySelector('#bp3-ui-font-overrides');if(!sheet){sheet=doc.createElement('style');sheet.id='bp3-ui-font-overrides';doc.head.append(sheet);}
 function fontRules(rules){let css='';for(const rule of rules){if(rule.selectorText && !rule.selectorText.includes('::')){const value=rule.style.fontSize;if(/^\d+(\.\d+)?px$/.test(value))css+='html[data-ui-text-size]:not([data-ui-text-size="normal"]) :is('+rule.selectorText+'):not(:where('+excluded+')){font-size:calc('+value+' * var(--bp3-ui-font-scale)) !important;}\n';}else if(rule.cssRules && rule.conditionText){css+='@'+(rule.constructor.name==='CSSMediaRule'?'media':'supports')+' '+rule.conditionText+'{'+fontRules(rule.cssRules)+'}\n';}}return css;}
 function refreshRules(){let css='';for(const item of doc.styleSheets){if(item.ownerNode?.id==='bp3-ui-font-overrides')continue;try{css+=fontRules(item.cssRules);}catch{}}sheet.textContent=css+'\nhtml[data-ui-text-size]:not([data-ui-text-size="normal"]) [data-ui-inline-font]:not(:where('+excluded+')){font-size:calc(var(--bp3-ui-inline-font) * var(--bp3-ui-font-scale)) !important;}';}
 function inline(root){if(root.nodeType!==1 || root.matches(excluded) || root.closest('#composerCanvasStage,#obsCanvasStage,#cwcPreviewStage,#chatPreviewBox,.chat-body-msg'))return;const nodes=[root,...root.querySelectorAll('[style]')];for(const node of nodes){if(node.matches(excluded))continue;const value=node.style.fontSize;if(/^\d+(\.\d+)?px$/.test(value)){if(node.style.getPropertyValue('--bp3-ui-inline-font')!==value)node.style.setProperty('--bp3-ui-inline-font',value);if(!node.hasAttribute('data-ui-inline-font'))node.setAttribute('data-ui-inline-font','');}else if(node.hasAttribute('data-ui-inline-font')){node.removeAttribute('data-ui-inline-font');}}}
 function flush(){pending=null;if(disposed)return;for(const node of dirty)inline(node);dirty.clear();}
 const observer=new view.MutationObserver(records=>{for(const record of records){if(record.type==='attributes')dirty.add(record.target);else for(const node of record.addedNodes){if(node.nodeType===1)dirty.add(node);}}if(dirty.size && pending===null)pending=view.setTimeout(flush,30);});
 observer.observe(doc.body,{subtree:true,childList:true,attributes:true,attributeFilter:['style']});
 function apply(){doc.documentElement.dataset.uiTextSize=mode;doc.documentElement.style.setProperty('--bp3-ui-font-scale',levels[mode]);const control=doc.getElementById('selUiTextSize');if(control)control.value=mode;inline(doc.body);view.dispatchEvent(new view.Event('resize'));}
 function dispose(){if(disposed)return;disposed=true;observer.disconnect();if(pending!==null)view.clearTimeout(pending);docs.delete(doc);view.removeEventListener('pagehide',dispose);view.removeEventListener('beforeunload',dispose);}
 docs.set(doc,{apply,refreshRules});view.addEventListener('pagehide',dispose,{once:true});view.addEventListener('beforeunload',dispose,{once:true});refreshRules();apply();
}
function setMode(value){if(!(value in levels))return;mode=value;localStorage.setItem('bp3_ui_text_size',mode);for(const item of docs.values())item.apply();window.applyUiChatFontDefault?.(mode);}
function init(){const section=document.getElementById('sec-themes');if(section && !document.getElementById('selUiTextSize')){const card=document.createElement('div');card.className='section-card ui-readability-card';card.innerHTML='<div class="section-card-title">🔎 ขนาดตัวอักษรในโปรแกรม</div><label class="modal-form-label" for="selUiTextSize">โหมดอ่านง่าย</label><select class="voice-select-box" id="selUiTextSize"><option value="normal">ปกติ — 100%</option><option value="large">ใหญ่ — 120%</option><option value="xlarge">ใหญ่พิเศษ — 140%</option></select><p class="settings-section-desc">ขยายเมนูและหน้าตั้งค่า โดยไม่เปลี่ยน Widget บน Overlay<br>แชทสดปรับเพิ่มได้จากปุ่ม A+ และ A−</p>';section.insertBefore(card,section.children[2] || null);card.querySelector('select').onchange=event=>setMode(event.target.value);}
 install(document);
}
window.BP3UiText={install,setMode,getMode:()=>mode};if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
