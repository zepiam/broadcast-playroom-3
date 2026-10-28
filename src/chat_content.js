(function(){
  function parts(msg) {
    if (msg.is_translated) return [{type:'text',content:msg.text || ''}];
    if (Array.isArray(msg.segments) && msg.segments.length) return msg.segments.map(s=>({type:s.type,content:s.type==='emoji' ? s.char : (s.content || s.name || (s.id != null ? String(s.id) : '')),url:s.url}));
    const emotes=msg.twitch_emotes || msg.emotes || [], text=msg.raw_text || msg.text || '';
    if (emotes.length && text) {let at=0;const result=[];for(const e of [...emotes].sort((a,b)=>a.start-b.start)){if(!Number.isInteger(e.start)||!Number.isInteger(e.end)||e.start<at)continue;if(e.start>at)result.push({type:'text',content:text.slice(at,e.start)});result.push({type:'emote',url:e.url || (e.id!=null?'/emote/'+encodeURIComponent(e.id):''),content:e.name || text.slice(e.start,e.end+1)});at=e.end+1;}if(at<text.length)result.push({type:'text',content:text.slice(at)});if(result.length)return result;}
    if (msg.sticker_url) return [{type:'emote',url:msg.sticker_url}];
    return [{type:'text',content:msg.text || msg.system_text || ''}];
  }
  function speakable(msg){return parts(msg).filter(p=>p.type==='text').map(p=>p.content || '').join(' ').replace(/[\p{Extended_Pictographic}\p{Emoji_Presentation}\uFE0F\u200D]/gu,'').trim();}
  function render(el,msg){el.replaceChildren();for(const p of parts(msg)){if(p.type==='emote'&&p.url){const img=document.createElement('img');img.className='live-chat-emote';img.src=p.url;img.alt=p.content || '';img.style.cssText='height:1.6em;max-width:4em;vertical-align:middle;object-fit:contain';el.appendChild(img);}else if(p.type==='text'||p.type==='emoji')el.appendChild(document.createTextNode(p.content || ''));}}
  function historyText(msg){return parts(msg).map(p=>p.type==='emote' ? (p.content || '[emote]') : (p.content || '')).join('') || (msg.sticker_url ? '[sticker]' : '');}
  window.BP3ChatContent={parts,render,speakable,historyText};
})();
