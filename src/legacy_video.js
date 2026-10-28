/* Legacy video color key, scoped to connected video widgets. */
(()=>{'use strict';
const active=new Map();
function stop(id,keepPlaying=false){const item=active.get(id);if(!item)return;if(item.frame)cancelAnimationFrame(item.frame);if(!keepPlaying)item.video.pause();item.video.style.opacity='';item.video.style.position='';item.canvas.remove();active.delete(id);}
function dispose(){for(const id of [...active.keys()])stop(id);}
function mount(){
 const widgets=window._overlayWidgets || window.ComposerStudio?.getActivePage?.()?.widgets || [];
 for(const [id,item] of active)if(!item.video.isConnected)stop(id);
 for(const widget of widgets){
  if(widget.type!=='video' || widget.hidden)continue;
  if(!(widget.ckEnabled ?? widget.ck_enabled)){if(active.has(widget.id))stop(widget.id,true);continue;}
  const element=document.getElementById('widget-'+widget.id) || document.querySelector('.widget[data-id="'+CSS.escape(widget.id)+'"]');const video=element?.querySelector('video');if(!video)continue;
  const previous=active.get(widget.id);if(previous?.video===video){previous.widget=widget;previous.canvas.style.objectFit=widget.fitMode || 'cover';video.style.opacity='0';video.style.position='absolute';continue;}if(previous)stop(widget.id);
  const canvas=video.ownerDocument.createElement('canvas');canvas.dataset.videoColorKey=widget.id;canvas.style.cssText='position:absolute;inset:0;width:100%;height:100%;object-fit:'+ (widget.fitMode || 'cover')+';pointer-events:none';
  const stage=video.parentElement;stage.style.position='relative';stage.append(canvas);const context=canvas.getContext('2d',{willReadFrequently:true});
  const hex=widget.ckColor || widget.ck_color || '#00ff00',key=[1,3,5].map(index=>parseInt(hex.slice(index,index+2),16));const threshold=Number(widget.ckSimilarity ?? widget.ck_similarity ?? 50)/100*442,smooth=Number(widget.ckSmoothness ?? widget.ck_smoothness ?? 30)/100*Math.max(threshold*.4,20);
  const item={video,canvas,frame:null,widget};active.set(widget.id,item);
  function paint(){
   if(!canvas.isConnected){stop(widget.id);return;}
   if(video.readyState>=2){
    const settings=item.widget,hex=settings.ckColor || settings.ck_color || '#00ff00',key=[1,3,5].map(index=>parseInt(hex.slice(index,index+2),16)),threshold=Number(settings.ckSimilarity ?? settings.ck_similarity ?? 50)/100*442,smooth=Number(settings.ckSmoothness ?? settings.ck_smoothness ?? 30)/100*Math.max(threshold*.4,20);
    canvas.width=video.videoWidth;canvas.height=video.videoHeight;
    try{context.drawImage(video,0,0);const image=context.getImageData(0,0,canvas.width,canvas.height),pixels=image.data;for(let index=0;index<pixels.length;index+=4){const distance=Math.hypot(pixels[index]-key[0],pixels[index+1]-key[1],pixels[index+2]-key[2]);if(distance<threshold-smooth)pixels[index+3]=0;else if(distance<threshold)pixels[index+3]=Math.round((distance-(threshold-smooth))/smooth*255);}context.putImageData(image,0,0);video.style.opacity='0';video.style.position='absolute';}catch{stop(widget.id);video.play().catch(()=>{});return;}
   }
   item.frame=requestAnimationFrame(paint);
  }
  video.muted=true;video.loop=true;video.play().catch(()=>{});paint();
 }
}
window.BP3LegacyVideos={mount,dispose};window.addEventListener('pagehide',dispose);
})();
