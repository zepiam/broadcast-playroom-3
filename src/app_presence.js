/* Overlay visibility follows the main window without reloading its content. */
(()=>{'use strict';const role=document.currentScript?.dataset.role;
if(role==='app'){
 const client=crypto.randomUUID();const stream=new EventSource('/api/app-presence/stream?client='+encodeURIComponent(client));
 function leave(){stream.close();navigator.sendBeacon('/api/app-presence/leave',new Blob([JSON.stringify({client})],{type:'application/json'}));}
 window.addEventListener('pagehide',leave,{once:true});return;
}
const style=document.createElement('style');style.textContent='html.bp3-app-offline{background:transparent!important}html.bp3-app-offline body{background:transparent!important;opacity:0!important;visibility:hidden!important;pointer-events:none!important}';document.head.append(style);
let offline=true,stopped=false;const paused=new Set();document.documentElement.classList.add('bp3-app-offline');
function apply(active){const next=!active;document.documentElement.classList.toggle('bp3-app-offline',next);if(next){document.querySelectorAll('video,audio').forEach(media=>{if(!media.paused){paused.add(media);media.pause();}});}else if(offline){for(const media of paused)if(media.isConnected)media.play().catch(()=>{});paused.clear();}offline=next;}
document.addEventListener('play',event=>{const media=event.target;if(offline && media instanceof HTMLMediaElement){paused.add(media);media.pause();}},true);
async function poll(){try{const response=await fetch('/api/app-presence',{cache:'no-store',signal:AbortSignal.timeout(1500)});if(!response.ok)throw Error();apply((await response.json()).active===true);}catch{apply(false);}if(!stopped)setTimeout(poll,1000);}
window.addEventListener('pagehide',()=>{stopped=true;});window.addEventListener('pageshow',()=>{if(stopped){stopped=false;poll();}});poll();
})();
