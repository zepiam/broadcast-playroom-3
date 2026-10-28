/* Native desktop overlays: real windows, retained legacy URLs and geometry. */
(()=>{'use strict';
let state={instances:[],settings:{}};
async function refresh(){try{const response=await fetch('/api/desktop-overlays');if(!response.ok)return;state=await response.json();if(window.ComposerStudio?.state)Object.assign(ComposerStudio.state.legacyTools ||= {},state.settings || {});for(const [id,kind] of [['topbar-item-game-overlay','game'],['topbar-item-overlay-plus','overlay+']]){const button=document.getElementById(id);if(button){const active=state.instances.some(item=>item.kind===kind);button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));}}}catch{}}
window.desktopOverlayAction=async function(kind,action='toggle'){
 try{const response=await fetch('/api/desktop-overlays',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind,action})});const result=await response.json();if(!response.ok)throw Error(result.error || 'เปิด Overlay ไม่สำเร็จ');await refresh();showToast(action==='edit'?'สลับกรอบปรับตำแหน่งแล้ว':action==='demo'?'สลับสถานะ Loop Demo แล้ว':'เปลี่ยนสถานะหน้าต่าง Overlay แล้ว');}catch(error){showToast(error.message);}
};
window.openDesktopOverlaySettings=async function(tab='game'){
 openToolWindow('game-overlay');
 if(typeof switchGameOverlayTab==='function')switchGameOverlayTab(tab);
 if(typeof loadGameOverlaySettings==='function')await loadGameOverlaySettings();
};
window.addEventListener('bp3:remote-event',event=>{if(event.detail?.event==='DESKTOP_OVERLAY_STATE' && window.ComposerStudio?.state)Object.assign(ComposerStudio.state.legacyTools ||= {},event.detail.payload);if(event.detail?.event==='DESKTOP_OVERLAY_SETTINGS')openDesktopOverlaySettings(event.detail?.payload?.kind==='viewer'?'viewer':'game');});
setInterval(refresh,3000);refresh();
})();
