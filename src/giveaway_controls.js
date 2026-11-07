/* Giveaway tool: set a code, collect unique viewers from chat, draw winners (no repeat winners by default).
 * One page with three steps. Overlay payload goes through emitGwState (GIVEAWAY_UPDATE), unchanged contract. */
(()=>{'use strict';
const STYLES=[
 {id:'gachapon',icon:'🎁',label:'กล่องปริศนา',hint:'เขย่ากล่อง ฝาเด้งเปิดพร้อมแสง ไม่แสดงรายชื่อ ใช้ได้กับทุกจำนวน'},
 {id:'slot',icon:'🎰',label:'สล็อตเลื่อนวน',hint:'รายชื่อจริงไหลผ่านแล้วชะลอหยุด เหมาะกับคนเยอะเป็นร้อย'},
 {id:'shuffle',icon:'🃏',label:'การ์ดพลิก',hint:'พลิกการ์ดเฉลยชื่อ ใช้ได้กับทุกจำนวน'},
 {id:'wheel',icon:'🎡',label:'วงล้อ',hint:'เหมาะกับไม่เกิน 12 คน ถ้ามากกว่านั้นแสดงเพียงบางชื่อ'}
];
// how many names each style can show readably: the wheel only a few slices, the reel scrolls through many real names
const SAMPLE_CAP={wheel:12,slot:60,shuffle:40,gachapon:40};
let drawTotal=0,drawIcons=null;
const DURATIONS=[[0,'ไม่จำกัดเวลา'],[60,'1 นาที'],[180,'3 นาที'],[300,'5 นาที'],[600,'10 นาที']];
const SAMPLE=['สมชายใจดี','น้องมะลิ','Gamer_01','PandaTV','ฟ้าใส','Kitty99','โอ๊ตสตรีม','มายด์'];
let settings={code:'#join',duration:0,display:'banner',imageUrl:'',drawStyle:'slot',drawTheme:'gold',drawFont:'prompt',exclude:true,calm:false,hold:15};
try{Object.assign(settings,JSON.parse(localStorage.getItem('bp3_giveaway_settings')) || {});}catch{}
if(!STYLES.some(s=>s.id===settings.drawStyle))settings.drawStyle='slot';
// winners survive a reload (so nobody wins twice by accident); entries older than 12 hours are ignored so a new stream starts fresh
const WINS_KEY='bp3_giveaway_wins';
function loadWins(){try{const raw=JSON.parse(localStorage.getItem(WINS_KEY))||[];const limit=Date.now()-12*3600*1000;return raw.filter(w=>w&&w.username&&Number(w.at)>limit).map(w=>({username:w.username,platform:w.platform,time:w.time,at:w.at}));}catch(_){return [];}}
function saveWins(){try{localStorage.setItem(WINS_KEY,JSON.stringify(wins.map(w=>({username:w.username,platform:w.platform,time:w.time,at:w.at}))));}catch(_){}}
const shown=()=>wins.filter(w=>!w.pending);
let wins=loadWins(),timer=null,deadline=0,saveTimer=null,drawing=false,drawTimer=0,drawSeq=0,drawPool=null,drawWinnerIndex=-1,imageName='';
const doc=()=>getToolDocument('giveaway');
const $=(id)=>doc().getElementById(id);
const keyOf=(p)=>String(p.username||'').toLowerCase().trim()+'|'+String(p.platform||'').toLowerCase().trim();
const label=(p)=>p.username+' ('+p.platform+')';
// platform logos shipped with the project (assets/platforms, assets/mylive.png); unknown platforms fall back to plain text
const PLAT={twitch:['Twitch','assets/platforms/twitch.png'],youtube:['YouTube','assets/platforms/youtube.png'],tiktok:['TikTok','assets/platforms/tiktok.png'],kick:['Kick','assets/platforms/kick.png'],facebook:['Facebook','assets/platforms/facebook.png'],soop:['SOOP','assets/platforms/soop.png'],mylive:['MyLive','assets/mylive.png']};
const platInfo=(v)=>PLAT[String(v||'').toLowerCase().trim()]||null;
const platIcon=(person)=>{const i=platInfo(person&&person.platform);return i?{src:i[1],name:i[0]}:null;};
// a table cell showing the platform as a logo with an accessible name, text only for unknown platforms
function platCell(d,v){const c=d.createElement('td');const i=platInfo(v);if(i){const im=d.createElement('img');im.src=i[1];im.alt=i[0];im.title=i[0];im.className='gw-plat';im.addEventListener('error',()=>{const t=d.createElement('span');t.textContent=i[0];im.replaceWith(t);});c.append(im);}else c.textContent=String(v||'');return c;}
const V=()=>window.BP3RandomizerVisual;
const fmt=(s)=>String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');
function announce(text){const d=doc();let box=d.getElementById('gwAnnounce');if(!box){box=d.createElement('div');box.id='gwAnnounce';box.setAttribute('role','status');box.setAttribute('aria-live','polite');box.style.cssText='position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);';(d.getElementById('gwBody')||d.body).append(box);}box.textContent='';setTimeout(()=>{box.textContent=text;},40);}
function persist(){
 const data={...settings};localStorage.setItem('bp3_giveaway_settings',JSON.stringify(data));
 if(window.ComposerStudio?.state)(ComposerStudio.state.legacyTools ||= {}).giveaway=data;
 clearTimeout(saveTimer);saveTimer=setTimeout(async()=>{try{const response=await fetch('/api/giveaway-settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});if(!response.ok)throw Error('บันทึกการตั้งค่า Giveaway ไม่สำเร็จ');}catch(error){showToast(error.message);}},150);
}
const participants=()=>window._gwParticipants || [];
function eligible(){const won=new Set(wins.map(keyOf));return settings.exclude?participants().filter(p=>!won.has(keyOf(p))):[...participants()];}
/* ---------- rendering ---------- */
function renderSettings(){
 const d=doc(),q=(id)=>d.getElementById(id);if(!q('gwInputCodeCustom'))return;
 q('gwInputCodeCustom').value=settings.code;q('gwActiveCodeLabel').textContent=settings.code;q('gwReceiveDuration').value=settings.duration;
 q('gwDrawStyle').value=settings.drawStyle;
 d.querySelectorAll('[name="gwOverlayMode"]').forEach(input=>input.checked=input.value===settings.display);
 d.querySelectorAll('[name="gwStyle"]').forEach(input=>input.checked=input.value===settings.drawStyle);
 if(q('gwDrawTheme'))q('gwDrawTheme').value=settings.drawTheme;
 d.querySelectorAll('[name="gwFont"]').forEach(input=>input.checked=input.value===settings.drawFont);
 if(q('chkGwExclude'))q('chkGwExclude').checked=!!settings.exclude;
 if(q('chkGwCalm'))q('chkGwCalm').checked=!!settings.calm;
 if(q('gwHold'))q('gwHold').value=String(settings.hold);
 d.querySelectorAll('#gwDurationChips button').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.sec)===Number(settings.duration))));
 if(q('gwImageName'))q('gwImageName').textContent=settings.imageUrl?('ใช้ภาพ: '+(imageName||'ภาพที่เลือกไว้แล้ว')):'';
}
function renderHistory(){const d=doc(),body=d.getElementById('gwWinnerHistory');if(!body)return;body.replaceChildren();
 if(!shown().length){const row=d.createElement('tr'),cell=d.createElement('td');cell.colSpan=4;cell.className='gw-empty';cell.textContent='ยังไม่มีผู้ชนะ';row.append(cell);body.append(row);return;}
 shown().forEach((person,index)=>{const row=d.createElement('tr');[index+1,person.username,person.platform,person.time].forEach((value,col)=>{let cell;if(col===2)cell=platCell(d,value);else{cell=d.createElement('td');cell.textContent=String(value || '');}row.append(cell);});body.append(row);});}
function updateButton(){const button=doc().getElementById('btnGwToggleLiveCode');if(!button)return;const on=!!window._isGwCodeBroadcasting;button.textContent=on?'ปิดรับโค้ด':'เปิดรับโค้ด';button.setAttribute('aria-pressed',String(on));button.classList.toggle('active',on);}
function updateStatus(){
 const d=doc(),bar=d.getElementById('gwStatusBar'),text=d.getElementById('gwStatusText'),meta=d.getElementById('gwStatusMeta');if(!bar)return;
 const n=participants().length,on=!!window._isGwCodeBroadcasting;let state='idle',msg,extra='';
 if(drawing){state='winner';msg='กำลังสุ่มผู้โชคดี...';}
 else if(on){state='open';msg='กำลังเปิดรับ พิมพ์ '+settings.code+' ในแชท';extra=n+' คน'+(deadline?' เหลือ '+fmt(Math.max(0,Math.ceil((deadline-Date.now())/1000))):'');}
 else if(shown().length&&drawSeq&&shown()[shown().length-1]){state='winner';msg='ประกาศผู้ชนะแล้ว '+shown()[shown().length-1].username;extra=n+' คนเข้าร่วม';}
 else if(n){msg='ปิดรับแล้ว มีผู้เข้าร่วม '+n+' คน พร้อมสุ่ม';}
 else msg='ยังไม่เปิดรับรายชื่อ';
 bar.dataset.state=state;if(text.textContent!==msg)text.textContent=msg;meta.textContent=extra;
}
function renderTable(){
 const d=doc(),tbody=d.getElementById('gwTableBody'),list=participants();
 const count=d.getElementById('gwParticipantCount');if(count)count.textContent=list.length+' คน';
 const pool=eligible(),el=d.getElementById('gwEligibleCount');if(el)el.textContent=String(pool.length);
 const draw=d.getElementById('btnGwDraw');if(draw){draw.setAttribute('aria-disabled',String(!pool.length||drawing));}
 const line=d.getElementById('gwEligibleLine');if(line){line.classList.toggle('warn',list.length>0&&!pool.length);let note=d.getElementById('gwStyleNote');if(!note&&line){note=d.createElement('span');note.id='gwStyleNote';note.style.display='block';line.appendChild(note);}
  if(note){note.textContent=(settings.drawStyle==='wheel'&&pool.length>12)?'มีผู้มีสิทธิ์มากกว่า 12 คน วงล้อจะแสดงเพียง 12 ชื่อ แต่ผู้ชนะยังสุ่มจากทุกคน แนะนำเปลี่ยนเป็นสล็อตเลื่อนวน':'';}}
 if(tbody){tbody.replaceChildren();
  if(!list.length){const row=d.createElement('tr'),cell=d.createElement('td');cell.colSpan=6;cell.className='gw-empty';cell.textContent='ยังไม่มีผู้เข้าร่วม กดเปิดรับโค้ด แล้วให้ผู้ชมพิมพ์โค้ดในแชท';row.append(cell);tbody.append(row);}
  else{const won=new Set(shown().map(keyOf));
   list.forEach((p,index)=>{const row=d.createElement('tr');
    [index+1,p.username,p.platform,p.time].forEach((value,col)=>{let c;if(col===2)c=platCell(d,value);else{c=d.createElement('td');c.textContent=String(value ?? '');}row.append(c);});
    const st=d.createElement('td');if(won.has(keyOf(p))){const b=d.createElement('span');b.className='gw-badge';b.textContent='ชนะแล้ว';st.append(b);}row.append(st);
    const act=d.createElement('td'),btn=d.createElement('button');btn.type='button';btn.className='btn-topbar-action gw-rm';btn.textContent='ลบ';btn.setAttribute('aria-label','ลบ '+p.username+' ออกจากรายชื่อ');btn.addEventListener('click',()=>removeEntrant(p.id,btn));act.append(btn);row.append(act);tbody.append(row);});}
 }
 updateStatus();refreshPreviewSoon();
}
window.renderGwTable=renderTable;
function removeEntrant(id,btn){
 const list=participants(),index=list.findIndex(p=>p.id===id);if(index<0)return;const name=list[index].username;
 window._gwParticipants=list.filter(p=>p.id!==id);renderTable();emitGwState();announce('ลบ '+name+' ออกจากรายชื่อแล้ว');
 const d=doc(),buttons=d.querySelectorAll('#gwTableBody .gw-rm');(buttons[Math.min(index,buttons.length-1)]||d.getElementById('btnGwToggleLiveCode'))?.focus();
}
window.removeGwEntrant=(id)=>removeEntrant(id);
/* ---------- overlay payload ---------- */
window.setGiveawayCode=function(value){settings.code=String(value || '').trim();const l=doc().getElementById('gwActiveCodeLabel');if(l)l.textContent=settings.code;persist();updateStatus();emitGwState();};
window.switchGwStep=()=>{};window.switchGwMainTab=()=>{};
window.getGwEligibleParticipants=()=>eligible();
window.getGwOverlayOptions=()=>({drawId:drawSeq,style:settings.drawStyle,candidates:(drawPool || participants().map(label)),total:drawPool?drawTotal:undefined,icons:drawPool?drawIcons:undefined,winnerIndex:drawWinnerIndex,mode:'single',duration:settings.duration,holdDuration:settings.hold,remainingSec:deadline?Math.max(0,Math.ceil((deadline-Date.now())/1000)):0,config:{overlay_display_mode:settings.display,overlay_has_image:Boolean(settings.imageUrl),overlay_image_url:settings.imageUrl || '',draw_theme:settings.drawTheme,draw_font:settings.drawFont,draw_calm:!!settings.calm}});
window.recordGwWinner=function(person){wins.push({username:person.username,platform:person.platform,time:new Date().toLocaleTimeString('th-TH'),at:Date.now()});saveWins();renderHistory();updateButton();};
function stopReceiving(){clearInterval(timer);deadline=0;window._isGwCodeBroadcasting=false;updateButton();}
window.toggleGwLiveCode=function(){
 if(drawing)return;
 if(!window._isGwCodeBroadcasting && !settings.code){showToast('กรุณากรอกโค้ดเข้าร่วม');announce('กรุณากรอกโค้ดเข้าร่วมก่อน');doc().getElementById('gwInputCodeCustom')?.focus();return;}
 const opening=!window._isGwCodeBroadcasting;
 clearInterval(timer);
 if(opening){drawPool=null;drawWinnerIndex=-1;}
 window._isGwCodeBroadcasting=opening;deadline=opening && settings.duration>0?Date.now()+settings.duration*1000:0;updateButton();updateStatus();emitGwState();
 announce(opening?('เปิดรับรายชื่อแล้ว ให้ผู้ชมพิมพ์ '+settings.code):('ปิดรับรายชื่อแล้ว มีผู้เข้าร่วม '+participants().length+' คน'));
 if(opening)timer=setInterval(()=>{if(deadline&&Date.now()>=deadline){stopReceiving();updateStatus();emitGwState();announce('หมดเวลา ปิดรับรายชื่ออัตโนมัติ มีผู้เข้าร่วม '+participants().length+' คน');return;}updateStatus();emitGwState();},1000);
};
window.resetGiveaway=function(){
 clearInterval(timer);clearTimeout(drawTimer);clearInterval(window._gwSpinTimer);deadline=0;drawing=false;drawPool=null;drawWinnerIndex=-1;window._isGwCodeBroadcasting=false;window._gwParticipants=[];wins=[];saveWins();
 const w=doc().getElementById('gwWinnerDisplay');if(w){w.textContent='ยังไม่ได้สุ่มผู้ชนะ';w.dataset.has='0';}
 hideConfirm(false);updateButton();renderHistory();renderTable();emitGwState();announce('ล้างรายชื่อและประวัติผู้ชนะทั้งหมดแล้ว');
 doc().getElementById('btnGwToggleLiveCode')?.focus();
};
function showWinner(person,n){
 const d=doc(),box=d.getElementById('gwWinnerDisplay');if(!box)return;box.replaceChildren();box.dataset.has='1';
 const a=d.createElement('span');a.textContent='ผู้โชคดีคนที่ '+n;const b=d.createElement('b');b.textContent=person.username;const c=d.createElement('span');const pi=platInfo(person.platform);if(pi){const im=d.createElement('img');im.src=pi[1];im.alt='แพลตฟอร์ม '+pi[0];im.title=pi[0];im.className='gw-plat';c.append(im);}else c.textContent='แพลตฟอร์ม '+person.platform;box.append(a,b,c);
}
window.rerollGwWinner=function(){
 if(drawing)return;
 const pool=eligible();
 if(!pool.length){
  const msg=participants().length?'ทุกคนในรายชื่อชนะไปแล้ว ปิดตัวเลือก ไม่ให้คนเดิมชนะซ้ำ หรือเปิดรับรายชื่อเพิ่ม':'ยังไม่มีผู้เข้าร่วม กดเปิดรับโค้ดแล้วให้ผู้ชมพิมพ์โค้ดในแชทก่อน';
  const box=doc().getElementById('gwWinnerDisplay');if(box){box.textContent=msg;box.dataset.has='0';}showToast(msg);return;
 }
 const picked=pool[Math.floor(Math.random()*pool.length)];
 stopReceiving();
 // the overlay shows a sample of the pool; the winner is always in it
 const winnerName=label(picked);const shortWinner=String(picked.username);let entries=pool.map(p=>({n:String(p.username),i:platIcon(p)}));const winEntry=entries.find(e=>e.n===shortWinner&&pool.indexOf(picked)===entries.indexOf(e))||entries[pool.indexOf(picked)];
 const cap=SAMPLE_CAP[settings.drawStyle]||40;drawTotal=entries.length;if(entries.length>cap){const rest=entries.filter(e=>e!==winEntry).sort(()=>Math.random()-0.5).slice(0,cap-1);entries=[winEntry,...rest].sort(()=>Math.random()-0.5);}const names=entries.map(e=>e.n);drawIcons=entries.map(e=>e.i);
 drawPool=names;drawWinnerIndex=entries.indexOf(winEntry);drawSeq++;drawing=true;
 // counted as a winner right away (hidden from the list until the reveal) so a closed window or reload cannot let the same person win again
 const entry={username:picked.username,platform:picked.platform,time:new Date().toLocaleTimeString('th-TH'),at:Date.now(),pending:true};wins.push(entry);saveWins();
 const box=doc().getElementById('gwWinnerDisplay');if(box){box.textContent='กำลังสุ่มผู้โชคดี...';box.dataset.has='0';}
 updateStatus();renderTable();
 emitGwState(winnerName);
 playInPanel();
 const calm=settings.calm||(window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches);
 drawTimer=setTimeout(()=>{
  drawing=false;entry.pending=false;saveWins();renderHistory();updateButton();showWinner(picked,shown().length);renderTable();
  showToast('ผู้โชคดีคือ '+winnerName);announce('ผู้โชคดีคือ '+picked.username+' จาก '+picked.platform);
  try{appendActivityEvent({event:'giveaway_winner',username:picked.username,platform:picked.platform,text:'',time:new Date().toLocaleTimeString()});}catch(_){}
 },calm?900:5800);
};
window.exportGiveawayCsv=function(){
 const rows=[['ลำดับ','ชื่อผู้เข้าร่วม','แพลตฟอร์ม','เวลา']];participants().forEach((person,index)=>rows.push([index+1,person.username,person.platform,person.time]));if(shown().length){rows.push([],['ประวัติผู้ชนะ']);shown().forEach((person,index)=>rows.push([index+1,person.username,person.platform,person.time]));}
 const encode=value=>'"'+String(value ?? '').replace(/"/g,'""')+'"';const csv='﻿'+rows.map(row=>row.map(encode).join(',')).join('\r\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const d=doc(),anchor=d.createElement('a');anchor.href=url;anchor.download='giveaway-'+Date.now()+'.csv';d.body.append(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);announce('ส่งออกไฟล์ CSV แล้ว');
};
window.BP3Giveaway={import(data){if(!data || typeof data!=='object')return;const incoming=data.settings || data;if(typeof incoming.code!=='string')return;
 Object.assign(settings,{code:incoming.code,duration:Number(incoming.duration)||0,display:incoming.display || 'banner',imageUrl:incoming.imageUrl || ''});
 if(STYLES.some(s=>s.id===incoming.drawStyle))settings.drawStyle=incoming.drawStyle;
 if(V()?.THEMES[incoming.drawTheme])settings.drawTheme=incoming.drawTheme;
 if(V()?.FONTS&&V().FONTS[incoming.drawFont])settings.drawFont=incoming.drawFont;
 if(typeof incoming.exclude==='boolean')settings.exclude=incoming.exclude;if(typeof incoming.calm==='boolean')settings.calm=incoming.calm;if(Number.isFinite(Number(incoming.hold)))settings.hold=Number(incoming.hold);
 renderSettings();localStorage.setItem('bp3_giveaway_settings',JSON.stringify(settings));if(window.ComposerStudio?.state)(ComposerStudio.state.legacyTools ||= {}).giveaway={...settings};}};
/* ---------- live preview of the winner announcement ---------- */
let ctl=null,fitBox=null,previewTimer=0;
function sampleNames(){const names=participants().map(p=>p.username).slice(0,12);return names.length>=2?names:SAMPLE;}
function previewData(idx){const items=sampleNames();return {title:'ประกาศผู้โชคดี',items,winnerIndex:Math.min(idx||0,items.length-1),settings:{style:settings.drawStyle,color_theme:settings.drawTheme,font:settings.drawFont,spin_duration:5,duration:60,reduce_motion:!!settings.calm,scale:100}};}
const LABELS={winner:'ผู้โชคดี',live:'ผู้โชคดี',done:'ประกาศผู้ชนะแล้ว',idle:'พร้อมสุ่ม',running:'กำลังสุ่ม...'};
function fit(){if(!ctl||!fitBox)return;const stage=fitBox.parentElement,avail=Math.max(160,stage.clientWidth-22),nat=ctl.naturalSize();const s=Math.max(0.2,Math.min(avail/640,480/Math.max(1,nat.h||700),1));ctl.setFit(s);fitBox.style.width=Math.round(640*s)+'px';fitBox.style.height=Math.round((nat.h||700)*s)+'px';}
function mount(){const stage=$('gwStage'),v=V();if(!stage||!v||ctl)return;fitBox=doc().createElement('div');fitBox.className='rz-fit';stage.append(fitBox);
 try{ctl=v.create(fitBox,previewData(0),{position:'static',keepVisible:true,labels:LABELS,onDone:()=>{const b=$('btnGwPreview');if(b)b.textContent='ดูตัวอย่างอีกครั้ง';}}).show();fit();}catch(e){console.warn('giveaway preview',e);}
 if(window.ResizeObserver)new ResizeObserver(fit).observe(stage);}
// the real draw also plays in the panel's own stage so the operator sees the suspense even when OBS is not on screen
function playInPanel(){if(!ctl||!drawPool)return;try{if(ctl.running)ctl.stop();ctl.setLook({title:'ประกาศผู้โชคดี',items:drawPool,total:drawTotal,icons:drawIcons,winnerIndex:drawWinnerIndex,settings:{style:settings.drawStyle,color_theme:settings.drawTheme,font:settings.drawFont,spin_duration:5,duration:60,reduce_motion:!!settings.calm,scale:100}});fit();ctl.start();const b=$('btnGwPreview');if(b)b.textContent='หยุดตัวอย่าง';const st=$('gwStage');if(st&&st.scrollIntoView)st.scrollIntoView({block:'nearest',behavior:'auto'});}catch(e){console.warn('giveaway panel draw',e);}}
function refreshPreview(){if(!ctl)return;if(ctl.running)return;ctl.setLook(previewData(0));const b=$('btnGwPreview');if(b)b.textContent='ดูตัวอย่างการสุ่ม ไม่ขึ้นจอ OBS';fit();}
function refreshPreviewSoon(){clearTimeout(previewTimer);previewTimer=setTimeout(refreshPreview,160);}
/* ---------- wiring ---------- */
function hideConfirm(focus){const c=doc().getElementById('gwResetConfirm');if(c)c.classList.remove('show');if(focus)doc().getElementById('btnGwAskReset')?.focus();}
function init(){
 const d=doc();if(!d.getElementById('gwInputCodeCustom'))return;
 const v=V();
 // draw style cards (hidden select stays as the stored value)
 const list=d.getElementById('gwStyleList');
 STYLES.forEach(s=>{const l=d.createElement('label');l.className='rz-opt';const i=d.createElement('input');i.type='radio';i.name='gwStyle';i.value=s.id;i.checked=settings.drawStyle===s.id;
  const f=d.createElement('span');f.className='rz-face';f.innerHTML='<span class="rz-face-icon" aria-hidden="true">'+s.icon+'</span><span class="rz-face-name">'+s.label+'</span><span class="rz-face-hint">'+s.hint+'</span><span class="rz-check" aria-hidden="true">✓</span>';l.append(i,f);list.append(l);});
 list.addEventListener('change',e=>{if(e.target.name!=='gwStyle')return;settings.drawStyle=e.target.value;d.getElementById('gwDrawStyle').value=settings.drawStyle;persist();renderTable();refreshPreview();emitGwState();});
 const theme=d.getElementById('gwDrawTheme');if(v)Object.entries(v.THEMES).forEach(([id,t])=>theme.add(new Option(t.label,id)));

 theme.addEventListener('change',()=>{settings.drawTheme=theme.value;persist();refreshPreview();});
 const fl=d.getElementById('gwFontList');
 if(fl&&v&&v.FONTS){Object.entries(v.FONTS).forEach(([id,f])=>{const l=d.createElement('label');l.className='rz-opt';const i=d.createElement('input');i.type='radio';i.name='gwFont';i.value=id;i.checked=settings.drawFont===id;
  const face=d.createElement('span');face.className='rz-face gw-fontface';const sample=d.createElement('span');sample.className='gw-fontsample';sample.textContent='ผู้โชคดี Aa';sample.style.fontFamily=f.family+",'Noto Sans Thai',sans-serif";
  const nm=d.createElement('span');nm.className='rz-face-hint';nm.textContent=f.label;const ck=d.createElement('span');ck.className='rz-check';ck.setAttribute('aria-hidden','true');ck.textContent='✓';face.append(sample,nm,ck);l.append(i,face);fl.append(l);v.loadFont(d,id);});
  fl.addEventListener('change',e=>{if(e.target.name!=='gwFont')return;settings.drawFont=e.target.value;persist();refreshPreview();emitGwState();});}
 d.getElementById('chkGwExclude').addEventListener('change',e=>{settings.exclude=e.target.checked;persist();renderTable();announce(settings.exclude?'เปิด ไม่ให้คนเดิมชนะซ้ำ':'ปิด ไม่ให้คนเดิมชนะซ้ำ');});
 d.getElementById('chkGwCalm').addEventListener('change',e=>{settings.calm=e.target.checked;persist();refreshPreview();});
 d.getElementById('gwHold').addEventListener('change',e=>{settings.hold=Number(e.target.value)||0;persist();});
 // auto-close chips
 const chips=d.getElementById('gwDurationChips');
 DURATIONS.forEach(([sec,name])=>{const b=d.createElement('button');b.type='button';b.className='btn-topbar-action';b.dataset.sec=sec;b.textContent=name;b.addEventListener('click',()=>{settings.duration=sec;d.getElementById('gwReceiveDuration').value=sec;persist();renderSettings();emitGwState();});chips.append(b);});
 const saveGw=()=>{settings.duration=Math.max(0,Math.min(86400,Math.round(Number(d.getElementById('gwReceiveDuration')?.value)||0)));settings.display=d.querySelector('[name="gwOverlayMode"]:checked')?.value || 'banner';persist();renderSettings();emitGwState();};
 d.getElementById('gwReceiveDuration').addEventListener('change',saveGw);
 d.querySelectorAll('[name="gwOverlayMode"]').forEach(r=>r.addEventListener('change',saveGw));
 d.getElementById('btnGiveawayImportImage').onclick=()=>{const picker=d.createElement('input');picker.type='file';picker.accept='image/*';picker.hidden=true;d.body.append(picker);picker.onchange=async()=>{try{const file=picker.files[0];if(!file)return;if(!file.type.startsWith('image/'))throw Error('กรุณาเลือกไฟล์รูปภาพ');const response=await fetch('/api/playroom/import',{method:'POST',headers:{'Content-Type':'application/octet-stream','X-Filename':encodeURIComponent(file.name)},body:file});const image=await response.json();if(!response.ok)throw Error(image.error);imageName=file.name;settings.imageUrl=image.url;settings.display='image';persist();renderSettings();emitGwState();announce('เลือกภาพแบนเนอร์แล้ว '+file.name);}catch(error){showToast(error.message);announce(error.message);}finally{picker.remove();}};picker.click();};
 // reset needs a second click
 d.getElementById('btnGwAskReset').addEventListener('click',()=>{if(!participants().length&&!shown().length){announce('ไม่มีรายชื่อให้ล้าง');return;}d.getElementById('gwResetConfirm').classList.add('show');d.getElementById('btnGwResetNo').focus();});
 d.getElementById('btnGwResetNo').addEventListener('click',()=>hideConfirm(true));
 d.getElementById('gwResetConfirm').addEventListener('keydown',e=>{if(e.key==='Escape'){e.stopPropagation();hideConfirm(true);}});
 const drawBtn=d.getElementById('btnGwDraw');drawBtn.addEventListener('click',e=>{if(drawBtn.getAttribute('aria-disabled')==='true'){e.preventDefault();e.stopImmediatePropagation();if(!drawing)window.rerollGwWinner();}},true);
 d.getElementById('btnGwPreview').addEventListener('click',()=>{if(!ctl)return;if(ctl.running){ctl.stop();refreshPreview();return;}const n=sampleNames().length;ctl.setLook(previewData(Math.floor(Math.random()*n)));fit();ctl.start();d.getElementById('btnGwPreview').textContent='หยุดตัวอย่าง';});
 renderSettings();renderHistory();updateButton();renderTable();mount();
 fetch('/api/giveaway-settings').then(response=>response.ok?response.json():null).then(data=>{window.BP3Giveaway.import(data);refreshPreview();}).catch(()=>{});
}
window.BP3GiveawayUI={get settings(){return {...settings};},get wins(){return [...wins];},eligible};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
