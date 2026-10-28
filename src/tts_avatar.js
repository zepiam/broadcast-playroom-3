(()=>{
'use strict';const active=new Set();let last=false;
function publish(){const talking=active.size>0;if(talking===last)return;last=talking;window.BP3LegacyAvatar?.receive({talking});window.BP3_BUS?.emit('AVATAR_STATE',{talking});}
window.bindTtsAvatarAudio=audio=>{audio.addEventListener('playing',()=>{active.add(audio);publish();});['ended','pause','error','abort'].forEach(event=>audio.addEventListener(event,()=>{active.delete(audio);publish();}));};
window.bindTtsAvatarUtterance=utterance=>{utterance.addEventListener('start',()=>{active.add(utterance);publish();});['end','error'].forEach(event=>utterance.addEventListener(event,()=>{active.delete(utterance);publish();}));};
window.addEventListener('pagehide',()=>{active.clear();publish();});
})();
