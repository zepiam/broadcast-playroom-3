/* Local profanity filtering; emote segments are preserved. */
(() => {
 const key='bp3_banned_words_v1';let saved;
 try{saved=JSON.parse(localStorage.getItem(key)||'null');}catch(_){saved=null;}
 let state={words:typeof saved?.words==='string'?saved.words:'ควย',display:saved?.display==='censor'?'censor':'hide',tts:saved?.tts==='remove'?'remove':'skip'};
 function persist(){localStorage.setItem(key,JSON.stringify(state));window.BP3SyncBotBlocklist?.();}
 function pattern(){const words=state.words.split(/\r?\n/).map(x=>x.trim()).filter(Boolean).sort((a,b)=>b.length-a.length);return words.length?new RegExp(words.map(w=>w.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('|'),'giu'):null;}
 function refresh(){const root=window._toolWindowNodes?.settings || document;for(const [id,value] of [['bannedWordsList',state.words],['bannedDisplayMode',state.display],['bannedTtsMode',state.tts]]){const el=root.querySelector?.('#'+id);if(el && el.value!==value)el.value=value;}}
 window.BP3BannedWords={
  words(){return state.words.split(/\r?\n/).map(x=>x.trim()).filter(Boolean);},
  apply(msg){
   const speech=window.BP3ChatContent.speakable(msg), re=pattern();
   if(!re || (msg.event && msg.event!=='message') || !re.test(speech))return {display:msg,hide:false,speech};
   const remove=value=>String(value || '').replace(re,' '), mask=value=>String(value || '').replace(re,'***');
   const spoken=state.tts==='remove'?remove(speech).replace(/\s+/g,' ').trim():'';
   if(state.display==='hide')return {display:msg,hide:true,speech:spoken,matched:true};
   const segments=window.BP3ChatContent.parts(msg).map(part=>part.type==='text'?{...part,content:mask(part.content)}:part.type==='emoji'?{type:'emoji',char:part.content}:part);
   const display={...msg,segments,text:mask(msg.text),raw_text:mask(msg.raw_text),original_text:mask(msg.original_text),is_translated:!!msg.is_translated};
   return {display,hide:false,speech:spoken,matched:true};
  },
  importLegacy(tools){
   if(!Array.isArray(tools?.banned_words) || localStorage.getItem(key))return;
   state.words=tools.banned_words.map(String).join('\n');persist();refresh();
  }
 };
 function init(){
  for(const [id,field] of [['bannedWordsList','words'],['bannedDisplayMode','display'],['bannedTtsMode','tts']]){
   const el=document.getElementById(id);if(!el)continue;el.addEventListener(field==='words'?'input':'change',()=>{state[field]=el.value;persist();});
  }refresh();
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
