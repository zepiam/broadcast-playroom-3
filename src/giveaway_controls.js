/* Giveaway: receive a code, collect unique names, draw from that list. */
(()=>{'use strict';
let settings={code:'#join',duration:0,display:'banner',imageUrl:'',drawStyle:'gachapon'};
try{Object.assign(settings,JSON.parse(localStorage.getItem('bp3_giveaway_settings')) || {});}catch{}
let wins=[],timer=null,deadline=0,saveTimer=null;
const doc=()=>getToolDocument('giveaway');
function persist(){
 const data={...settings};localStorage.setItem('bp3_giveaway_settings',JSON.stringify(data));
 if(window.ComposerStudio?.state)(ComposerStudio.state.legacyTools ||= {}).giveaway=data;
 clearTimeout(saveTimer);saveTimer=setTimeout(async()=>{try{const response=await fetch('/api/giveaway-settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});if(!response.ok)throw Error('บันทึกการตั้งค่า Giveaway ไม่สำเร็จ');}catch(error){showToast(error.message);}},150);
}
function renderSettings(){const d=doc();d.getElementById('gwInputCodeCustom').value=settings.code;d.getElementById('gwActiveCodeLabel').textContent=settings.code;d.getElementById('gwReceiveDuration').value=settings.duration;d.getElementById('gwDrawStyle').value=settings.drawStyle;d.querySelectorAll('[name="gwOverlayMode"]').forEach(input=>input.checked=input.value===settings.display);}
function renderHistory(){const d=doc(),body=d.getElementById('gwWinnerHistory');if(!body)return;body.replaceChildren();wins.forEach((person,index)=>{const row=d.createElement('tr');for(const value of [index+1,person.username,person.platform,person.time]){const cell=d.createElement('td');cell.textContent=String(value || '');row.append(cell);}body.append(row);});}
function updateButton(){const button=doc().getElementById('btnGwToggleLiveCode');if(button){button.textContent=window._isGwCodeBroadcasting?'ปิดรับโค้ด':'เปิดรับโค้ด';button.classList.toggle('active',!!window._isGwCodeBroadcasting);}}
window.setGiveawayCode=function(value){settings.code=String(value || '').trim();doc().getElementById('gwActiveCodeLabel').textContent=settings.code;persist();emitGwState();};
window.switchGwStep=()=>{};window.switchGwMainTab=()=>{};
window.getGwEligibleParticipants=()=>[...(window._gwParticipants || [])];
window.getGwOverlayOptions=()=>({drawId:wins.length,style:settings.drawStyle,candidates:(window._gwParticipants || []).map(person=>person.username+' ('+person.platform+')'),mode:'single',duration:settings.duration,remainingSec:deadline?Math.max(0,Math.ceil((deadline-Date.now())/1000)):0,config:{overlay_display_mode:settings.display,overlay_has_image:Boolean(settings.imageUrl),overlay_image_url:settings.imageUrl || ''}});
window.recordGwWinner=function(person){clearInterval(timer);deadline=0;window._isGwCodeBroadcasting=false;wins.push({username:person.username,platform:person.platform,time:new Date().toLocaleTimeString('th-TH')});renderHistory();updateButton();};
window.toggleGwLiveCode=function(){
 if(!window._isGwCodeBroadcasting && !settings.code){showToast('กรุณากรอกโค้ดเข้าร่วม');return;}
 window._isGwCodeBroadcasting=!window._isGwCodeBroadcasting;clearInterval(timer);deadline=window._isGwCodeBroadcasting && settings.duration>0?Date.now()+settings.duration*1000:0;updateButton();emitGwState();
 if(deadline)timer=setInterval(()=>{if(Date.now()>=deadline){clearInterval(timer);deadline=0;window._isGwCodeBroadcasting=false;updateButton();}emitGwState();},1000);
};
window.resetGiveaway=function(){clearInterval(timer);clearInterval(window._gwSpinTimer);deadline=0;window._isGwCodeBroadcasting=false;window._gwParticipants=[];wins=[];doc().getElementById('gwWinnerDisplay').textContent='ยังไม่ได้สุ่มชื่อ';updateButton();renderHistory();renderGwTable();emitGwState();};
window.exportGiveawayCsv=function(){
 const rows=[['ลำดับ','ชื่อผู้เข้าร่วม','แพลตฟอร์ม','เวลา']];(window._gwParticipants || []).forEach((person,index)=>rows.push([index+1,person.username,person.platform,person.time]));if(wins.length){rows.push([],['ประวัติการสุ่มชื่อ']);wins.forEach((person,index)=>rows.push([index+1,person.username,person.platform,person.time]));}
 const encode=value=>'"'+String(value ?? '').replace(/"/g,'""')+'"';const csv='\ufeff'+rows.map(row=>row.map(encode).join(',')).join('\r\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const d=doc(),anchor=d.createElement('a');anchor.href=url;anchor.download='giveaway-'+Date.now()+'.csv';d.body.append(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
};
window.BP3Giveaway={import(data){if(!data || typeof data!=='object')return;const incoming=data.settings || data;if(typeof incoming.code!=='string')return;Object.assign(settings,{code:incoming.code,duration:Number(incoming.duration)||0,display:incoming.display || 'banner',imageUrl:incoming.imageUrl || '',drawStyle:['gachapon','slot','shuffle'].includes(incoming.drawStyle)?incoming.drawStyle:'gachapon'});renderSettings();localStorage.setItem('bp3_giveaway_settings',JSON.stringify(settings));if(window.ComposerStudio?.state)(ComposerStudio.state.legacyTools ||= {}).giveaway={...settings};}};
function init(){
 renderSettings();renderHistory();updateButton();
 doc().getElementById('gwDrawStyle').onchange=event=>{settings.drawStyle=event.target.value;persist();};
 doc().getElementById('btnSaveGiveawaySettings').onclick=()=>{settings.duration=Math.max(0,Number(doc().getElementById('gwReceiveDuration').value)||0);settings.display=doc().querySelector('[name="gwOverlayMode"]:checked')?.value || 'banner';persist();emitGwState();showToast('บันทึกการตั้งค่าแล้ว');};
 doc().getElementById('btnGiveawayImportImage').onclick=()=>{const d=doc(),picker=d.createElement('input');picker.type='file';picker.accept='image/*';picker.hidden=true;d.body.append(picker);picker.onchange=async()=>{try{const file=picker.files[0];if(!file)return;if(!file.type.startsWith('image/'))throw Error('กรุณาเลือกไฟล์รูปภาพ');const response=await fetch('/api/playroom/import',{method:'POST',headers:{'Content-Type':'application/octet-stream','X-Filename':encodeURIComponent(file.name)},body:file});const image=await response.json();if(!response.ok)throw Error(image.error);settings.imageUrl=image.url;settings.display='image';persist();renderSettings();emitGwState();}catch(error){showToast(error.message);}finally{picker.remove();}};picker.click();};
 fetch('/api/giveaway-settings').then(response=>response.ok?response.json():null).then(data=>BP3Giveaway.import(data)).catch(()=>{});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
