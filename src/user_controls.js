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
window.pruneViewerChatHistory = pruneViewerChatHistory;
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
window.registerUserToRoster=function(msg){
  if(!msg?.username || ['คุณ','HOST'].includes(msg.username))return;
  const platform=String(msg.platform || 'Twitch'),key=platform.toLowerCase()+':'+msg.username.toLowerCase();
  const previous=people.get(key);
  const extra=msg.extra || {};
  const isEvent=Boolean(msg.event && msg.event!=='message');
  let eventsList=[...(previous?.events || [])];
  if(isEvent){
    const evRecord={
      event:msg.event,
      amount:msg.amount!=null ? msg.amount : extra.amount,
      currency:msg.currency || extra.currency,
      gift_name:msg.gift_name || extra.gift_name,
      count:msg.gift_count || msg.count || extra.gift_count || extra.count,
      months:msg.months || extra.months,
      viewers:msg.viewers || extra.viewers,
      details:msg.event_details || extra.event_details,
      text:String(msg.text || '').trim(),
      time:Date.now()
    };
    eventsList.push(evRecord);
  }
  const historyList=[...(previous?.history || []),{
    text:window.BP3ChatContent.historyText(msg),
    event:msg.event || 'message',
    amount:msg.amount!=null ? msg.amount : extra.amount,
    time:Date.now()
  }].slice(-250);

  people.set(key,{
    username:msg.username,
    platform,
    avatar:msg.avatar || previous?.avatar || '',
    isVip:previous?.isVip || !!msg.isVip,
    count:(previous?.count || 0)+1,
    lastSeen:Date.now(),
    joinCount:previous?.joinCount || 0,
    events:eventsList,
    history:historyList
  });
  schedule();
};
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
window.exportUserChatHistory = function(targetUsername, targetPlatform) {
  const username = targetUsername || _activeUserRecord?.username;
  const platform = targetPlatform || _activeUserRecord?.platform || 'Twitch';
  if (!username) {
    if (window.showToast) showToast('⚠️ ไม่พบข้อมูลคนดูที่ต้องการส่งออก');
    return;
  }

  const key = String(platform).toLowerCase() + ':' + String(username).toLowerCase();
  const person = people.get(key) || [...people.values()].find(p => p.username.toLowerCase() === username.toLowerCase());
  const effectiveName = getEffectiveAuthorName(username);

  const history = person?.history || [];
  const events = person?.events || [];

  if (history.length === 0 && events.length === 0) {
    if (window.showToast) showToast(`ℹ️ ไม่พบประวัติข้อความแชทของ ${effectiveName || username}`);
    return;
  }

  // Combine chat messages and events chronologically
  const allLogs = [];
  history.forEach(item => {
    allLogs.push({
      time: item.time || Date.now(),
      type: 'CHAT',
      content: item.text || ''
    });
  });

  events.forEach(item => {
    const detailParts = [
      item.event,
      item.amount ? `ยอด: ${item.amount}` : '',
      item.gift_name ? `ของขวัญ: ${item.gift_name}${item.count ? ' x' + item.count : ''}` : '',
      item.months ? `${item.months} เดือน` : '',
      item.viewers ? `${item.viewers} ผู้ชม` : '',
      item.details ? `รายละเอียด: ${item.details}` : '',
      item.text ? `ข้อความ: "${item.text}"` : ''
    ].filter(Boolean).join(' | ');
    allLogs.push({
      time: item.time || Date.now(),
      type: 'EVENT',
      content: detailParts
    });
  });

  allLogs.sort((a, b) => a.time - b.time);

  let fileContent = `====================================================\r\n`;
  fileContent += `ประวัติข้อความแชทและกิจกรรม: ${username} (${effectiveName})\r\n`;
  fileContent += `แพลตฟอร์ม: ${platform}\r\n`;
  fileContent += `ข้อความทั้งหมด: ${person?.count || history.length} ข้อความ\r\n`;
  fileContent += `กิจกรรมทั้งหมด: ${events.length} กิจกรรม\r\n`;
  fileContent += `วันที่ส่งออกข้อมูล: ${new Date().toLocaleString('th-TH')}\r\n`;
  fileContent += `====================================================\r\n\r\n`;

  allLogs.forEach(entry => {
    const timeStr = new Date(entry.time).toLocaleString('th-TH');
    fileContent += `[${timeStr}] [${entry.type}] ${entry.content}\r\n`;
  });

  const blob = new Blob([fileContent], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const doc = getToolDocument('author-profile') || document;
  const a = doc.createElement('a');
  const safeName = username.replace(/[^a-zA-Z0-9_\u0E00-\u0E7F-]/g, '_');
  a.href = url;
  a.download = `chat_${safeName}_${Date.now()}.txt`;
  doc.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);

  if (window.showToast) {
    showToast(`📥 ส่งออกประวัติแชทของ ${effectiveName || username} เรียบร้อยแล้ว`);
  }
};

const profile=window.openAuthorModal;
window.openAuthorModal=function(username,platform,avatar,nickname,isVip){
 window.pruneViewerChatHistory = pruneViewerChatHistory;
 pruneViewerChatHistory();
 const person=people.get(String(platform || 'Twitch').toLowerCase()+':'+String(username).toLowerCase());

 profile(username,platform,avatar,nickname,person?.isVip ?? isVip);

 // Layering: If User Manager is running in a popout window, mount author-profile directly inside userMgrPop!
 const userMgrPop = window._popoutWindows?.['user-manager'];
 if (userMgrPop && !userMgrPop.closed) {
   if (window.mountAuthorProfileInPopout) {
     window.mountAuthorProfileInPopout(userMgrPop);
   }
 } else {
   const mainWin = document.getElementById('win-author-profile');
   if (mainWin) {
     window.highestZ = Math.max(window.highestZ || 500, 2500) + 100;
     mainWin.style.zIndex = window.highestZ;
   }
 }

 setTimeout(()=>{
  if(_activeUserRecord.username!==username)return;
  const doc=getToolDocument('author-profile');
  const set=(id,text)=>{const element=doc.getElementById(id);if(element)element.textContent=text;};
  set('profMsgCount',(person?.count || 0)+' ข้อความ');
  set('profGwCount',(person?.joinCount || 0)+' ครั้ง');
  set('profLastSeen',person?.lastSeen?new Date(person.lastSeen).toLocaleString():'ยังไม่มีข้อมูล');

  // Tab 1: Chat History
  const pane1 = doc.getElementById('paneProfTab1');
  if (pane1) {
    pane1.replaceChildren();
    const chats = (person?.history || []).filter(item => !item.event || item.event === 'message');
    if (chats.length === 0) {
      const empty = doc.createElement('div');
      empty.style.cssText = 'text-align:center; padding:20px; color:var(--dc-text-dim); font-size:12px;';
      empty.textContent = 'ยังไม่มีประวัติแชท';
      pane1.append(empty);
    } else {
      for (const item of chats) {
        const row = doc.createElement('div');
        row.style.cssText = 'background:#1e1f22; padding:8px 12px; border-radius:6px; font-size:12px; border:1px solid rgba(255,255,255,0.04);';
        const t = doc.createElement('div');
        t.style.cssText = 'font-size:10.5px; color:var(--dc-text-dim); margin-bottom:2px;';
        t.textContent = new Date(item.time).toLocaleTimeString('th-TH') + ' • ' + (person?.platform || 'Live');
        const c = doc.createElement('div');
        c.style.cssText = 'color:#e2e8f0; word-break:break-word;';
        c.textContent = item.text || '';
        row.append(t, c);
        pane1.append(row);
      }
    }
  }

  // Tab 2: Events History (PERMANENT - จดจำตลอด ห้ามลบ)
  const pane2 = doc.getElementById('paneProfTab2');
  if (pane2) {
    pane2.replaceChildren();
    const eventLabels = {
      bits: 'ส่งบิต (Bits)', cheer: 'ส่งบิต (Cheer)', sub: 'สมัครสมาชิก', resub: 'ต่ออายุสมาชิก',
      subgift: 'มอบสมาชิกให้ผู้อื่น', gift: 'ส่งของขวัญ', superchat: 'ส่ง Super Chat',
      super_chat: 'ส่ง Super Chat', supersticker: 'ส่ง Super Sticker', member: 'สมัครสมาชิก (Member)',
      membership: 'สมัครสมาชิก (Member)', follow: 'กดติดตาม', like: 'กดถูกใจไลฟ์',
      share: 'แชร์ไลฟ์สด', raid: 'พาผู้ชมเข้ามา (Raid)', donation: 'โดเนท', donate: 'โดเนท',
      tip: 'ส่งทิปโดเนท', stars: 'ส่งดาว', giveaway_winner: 'ชนะ Giveaway'
    };
    const eventIcons = {
      bits: '💎', cheer: '💎', sub: '👑', resub: '👑', subgift: '🎁', gift: '🎁',
      superchat: '💰', super_chat: '💰', supersticker: '✨', member: '👑', membership: '👑',
      follow: '⭐', like: '❤️', share: '📢', raid: '🚀', donation: '💵', donate: '💵',
      tip: '💵', stars: '⭐', giveaway_winner: '🎉'
    };

    const userEvents = [...(person?.events || [])].sort((a, b) => b.time - a.time);
    if (userEvents.length === 0) {
      const empty = doc.createElement('div');
      empty.style.cssText = 'text-align:center; padding:20px; color:var(--dc-text-dim); font-size:12px;';
      empty.textContent = 'ยังไม่มีประวัติกิจกรรม (เช่น โดเนท, ซับ, บิต, ของขวัญ, ติดตาม)';
      pane2.append(empty);
    } else {
      for (const item of userEvents) {
        const evKey = String(item.event || '').toLowerCase();
        const row = doc.createElement('div');
        row.style.cssText = 'background:#1e1f22; padding:8px 12px; border-radius:6px; font-size:12px; border:1px solid rgba(255,255,255,0.04); display:flex; flex-direction:column; gap:3px;';

        const topRow = doc.createElement('div');
        topRow.style.cssText = 'display:flex; align-items:center; justify-content:space-between; gap:6px;';

        const labelBox = doc.createElement('div');
        labelBox.style.cssText = 'font-weight:700; color:#38bdf8; display:flex; align-items:center; gap:5px;';
        const icon = eventIcons[evKey] || '⚡';
        const labelText = eventLabels[evKey] || item.event;
        labelBox.innerHTML = `<span>${icon}</span> <span>${labelText}</span>`;

        let amtStr = '';
        if (item.amount) amtStr = (evKey === 'bits' ? `${item.amount} Bits` : (/^\d/.test(String(item.amount)) ? `฿${item.amount}` : String(item.amount)));
        else if (item.gift_name) amtStr = `${item.gift_name}${item.count ? ' x' + item.count : ''}`;
        else if (item.months) amtStr = `${item.months} เดือน`;
        else if (item.viewers) amtStr = `${item.viewers} ผู้ชม`;
        else if (item.details) amtStr = String(item.details);

        if (amtStr) {
          labelBox.innerHTML += ` <span style="background:rgba(234,179,8,0.16); color:#facc15; border:1px solid rgba(234,179,8,0.3); padding:1px 6px; border-radius:4px; font-size:11px; margin-left:4px;">${amtStr}</span>`;
        }

        const timeSpan = doc.createElement('div');
        timeSpan.style.cssText = 'font-size:10.5px; color:var(--dc-text-dim);';
        timeSpan.textContent = new Date(item.time).toLocaleString('th-TH');

        topRow.append(labelBox, timeSpan);
        row.append(topRow);

        if (item.text) {
          const msgDiv = doc.createElement('div');
          msgDiv.style.cssText = 'color:#cbd5e1; font-style:italic; font-size:11.5px; margin-top:2px;';
          msgDiv.textContent = `"${item.text}"`;
          row.append(msgDiv);
        }
        pane2.append(row);
      }
    }
  }

  // Tab 3: Notes
  const key=String(username).toLowerCase(),notes=read('bp3_user_notes',{}),pane=doc.getElementById('paneProfTab3'),field=pane?.querySelector('textarea');
  if(field){
    field.value=notes[key] || '';
    const button=doc.querySelector('.floating-footer-right .primary');
    if(button){
      button.id='btnSaveUserNotes';
      button.onclick=()=>{
        const current=read('bp3_user_notes',{});
        current[key]=field.value;
        localStorage.setItem('bp3_user_notes',JSON.stringify(current));
        showToast('บันทึกโน้ตแล้ว');
        closeToolWindow('author-profile');
      };
    }
  }

  const block=doc.querySelector('[onclick="blockUserFromProfile()"]');
  if(block)block.textContent='🛑 ตั้งค่าการบล็อก';

  const expBtn = doc.getElementById('btnExportUserChat');
  if (expBtn) {
    expBtn.onclick = () => window.exportUserChatHistory(username, platform);
  }
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

