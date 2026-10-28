/* User-selected Ragnarok cursors, scoped to app documents. Original ANI frames/timing. */
(()=>{'use strict';
const root=new URL('./assets/cursors/ragnarok/',document.currentScript.src);
const installed=new WeakMap();
const ready=fetch(new URL('manifest.json',root)).then(response=>{if(!response.ok)throw Error('Cursor assets unavailable');return response.json();});
ready.catch(()=>{}); // Native keyword cursors remain available if assets fail.
const roles={'default':'normal','auto':'normal','pointer':'link','n-resize':'vertical','s-resize':'vertical','ns-resize':'vertical','row-resize':'vertical','e-resize':'horizontal','w-resize':'horizontal','ew-resize':'horizontal','col-resize':'horizontal','nw-resize':'diagonal','se-resize':'diagonal','nwse-resize':'diagonal'};
const fallback={normal:'default',link:'pointer',vertical:'ns-resize',horizontal:'ew-resize',diagonal:'nwse-resize'};
function install(doc){
 if(installed.has(doc))return installed.get(doc);
 const view=doc.defaultView;if(!view)return;
 let style=doc.head.querySelector('#bp3-cursor-skin-style');
 if(!style){style=doc.createElement('style');style.id='bp3-cursor-skin-style';doc.head.append(style);}
 style.textContent='[data-bp3-cursor]{cursor:var(--bp3-active-cursor) !important;}';
 let manifest=null,target=null,role=null,timer=null,step=0,lastPoint=null,queued=false,disposed=false;
 function stop(){if(timer!==null)view.clearTimeout(timer);timer=null;if(target)target.removeAttribute('data-bp3-cursor');target=null;role=null;step=0;}
 function frame(){
  if(!target?.isConnected || doc.hidden){stop();return;}
  const animation=manifest[role],item=animation.frames[animation.sequence[step]];
  doc.documentElement.style.setProperty('--bp3-active-cursor',`url("${new URL(item.file,root)}") ${item.hotspot[0]} ${item.hotspot[1]}, ${fallback[role]}`);
  timer=view.setTimeout(()=>{step=(step+1)%animation.sequence.length;frame();},animation.durationsMs[step]);
 }
 function update(){
  queued=false;if(disposed || !manifest || !lastPoint)return;
  const element=doc.elementFromPoint(lastPoint.x,lastPoint.y);if(!element){stop();return;}
  // Read the original cursor without inheriting our previous override.
  if(target)target.removeAttribute('data-bp3-cursor');
  let keyword=view.getComputedStyle(element).cursor.split(',').at(-1).trim();
  if(doc.body.classList.contains('win-is-resizing'))keyword='se-resize';
  else if(/(?:col|row|[nesw]{1,4})-resize$/.test(doc.body.style.cursor))keyword=doc.body.style.cursor;
  if(['auto','default'].includes(keyword) && element.closest('button,a[href],[role="button"],input:is([type="button"],[type="submit"],[type="reset"])'))keyword='pointer';
  const textField=element.closest('textarea,[contenteditable="true"],input:not([type]),input:is([type="text"],[type="password"],[type="search"],[type="email"],[type="url"],[type="tel"],[type="number"],[type="date"],[type="time"])');
  const next=(textField && ['auto','default','text'].includes(keyword)) || element.closest(':disabled')?null:roles[keyword];
  if(!next){stop();return;}
  if(next===role && target===element){target.setAttribute('data-bp3-cursor',next);return;}
  stop();target=element;role=next;target.setAttribute('data-bp3-cursor',role);frame();
 }
 function schedule(event){
  if(event?.clientX!==undefined)lastPoint={x:event.clientX,y:event.clientY};
  if(!queued){queued=true;view.queueMicrotask(update);}
 }
 function leave(event){if(!event.relatedTarget){lastPoint=null;stop();}}
 function blur(){lastPoint=null;stop();}
 function visibility(){if(doc.hidden)blur();}
 function dispose(){disposed=true;blur();for(const type of ['pointerover','pointermove','pointerdown','pointerup','pointercancel'])doc.removeEventListener(type,schedule,true);doc.removeEventListener('load',schedule,true);doc.removeEventListener('pointerout',leave);doc.removeEventListener('visibilitychange',visibility);view.removeEventListener('blur',blur);view.removeEventListener('pagehide',dispose);installed.delete(doc);}
 installed.set(doc,dispose);
 for(const type of ['pointerover','pointermove','pointerdown','pointerup','pointercancel'])doc.addEventListener(type,schedule,true);
 doc.addEventListener('load',schedule,true);doc.addEventListener('pointerout',leave);doc.addEventListener('visibilitychange',visibility);view.addEventListener('blur',blur);view.addEventListener('pagehide',dispose,{once:true});
 ready.then(data=>{if(disposed)return;manifest=data;for(const animation of Object.values(data))for(const item of animation.frames){const image=new view.Image();image.src=new URL(item.file,root).href;}schedule();}).catch(()=>{});
 return dispose;
}
window.BP3CursorSkin={install,ready};install(document);
})();
