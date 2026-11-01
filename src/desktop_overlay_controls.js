/* Native desktop overlays: real windows, retained legacy URLs and geometry. */
(()=>{'use strict';
let state={instances:[],settings:{}},overlayPlusEntries=[];
async function refresh(){
  try{
    const response=await fetch('/api/desktop-overlays');
    if(!response.ok)return;
    state=await response.json();
    if(window.ComposerStudio?.state)Object.assign(ComposerStudio.state.legacyTools ||= {},state.settings || {});

    const game = state.instances.find(item => item.kind === 'game');
    const overlayPlus = state.instances.find(item => item.kind === 'overlay+');

    // 1. Game Overlay main button & frame toggle companion button
    const btnGame = document.getElementById('topbar-item-game-overlay');
    const btnGameFrame = document.getElementById('topbar-btn-game-overlay-frame');
    if (btnGame) {
      const isGameActive = !!game;
      btnGame.classList.toggle('active', isGameActive);
      btnGame.setAttribute('aria-pressed', String(isGameActive));
      const lbl = btnGame.querySelector('.btn-label-text');
      if (lbl) {
        lbl.textContent = isGameActive ? 'ปิด Game Overlay' : 'Game Overlay';
      }
      if (isGameActive) {
        btnGame.style.borderColor = 'rgba(239, 68, 68, 0.55)';
        btnGame.style.background = 'rgba(239, 68, 68, 0.18)';
        btnGame.style.color = '#fca5a5';
        btnGame.title = 'คลิกเพื่อปิด Game Overlay ออกจากหน้าจอ';
      } else {
        btnGame.style.borderColor = '';
        btnGame.style.background = '';
        btnGame.style.color = '';
        btnGame.title = 'คลิกสลับ Game Overlay / คลิกขวาเพื่อเปิดเมนู & ซ่อนปุ่ม';
      }
    }
    if (btnGameFrame) {
      if (game) {
        btnGameFrame.removeAttribute('hidden');btnGameFrame.style.setProperty('display','inline-flex','important');
        const isEditing = game.editing !== false;
        const frameLbl = btnGameFrame.querySelector('.frame-label-text');
        if (frameLbl) {
          frameLbl.textContent = isEditing ? '👁️ ซ่อนกรอบ' : '📐 แสดงกรอบ';
        }
        btnGameFrame.title = isEditing ? 'คลิกเพื่อล็อกตำแหน่งและซ่อนกรอบสีแดง (Ctrl+Shift+H)' : 'คลิกเพื่อแสดงกรอบสีแดงสำหรับลากปรับตำแหน่ง (Ctrl+Shift+H)';
        if (isEditing) {
          btnGameFrame.style.background = 'rgba(245, 158, 11, 0.2)';
          btnGameFrame.style.borderColor = 'rgba(245, 158, 11, 0.5)';
          btnGameFrame.style.color = '#fde68a';
        } else {
          btnGameFrame.style.background = 'rgba(59, 130, 246, 0.2)';
          btnGameFrame.style.borderColor = 'rgba(59, 130, 246, 0.5)';
          btnGameFrame.style.color = '#93c5fd';
        }
      } else {
        btnGameFrame.setAttribute('hidden','');btnGameFrame.style.setProperty('display','none','important');
      }
    }

    // 2. Overlay+ main button & frame toggle companion button
    const btnOp = document.getElementById('topbar-item-overlay-plus');
    const btnOpFrame = document.getElementById('topbar-btn-overlay-plus-frame');
    if (btnOp) {
      const isOpActive = !!overlayPlus;
      btnOp.classList.toggle('active', isOpActive);
      btnOp.setAttribute('aria-pressed', String(isOpActive));
      const lbl = btnOp.querySelector('.btn-label-text');
      if (lbl) {
        lbl.textContent = isOpActive ? 'ปิด Overlay+' : 'Overlay+';
      }
      if (isOpActive) {
        btnOp.style.borderColor = 'rgba(239, 68, 68, 0.55)';
        btnOp.style.background = 'rgba(239, 68, 68, 0.18)';
        btnOp.style.color = '#fca5a5';
        btnOp.title = 'คลิกเพื่อปิด Overlay+ ออกจากหน้าจอ';
      } else {
        btnOp.style.borderColor = '';
        btnOp.style.background = '';
        btnOp.style.color = '';
        btnOp.title = 'คลิกสลับ Overlay+ / คลิกขวาเพื่อเปิดเมนู & ซ่อนปุ่ม';
      }
    }
    if (btnOpFrame) {
      if (overlayPlus) {
        btnOpFrame.removeAttribute('hidden');btnOpFrame.style.setProperty('display','inline-flex','important');
        const isEditing = overlayPlus.editing !== false;
        const frameLbl = btnOpFrame.querySelector('.frame-label-text');
        if (frameLbl) {
          frameLbl.textContent = isEditing ? '👁️ ซ่อนกรอบ' : '📐 แสดงกรอบ';
        }
        btnOpFrame.title = isEditing ? 'คลิกเพื่อล็อกตำแหน่งและซ่อนกรอบสีแดง (Ctrl+Shift+N)' : 'คลิกเพื่อแสดงกรอบสีแดงสำหรับลากปรับตำแหน่ง (Ctrl+Shift+N)';
        if (isEditing) {
          btnOpFrame.style.background = 'rgba(245, 158, 11, 0.2)';
          btnOpFrame.style.borderColor = 'rgba(245, 158, 11, 0.5)';
          btnOpFrame.style.color = '#fde68a';
        } else {
          btnOpFrame.style.background = 'rgba(59, 130, 246, 0.2)';
          btnOpFrame.style.borderColor = 'rgba(59, 130, 246, 0.5)';
          btnOpFrame.style.color = '#93c5fd';
        }
      } else {
        btnOpFrame.setAttribute('hidden','');btnOpFrame.style.setProperty('display','none','important');
      }
    }

    const doc=typeof getToolDocument==='function'?getToolDocument('game-overlay'):document;
    const viewer=state.instances.find(item=>item.kind==='viewer');
    const badge=doc.getElementById('goGameStatusBadge'),toggle=doc.getElementById('btnGoToggle'),demo=doc.getElementById('btnGoDemo'),viewerToggle=doc.getElementById('btnGoViewerToggle');
    if(badge){badge.textContent=game?(game.ready?'เปิดอยู่':'กำลังเปิด...'):'ยังไม่ได้เปิด';badge.style.color=game?'#10b981':'#94a3b8'}
    if(toggle)toggle.textContent=game?'⏹ ปิด Game Overlay':'🚀 เปิด Game Overlay';
    if(demo)demo.textContent=game?.demo_running?'⏹ หยุด Loop Demo':'▶️ เปิด Loop Demo';
    if(viewerToggle)viewerToggle.textContent=viewer?'ปิด Viewer Overlay':'เปิด Viewer Overlay';
  }catch{}
}
window.desktopOverlayAction=async function(kind,action='toggle'){
  try{
    const response=await fetch('/api/desktop-overlays',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind,action})});
    const result=await response.json();
    if(!response.ok)throw Error(result.error || 'เปิด Overlay ไม่สำเร็จ');
    await refresh();
    showToast(action==='edit'?'สลับกรอบปรับตำแหน่งแล้ว':action==='demo'?'สลับสถานะ Loop Demo แล้ว':'เปลี่ยนสถานะหน้าต่าง Overlay แล้ว');
  }catch(error){
    showToast(error.message);
  }
};
window.openDesktopOverlaySettings=async function(tab='game'){
  if (typeof openToolWindow === 'function') openToolWindow('game-overlay');
  setTimeout(async () => {
    const doc = typeof getToolDocument === 'function' ? getToolDocument('game-overlay') : document;
    if (typeof switchGameOverlayTab === 'function') switchGameOverlayTab(tab);
    if (typeof loadGameOverlaySettings === 'function') await loadGameOverlaySettings();
    if (window.BP3GameChatSettings?.init) await window.BP3GameChatSettings.init(doc);
    if (window.BP3GameSliders?.init) window.BP3GameSliders.init(doc);
    if (window.BP3ViewerOverlaySettings?.init) window.BP3ViewerOverlaySettings.init(doc);
    await refresh();
    try { window.focus(); } catch (_) {}
  }, 50);
};
window.openOverlayPlusSettings=async function(){
  if(typeof openToolWindow==='function')openToolWindow('overlay-plus-settings');
  try{
    const response=await fetch('/api/desktop-overlays');
    if(!response.ok)throw Error('โหลดการตั้งค่าไม่สำเร็จ');
    const data=await response.json();
    const doc=getToolDocument('overlay-plus-settings');
    overlayPlusEntries=data.settings?.more_overlays||[];
    for(let i=0;i<3;i++){
      const entry=overlayPlusEntries[i]||{};
      const checkbox=doc.getElementById('opEnabled'+i),input=doc.getElementById('opUrl'+i);
      if(checkbox)checkbox.checked=entry.enabled!==false && !!entry.url;
      if(input)input.value=entry.url||'';
      if(checkbox&&!checkbox.dataset.asBound){
        checkbox.dataset.asBound='1';
        checkbox.addEventListener('change',()=>window.persistOverlayPlusSettings());
      }
      if(input&&!input.dataset.asBound){
        input.dataset.asBound='1';
        input.addEventListener('change',()=>window.persistOverlayPlusSettings());
        input.addEventListener('input',()=>window.persistOverlayPlusSettings());
      }
    }
  }catch(error){showToast(error.message);}
};
window.saveOverlayPlusSettings=async function(){
  const doc=getToolDocument('overlay-plus-settings'),status=doc.getElementById('overlayPlusSaveStatus');
  try{
    const overlays=[0,1,2].map(i=>({...overlayPlusEntries[i],url:(doc.getElementById('opUrl'+i)?.value||'').trim(),enabled:!!doc.getElementById('opEnabled'+i)?.checked}));
    const response=await fetch('/api/desktop-overlays',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:'configure',overlays})});
    const result=await response.json();
    if(!response.ok)throw Error(result.error||'บันทึกไม่สำเร็จ');
    closeToolWindow('overlay-plus-settings');
    showToast('บันทึก Overlay+ แล้ว');
  }catch(error){
    if(status){status.textContent=error.message;status.classList.add('error');}
    else showToast(error.message);
  }
};
window.addEventListener('bp3:remote-event',event=>{
  if(event.detail?.event==='DESKTOP_OVERLAY_STATE' && window.ComposerStudio?.state)Object.assign(ComposerStudio.state.legacyTools ||= {},event.detail.payload);
  if(event.detail?.event==='DESKTOP_OVERLAY_SETTINGS'){
    const kind=event.detail?.payload?.kind;
    if(kind==='overlay+')openOverlayPlusSettings();
    else openDesktopOverlaySettings(kind==='viewer'?'viewer':'game');
  }
});
setInterval(refresh,3000);
refresh();
})();
