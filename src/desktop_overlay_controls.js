/* Native desktop overlays: real windows, retained legacy URLs and geometry. */
(()=>{'use strict';
let state={instances:[],settings:{}},overlayPlusEntries=[];
async function refresh(){try{const response=await fetch('/api/desktop-overlays');if(!response.ok)return;state=await response.json();if(window.ComposerStudio?.state)Object.assign(ComposerStudio.state.legacyTools ||= {},state.settings || {});for(const [id,kind] of [['topbar-item-game-overlay','game'],['topbar-item-overlay-plus','overlay+']]){const button=document.getElementById(id);if(button){const active=state.instances.some(item=>item.kind===kind);button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));}}const doc=typeof getToolDocument==='function'?getToolDocument('game-overlay'):document;const game=state.instances.find(item=>item.kind==='game'),viewer=state.instances.find(item=>item.kind==='viewer');const badge=doc.getElementById('goGameStatusBadge'),toggle=doc.getElementById('btnGoToggle'),demo=doc.getElementById('btnGoDemo'),viewerToggle=doc.getElementById('btnGoViewerToggle');if(badge){badge.textContent=game?(game.ready?'เปิดอยู่':'กำลังเปิด...'):'ยังไม่ได้เปิด';badge.style.color=game?'#10b981':'#94a3b8'}if(toggle)toggle.textContent=game?'⏹ ปิด Game Overlay':'🚀 เปิด Game Overlay';if(demo)demo.textContent=game?.demo_running?'⏹ หยุด Loop Demo':'▶️ เปิด Loop Demo';if(viewerToggle)viewerToggle.textContent=viewer?'ปิด Viewer Overlay':'เปิด Viewer Overlay';}catch{}}
window.desktopOverlayAction=async function(kind,action='toggle'){
 try{const response=await fetch('/api/desktop-overlays',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind,action})});const result=await response.json();if(!response.ok)throw Error(result.error || 'เปิด Overlay ไม่สำเร็จ');await refresh();showToast(action==='edit'?'สลับกรอบปรับตำแหน่งแล้ว':action==='demo'?'สลับสถานะ Loop Demo แล้ว':'เปลี่ยนสถานะหน้าต่าง Overlay แล้ว');}catch(error){showToast(error.message);}
};
window.openDesktopOverlaySettings=async function(tab='game'){
 if (typeof openToolWindow === 'function') openToolWindow('game-overlay');
 setTimeout(async () => {
  if (typeof switchGameOverlayTab === 'function') switchGameOverlayTab(tab);
  if (typeof loadGameOverlaySettings === 'function') await loadGameOverlaySettings();
  await refresh();
  try { window.focus(); } catch (_) {}
 }, 50);
};
window.openOverlayPlusSettings=async function(){
 if(typeof openToolWindow==='function')openToolWindow('overlay-plus-settings');
 try{const response=await fetch('/api/desktop-overlays');if(!response.ok)throw Error('โหลดการตั้งค่าไม่สำเร็จ');const data=await response.json();const doc=getToolDocument('overlay-plus-settings');overlayPlusEntries=data.settings?.more_overlays||[];for(let i=0;i<3;i++){const entry=overlayPlusEntries[i]||{};const checkbox=doc.getElementById('opEnabled'+i),input=doc.getElementById('opUrl'+i);if(checkbox)checkbox.checked=entry.enabled!==false && !!entry.url;if(input)input.value=entry.url||''}}catch(error){showToast(error.message)}
};
window.saveOverlayPlusSettings=async function(){
 const doc=getToolDocument('overlay-plus-settings'),status=doc.getElementById('overlayPlusSaveStatus');
 try{const overlays=[0,1,2].map(i=>({...overlayPlusEntries[i],url:(doc.getElementById('opUrl'+i)?.value||'').trim(),enabled:!!doc.getElementById('opEnabled'+i)?.checked}));const response=await fetch('/api/desktop-overlays',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:'configure',overlays})});const result=await response.json();if(!response.ok)throw Error(result.error||'บันทึกไม่สำเร็จ');closeToolWindow('overlay-plus-settings');showToast('บันทึก Overlay+ แล้ว')}catch(error){if(status){status.textContent=error.message;status.classList.add('error')}else showToast(error.message)}
};
window.addEventListener('bp3:remote-event',event=>{if(event.detail?.event==='DESKTOP_OVERLAY_STATE' && window.ComposerStudio?.state)Object.assign(ComposerStudio.state.legacyTools ||= {},event.detail.payload);if(event.detail?.event==='DESKTOP_OVERLAY_SETTINGS'){const kind=event.detail?.payload?.kind;if(kind==='overlay+')openOverlayPlusSettings();else openDesktopOverlaySettings(kind==='viewer'?'viewer':'game');}});
setInterval(refresh,3000);refresh();
})();
