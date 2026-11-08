/* Real viewer roster, profile blocking and CSV export. */

(()=>{

'use strict';

const read=(key,fallback)=>{try{return JSON.parse(localStorage.getItem(key)) ?? fallback;}catch{return fallback;}};

const rawRoster = read('bp3_user_roster', []);
const validPeople = Array.isArray(rawRoster)
  ? rawRoster.filter(p => p && (p.username || p.name)).map(p => {
      const u = String(p.username || p.name).trim();
      const plat = String(p.platform || 'Twitch').trim();
      return [plat.toLowerCase() + ':' + u.toLowerCase(), { ...p, username: u, platform: plat }];
    })
  : [];
const people = new Map(validPeople);

// Remove sample/test viewers left by the old "simulate activity" button (never real viewers).
(function purgeMockViewers(){
  const MOCK=new Set(['twitch:testviewer','twitch:alexgamer','twitch:kittenlover','twitch:prostreamer99','twitch:richwhale','twitch:speedrunnerth','twitch:newwatcher','youtube:somsak studio','youtube:animefanatic','youtube:gamingchannel','tiktok:ploy_charming','tiktok:megasupporter','tiktok:user123456','tiktok:tiktoklover','kick:kickchampion','promptpay:นายกิตติคุณ (ไม่ประสงค์ออกนาม)','truemoney:น้องมิว สายเปย์']);
  let removed=false;
  for(const [key,person] of [...people.entries()]){
    if(MOCK.has(key) && Number(person.count||0)<=3){people.delete(key);removed=true;}
  }
  if(removed){try{localStorage.setItem('bp3_user_roster',JSON.stringify([...people.values()]));}catch(_){}}
})();

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

// prune once at startup only (above); no hourly timer

window._blockedUsers=read('bp3_blocked_users',{});

const isBlocked=name=>Object.values(window.BP3Blacklist.classify({username:name}).rule).some(Boolean);

let query='',category='all',renderTimer=null,saveTimer=null;

const tool=()=>window._toolWindowNodes?.['user-manager'] || getToolDocument('user-manager').getElementById('win-user-manager');

function getActiveManagerRoots() {
 const roots = [];
 const mainWin = document.getElementById('win-user-manager');
 if (mainWin && mainWin.classList.contains('active') && !mainWin.classList.contains('minimized')) {
  roots.push(mainWin);
 }
 try {
  const popup = window._popoutWindows?.['user-manager'];
  if (popup && !popup.closed && popup.document) {
   const popWin = popup.document.getElementById('win-user-manager');
   if (popWin && !roots.includes(popWin)) roots.push(popWin);
  }
 } catch (_) {}
 try {
  const t = (typeof tool === 'function') ? tool() : null;
  if (t && !roots.includes(t)) roots.push(t);
 } catch (_) {}
 return roots;
}

if (typeof BroadcastChannel !== 'undefined' && !window._userRosterChannel) {
 window._userRosterChannel = new BroadcastChannel('bp3_user_roster_channel');
 window._userRosterChannel.onmessage = (e) => {
  if (e?.data?.action === 'roster_updated' && Array.isArray(e.data.roster) && e.data.roster.length > 0) {
   let changed = false;
   for (const person of e.data.roster) {
    if (!person || !person.username) continue;
    const key = (person.platform || 'Twitch').toLowerCase() + ':' + person.username.toLowerCase();
    const existing = people.get(key);
    if (!existing || (person.lastSeen || 0) >= (existing.lastSeen || 0)) {
     people.set(key, person);
     changed = true;
    }
   }
   if (changed) {
    try{localStorage.setItem('bp3_user_roster',JSON.stringify([...people.values()]));}catch(_){}
    render();
   }
  }
 };
}

const save=()=>{
 const rosterList = [...people.values()];
 if (!rosterList.length) return;
 try{localStorage.setItem('bp3_user_roster',JSON.stringify(rosterList));}catch{
  try{localStorage.setItem('bp3_user_roster',JSON.stringify(rosterList.map(person=>({...person,history:(person.history || []).slice(-1)}))));}catch{}
 }
 if(typeof fetch==='function'){
  fetch('/api/user-roster',{
   method:'POST',
   headers:{'Content-Type':'application/json'},
   body:JSON.stringify({roster:rosterList})
  }).catch(()=>{});
 }
 if (window._userRosterChannel) {
  try {
   window._userRosterChannel.postMessage({ action: 'roster_updated', roster: rosterList });
  } catch(_) {}
 }
};

async function syncRosterFromBackend(){
 try{
  const res = await fetch('/api/user-roster');
  if (res.ok) {
   const data = await res.json();
   const serverRoster = data.roster || data;
   let changed = false;
   if (Array.isArray(serverRoster) && serverRoster.length > 0) {
    for (const person of serverRoster) {
     if (!person || !person.username) continue;
     const key = (person.platform || 'Twitch').toLowerCase() + ':' + person.username.toLowerCase();
     const existing = people.get(key);
     if (!existing) {
      people.set(key, person);
      changed = true;
     } else {
      let personUpdated = false;
      const mergedCount = Math.max(Number(existing.count || 0), Number(person.count || 0));
      if (mergedCount !== existing.count) { existing.count = mergedCount; personUpdated = true; }
      const mergedJoin = Math.max(Number(existing.joinCount || 0), Number(person.joinCount || 0));
      if (mergedJoin !== existing.joinCount) { existing.joinCount = mergedJoin; personUpdated = true; }
      const mergedLastSeen = Math.max(Number(existing.lastSeen || 0), Number(person.lastSeen || 0));
      if (mergedLastSeen !== existing.lastSeen) { existing.lastSeen = mergedLastSeen; personUpdated = true; }
      if (!existing.avatar && person.avatar) { existing.avatar = person.avatar; personUpdated = true; }
      if (!existing.nickname && person.nickname) { existing.nickname = person.nickname; personUpdated = true; }
      if (!existing.isVip && person.isVip) { existing.isVip = true; personUpdated = true; }
      const hMap = new Map();
      for (const h of (existing.history || [])) {
       if (h && (h.text || h.time)) hMap.set(String(h.time)+':'+String(h.text), h);
      }
      for (const h of (person.history || [])) {
       if (h && (h.text || h.time)) hMap.set(String(h.time)+':'+String(h.text), h);
      }
      const newHistory = [...hMap.values()].sort((a,b) => (a.time || 0) - (b.time || 0)).slice(-250);
      if (newHistory.length !== (existing.history || []).length) {
       existing.history = newHistory;
       personUpdated = true;
      }
      if (personUpdated) changed = true;
     }
    }
   }
   if (changed || people.size > 0) {
    try{localStorage.setItem('bp3_user_roster',JSON.stringify([...people.values()]));}catch(_){}
    render();
    if (people.size > (Array.isArray(serverRoster) ? serverRoster.length : 0) || changed) {
     save();
    }
   }
  }
 }catch(err){
  console.warn('Could not sync user roster from backend:', err);
 }
}

if (typeof window !== 'undefined') {
  const flushRoster = () => {
    try {
      const list = [...people.values()];
      if (list.length > 0) {
        localStorage.setItem('bp3_user_roster', JSON.stringify(list));
        if (typeof navigator !== 'undefined' && navigator.sendBeacon) {
          const blob = new Blob([JSON.stringify({ roster: list })], { type: 'application/json' });
          navigator.sendBeacon('/api/user-roster', blob);
        }
      }
    } catch(_) {}
  };
  window.addEventListener('beforeunload', flushRoster);
  window.addEventListener('pagehide', flushRoster);
}
syncRosterFromBackend();

const cell=(doc,value)=>{const td=doc.createElement('td');td.textContent=String(value ?? '');return td;};

function render(){
 const roots = getActiveManagerRoots();
 if (!roots.length) return;
 const list=[...people.values()].sort((a,b)=>(b.lastSeen || 0)-(a.lastSeen || 0));
 const counts={
  all:list.length,
  vip:list.filter(person=>person.isVip).length,
  blocked:list.filter(person=>isBlocked(person.username)).length,
  active:list.filter(person=>(Date.now()-(person.lastSeen || 0))<5*60*1000).length
 };

 for (const root of roots) {
  const doc = root.ownerDocument, body = root.querySelector('#userRosterBody');
  if (!body) continue;
  body.replaceChildren();

  const matches = list.filter(person => {
   const blocked = isBlocked(person.username);
   const text = [person.username, getEffectiveAuthorName(person.username), person.platform].join(' ').toLowerCase();
   return text.includes(query) && (category==='blocked'?blocked:category==='vip'?person.isVip:category==='active'?(Date.now()-(person.lastSeen || 0))<5*60*1000:true);
  });

  const fragment = doc.createDocumentFragment();
  for (const person of matches) {
   const row = doc.createElement('tr');
   row.className = 'user-row';
   row.dataset.name = person.username.toLowerCase();
   row.dataset.vip = String(!!person.isVip);

   const name = cell(doc, '');
   name.style.cursor = 'pointer';
   const wrap = doc.createElement('div');
   wrap.style.display = 'flex';
   wrap.style.alignItems = 'center';
   wrap.style.gap = '8px';
   if (person.avatar) {
    const img = doc.createElement('img');
    img.src = person.avatar;
    img.style.width = '24px';
    img.style.height = '24px';
    img.style.borderRadius = '50%';
    img.style.objectFit = 'cover';
    img.onerror = () => { img.style.display = 'none'; };
    wrap.append(img);
   }
   const strong = doc.createElement('strong');
   strong.textContent = person.username;
   strong.style.color = person.isVip ? '#f87171' : '#f2f3f5';
   wrap.append(strong);
   name.append(wrap);
   name.onclick = () => openAuthorModal(person.username, person.platform, person.avatar, getEffectiveAuthorName(person.username), person.isVip);

   const effNick = getEffectiveAuthorName(person.username);
   const nickname = cell(doc, (effNick && effNick !== person.username) ? effNick : '-');
   nickname.style.color = '#38bdf8';
   nickname.style.cursor = 'pointer';
   nickname.onclick = () => editUserNickname(person.username);

   const blocked = isBlocked(person.username);
   const statusCell = cell(doc, blocked ? 'ถูกบล็อก' : person.isVip ? 'VIP' : 'คนดูทั่วไป');
   if (blocked) statusCell.style.color = '#ef4444';
   else if (person.isVip) statusCell.style.color = '#eab308';
   else statusCell.style.color = '#94a3b8';

   const lastSeenStr = person.lastSeen ? new Date(person.lastSeen).toLocaleTimeString() : '-';

   row.append(name, nickname, cell(doc, person.platform || 'Twitch'), cell(doc, person.count || 1), statusCell, cell(doc, lastSeenStr));

   const action = doc.createElement('button');
   action.className = 'btn-topbar-action';
   action.textContent = 'โปรไฟล์';
   action.onclick = name.onclick;
   const actions = cell(doc, '');
   actions.append(action);
   row.append(actions);
   fragment.append(row);
  }
  body.append(fragment);

  for (const [cat, id, label] of [['all','btnFilterAll','ทั้งหมด'],['vip','btnFilterVip','🌟 ผู้สนับสนุน'],['blocked','btnFilterBlocked','🛑 ถูกบล็อก'],['active','btnFilterActive','🟢 ล่าสุด']]) {
   const button = root.querySelector('#' + id);
   if (button) button.textContent = label + ' (' + counts[cat] + ')';
  }

  root.querySelectorAll('.win-tabs .win-tab-btn').forEach(button => button.classList.remove('active'));
  root.querySelector('#' + ({all:'btnFilterAll',vip:'btnFilterVip',blocked:'btnFilterBlocked',active:'btnFilterActive'}[category] || 'btnFilterAll'))?.classList.add('active');
 }
}

function schedule(){
 clearTimeout(saveTimer);
 saveTimer=setTimeout(save,300);
 if(renderTimer)return;
 renderTimer=setTimeout(()=>{
  renderTimer=null;
  render();
 },150);
}

window.BP3RegisterUserToRoster = function(msg){
  if (!msg || typeof msg !== 'object') return;

  // STRICT GUARD: Only genuine live viewers from real live broadcasts are recorded!
  // Any demo, mockup, simulated, test buttons, preview, sample, or local program host message is strictly forbidden!
  if (
    msg.demo || msg.is_demo || msg.test || msg.is_test ||
    msg.mock || msg.is_mock || msg.simulated || msg.is_simulated ||
    msg.sample || msg.is_sample || msg.preview || msg.sent_from_program ||
    msg.is_self || msg.extra?.is_test || msg.extra?.demo || msg.extra?.simulated
  ) {
    return;
  }

  const rawUsername = String(msg.username || '').trim();
  if (!rawUsername) return;

  const reservedNames = ['คุณ', 'HOST', 'Host', 'host', 'ระบบ', 'System', 'system', 'BOT', 'Bot', 'bot'];
  if (reservedNames.includes(rawUsername) || rawUsername.startsWith('[DEMO]')) return;

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

  try {
    localStorage.setItem('bp3_user_roster', JSON.stringify([...people.values()]));
  } catch(_) {}

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

window.registerUserToRoster = window.BP3RegisterUserToRoster;

window.BP3FilterUserRoster = value => { query = String(value || '').toLowerCase().trim(); render(); };
window.filterUserRoster = window.BP3FilterUserRoster;

window.BP3FilterUserCategory = value => { category = value; render(); };
window.filterUserCategory = window.BP3FilterUserCategory;

window.BP3RenderUserRoster = render;
window.BP3SyncRosterFromBackend = syncRosterFromBackend;

window.blockUserFromProfile=function(){
 const name=window._activeUserRecord?.username || (typeof _activeUserRecord !== 'undefined' ? _activeUserRecord?.username : null);
 if(!name)return;
 if(typeof window.openBlockUserModal === 'function'){
   window.openBlockUserModal(name);
 } else if(window.opener && typeof window.opener.openBlockUserModal === 'function'){
   window.opener.openBlockUserModal(name);
 } else if(window.parent && typeof window.parent.openBlockUserModal === 'function'){
   window.parent.openBlockUserModal(name);
 }
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



try {

  if (!window._authorProfileChannel) {

    window._authorProfileChannel = new BroadcastChannel('bp3_author_profile_sync');

  }

  window._authorProfileChannel.onmessage = (e) => {

    if (e.data && e.data.action === 'openAuthor' && e.data.payload) {

      const p = e.data.payload;

      if (typeof window.openAuthorModal === 'function') {

        window._isHandlingProfileSync = true;

        try {

          window.openAuthorModal(p.username, p.platform, p.avatarUrl, p.nickname, p.isVip);

        } finally {

          window._isHandlingProfileSync = false;
        }
      }
    } else if (e.data && e.data.action === 'avatarChanged') {
      const { username, avatarUrl } = e.data;
      if (window._customUserAvatars) {
        window._customUserAvatars[username] = avatarUrl;
      }
      if (typeof window.syncChatRowAvatars === 'function') {
        window.syncChatRowAvatars(username, avatarUrl);
      }
      if (window._activeUserRecord && window._activeUserRecord.username?.toLowerCase() === username?.toLowerCase()) {
        window._activeUserRecord.avatar = avatarUrl;
        const img = (typeof getToolDocument === 'function' ? getToolDocument('author-profile') : document)?.getElementById('profAvatarImg');
        if (img) img.src = avatarUrl;
      }
    }

  };

} catch (_) {}



window.syncAuthorProfile = function() {
  try {
    const raw = localStorage.getItem('bp3_active_author_profile');
    if (raw) {
      const p = JSON.parse(raw);
      if (p.username && typeof window.openAuthorModal === 'function') {
        window.openAuthorModal(p.username, p.platform, p.avatarUrl, p.nickname, p.isVip);
      }
    }
  } catch (_) {}
};

const profile=window.openAuthorModal;

window.openAuthorModal=function(username,platform,avatar,nickname,isVip){

 try {

   localStorage.setItem('bp3_active_author_profile', JSON.stringify({ username, platform: platform || 'Twitch', avatarUrl: avatar, nickname, isVip: !!isVip }));

   if (!window._isHandlingProfileSync) {

     window._authorProfileChannel?.postMessage({ action: 'openAuthor', payload: { username, platform: platform || 'Twitch', avatarUrl: avatar, nickname, isVip: !!isVip } });

   }

 } catch (_) {}

 window.pruneViewerChatHistory = pruneViewerChatHistory;

 // (removed) prune only runs once at startup

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

 const find=()=>window._gwParticipants.find(person=>person && String(person.username||'').toLowerCase()===String(name).toLowerCase() && String(person.platform || 'Twitch').toLowerCase()===String(msg?.platform || 'Twitch').toLowerCase());

 const previous=find();const before=previous?(previous.checkins || [1]).length:0;entry(msg,name);const after=find();

 if(after && (after.checkins || [1]).length>before){const person=people.get(String(msg.platform || 'Twitch').toLowerCase()+':'+String(msg.username || name).toLowerCase());if(person){person.joinCount=(person.joinCount || 0)+1;schedule();}}

};

const open=window.openToolWindow;window.openToolWindow=function(name, section){const fn=open || window.openToolWindowBase;const win=document.getElementById(`win-${name}`);if(fn)fn(name, section);else if(win){win.classList.add('active');win.classList.remove('minimized');if(name==='settings' && section && typeof switchSettingsSection==='function')switchSettingsSection(section);}if(name==='user-manager')setTimeout(()=>{render();const root=tool();const exportButton=root && [...root.querySelectorAll('button')].find(button=>button.textContent.includes('Export CSV'));if(exportButton){exportButton.id='btnUserRosterExport';exportButton.onclick=exportUserRosterCsv;}},100);};

const vip=window.toggleUserVip;window.toggleUserVip=function(){vip();for(const person of people.values())if(_activeUserRecord?.username && String(person.username||'').toLowerCase()===String(_activeUserRecord.username).toLowerCase())person.isVip=_activeUserRecord.isVip;save();render();};

const nickname=window.editUserNickname;window.editUserNickname=function(name){nickname(name);render();};

function init(){render();renderBlockedSettings();const root=tool();const button=root && [...root.querySelectorAll('button')].find(button=>button.textContent.includes('Export CSV'));if(button){button.id='btnUserRosterExport';button.onclick=exportUserRosterCsv;}}

window.addEventListener('pagehide',save);

if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();

})();



