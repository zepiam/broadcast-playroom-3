/* Legacy blacklist: bots are muted in TTS and may be hidden from overlay. */
(() => {
 const key='bp3_bot_blacklist_v1';
 const defaults=['nightbot','streamelements','streamlabs','moobot','wizebot','fossabot','deepbot','phantombot','sery_bot','buttsbot','kapsulebot'];
 let saved;try{saved=JSON.parse(localStorage.getItem(key)||'null');}catch(_){saved=null;}
 let state={names:Array.isArray(saved?.names)?saved.names:defaults,hideOverlay:typeof saved?.hideOverlay==='boolean'?saved.hideOverlay:true,botName:typeof saved?.botName==='string'?saved.botName:'Baitoei-Bot'};
 const clean=value=>String(value || '').trim().toLowerCase();
 const persist=()=>{localStorage.setItem(key,JSON.stringify(state));syncBotBlocklist();window.BP3PruneBlockedSpeech?.();};
 let syncTimer;
 function syncBotBlocklist(){
  clearTimeout(syncTimer);syncTimer=setTimeout(()=>{
   const blocked=Object.entries(window._blockedUsers || {}).filter(([,value])=>flags(value).all).map(([name])=>name);
   const names=[...new Set([...state.names,state.botName,...blocked].map(clean).filter(Boolean))];
   fetch('/api/chatbot/blocklist',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({names,banned_words:window.BP3BannedWords?.words() || []})}).catch(()=>{});
  },50);
 }
 window.BP3SyncBotBlocklist=syncBotBlocklist;
 function refresh(){const root=window._toolWindowNodes?.settings || document,names=root.querySelector?.('#botBlacklistNames'),hide=root.querySelector?.('#botBlacklistHideOverlay'),own=root.querySelector?.('#botBlacklistOwnName');if(names && names.value!==state.names.join('\n'))names.value=state.names.join('\n');if(hide)hide.checked=state.hideOverlay;if(own && own.value!==state.botName)own.value=state.botName;}
 function isBot(msg){
  const name=clean(msg.username || msg.author);
  if(!name)return false;
  const platform=clean(msg.platform_key || msg.platform),account=window._botAuthStatuses?.[platform];
  if(account?.username && clean(account.username)===name)return false;
  if(name===clean(state.botName) || state.names.some(item=>clean(item)===name))return true;
  return false;
 }
 function flags(value){
  if(value===true || value==='all')return {replie:false,overlay:false,tts:false,all:true};
  if(value==='tts')return {replie:false,overlay:false,tts:true,all:false};
  return {replie:!!value?.replie,overlay:!!value?.overlay,tts:!!value?.tts,all:!!value?.all};
 }
 window.BP3Blacklist={
  flags,
  botNames(){return [...new Set([...state.names,state.botName].map(clean).filter(Boolean))];},
  classify(msg){
   const name=clean(msg.username || msg.author),value=window._blockedUsers?.[name],bot=isBot(msg),own=!!(msg.own_message || msg.extra?._own_message);
   let rule=flags(value);
   if(bot && !value)rule={replie:true,overlay:state.hideOverlay,tts:true,all:false};
   else if(bot && value==='tts')rule={replie:true,overlay:state.hideOverlay,tts:true,all:false};
   return {blockAll:rule.all,bot,mute:rule.all || rule.tts,hideOverlay:rule.all || rule.overlay,replie:rule.all || rule.replie,rule};
  },
  importLegacy(tools){
   if(!tools || localStorage.getItem('bp3_blacklist_legacy_imported'))return;
   const has=Array.isArray(tools.blocked_users)||Array.isArray(tools.tts_bot_blacklist)||typeof tools.overlay_hide_bots==='boolean'||typeof tools.twitch_bot_name==='string';
   if(!has)return;
   const users=window._blockedUsers || {};
   for(const item of tools.blocked_users || []){
    const name=clean(typeof item==='string'?item:item?.name);if(!name || users[name])continue;
    users[name]=typeof item==='object' && item.hide_overlay===false?'tts':true;
   }
   window._blockedUsers=users;localStorage.setItem('bp3_blocked_users',JSON.stringify(users));syncBotBlocklist();
   if(!localStorage.getItem(key)){
    if(Array.isArray(tools.tts_bot_blacklist))state.names=tools.tts_bot_blacklist.map(String);
    if(typeof tools.overlay_hide_bots==='boolean')state.hideOverlay=tools.overlay_hide_bots;
    if(typeof tools.twitch_bot_name==='string')state.botName=tools.twitch_bot_name;
    persist();
   }
   localStorage.setItem('bp3_blacklist_legacy_imported','1');refresh();window.BP3RefreshBlockedSettings?.();
  }
 };
 function init(){
  const names=document.getElementById('botBlacklistNames'),hide=document.getElementById('botBlacklistHideOverlay'),own=document.getElementById('botBlacklistOwnName');
  names?.addEventListener('input',()=>{state.names=names.value.split(/\r?\n/).map(x=>x.trim()).filter(Boolean);persist();window.BP3RefreshBlockedSettings?.();});
  hide?.addEventListener('change',()=>{state.hideOverlay=hide.checked;persist();window.BP3RefreshBlockedSettings?.();});own?.addEventListener('input',()=>{state.botName=own.value;persist();window.BP3RefreshBlockedSettings?.();});refresh();
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
 window.addEventListener('load',()=>{
  syncBotBlocklist();
  fetch('/api/legacy/user-filters').then(response=>response.ok?response.json():{}).then(data=>{window.BP3Blacklist.importLegacy(data);window.BP3BannedWords?.importLegacy(data);}).catch(()=>{});
 },{once:true});setInterval(syncBotBlocklist,5000);
})();
