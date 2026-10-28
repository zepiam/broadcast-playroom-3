/* Shared live Now Playing presentation for Composer and independent Overlay. */
(()=>{'use strict';const states=new Map();let busy=false,timer=null,lastKey='';
const widgets=()=> (window._overlayWidgets || window.ComposerStudio?.getActivePage?.()?.widgets || []).filter(w=>w.type==='now_playing' && !w.hidden);
const element=w=>document.getElementById('widget-'+w.id) || document.querySelector('.widget[data-id="'+CSS.escape(String(w.id))+'"]');
const time=value=>{const n=Math.max(0,Math.floor(Number(value)||0));return Math.floor(n/60)+':'+String(n%60).padStart(2,'0');};
function render(){for(const w of widgets()){
 const el=element(w),inner=el?.querySelector('.widget-type-now-playing');if(!inner)continue;const data=states.get(w.npSource || w.np_source || 'auto');inner.style.visibility=data?.title && data.is_playing?'visible':'hidden';if(!data)continue;
 const set=(selector,value)=>{const node=el.querySelector(selector);if(node && node.textContent!==value)node.textContent=value;};
 set('.np-title-text',data.title || '');set('.np-artist',data.artist || '');
 const position=Math.min(Number(data.duration)||Infinity,(Number(data.position)||0)+(data.is_playing?(performance.now()-data.sampleAt)/1000:0));
 set('[data-np-position]',time(position));set('[data-np-duration]',time(data.duration));const bar=el.querySelector('.np-progress-row > div > div');if(bar)bar.style.width=(data.duration?Math.min(100,Math.max(0,position/data.duration*100)):0)+'%';
 const art=el.querySelector('.np-art');if(art){const url=data.thumbnail?data.thumbnail+'&track='+encodeURIComponent(data.title):'';if(art.dataset.url!==url){art.replaceChildren();art.dataset.url=url;if(url){const image=art.ownerDocument.createElement('img');image.src=url;image.style.cssText='width:100%;height:100%;object-fit:cover';art.append(image);}}}
 const title=el.querySelector('.np-title-text');if(title){const enabled=(w.npScrollTitle ?? w.np_scroll_title)!==false;title.style.maxWidth=enabled?'none':'100%';title.style.width=enabled?'max-content':'auto';title.style.overflow=enabled?'visible':'hidden';const distance=title.scrollWidth-(title.parentElement?.clientWidth || 0);title.style.setProperty('--np-scroll-distance',-Math.max(0,distance)+'px');title.style.animation=enabled && data.is_playing && distance>5?'bp3-np-scroll '+Math.max(6,distance/25+4)+'s linear infinite':'none';}
}}
async function refresh(){if(busy)return;busy=true;try{await Promise.all([...new Set(widgets().map(w=>w.npSource || w.np_source || 'auto'))].map(async source=>{try{const response=await fetch('/api/now-playing?source='+encodeURIComponent(source),{cache:'no-store'});if(response.ok)states.set(source,{...await response.json(),sampleAt:performance.now()});}catch{}}));render();}finally{busy=false;clearTimeout(timer);timer=setTimeout(refresh,widgets().some(w=>(w.npSyncMode || w.np_sync_mode)==='precise')?1000:3000);}}
function mount(){const key=widgets().map(w=>(w.npSource || w.np_source || 'auto')+':'+(w.npSyncMode || w.np_sync_mode || 'browser')).join('|');if(key!==lastKey){lastKey=key;refresh();}else render();}
window.BP3Music={render,refresh,mount};setInterval(render,1000);mount();
})();
