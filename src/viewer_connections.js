/* Shared connection visibility for Composer and OBS; no per-widget platform override. */
(()=>{'use strict';let busy=false;window.BP3ConnectedPlatforms=[];
function apply(data){const active=data.connected || [];window.BP3ConnectedPlatforms=active;document.querySelectorAll('.widget.type-viewer .viewer-chip[data-platform]').forEach(chip=>{chip.style.display=active.includes(chip.dataset.platform)?'inline-flex':'none';});}
window.addEventListener('bp3:remote-event',event=>{if(event.detail?.event==='VIEWERS_UPDATE')apply(event.detail.payload || {});});
async function poll(){if(busy)return;busy=true;try{const response=await fetch('/api/status',{cache:'no-store'});if(!response.ok)return;const statuses=await response.json();const active=Object.keys(statuses).filter(key=>statuses[key]?.connected),counts=Object.fromEntries(Object.entries(statuses).map(([key,s])=>[key,s.connected?Number(s.viewers)||0:0]));const data={connected:active,per_platform:counts,total:Object.values(counts).reduce((a,b)=>a+b,0)};apply(data);if(document.getElementById('obsCanvasStage')||document.getElementById('composerCanvasStage'))window.BP3Live?.receive({event:'VIEWERS_UPDATE',payload:data});}catch{}finally{busy=false;}}
setInterval(poll,1000);poll();window.BP3ViewerConnections={apply,refresh:poll};
})();
