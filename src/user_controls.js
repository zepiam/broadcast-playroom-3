/* Real viewer roster, profile blocking and CSV export. */
(()=>{
'use strict';
const read=(key,fallback)=>{try{return JSON.parse(localStorage.getItem(key)) ?? fallback;}catch{return fallback;}};
const people=new Map(read('bp3_user_roster',[]).map(person=>[person.platform.toLowerCase()+':'+person.username.toLowerCase(),person]));
const CHAT_RETENTION_MS=7*24*60*60*1000;
function pruneViewerChatHistory(now=Date.now()){
 let changed=false;
 for(const person of people.values()){
  if(!Array.isArray(person.history))continue;
  const retained=person.history.filter(item=>item?.event && item.event!=='message' || item?.time==null || !Number.isFinite(Number(item.time)) || Number(item.time)>=now-CHAT_RETENTION_MS);
  if(retained.length!==person.history.length){person.history=retained;changed=true;}
 }
 if(changed){try{localStorage.setItem('bp3_user_roster',JSON.stringify([...people.values()]));}catch{}}
}
pruneViewerChatHistory();
setInterval(pruneViewerChatHistory,60*60*1000);
window._blockedUsers=read('bp3_blocked_users',{});
const isBlocked=name=>Object.values(window.BP3Blacklist.classify({username:name}).rule).some(Boolean);
let query='',category='all',renderTimer=null,saveTimer=null;
const tool=()=>window._toolWindowNodes?.['user-manager'] || getToolDocument('user-manager').getElementById('win-user-manager');
const save=()=>{try{localStorage.setItem('bp3_user_roster',JSON.stringify([...people.values()]));}catch{try{localStorage.setItem('bp3_user_roster',JSON.stringify([...people.values()].map(person=>({...person,history:(person.history || []).slice(-1)}))));}catch{}}};
const cell=(doc,value)=>{const td=doc.createElement('td');td.textContent=String(value ?? '');return td;};
function render(){
 const root=tool();if(!root)return;const doc=root.ownerDocument,body=root.querySelector('#userRosterBody');if(!body)return;body.replaceChildren();
 const list=[...people.values()].sort((a,b)=>b.lastSeen-a.lastSeen);
 const matches=list.filter(person=>{const blocked=isBlocked(person.username);const text=[person.username,getEffectiveAuthorName(person.username),person.platform].join(' ').toLowerCase();return text.includes(query) && (category==='blocked'?blocked:category==='vip'?person.isVip:category==='active'?Date.now()-person.lastSeen<5*60*1000:true);});
 const fragment=doc.createDocumentFragment();
 for(const person of matches){const row=doc.createElement('tr');row.className='user-row';row.dataset.name=person.username.toLowerCase();row.dataset.vip=String(!!person.isVip);
  const name=cell(doc,person.username);name.style.cursor='pointer';name.onclick=()=>openAuthorModal(person.username,person.platform,person.avatar,getEffectiveAuthorName(person.username),person.isVip);
  const nickname=cell(doc,getEffectiveAuthorName(person.username)===person.username?'-':getEffectiveAuthorName(person.username));nickname.style.color='#38bdf8';nickname.style.cursor='pointer';nickname.onclick=()=>editUserNickname(person.username);
  row.append(name,nickname,cell(doc,person.platform),cell(doc,person.count),cell(doc,isBlocked(person.username)?'บล็อก':person.isVip?'VIP':'คนดูทั่วไป'),cell(doc,new Date(person.lastSeen).toLocaleTimeString()));
  const action=doc.createElement('button');action.className='btn-topbar-action';action.textContent='โปรไฟล์';action.onclick=name.onclick;const actions=cell(doc,'');actions.append(action);row.append(actions);fragment.append(row);
 }body.append(fragment);
 const counts={all:list.length,vip:list.filter(person=>person.isVip).length,blocked:list.filter(person=>isBlocked(person.username)).length,active:list.filter(person=>Date.now()-person.lastSeen<5*60*1000).length};for(const [cat,id,label] of [['all','btnFilterAll','ทั้งหมด'],['vip','btnFilterVip','🌟 ผู้สนับสนุน'],['blocked','btnFilterBlocked','🛑 ถูกบล็อก'],['active','btnFilterActive','🟢 ล่าสุด']]){const button=root.querySelector('#'+id);if(button)button.textContent=label+' ('+counts[cat]+')';}
 root.querySelectorAll('.win-tabs .win-tab-btn').forEach(button=>button.classList.remove('active'));
 root.querySelector('#'+({all:'btnFilterAll',vip:'btnFilterVip',blocked:'btnFilterBlocked',active:'btnFilterActive'}[category] || 'btnFilterAll'))?.classList.add('active');
}
function schedule(){clearTimeout(saveTimer);saveTimer=setTimeout(save,250);const popup=window._popoutWindows?.['user-manager'];if(!popup || popup.closed)return;if(renderTimer)return;renderTimer=setTimeout(()=>{renderTimer=null;render();},150);}
window.registerUserToRoster=function(msg){if(!msg?.username || ['คุณ','HOST'].includes(msg.username))return;const platform=String(msg.platform || 'Twitch'),key=platform.toLowerCase()+':'+msg.username.toLowerCase();const previous=people.get(key);people.set(key,{username:msg.username,platform,avatar:msg.avatar || '',isVip:previous?.isVip || !!msg.isVip,count:(previous?.count || 0)+1,lastSeen:Date.now(),joinCount:previous?.joinCount || 0,history:[...(previous?.history || []),{text:window.BP3ChatContent.historyText(msg),event:msg.event || 'message',time:Date.now()}].slice(-10)});schedule();};
function renderBlockedSettings(){
 const doc=getToolDocument('settings'),body=doc.getElementById('blockedViewerList');if(!body)return;
 body.replaceChildren();
 const botNames=new Set(window.BP3Blacklist.botNames());
 const names=[...new Set([...Object.keys(window._blockedUsers).filter(name=>window._blockedUsers[name]),...botNames])].sort((a,b)=>a.localeCompare(b));
 for(const name of names){
  const row=doc.createElement('tr');row.append(cell(doc,name));
  for(const [field,label] of [['replie','Replie'],['overlay','Overlay'],['tts','TTS'],['all','ทุกส่วน']]){
   const td=cell(doc,''),checkbox=doc.createElement('input');checkbox.type='checkbox';checkbox.setAttribute('aria-label','บล็อก '+label+' '+name);checkbox.checked=window.BP3Blacklist.classify({username:name}).rule[field];
   checkbox.addEventListener('change',()=>{const rule={...window.BP3Blacklist.classify({username:name}).rule};rule[field]=checkbox.checked;window._blockedUsers[name]=rule;localStorage.setItem('bp3_blocked_users',JSON.stringify(window._blockedUsers));window.BP3SyncBotBlocklist?.();window.BP3PruneBlockedSpeech?.();render();});td.append(checkbox);row.append(td);
  }
  const action=cell(doc,''),button=doc.createElement('button');button.className='btn-topbar-action';button.textContent=botNames.has(name)?'คืนค่าเริ่มต้น':'ปลดบล็อก';button.onclick=()=>{delete window._blockedUsers[name];localStorage.setItem('bp3_blocked_users',JSON.stringify(window._blockedUsers));window.BP3SyncBotBlocklist?.();window.BP3PruneBlockedSpeech?.();renderBlockedSettings();render();};action.append(button);row.append(action);body.append(row);
 }
}
window.BP3RefreshBlockedSettings=renderBlockedSettings;
window.blockViewerFromSettings=function(){
 const doc=getToolDocument('settings'),field=doc.getElementById('blockedViewerName'),name=String(field?.value || '').trim().toLowerCase();
 if(!name){doc.defaultView.alert('กรุณาพิมพ์ชื่อคนดูที่ต้องการบล็อก');return;}
 window._blockedUsers[name]=true;localStorage.setItem('bp3_blocked_users',JSON.stringify(window._blockedUsers));window.BP3SyncBotBlocklist?.();window.BP3PruneBlockedSpeech?.();field.value='';renderBlockedSettings();render();
};
window.filterUserRoster=value=>{query=String(value || '').toLowerCase().trim();render();};
window.filterUserCategory=value=>{category=value;render();};
window.blockUserFromProfile=function(){
 const name=_activeUserRecord?.username;if(!name)return;
 const doc=getToolDocument('author-profile'),root=doc.getElementById('win-author-profile');if(!root)return;
 let panel=root.querySelector('#profileBlockRules');if(panel){panel.remove();return;}
 panel=doc.createElement('div');panel.id='profileBlockRules';panel.style.cssText='padding:12px;display:flex;flex-wrap:wrap;gap:12px;border-top:1px solid #444';
 const rule=window.BP3Blacklist.classify({username:name}).rule;
 for(const [field,label] of [['replie','ไม่ให้ใช้คำสั่ง Replie'],['overlay','ไม่ให้ขึ้น Overlay'],['tts','ไม่ให้อ่าน TTS'],['all','ไม่อนุญาตทุกส่วน']]){
  const wrapper=doc.createElement('label'),checkbox=doc.createElement('input');checkbox.type='checkbox';checkbox.dataset.blockRule=field;checkbox.checked=!!rule[field];wrapper.append(checkbox,doc.createTextNode(' '+label));panel.append(wrapper);
 }
 const saveButton=doc.createElement('button');saveButton.type='button';saveButton.className='btn-topbar-action primary';saveButton.textContent='บันทึกการบล็อก';saveButton.onclick=()=>{
  const values={};panel.querySelectorAll('input[data-block-rule]').forEach(box=>values[box.dataset.blockRule]=box.checked);
  const key=name.toLowerCase();if(Object.values(values).some(Boolean))window._blockedUsers[key]=values;else if(window.BP3Blacklist.classify({username:key}).bot)window._blockedUsers[key]=values;else delete window._blockedUsers[key];
  localStorage.setItem('bp3_blocked_users',JSON.stringify(window._blockedUsers));window.BP3SyncBotBlocklist?.();window.BP3PruneBlockedSpeech?.();render();renderBlockedSettings();panel.remove();showToast('บันทึกการบล็อกแล้ว');
 };panel.append(saveButton);root.querySelector('.floating-footer')?.before(panel);
};

window.exportUserRosterCsv=function(){
 const rows=[['ชื่อผู้ชม','ชื่อเรียก','แพลตฟอร์ม','จำนวนข้อความ','สถานะ','ใช้งานล่าสุด'],...[...people.values()].map(person=>[person.username,getEffectiveAuthorName(person.username),person.platform,person.count,isBlocked(person.username)?'บล็อก':person.isVip?'VIP':'คนดูทั่วไป',new Date(person.lastSeen).toLocaleString()])];
 const csv='\ufeff'+rows.map(row=>row.map(value=>'"'+String(value ?? '').replace(/"/g,'""')+'"').join(',')).join('\r\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
 const doc=getToolDocument('user-manager'),link=doc.createElement('a');link.href=url;link.download='viewers-'+Date.now()+'.csv';doc.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
};
const profile=window.openAuthorModal;window.openAuthorModal=function(username,platform,avatar,nickname,isVip){
 pruneViewerChatHistory();
 const person=people.get(String(platform || 'Twitch').toLowerCase()+':'+String(username).toLowerCase());
 profile(username,platform,avatar,nickname,person?.isVip ?? isVip);
 setTimeout(()=>{
  if(_activeUserRecord.username!==username)return;
  const doc=getToolDocument('author-profile');
  const set=(id,text)=>{const element=doc.getElementById(id);if(element)element.textContent=text;};
  set('profMsgCount',(person?.count || 0)+' ข้อความ');set('profGwCount',(person?.joinCount || 0)+' ครั้ง');set('profLastSeen',person?.lastSeen?new Date(person.lastSeen).toLocaleString():'ยังไม่มีข้อมูล');
  for(const [id,eventOnly] of [['paneProfTab1',false],['paneProfTab2',true]]){const pane=doc.getElementById(id);if(!pane)continue;pane.replaceChildren();for(const item of person?.history || []){if(eventOnly && item.event==='message')continue;const row=doc.createElement('div');row.className='clean-row';row.textContent=new Date(item.time).toLocaleTimeString()+' · '+(eventOnly?item.event+' · ':'')+item.text;pane.append(row);}}
  const key=String(username).toLowerCase(),notes=read('bp3_user_notes',{}),pane=doc.getElementById('paneProfTab3'),field=pane?.querySelector('textarea');
  if(field){field.value=notes[key] || '';const button=doc.querySelector('.floating-footer-right .primary');if(button){button.id='btnSaveUserNotes';button.onclick=()=>{const current=read('bp3_user_notes',{});current[key]=field.value;localStorage.setItem('bp3_user_notes',JSON.stringify(current));showToast('บันทึกโน้ตแล้ว');closeToolWindow('author-profile');};}}
  const block=doc.querySelector('[onclick="blockUserFromProfile()"]');if(block)block.textContent='ตั้งค่าการบล็อก';
 },60);
};
const entry=window.checkRealGwEntry;window.checkRealGwEntry=function(msg,name){
 const find=()=>window._gwParticipants.find(person=>person.username.toLowerCase()===String(name).toLowerCase() && person.platform.toLowerCase()===String(msg.platform || 'Twitch').toLowerCase());
 const previous=find();const before=previous?(previous.checkins || [1]).length:0;entry(msg,name);const after=find();
 if(after && (after.checkins || [1]).length>before){const person=people.get(String(msg.platform || 'Twitch').toLowerCase()+':'+String(msg.username || name).toLowerCase());if(person){person.joinCount=(person.joinCount || 0)+1;schedule();}}
};
const open=window.openToolWindow;window.openToolWindow=function(name){const fn=open || window.openToolWindowBase;const win=document.getElementById(`win-${name}`);if(fn)fn(name);else if(win){win.classList.add('active');win.classList.remove('minimized');}if(name==='user-manager')setTimeout(()=>{render();const root=tool();const exportButton=root && [...root.querySelectorAll('button')].find(button=>button.textContent.includes('Export CSV'));if(exportButton){exportButton.id='btnUserRosterExport';exportButton.onclick=exportUserRosterCsv;}},100);};
const vip=window.toggleUserVip;window.toggleUserVip=function(){vip();for(const person of people.values())if(person.username.toLowerCase()===_activeUserRecord.username.toLowerCase())person.isVip=_activeUserRecord.isVip;save();render();};
const nickname=window.editUserNickname;window.editUserNickname=function(name){nickname(name);render();};
function init(){render();renderBlockedSettings();const root=tool();const button=root && [...root.querySelectorAll('button')].find(button=>button.textContent.includes('Export CSV'));if(button){button.id='btnUserRosterExport';button.onclick=exportUserRosterCsv;}}
window.addEventListener('pagehide',save);
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();

