/* User-specified codes are removed only from spoken text; chat content is unchanged. */
(() => {
  const key='bp3_secret_codes_v1';
  let saved;try{saved=JSON.parse(localStorage.getItem(key) || '{}');}catch(_){saved={};}
  let state={enabled:saved.enabled!==false, codes:typeof saved.codes==='string'?saved.codes:''};
  function persist(){localStorage.setItem(key,JSON.stringify(state));}
  function updateControls(){
    const root=window._toolWindowNodes?.settings || document;
    const enabled=root.querySelector?.('#secretCodesEnabled'),list=root.querySelector?.('#secretCodesList');
    if(enabled)enabled.checked=state.enabled;if(list && list.value!==state.codes)list.value=state.codes;
  }
  window.BP3SecretCodes={removeFromSpeech(text){
    if(!state.enabled)return String(text || '');
    let clean=String(text || '');
    const codes=state.codes.split(/\r?\n/).map(x=>x.trim()).filter(Boolean).sort((a,b)=>b.length-a.length);
    for(const code of codes){const escaped=code.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');clean=clean.replace(new RegExp('(^|[^\\p{L}\\p{N}_])'+escaped+'(?=$|[^\\p{L}\\p{N}_])','giu'),'$1 ');}
    return clean;
  }};
  function init(){
    const enabled=document.getElementById('secretCodesEnabled'),list=document.getElementById('secretCodesList');
    enabled?.addEventListener('change',()=>{state.enabled=enabled.checked;persist();updateControls();});
    list?.addEventListener('input',()=>{state.codes=list.value;persist();});updateControls();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
