/* OBS links use the active local server, including when settings opens in a separate window. */
(() => {
  const base = new URL('/', window.location.href);
  const urls = { composer: base.href, dock: new URL('dock.html', base).href };
  function refresh() {
    const root = window._toolWindowNodes?.settings || document;
    for (const [id, value] of [['inpSettingsObsOverlayUrl', urls.composer], ['inpSettingsObsDockUrl', urls.dock]]) {
      const input = root.querySelector?.('#' + id);
      if (input) input.value = value;
    }
    const status = document.getElementById('localServerStatus');
    if (status) status.textContent = `เซิร์ฟเวอร์ในเครื่อง: ${base.host}`;
  }
  window.openObsPage = function (kind) { if (urls[kind]) window.open(urls[kind], '_blank'); };
  window.copyObsDockUrl = async function () {
    try { await navigator.clipboard.writeText(urls.dock); }
    catch (_) { window.alert('คัดลอกไม่สำเร็จ กรุณาคัดลอกลิงก์จากช่อง OBS Dock'); }
  };
  let obsInitialized = false;
  async function updateObsStatus() {
    try {
      const response = await fetch('/api/obs/status'); if (!response.ok) return;
      const state = await response.json();
      const status = document.getElementById('obsConnectionStatus');
      const label = {disabled:'ปิดใช้งาน', waiting:'รอเชื่อมต่อ', connected:'เชื่อมต่อแล้ว', error:'อ่านการตั้งค่าไม่ได้'};
      if (status) status.textContent = 'OBS WebSocket: ' + (label[state.state] || 'ยังไม่ได้ตรวจสอบ');
      const root = window._toolWindowNodes?.settings || document;
      const host = root.querySelector?.('#obsWsHost');
      if (!obsInitialized && host) {
        host.value=state.host;root.querySelector('#obsWsPort').value=state.port;root.querySelector('#obsWsEnabled').checked=state.enabled;
        root.querySelector('#obsWsPassword').placeholder=state.has_password?'เว้นว่างเพื่อใช้รหัสที่บันทึกไว้':'รหัสผ่าน OBS WebSocket';
        obsInitialized=true;
      }
    } catch (_) {}
  }
  window.saveObsConnection = async function () {
    const doc = typeof getToolDocument === 'function' ? getToolDocument('settings') : document;
    const data={enabled:doc.getElementById('obsWsEnabled').checked,host:doc.getElementById('obsWsHost').value.trim(),port:Number(doc.getElementById('obsWsPort').value),password:doc.getElementById('obsWsPassword').value,clear_password:doc.getElementById('obsWsClearPassword').checked};
    try {
      const response=await fetch('/api/obs/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
      const result=await response.json();if(!response.ok)throw Error(result.error || 'บันทึกไม่สำเร็จ');
      doc.getElementById('obsWsPassword').value='';doc.getElementById('obsWsClearPassword').checked=false;
      doc.getElementById('obsWsPassword').placeholder=result.has_password?'เว้นว่างเพื่อใช้รหัสที่บันทึกไว้':'รหัสผ่าน OBS WebSocket';
      await updateObsStatus();doc.defaultView.alert('บันทึกการตั้งค่า OBS แล้ว');
    } catch(error){doc.defaultView.alert(error.message || 'บันทึกการตั้งค่า OBS ไม่สำเร็จ');}
  };
  updateObsStatus();setInterval(updateObsStatus,3000);
  window.testObsConnection = async function () {
    const doc = typeof getToolDocument === 'function' ? getToolDocument('settings') : document;
    const host = doc.getElementById('obsWsHost').value.trim();
    const port = Number(doc.getElementById('obsWsPort').value);
    const password = doc.getElementById('obsWsPassword').value;
    if (!host || !Number.isInteger(port) || port < 1 || port > 65535) { doc.defaultView.alert('กรุณาตรวจสอบ IP และพอร์ต OBS'); return; }
    try {
      const response = await fetch('/api/obs/test', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({host, port, password, clear_password:doc.getElementById('obsWsClearPassword').checked}) });
      const result = await response.json();
      doc.defaultView.alert(result.message || 'ทดสอบการเชื่อมต่อไม่สำเร็จ');
      const status = document.getElementById('obsConnectionStatus');
      if (status && !obsInitialized) status.textContent = result.ok ? 'OBS WebSocket: ทดสอบเชื่อมต่อสำเร็จ' : 'OBS WebSocket: ทดสอบไม่สำเร็จ';
    } catch (_) { doc.defaultView.alert('ติดต่อโปรแกรมเพื่อทดสอบ OBS ไม่สำเร็จ'); }
  };
  let clipHotkeyMessage = '';
  async function pollClipHotkey() {
    try {
      const response=await fetch('/api/clip-hotkey/status');if(!response.ok)return;
      const state=await response.json(),button=document.querySelector('.split-btn-main[onclick*=markClip]');
      if(button)button.title='มาร์กคลิป'+(state.active?' ('+state.shortcut.toUpperCase()+')':'');
      if(state.message && state.message!==clipHotkeyMessage){clipHotkeyMessage=state.message;const status=document.getElementById('clipMarkerStatus');if(status){status.textContent=state.message;status.title=state.message;}}
    } catch (_) {}
  }
  window.configureClipHotkey = async function () {
    try {
      const response=await fetch('/api/clip-hotkey/status');const state=await response.json();
      const shortcut=window.prompt('ปุ่มลัดมาร์กคลิป เช่น f9 หรือ ctrl+shift+m (เว้นว่างเพื่อปิด)',state.shortcut || '');if(shortcut===null)return;
      const result=await fetch('/api/clip-hotkey',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({shortcut})});const data=await result.json();
      if(!result.ok)throw Error(data.error || 'ตั้งปุ่มลัดไม่สำเร็จ');await pollClipHotkey();window.alert(data.active?'ตั้งปุ่มลัดมาร์กคลิปแล้ว':'ปิดปุ่มลัดมาร์กคลิปแล้ว');
    } catch(error){window.alert(error.message || 'ตั้งปุ่มลัดไม่สำเร็จ');}
  };
  // Clip Marker is temporarily suspended; no hotkey status polling.
  window.clipMarkerAction = async function (action) {
    if (action === 'clear' && !window.confirm('ล้างประวัติมาร์กคลิปทั้งหมดใช่ไหม?')) return;
    try {
      const response = await fetch('/api/clip-markers', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({action})});
      const result = await response.json();
      const status = document.getElementById('clipMarkerStatus');
      if (status) { status.textContent = result.message || ''; status.title = result.message || ''; }
      if (!result.ok) window.alert(result.message || 'ทำรายการไม่สำเร็จ');
    } catch (_) { window.alert('ติดต่อโปรแกรมไม่สำเร็จ'); }
  };
  window.markClip = () => window.clipMarkerAction('mark');
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', refresh);
  else refresh();
})();
