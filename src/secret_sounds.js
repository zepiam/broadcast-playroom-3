/* User-supplied secret-code sounds. No default sounds are installed. */
(() => {
 const key='bp3_secret_sound_settings_v1',usageKey='bp3_secret_sound_usage_v1';
 let stored;try{stored=JSON.parse(localStorage.getItem(key)||'null');}catch(_){stored=null;}
 let state={entries:Array.isArray(stored?.entries)?stored.entries.filter(item=>item && typeof item.code==='string'):[],muted:stored?.muted===true,dailyLimit:Math.max(0,Math.min(100,Number(stored?.dailyLimit)||0))};
 const doc=()=>typeof getToolDocument==='function'?getToolDocument('settings'):document;
 const save=()=>{localStorage.setItem(key,JSON.stringify(state));stored=state;};
 const safeUrl=url=>typeof url==='string' && /^\/(?:playroom-media\/[a-f0-9]{64}\.(?:mp3|wav|ogg|flac|m4a|aac)|legacy-secret-sound\/[a-f0-9]{64})$/i.test(url);
 const normalizeCode=value=>{let code=String(value || '').trim();if(code && !code.startsWith('!'))code='!'+code;return /^![^\s]{1,99}$/.test(code)?code:'';};
 async function importAudio(file){if(!file || !/\.(mp3|wav|ogg|flac|m4a|aac)$/i.test(file.name))throw Error('รองรับไฟล์ mp3, wav, ogg, flac, m4a หรือ aac');const response=await fetch('/api/playroom/import',{method:'POST',headers:{'X-Filename':encodeURIComponent(file.name),'Content-Type':'application/octet-stream'},body:file});const result=await response.json();if(!response.ok || result.type!=='audio' || !safeUrl(result.url))throw Error('เพิ่มไฟล์เสียงไม่สำเร็จ');return result;}
 const codePattern=code=>new RegExp('(^|[^\\p{L}\\p{N}_])'+code.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'(?=$|[^\\p{L}\\p{N}_])','giu');
 function render(){
  const d=doc(),list=d.getElementById('secretSoundList'),limit=d.getElementById('secretSoundLimit'),button=document.getElementById('btnChatCodeMute');
  if(limit)limit.value=state.dailyLimit;
  if(button){button.classList.toggle('toggled-on',state.muted);button.setAttribute('aria-pressed',String(state.muted));button.title=state.muted?'เสียงโค้ดลับ: ปิด (คลิกเพื่อเปิด)':'เสียงโค้ดลับ: เปิด (คลิกเพื่อปิด)';}
  if(!list)return;list.replaceChildren();
  for(const entry of state.entries){
   const row=d.createElement('div');row.style.cssText='display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:8px 0;border-bottom:1px solid var(--dc-border)';
   const name=d.createElement('span');name.textContent=entry.code+' · '+entry.name+(entry.available===false?' (ไม่พบไฟล์)':'');name.style.flex='1 1 180px';row.append(name);
   const volume=d.createElement('input');volume.type='range';volume.min='0';volume.max='100';volume.value=String(Math.round((Number(entry.volume) || 0)*100));volume.setAttribute('aria-label','ความดัง '+entry.code);
   const volumeLabel=d.createElement('span');volumeLabel.textContent=volume.value+'%';volume.addEventListener('input',()=>{entry.volume=Number(volume.value)/100;volumeLabel.textContent=volume.value+'%';save();});row.append(volume,volumeLabel);
   const edit=d.createElement('button');edit.type='button';edit.className='btn-topbar-action';edit.textContent='แก้โค้ด';edit.onclick=()=>{const input=doc().defaultView.prompt('แก้โค้ดลับ',entry.code);if(input===null)return;const code=normalizeCode(input);if(!code || state.entries.some(other=>other!==entry && other.code.toLowerCase()===code.toLowerCase())){doc().getElementById('secretSoundStatus').textContent='โค้ดไม่ถูกต้องหรือซ้ำ';return;}entry.code=code;save();render();};row.append(edit);
   const replace=d.createElement('input');replace.type='file';replace.accept='audio/*,.mp3,.wav,.ogg,.flac,.m4a,.aac';replace.hidden=true;replace.addEventListener('change',async()=>{const file=replace.files[0];if(!file)return;try{const result=await importAudio(file);entry.url=result.url;entry.name=file.name;entry.available=true;save();render();}catch(error){doc().getElementById('secretSoundStatus').textContent=error.message || 'เปลี่ยนไฟล์ไม่สำเร็จ';}});const replaceButton=d.createElement('button');replaceButton.type='button';replaceButton.className='btn-topbar-action';replaceButton.textContent='เปลี่ยนไฟล์';replaceButton.onclick=()=>replace.click();row.append(replace,replaceButton);
   const test=d.createElement('button');test.type='button';test.className='btn-topbar-action';test.textContent='▶ ฟัง';test.disabled=!safeUrl(entry.url);test.onclick=()=>{const audio=new Audio(entry.url);audio.volume=Math.max(0,Math.min(1,Number(entry.volume) || 0));audio.play().catch(()=>{doc().getElementById('secretSoundStatus').textContent='เล่นไฟล์เสียงไม่สำเร็จ';});};row.append(test);
   const del=d.createElement('button');del.type='button';del.className='btn-topbar-action';del.textContent='ลบ';del.onclick=()=>{state.entries=state.entries.filter(item=>item!==entry);save();render();};row.append(del);list.append(row);
  }
 }
 function find(text){return [...state.entries].sort((a,b)=>b.code.length-a.code.length).find(entry=>entry.code && codePattern(entry.code).test(String(text||''))) || null;}
 function allowed(entry,author){
  if(!entry || state.muted || !safeUrl(entry.url))return false;
  if(!state.dailyLimit)return true;
  const today=new Date().toLocaleDateString('en-CA'),name=String(author||'').trim().toLowerCase(),id=name+'\u0000'+entry.code.toLowerCase();
  let usage;try{usage=JSON.parse(localStorage.getItem(usageKey)||'{}');}catch(_){usage={};}
  if(usage.date!==today)usage={date:today,counts:{}};usage.counts ||= {};
  if((usage.counts[id]||0)>=state.dailyLimit)return false;
  usage.counts[id]=(usage.counts[id]||0)+1;localStorage.setItem(usageKey,JSON.stringify(usage));return true;
 }
 window.BP3SecretSounds={
  match:find,
  strip(text,entry){return entry?String(text||'').replace(codePattern(entry.code),'$1 ').replace(/\s+/g,' ').trim():String(text||'');},
  reserve(entry,author){return allowed(entry,author);},
  toggleMute(){state.muted=!state.muted;save();render();if(state.muted)window.BP3ClearSecretSoundQueue?.();},
  muted(){return state.muted;}
 };
 window.toggleCodeMute=()=>window.BP3SecretSounds.toggleMute();
 window.addSecretSound=async()=>{
  const d=doc(),field=d.getElementById('secretSoundCode'),file=d.getElementById('secretSoundFile').files[0],status=d.getElementById('secretSoundStatus');
  const code=normalizeCode(field.value);
  if(!code || !file){status.textContent='กรุณาระบุโค้ดและเลือกไฟล์เสียง';return;}
  if(!/\.(mp3|wav|ogg|flac|m4a|aac)$/i.test(file.name)){status.textContent='รองรับไฟล์ mp3, wav, ogg, flac, m4a หรือ aac';return;}
  try{
   status.textContent='กำลังเพิ่มไฟล์เสียง...';
   const result=await importAudio(file);
   state.entries=state.entries.filter(entry=>entry.code.toLowerCase()!==code.toLowerCase());state.entries.push({code,name:file.name,url:result.url,volume:.8,available:true});save();field.value='';d.getElementById('secretSoundFile').value='';status.textContent='เพิ่มโค้ดเสียงแล้ว';render();
  }catch(error){status.textContent=error.message || 'เพิ่มไฟล์เสียงไม่สำเร็จ';}
 };
 function init(){const limit=document.getElementById('secretSoundLimit');limit?.addEventListener('change',()=>{state.dailyLimit=Math.max(0,Math.min(100,Number(limit.value)||0));save();render();});render();
  fetch('/api/legacy/secret-sounds').then(r=>r.ok?r.json():{}).then(data=>{if(!stored && data.found){state.entries=Array.isArray(data.entries)?data.entries:[];state.dailyLimit=Math.max(0,Math.min(100,Number(data.daily_limit)||0));state.muted=!!data.muted;save();stored=state;render();}}).catch(()=>{});
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
