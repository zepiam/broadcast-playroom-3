(() => {
  'use strict';
  const chat = [];
  let viewerState = {per_platform:{},total:0};
  let replie = null;
  const timers = new Map();
  function later(key, fn, ms) {clearTimeout(timers.get(key));timers.set(key,setTimeout(fn,ms));}
  function widgets(type) {return (window._overlayWidgets || []).filter(w=>w.type===type && !w.hidden);}
  const textNode=(cls,text)=>{const node=document.createElement('span');node.className=cls;node.textContent=text || '';return node;};
  function addChat(msg, remember=true) {
    if (remember) {chat.push(msg);if (chat.length>100) chat.shift();}
    widgets('chat').forEach(w=>{
      const mode=w.chatMode || w.chat_mode || 'default';
      const duration=Math.max(.1,Number(w.hideTimeout ?? w.hide_timeout ?? 8));
      if(mode==='danmaku'){
        if(!remember)return;
        const feed=document.getElementById(`widget-danmaku-feed-${w.id}`);if(!feed)return;
        const row=textNode('danmaku-bullet-item',msg.text);
        const speed=Math.max(.1,Number(w.speed)||6);
        row.style.cssText=`position:absolute;white-space:nowrap;top:${Math.floor(Math.random()*80)}%;left:0;font-size:${w.fontSize || 24}px;color:${w.fontColor || '#fff'};animation:danmakuBulletRun ${speed}s linear forwards;${w.textStroke?`-webkit-text-stroke:${w.textStrokeWidth || 1.5}px ${w.strokeColor || '#000'};paint-order:stroke fill;`:''}`;
        feed.append(row);row.addEventListener('animationend',()=>row.remove(),{once:true});setTimeout(()=>row.remove(),speed*1000+100);return;
      }
      const feed=document.getElementById(`widget-${mode==='balloon'?'balloon':mode==='character'?'character':'chat'}-feed-${w.id}`);
      if (!feed) return;
      if(mode==='character'){
        feed.replaceChildren();feed.style.visibility='visible';feed.style.flexDirection=w.charAlign==='right'?'row-reverse':'row';feed.style.gap='14px';
        if(w.imageUrl){const image=document.createElement('img');image.src=w.imageUrl;image.style.cssText='width:110px;height:110px;object-fit:contain';feed.append(image);}
        const bubble=document.createElement('div');bubble.style.cssText=`padding:12px 18px;border-radius:16px;background:${w.charBubbleBg || 'rgba(255,255,255,.96)'};color:${w.charTextColor || '#0f172a'};font-size:${w.charFontSize || 15}px;`;
        const author=textNode('author',msg.username || msg.author),text=textNode('text',msg.text);author.style.cssText='display:block;font-weight:bold;font-size:12px';bubble.append(author,text);feed.append(bubble);
        later('character:'+w.id,()=>{feed.replaceChildren();feed.style.visibility='hidden';},duration*1000);return;
      }
      const row=document.createElement('div');row.className=`cwc-msg-item msg chat-line theme-${w.chatTheme || 'default'}`;
      const layout=w.layout || 'inline';
      const theme=w.chatTheme && w.chatTheme!=='default' && !w.customBoxStyle;
      const bg=w.bgColor || '#1e1f22';const rgb=/^#[0-9a-f]{6}$/i.test(bg)?[1,3,5].map(i=>parseInt(bg.slice(i,i+2),16)):[30,31,34];
      row.style.cssText=`font-family:${w.fontFamily || 'Kanit'},sans-serif;font-size:${w.fontSize || 15}px;font-weight:${w.fontWeight || 600};flex-shrink:0;align-self:${w.align==='right'?'flex-end':w.align==='center'?'center':'flex-start'};`;
      if(!theme)row.style.cssText+=`padding:${w.boxPadding ?? 6}px 12px;border-radius:${w.boxRadius ?? 8}px;background:${w.boxEnabled===false?'transparent':`rgba(${rgb.join(',')},${w.bgOpacity ?? .85})`};`;
      if(mode==='balloon')row.style.cssText+=`position:relative;padding:10px 16px;border-radius:${w.balloonRadius ?? 14}px;background:${w.balloonBg || '#fff'};color:${w.balloonTextColor || '#0f172a'};max-width:90%;opacity:${w.balloonOpacity ?? .95};`;
      const background=document.createElement('div');background.className='msg-bg';row.append(background);
      if((w.showTimestamp ?? w.show_timestamp) && layout!=='message_only')row.append(textNode('time',msg.time || ''));
      if(layout!=='message_only'){
        const meta=document.createElement('span');meta.className='meta-line';
        if(w.showAvatar && msg.avatar){const image=document.createElement('img');image.src=msg.avatar;image.className='avatar';image.style.cssText='width:24px;height:24px;border-radius:50%;vertical-align:middle';meta.append(image);}
        if(w.showBadges!==false && Array.isArray(msg.badges))msg.badges.forEach(badge=>{const url=typeof badge==='object' && (badge.url || badge.image_url);if(url){const image=document.createElement('img');image.src=url;image.className='badge';image.style.cssText='width:18px;height:18px;vertical-align:middle';meta.append(image);}});
        if((w.showLogo ?? w.show_logo ?? true) && !layout.includes('no_logo')){const platform=textNode('platform',msg.platform || '');platform.style.cssText='font-size:.7em;margin-right:5px;opacity:.75';meta.append(platform);}
        const author=textNode('author',(msg.username || msg.author || '')+(layout.startsWith('stacked')?'':': '));author.style.color=w.usernameColor || msg.color || '#38bdf8';author.style.fontWeight='700';meta.append(author);
        if(layout.startsWith('stacked'))meta.style.display='block';row.append(meta);
      }
      const text=textNode('text text-block',msg.text);text.style.color=mode==='balloon'?(w.balloonTextColor || '#0f172a'):(w.fontColor || '#ffffff');row.append(text);
      if(w.direction==='top')feed.append(row);else feed.insertBefore(row,feed.firstChild);
      const max=Math.max(1,Number(w.maxMessages ?? w.max_messages)||30);
      while(feed.children.length>max){if(w.direction==='top')feed.firstElementChild.remove();else feed.lastElementChild.remove();}
      if(w.autoHide ?? w.auto_hide)setTimeout(()=>row.remove(),duration*1000);
    });
    if(remember)showEmotes(msg);
  }
  function showEmotes(msg){
    const emotes=[...(Array.isArray(msg.emotes)?msg.emotes:[]),...(msg.segments || []).filter(segment=>segment.type==='emote' && segment.url)];
    const segments=typeof Intl.Segmenter==='function'?[...new Intl.Segmenter(undefined,{granularity:'grapheme'}).segment(msg.raw_text || msg.text || '')].map(value=>value.segment):Array.from(msg.raw_text || msg.text || '');
    emotes.push(...segments.filter(value=>/\p{Extended_Pictographic}/u.test(value)).map(text=>({text})));
    widgets('emote_party').forEach(w=>{
      if(window.BP3LegacyEmotes){window.BP3LegacyEmotes.show(w,emotes.map(emote=>({...emote,url:emote.url || emote.image_url,text:emote.text || emote.name})));return;}
      const feed=document.getElementById(`widget-emote-party-${w.id}`);if(!feed)return;
      const duration=Math.max(.1,Number(w.epDuration)||4);
      const max=Math.max(1,Number(w.epMaxEmotes)||20);
      emotes.slice(0,max).forEach(emote=>{
        const url=emote.url || emote.image_url;
        const node=document.createElement(url?'img':'span');if(url)node.src=url;else node.textContent=emote.text || emote.name || '';
        node.dataset.liveEmote='true';const size=Number(w.epEmoteSize)||48;
        node.style.cssText=`position:absolute;left:${Math.random()*85+5}%;bottom:0;width:${size}px;height:${size}px;object-fit:contain;font-size:${size}px;animation:emoteFloatUp ${duration}s ease-out forwards;pointer-events:none;`;
        feed.append(node);setTimeout(()=>node.remove(),duration*1000+100);
      });
      while(feed.children.length>max)feed.firstElementChild.remove();
    });
  }
  function clearChat(){
    window.BP3LegacyEmotes?.clear();
    chat.length=0;
    document.querySelectorAll('[id^="widget-chat-feed-"],[id^="widget-balloon-feed-"],[id^="widget-character-feed-"],[id^="widget-danmaku-feed-"],[id^="widget-emote-party-"]').forEach(el=>{el.replaceChildren();if(el.id.startsWith('widget-character'))el.style.visibility='hidden';});
  }
  function hideReplie() {if(window.BP3LegacyReplie)window.BP3LegacyReplie.dismiss();replie=null;document.querySelectorAll('[data-live-replie]').forEach(el=>{el.replaceChildren();el.style.display='none';});}
  function showReplie(data) {
    if(window.BP3LegacyReplie){replie=data;window.BP3LegacyReplie.render(data);clearTimeout(timers.get('replie'));if(!data.isLoop)later('replie',()=>{replie=null;},(Number(data.duration)||4)*1000);return;}
    hideReplie();replie=data;
    let targets=widgets('replie').map(w=>document.getElementById(`liveReplie_${w.id}`)).filter(Boolean);
    if (!targets.length) {
      let fallback=document.getElementById('liveReplie_fallback');
      if(!fallback){fallback=document.createElement('div');fallback.id='liveReplie_fallback';fallback.dataset.liveReplie='true';document.getElementById('obsCanvasStage').append(fallback);}
      targets=[fallback];
    }
    targets.forEach(el=>{
      el.style.cssText='position:absolute;left:50%;bottom:8%;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:12px;max-width:80%;padding:18px 24px;background:rgba(15,23,42,.94);border:1px solid rgba(255,255,255,.2);border-radius:16px;color:white;font-size:26px;z-index:100;';
      if(data.imageUrl || data.image){const image=document.createElement('img');image.src=data.imageUrl || data.image;image.style.cssText='max-width:420px;max-height:500px;object-fit:contain;';el.append(image);}
      const positions={'top-left':['40px','auto','40px','auto'],'top':['40px','auto','50%','auto'],'top-right':['40px','40px','auto','auto'],'left':['50%','auto','40px','auto'],'center':['50%','auto','50%','auto'],'right':['50%','40px','auto','auto'],'bottom-left':['auto','auto','40px','40px'],'bottom':['auto','auto','50%','40px'],'bottom-right':['auto','40px','auto','40px']};
      const anchor=data.anchor || 'bottom-right';const [top,right,left,bottom]=positions[anchor] || positions['bottom-right'];
      Object.assign(el.style,{top,right,left,bottom,transform:`translate(${left==='50%'?'-50%':'0'},${top==='50%'?'-50%':'0'}) scale(${(Number(data.scale)||100)/100})`,transformOrigin:anchor.includes('right')?'right bottom':anchor.includes('left')?'left bottom':'center'});
      const text=document.createElement('div');text.textContent=data.text || '';el.append(text);
    });
    clearTimeout(timers.get('replie'));
    if (!data.isLoop) later('replie',hideReplie,Math.max(.1,Number(data.duration)||5)*1000);
  }
  const mediaFrames = new Set();
  function keyMedia(media, stage, color, similarity=50, smoothness=30) {
    const canvas=document.createElement('canvas');canvas.dataset.liveMedia='true';canvas.style.cssText='max-width:100%;max-height:100%;object-fit:contain;';
    const context=canvas.getContext('2d',{willReadFrequently:true});
    const hex=/^#[0-9a-f]{6}$/i.test(color || '')?color:'#00ff00';
    const key=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
    const threshold=Math.max(0,Number(similarity))/100*442;
    const smooth=Math.max(0,Number(smoothness))/100*Math.max(threshold*.4,20);
    stage.append(canvas);
    function paint(){
      if(!canvas.isConnected)return;
      const width=media.videoWidth || media.naturalWidth, height=media.videoHeight || media.naturalHeight;
      if(width && height){
        if(canvas.width!==width || canvas.height!==height){canvas.width=width;canvas.height=height;}
        try{
          context.drawImage(media,0,0,width,height);
          const pixels=context.getImageData(0,0,width,height), data=pixels.data;
          for(let i=0;i<data.length;i+=4){const distance=Math.hypot(data[i]-key[0],data[i+1]-key[1],data[i+2]-key[2]);if(distance<threshold-smooth)data[i+3]=0;else if(distance<threshold)data[i+3]=Math.round(((distance-(threshold-smooth))/smooth)*255);}
          context.putImageData(pixels,0,0);media.style.display='none';
        }catch{canvas.remove();media.style.display='';return;}
      }
      if(media.tagName==='VIDEO' && !media.ended){const id=requestAnimationFrame(()=>{mediaFrames.delete(id);paint();});mediaFrames.add(id);}
    }
    media.addEventListener(media.tagName==='VIDEO'?'loadeddata':'load',paint,{once:true});
    if(media.complete || media.readyState>=2)paint();
  }
  const mediaPlayers=new Map();
  function stopPlayer(player){
    clearTimeout(player.timer);player.timer=null;
    if(player.stage){player.stage.querySelectorAll('[data-live-media]').forEach(el=>{if(el.pause)el.pause();el.remove();});player.stage.style.display='none';}
    player.active=null;
  }
  function playNext(player){
    stopPlayer(player);const data=player.queue.shift();if(!data)return;
    const stage=document.getElementById(`compPlayroomStage_${player.id}`);if(!stage){player.queue.length=0;return;}
    player.stage=stage;player.active=data;player.started=Date.now();stage.style.display='flex';
    const card=document.getElementById(`compPlayroomCard_${player.id}`);if(card)card.style.display='none';
    const media=document.createElement(data.type==='video'?'video':(data.type==='image'?'img':'audio'));
    media.dataset.liveMedia='true';media.crossOrigin='anonymous';media.src=data.url || '';media.style.cssText='max-width:100%;max-height:100%;object-fit:contain;';
    if(data.type==='audio')media.style.display='none';
    let finished=false;
    const finish=()=>{if(finished || player.active!==data)return;finished=true;playNext(player);};
    media.addEventListener('error',finish,{once:true});
    if(media.play){media.autoplay=true;media.volume=Math.max(0,Math.min(1,(data.vol ?? 85)/100));media.playsInline=true;media.addEventListener('ended',finish,{once:true});}
    stage.append(media);
    if(data.ckEnabled && data.type!=='audio')keyMedia(media,stage,data.ckColor,data.ckSimilarity,data.ckSmoothness);
    if(media.play)media.play().catch(()=>{});
    // Videos and audio finish on their real ended/error event, not an image timer.
    if(data.type==='image')player.timer=setTimeout(finish,Math.max(.1,Number(data.duration)||5)*1000);
  }
  function showClip(data){
    widgets('playroom').filter(w=>!data.targetWidgetIds?.length || data.targetWidgetIds.map(String).includes(String(w.id))).forEach(w=>{
      const id=String(w.id);let player=mediaPlayers.get(id);
      if(!player){player={id,queue:[],active:null,stage:null,timer:null};mediaPlayers.set(id,player);}
      if(player.queue.length>=5)return;
      const widgetKey=w.ckEnabled ?? w.ck_enabled;
      const payload={...data};if(widgetKey!==undefined){payload.ckEnabled=widgetKey;payload.ckColor=w.ckColor || w.ck_color || data.ckColor;payload.ckSimilarity=w.ckSimilarity ?? w.ck_similarity ?? 50;payload.ckSmoothness=w.ckSmoothness ?? w.ck_smoothness ?? 30;}
      player.queue.push(payload);if(!player.active)playNext(player);
    });
  }
  function restoreClips(){
    for(const [id,player] of mediaPlayers){
      const stage=document.getElementById(`compPlayroomStage_${id}`);
      if(!stage){stopPlayer(player);mediaPlayers.delete(id);continue;}
      if(stage===player.stage || !player.active)continue;
      const active={...player.active};if(active.type==='image')active.duration=Math.max(.1,(Number(active.duration)||5)-(Date.now()-player.started)/1000);
      stopPlayer(player);player.stage=stage;player.queue.unshift(active);playNext(player);
    }
  }
  function updateViewers(data) {
    viewerState=data;
    document.querySelectorAll('.widget.type-viewer, .widget-type-viewer').forEach(el=>{
      el.querySelectorAll('.viewer-total .viewer-ticker').forEach(node=>node.textContent=String(data.total || 0));
      el.querySelectorAll('[data-platform-ticker]').forEach(node=>node.textContent=String(data.per_platform?.[node.dataset.platformTicker] || 0));
    });
  }
  function renderMusic(){window.BP3Music?.mount();}
  function refreshNowPlaying(){return window.BP3Music?.refresh();}
  window.BP3Live={
    refreshNowPlaying,
    receive({event,payload}) {
      if(event==='AVATAR_STATE')window.BP3LegacyAvatar?.receive(payload || {});
      else if(event==='VIEWERS_UPDATE')updateViewers(payload || {per_platform:{},total:0});
      else if(event==='CHAT_MESSAGE' && !payload?.hide_from_overlay)addChat(payload || {});
      else if(event==='CHAT_CLEAR')clearChat();
      else if(event==='REPLIE_ACTION')showReplie(payload || {});
      else if(event==='REPLIE_DISMISS')hideReplie();
      else if(event==='PLAYROOM_PLAY_CLIP')showClip(payload || {});
    },
    restore() {
      renderMusic();refreshNowPlaying();
      updateViewers(viewerState);
      document.querySelectorAll('[id^="widget-chat-feed-"]').forEach(el=>el.replaceChildren());
      chat.forEach(msg=>addChat(msg,false));
      if(replie && !document.querySelector('.replie-wrapper'))showReplie(replie);
      restoreClips();
    }
  };
})();
