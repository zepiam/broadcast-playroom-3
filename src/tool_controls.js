(() => {
  'use strict';
  const read = (key, fallback) => {try {return JSON.parse(localStorage.getItem(key)) ?? fallback;} catch (_) {return fallback;}};
  const write = (key, value) => localStorage.setItem(key, JSON.stringify(value));
  const posMap={'บนซ้าย':'top-left','บนกลาง':'top','บนขวา':'top-right','ซ้าย':'left','กลาง':'center','ขวา':'right','ล่างซ้าย':'bottom-left','ล่างกลาง':'bottom','ล่างขวา':'bottom-right'};
  const cooldowns=new Map();
  window._replieCommands=read('bp3_replie_commands',window._replieCommands || {});
  let savedClips=read('bp3_playroom_clips',{});
  window._playroomTriggerMeta=read('bp3_playroom_trigger_meta',{});
  const dailyUsage=new Map();
  function pickWeighted(clips){const weights=clips.map(c=>Math.max(1,Number(c.weight)||1));let choice=Math.random()*weights.reduce((a,b)=>a+b,0);for(let i=0;i<clips.length;i++){choice-=weights[i];if(choice<=0)return clips[i];}return clips.at(-1);}
  function commandPattern(command){return new RegExp('(^|[^\\p{L}\\p{N}_])'+command.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'(?=$|[^\\p{L}\\p{N}_])','u');}
  Object.assign(PLAYROOM_PRESETS,savedClips);
  _activePlayroomClips=[...(PLAYROOM_PRESETS[_activePlayroomTrigger] || [])];
  function saveClips(){PLAYROOM_PRESETS[_activePlayroomTrigger]=_activePlayroomClips;savedClips[_activePlayroomTrigger]=_activePlayroomClips;write('bp3_playroom_clips',savedClips);}
  const originalPlayroomTable=window.renderPlayroomClipsTable;
  window.renderPlayroomClipsTable=function(){
    originalPlayroomTable();const doc=getToolDocument('playroom');
    doc.querySelectorAll('#tbodyPlayroomClips tr').forEach((row,index)=>{
      const clip=_activePlayroomClips[index];if(!clip)return;
      row.cells[1].textContent=clip.name;row.cells[2].textContent=clip.url;
      for(const [column,field] of [[3,'weight'],[4,'vol']]){const control=doc.createElement('input');control.type='number';control.min=field==='weight'?'1':'0';control.max='100';control.value=clip[field] ?? (field==='weight'?50:100);control.dataset['clip'+(field==='weight'?'Weight':'Volume')]=String(index);control.className='modal-input';control.style.width='66px';control.oninput=()=>{clip[field]=Math.max(field==='weight'?1:0,Math.min(100,Number(control.value)||0));saveClips();};row.cells[column].replaceChildren(control);}
      const edit=doc.createElement('button');edit.className='btn-topbar-action';edit.textContent='แก้ไข';edit.onclick=()=>{const name=doc.defaultView.prompt('ชื่อคลิป',clip.name);if(!name)return;const value=doc.defaultView.prompt('URL รูปภาพ วิดีโอ หรือเสียง',clip.url);if(!value)return;let url;try{url=new URL(value,location.href);if(!['http:','https:'].includes(url.protocol))return;}catch{return;}clip.name=name;clip.url=url.href;clip.type=/\.(png|jpe?g|gif|webp|svg)$/i.test(url.pathname)?'image':/\.(mp4|webm|mov)$/i.test(url.pathname)?'video':'audio';saveClips();renderPlayroomClipsTable();};row.cells[5].append(edit);
    });
  };
  const originalPlayroomSelection=window.onPlayroomTriggerSelect;
  window.onPlayroomTriggerSelect=function(command){originalPlayroomSelection(command);const limit=getToolDocument('playroom').getElementById('playroomDailyLimit');if(limit)limit.value=window._playroomTriggerMeta[command]?.daily_limit || 0;};
  window.addPlayroomTrigger=function(){
    const doc=getToolDocument('playroom');
    const command=doc.defaultView.prompt('คำสั่งใหม่ (ขึ้นต้นด้วย ! เช่น !jump)','!')?.trim();
    if(!command || !/^!\S+$/.test(command))return;
    if(Object.keys(PLAYROOM_PRESETS).some(key=>key.toLowerCase()===command.toLowerCase()))return;
    PLAYROOM_PRESETS[command]=[];savedClips[command]=[];write('bp3_playroom_clips',savedClips);
    const select=doc.getElementById('selPlayroomTrigger');if(select){select.add(new Option(command,command));select.value=command;}
    onPlayroomTriggerSelect(command);
  };
  window.addPlayroomClipRow=function(){
    const view=getToolDocument('playroom').defaultView;
    const name=view.prompt('ชื่อคลิป');if(!name)return;
    const url=view.prompt('URL รูปภาพ วิดีโอ หรือเสียง (http:// หรือ https://)');if(!url)return;
    let parsed;try {parsed=new URL(url,location.href);}catch(_){return;}
    if(!['http:','https:'].includes(parsed.protocol))return;
    const ext=parsed.pathname.toLowerCase();
    const type=/\.(png|jpe?g|gif|webp|svg)$/.test(ext)?'image':/\.(mp4|webm|mov)$/.test(ext)?'video':'audio';
    _activePlayroomClips.push({name,url:parsed.href,type,weight:100,vol:85,desc:''});saveClips();renderPlayroomClipsTable();
  };
  const deleteClip=window.deletePlayroomClip;
  window.deletePlayroomClip=function(index){deleteClip(index);saveClips();};
  window.runPlayroomSimulatedChat=function(){
    const doc=getToolDocument('playroom');
    const command=(doc.getElementById('txtPlayroomSimCmd')?.value || _activePlayroomTrigger).trim();
    const clips=command===_activePlayroomTrigger?_activePlayroomClips:(PLAYROOM_PRESETS[command] || []);
    if(!clips.length)return;
    const total=clips.reduce((n,c)=>n+Math.max(0,Number(c.weight)||0),0);
    let at=Math.random()*total;let selected=clips[0];
    for(const item of clips){at-=Math.max(0,Number(item.weight)||0);if(at<=0){selected=item;break;}}
    firePlayroomClipEvent(selected,command);
  };
  window.checkRealPlayroomCommand=function(msg){
    const command=Object.keys(PLAYROOM_PRESETS).sort((a,b)=>b.length-a.length).find(code=>commandPattern(code).test(String(msg.text || '')));
    if(!command)return;
    const clips=command===_activePlayroomTrigger?_activePlayroomClips:PLAYROOM_PRESETS[command];if(!clips?.length)return;
    const meta=window._playroomTriggerMeta[command] || {};
    const day=new Date().toLocaleDateString('en-CA');const key=String(msg.username || msg.author || '').toLowerCase()+':'+command+':'+day;
    const used=dailyUsage.get(key)||0;if(Number(meta.daily_limit)>0 && used>=Number(meta.daily_limit))return;
    dailyUsage.set(key,used+1);firePlayroomClipEvent(pickWeighted(clips),command);
  };
  function saveReplie(){write('bp3_replie_commands',window._replieCommands);}
  function replieSettings(){
    const doc=getToolDocument('replie');return {
      duration:Number(doc.querySelector('#paneReplieTab2 input[type="number"]')?.value)||4,
      scale:parseInt(doc.getElementById('lblReplieScale')?.textContent)||100,
      anchor:posMap[doc.querySelector('#paneReplieTab2 .pos-btn.active')?.textContent.trim()] || 'bottom-right',
      isLoop:doc.querySelector('#paneReplieTab1 input[type="checkbox"]')?.checked || false
    };
  }
  window.demoReplieAction=function(cmd,text,emotion){
    const command=window._replieCommands[cmd] || {};
    window._rpPanelTest=true;
    window.BP3_BUS?.emit('REPLIE_ACTION',{...command,...replieSettings(),cmd,text:text || command.text,emotion:emotion || command.emotion});
  };
  window.checkRealReplieCommand=function(msg,effectiveName){
    const userKey=String(msg?.username || msg?.author || effectiveName || '').toLowerCase().trim();
    const blClass=window.BP3Blacklist?.classify(msg);
    if(blClass?.blockAll || blClass?.replie || (window._blockedUsers && (window._blockedUsers[userKey]?.all || window._blockedUsers[userKey]?.replie)))return;
    const clean=String(msg.text || '').trim().toLowerCase();
    const cmd=Object.keys(window._replieCommands).sort((a,b)=>b.length-a.length).find(key=>clean===key.toLowerCase() || clean.startsWith(key.toLowerCase()+' '));
    const rule=window._replieCommands[cmd];if(!rule || rule.enabled===false)return;
    if(Date.now()-(cooldowns.get(cmd)||0)<(Number(rule.cooldown)||0)*1000)return;
    cooldowns.set(cmd,Date.now());demoReplieAction(cmd,`${effectiveName}: ${rule.text || ''}`,rule.emotion);
  };
  window.renderReplieCommands=function(){
    const doc=getToolDocument('replie');const tbody=doc.querySelector('#paneReplieTab1 tbody');if(!tbody)return;
    tbody.replaceChildren();
    for(const [cmd,rule] of Object.entries(window._replieCommands)){
      const row=doc.createElement('tr');
      for(const value of [cmd,rule.imageUrl || '—','ภาพ / ข้อความ',`${Number(rule.cooldown)||0}s`,replieSettings().anchor]){const td=doc.createElement('td');td.textContent=value;row.append(td);}
      const cell=doc.createElement('td');
      for(const [label,handler] of [['▶ DEMO',()=>demoReplieAction(cmd,rule.text,rule.emotion)],['✏️ แก้ไข',()=>editReplieCommand(cmd)],['✕',()=>{delete window._replieCommands[cmd];saveReplie();renderReplieCommands();}]]){
        const button=doc.createElement('button');button.className='btn-topbar-action';button.textContent=label;button.onclick=handler;cell.append(button);
      }
      row.append(cell);tbody.append(row);
    }
  };
  window.editReplieCommand=function(previous){
    const view=getToolDocument('replie').defaultView;const old=window._replieCommands[previous] || {};
    const raw=view.prompt('คำสั่งแชท เช่น !hello',previous || '!hello');if(!raw)return;
    const cmd=raw.trim().toLowerCase();const text=view.prompt('ข้อความที่จะแสดง',old.text || '');if(text===null)return;
    const imageUrl=view.prompt('URL รูปภาพ (เว้นว่างได้)',old.imageUrl || '');if(imageUrl===null)return;
    const cooldown=view.prompt('คูลดาวน์ (วินาที)',String(old.cooldown || 0));if(cooldown===null)return;
    if(previous && previous!==cmd)delete window._replieCommands[previous];
    window._replieCommands[cmd]={...old,legacyPayload:undefined,text,imageUrl,cooldown:Math.max(0,Number(cooldown)||0)};saveReplie();renderReplieCommands();
  };
  window.saveReplieSettings=function(){saveReplie();write('bp3_replie_settings',replieSettings());showToast('บันทึกการตั้งค่า Replie แล้ว');};
  function setupPresets(tool,pane){
    const select=pane.querySelector('.modal-form-group select');if(!select)return;
    select.id=tool+'PresetSelect';const key='bp3_'+tool+'_presets';let presets=read(key,{});
    function capture(){const doc=getToolDocument(tool);return tool==='ask'?{question:doc.getElementById('askQuestion').value,choices:Array.from(doc.querySelectorAll('#askChoicesList input')).map(x=>x.value),mode:doc.getElementById('askAnswerMode').value,duration:doc.getElementById('askDurationSelect').value}:{items:doc.getElementById('randItemsText').value,title:doc.getElementById('randTitleInput')?.value || ''};}
    function refresh(){select.replaceChildren(new Option('-- เลือก Preset --',''));Object.keys(presets).forEach(name=>select.add(new Option(name,name)));}
    refresh();
    select.onchange=()=>{
      const value=presets[select.value];if(!value)return;const doc=getToolDocument(tool);
      if(tool==='ask'){
        doc.getElementById('askQuestion').value=value.question;
        const list=doc.getElementById('askChoicesList');while(list.children.length<value.choices.length)addAskChoice();
        doc.querySelectorAll('#askChoicesList .ask-choice-row').forEach((row,i)=>{if(i>=value.choices.length)row.remove();else row.querySelector('input').value=value.choices[i];});
        doc.getElementById('askAnswerMode').value=value.mode;doc.getElementById('askDurationSelect').value=value.duration;
      }else{doc.getElementById('randItemsText').value=value.items;const title=doc.getElementById('randTitleInput');if(title)title.value=value.title;}
    };
    const buttons=select.parentElement.querySelectorAll('button');
    if(buttons[0])buttons[0].onclick=()=>{const name=getToolDocument(tool).defaultView.prompt('ชื่อ Preset',select.value);if(!name)return;presets[name]=capture();write(key,presets);refresh();select.value=name;};
    if(buttons[1])buttons[1].onclick=()=>{select.value='';const doc=getToolDocument(tool);if(tool==='ask')doc.getElementById('askQuestion').value='';else doc.getElementById('randItemsText').value='';};
  }
  window.applyLegacyToolData=function(layout){
    const tools=layout.legacyTools || {};
    const triggers=layout.legacyPlayroomTriggers || [];
    const signature=JSON.stringify([tools,triggers]);
    window.BP3Blacklist?.importLegacy(tools);
    window.BP3BannedWords?.importLegacy(tools);
    if(signature===localStorage.getItem('bp3_legacy_tool_signature'))return;
    if(tools.giveaway && window.BP3Giveaway)window.BP3Giveaway.import(tools.giveaway);
    const channels={twitch:'twitch_channel',youtube:'youtube_url',mylive:'mylive_url',tiktok:'tiktok_username',kick:'kick_channel',soop:'soop_bid'};
    for(const [platform,key] of Object.entries(channels)){
      if(typeof tools[key]==='string')setPlatformChannel(platform,tools[key]);
      const state=_platformStates[platform];if(!state)continue;
      if(typeof tools['read_tts_'+platform]==='boolean')state.muted=!tools['read_tts_'+platform];
      if(Number.isFinite(Number(tools['tts_volume_'+platform])))state.volume=Math.max(0,Math.min(100,Number(tools['tts_volume_'+platform])));
      const button=document.getElementById('btn-mute-'+platform);if(button){button.textContent=state.muted?'🔇':'🔊';button.classList.toggle('muted',state.muted);}
      const slider=document.getElementById('vol-'+platform);if(slider)slider.value=state.volume;
    }
    savePlatformAudio();
    if(tools.replie_commands){
      window._replieCommands={};
      for(const [cmd,raw] of Object.entries(tools.replie_commands)){
        window._replieCommands[cmd]={...raw,text:raw.text || raw.ticker?.text || raw.title || '',imageUrl:raw.image_url || raw.image?.image_url || '',cooldown:raw.cooldown_sec ?? tools.replie_cooldown_sec ?? 0,duration:raw.duration_sec ?? tools.replie_default_duration_sec ?? 8,legacyPayload:raw};
      }
      saveReplie();renderReplieCommands();
    }
    for(const trigger of triggers){
      const clips=(trigger.clips || []).map(clip=>({...clip,url:'/clip/'+encodeURIComponent(clip.name),type:/\.(png|jpe?g|gif|webp|svg|bmp)$/i.test(clip.path || '')?'image':/\.(mp3|wav|ogg|flac)$/i.test(clip.path || '')?'audio':'video',vol:clip.volume ?? clip.vol ?? 85}));
      PLAYROOM_PRESETS[trigger.code]=clips;savedClips[trigger.code]=clips;
      window._playroomTriggerMeta[trigger.code]={daily_limit:trigger.daily_limit || 0,widget_ids:trigger.widget_ids || []};
      const select=getToolDocument('playroom').getElementById('selPlayroomTrigger');
      if(select && !Array.from(select.options).some(option=>option.value===trigger.code))select.add(new Option(trigger.code,trigger.code));
    }
    if(triggers.length){
      write('bp3_playroom_clips',savedClips);
      write('bp3_playroom_trigger_meta',window._playroomTriggerMeta);
      _activePlayroomTrigger=triggers[0].code;_activePlayroomClips=[...PLAYROOM_PRESETS[_activePlayroomTrigger]];
      const select=getToolDocument('playroom').getElementById('selPlayroomTrigger');if(select)select.value=_activePlayroomTrigger;
      renderPlayroomClipsTable();
    }
    if(tools.ask_presets){
      const presets={};for(const preset of tools.ask_presets)presets[preset.name]={question:preset.question || '',choices:preset.choices || [],mode:preset.answer_mode || 'letters',duration:String(preset.duration_sec ?? 0)};
      write('bp3_ask_presets',presets);setupPresets('ask',getToolDocument('ask').getElementById('paneAskTab1'));
    }
    if(tools.voice_id && !['premwadee','niwat'].includes(String(tools.voice_id).toLowerCase())){
      (async()=>{
        try{
          const capabilities=await (await fetch('/api/capabilities')).json();if(!capabilities.rvc)return;
          const result=await (await fetch('/api/rvc/models')).json();
          const model=(result.models || []).find(item=>item.name.toLowerCase()===String(tools.voice_id).toLowerCase());
          if(model)await fetch('/api/rvc/select',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:model.id,enabled:true})});
        }catch(_){}
      })();
    }
    localStorage.setItem('bp3_legacy_tool_signature',signature);
  };
  /* ===== Quick Randomizer settings page (single page, live preview, WCAG 2.2) ===== */
  function setupRandomizerUI(){
    const V=window.BP3RandomizerVisual;const pane=document.getElementById('paneRandTab1');
    if(!V||!pane||window.BP3RandomizerUI)return;
    const $=(id)=>document.getElementById(id);
    const KEY='bp3_randomizer_display',LAST='bp3_randomizer_last';
    const DEFAULTS={style:'wheel',theme:'pastel',spin:4,hold:5,scale:100,ox:0,oy:0,anchor:'center',remove:true,calm:false};
    const SPEEDS=[[2,'เร็ว','2 วินาที'],[4,'ปกติ','4 วินาที'],[7,'ลุ้นระทึก','7 วินาที'],[10,'ยาวมาก','10 วินาที']];
    const ANCHOR_LABEL={'top-left':'บนซ้าย','top-center':'บนกลาง','top-right':'บนขวา','middle-left':'กลางซ้าย','center':'กลางจอ','middle-right':'กลางขวา','bottom-left':'ล่างซ้าย','bottom-center':'ล่างกลาง','bottom-right':'ล่างขวา'};
    const ANCHOR_ORDER=['top-left','top-center','top-right','middle-left','center','middle-right','bottom-left','bottom-center','bottom-right'];
    const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
    const toNum=(v,d)=>{const n=Number(v);return Number.isFinite(n)&&v!==''&&v!==null?n:d;};
    const saved=read(KEY,{});
    const st=Object.assign({},DEFAULTS);
    // read new keys, and migrate the values the old page stored as randAnchor and friends
    const pick=(a,b)=>saved[a]!==undefined?saved[a]:saved[b];
    if(V.STYLES.some(x=>x.id===pick('style','randDisplayMode')))st.style=pick('style','randDisplayMode');
    if(V.THEMES[pick('theme','randColorTheme')])st.theme=pick('theme','randColorTheme');
    if(V.ANCHORS[pick('anchor','randAnchor')])st.anchor=pick('anchor','randAnchor');
    st.spin=clamp(toNum(pick('spin','randSpinDuration'),4),1.5,12);
    st.hold=clamp(toNum(pick('hold','randHoldDuration'),5),1,120);
    st.scale=clamp(toNum(saved.scale,100),20,300);st.ox=clamp(toNum(saved.ox,0),-1920,1920);st.oy=clamp(toNum(saved.oy,0),-1080,1080);
    if(typeof saved.remove==='boolean')st.remove=saved.remove;if(typeof saved.calm==='boolean')st.calm=saved.calm;
    const persist=()=>{try{write(KEY,Object.assign({},read(KEY,{}),{v:2},st));}catch(_){}};
    const last=read(LAST,null);
    if(last&&typeof last.items==='string'){$('randItemsText').value=last.items;if(typeof last.title==='string')$('randTitleInput').value=last.title;}

    /* ---- build option cards ---- */
    const card=(group,value,checked,inner,compact)=>{
      const l=document.createElement('label');l.className='rz-opt';
      const i=document.createElement('input');i.type='radio';i.name=group;i.value=String(value);i.checked=checked;
      const f=document.createElement('span');f.className='rz-face'+(compact?' compact':'');f.innerHTML=inner+'<span class="rz-check" aria-hidden="true">✓</span>';
      l.append(i,f);return l;
    };
    const esc=(s)=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
    const styleList=$('rzStyleList');
    V.STYLES.forEach(s=>styleList.append(card('randStyle',s.id,st.style===s.id,`<span class="rz-face-icon" aria-hidden="true">${s.icon}</span><span class="rz-face-name">${esc(s.label)}</span><span class="rz-face-hint">${esc(s.hint)}</span>`)));
    const themeList=$('rzThemeList');
    Object.entries(V.THEMES).forEach(([id,t])=>themeList.append(card('randTheme',id,st.theme===id,`<span class="rz-swatch" aria-hidden="true" style="background:linear-gradient(90deg,${t.slices.slice(0,4).map((c,i)=>c+' '+(i*25)+'% '+((i+1)*25)+'%').join(',')})"></span><span class="rz-face-name">${esc(t.label)}</span>`,true)));
    const speedList=$('rzSpeedList');
    SPEEDS.forEach(([sec,name,hint])=>speedList.append(card('randSpeed',sec,Math.abs(st.spin-sec)<0.01,`<span class="rz-face-name">${name}</span><span class="rz-face-hint">${hint}</span>`)));
    const anchorList=$('rzAnchorList');
    ANCHOR_ORDER.forEach(a=>anchorList.append(card('randAnchorPos',a,st.anchor===a,`<span>${ANCHOR_LABEL[a]}</span>`)));
    const radio=(name)=>pane.ownerDocument.querySelector(`input[name="${name}"]:checked`);

    /* ---- items ---- */
    const text=$('randItemsText'),title=$('randTitleInput'),countEl=$('randItemsCount'),errEl=$('randItemsError');
    const readItems=()=>text.value.split('\n').map(x=>x.trim()).filter(Boolean).slice(0,200);
    const setItemsText=(arr)=>{text.value=arr.join('\n');text.dispatchEvent(new Event('input',{bubbles:true}));};
    const showCount=()=>{const n=readItems().length;countEl.textContent=n?`มี ${n} ตัวเลือก`:'ยังไม่มีตัวเลือก';};
    const setError=(msg)=>{errEl.textContent='';if(msg)setTimeout(()=>{errEl.textContent=msg;},30);};

    /* ---- settings object for the renderer ---- */
    const calmNow=()=>!!$('chkRandCalm').checked;
    const settingsObj=()=>({style:st.style,color_theme:st.theme,spin_duration:st.spin,duration:st.hold,scale:st.scale,offset_x:st.ox,offset_y:st.oy,anchor:st.anchor,reduce_motion:calmNow(),mode:st.style});
    const lookPayload=(winnerIndex)=>{const items=readItems();return {title:title.value.trim()||'สุ่มกิจกรรม',items:items.length?items:['ตัวเลือก 1','ตัวเลือก 2','ตัวเลือก 3'],winnerIndex:winnerIndex||0,settings:settingsObj()};};

    /* ---- inline preview ---- */
    const stage=$('rzStage');const fitBox=document.createElement('div');fitBox.className='rz-fit';stage.append(fitBox);
    let ctl=null,previewDirty=false;
    const btnSpin=$('btnRandPreviewSpin');
    const fit=()=>{
      if(!ctl)return;
      const avail=Math.max(160,stage.clientWidth-22);const nat=ctl.naturalSize();
      const scale=clamp(Math.min(avail/640,520/Math.max(1,nat.h)),0.2,1);
      ctl.setFit(scale);fitBox.style.width=Math.round(640*scale)+'px';fitBox.style.height=Math.round(nat.h*scale)+'px';
    };
    const mount=()=>{
      try{
        const p=lookPayload(0);
        ctl=V.create(fitBox,p,{position:'static',keepVisible:true,onDone:()=>{btnSpin.textContent='ทดลองหมุนอีกครั้ง';if(previewDirty){previewDirty=false;}}}).show();
        fit();
      }catch(e){console.warn('randomizer preview',e);}
    };
    let rebuildTimer=0;
    const refreshPreview=()=>{
      if(!ctl)return;
      if(ctl.running){previewDirty=true;return;}
      ctl.setLook(lookPayload(0));btnSpin.textContent='ทดลองหมุนในช่องตัวอย่าง';fit();drawLocator();
    };
    const refreshSoon=()=>{clearTimeout(rebuildTimer);rebuildTimer=setTimeout(refreshPreview,140);};

    /* ---- locator ---- */
    const loc=$('rzLocator'),locRect=$('rzLocRect'),locText=$('rzLocText');
    function drawLocator(){
      const nat=ctl?ctl.naturalSize():{w:640,h:700};if(!nat.h)nat.h=700;const k=st.scale/100,w=640*k,h=nat.h*k;
      const M=40;let x,y;
      if(st.anchor.endsWith('left'))x=M;else if(st.anchor.endsWith('right'))x=1920-M-w;else x=(1920-w)/2;
      if(st.anchor.startsWith('top'))y=M;else if(st.anchor.startsWith('bottom'))y=1080-M-h;else y=(1080-h)/2;
      x+=st.ox;y+=st.oy;
      locRect.style.left=(x/19.2)+'%';locRect.style.top=(y/10.8)+'%';locRect.style.width=(w/19.2)+'%';locRect.style.height=(h/10.8)+'%';
      const out=x<-1||y<-1||x+w>1921||y+h>1081;
      locText.textContent=`${ANCHOR_LABEL[st.anchor]} ขนาด ${Math.round(st.scale)} เปอร์เซ็นต์ เลื่อนซ้ายขวา ${st.ox} เลื่อนขึ้นลง ${st.oy} พิกเซล${out?' บางส่วนอยู่นอกจอ':''}`;
      locText.classList.toggle('rz-warn',out);
    }

    /* ---- drag / resize directly on the stream preview ---- */
    (function(){
      const handle=document.createElement('span');handle.className='rz-loc-handle';handle.setAttribute('aria-hidden','true');locRect.append(handle);
      const gv=document.createElement('span');gv.className='rz-loc-guide v';const gh=document.createElement('span');gh.className='rz-loc-guide h';loc.append(gv,gh);
      const M=40,SNAP=14;let drag=null;
      const geom=()=>{const r=locRect.getBoundingClientRect(),l=loc.getBoundingClientRect(),k=1920/Math.max(1,l.width);return {x:(r.left-l.left)*k,y:(r.top-l.top)*k,w:r.width*k,h:r.height*k,k};};
      const toTopLeft=(g)=>{st.anchor='top-left';const c=pane.querySelector('input[name="randAnchorPos"][value="top-left"]');if(c)c.checked=true;putOx(g.x-M);putOy(g.y-M);};
      const start=(mode)=>(e)=>{
        if(e.button!==undefined&&e.button!==0)return;e.preventDefault();e.stopPropagation();
        try{locRect.focus({preventScroll:true});}catch(_){}
        const g=geom();toTopLeft(g);drag={mode,sx:e.clientX,sy:e.clientY,g};
        locRect.classList.add('dragging');try{e.currentTarget.setPointerCapture(e.pointerId);}catch(_){}
      };
      locRect.tabIndex=0;locRect.setAttribute('role','slider');locRect.setAttribute('aria-label','ตำแหน่งวงล้อบนจอ ลากหรือกดลูกศรเพื่อย้าย ค้าง Ctrl เพื่อลากอิสระ');
      locRect.addEventListener('keydown',(e)=>{
        if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;e.preventDefault();
        const n=e.shiftKey?10:1;
        putOx(st.ox+(e.key==='ArrowLeft'?-n:e.key==='ArrowRight'?n:0));putOy(st.oy+(e.key==='ArrowUp'?-n:e.key==='ArrowDown'?n:0));
        onSetting(false);
      });
      locRect.addEventListener('pointerdown',start('move'));
      handle.addEventListener('pointerdown',start('size'));
      const move=(e)=>{
        if(!drag)return;const k=drag.g.k,dx=(e.clientX-drag.sx)*k,dy=(e.clientY-drag.sy)*k;
        const nat=ctl?ctl.naturalSize():{w:640,h:700};const ratio=(nat.h||700)/640;
        if(drag.mode==='move'){
          let x=drag.g.x+dx,y=drag.g.y+dy;const w=drag.g.w,h=drag.g.h;
          x=clamp(x,0,1920-w);y=clamp(y,0,1080-h);
          let sv=false,sh=false;
          if(!(e.ctrlKey||e.metaKey)){
          if(Math.abs(x+w/2-960)<SNAP){x=960-w/2;sv=true;}
          if(Math.abs(y+h/2-540)<SNAP){y=540-h/2;sh=true;}
          if(Math.abs(x)<SNAP/2)x=0;if(Math.abs(x+w-1920)<SNAP/2)x=1920-w;
          if(Math.abs(y)<SNAP/2)y=0;if(Math.abs(y+h-1080)<SNAP/2)y=1080-h;
          }
          gv.style.display=sv?'block':'none';gh.style.display=sh?'block':'none';
          putOx(x-M);putOy(y-M);
        }else{
          let w=drag.g.w+dx;const maxW=Math.min(1920-drag.g.x,(1080-drag.g.y)/ratio);
          const sc=clamp(Math.round(clamp(w,0,maxW)/640*100/5)*5,20,300);
          putScale(sc);
        }
        onSetting(false);
      };
      const end=()=>{if(!drag)return;drag=null;locRect.classList.remove('dragging');gv.style.display='none';gh.style.display='none';};
      [locRect,handle].forEach(el=>{el.addEventListener('pointermove',move);el.addEventListener('pointerup',end);el.addEventListener('pointercancel',end);});
    })();

    /* ---- live demo on OBS and Studio ---- */
    let demoOn=false,demoTimer=0,demoPending=false,keepalive=0;
    const demoBtn=$('btnRandDemo'),demoStatus=$('rzDemoStatus');
    const OFF_TEXT='ปิดอยู่ เปิดแล้วจะเห็นขนาดและตำแหน่งจริงบนจอสตรีม และปรับได้ทันทีโดยไม่ต้องเริ่มใหม่';
    function emit(payload){
      try{window.BP3_BUS?.emit('RANDOMIZER_SPIN',payload);}catch(_){}
      if(!window.BP3Transport&&'BroadcastChannel' in window){try{const bc=new BroadcastChannel('bp3_system_channel');bc.postMessage({event:'RANDOMIZER_SPIN',payload});bc.close();}catch(_){}}
    }
    const demoPayload=(action)=>Object.assign({type:'randomizer_spin',action,demo:true},lookPayload(0),{duration:st.hold});
    function demoSync(){
      if(!demoOn)return;
      if(demoPending)return;demoPending=true;
      demoTimer=setTimeout(()=>{demoPending=false;if(demoOn)emit(demoPayload('demo_layout'));},90);
    }
    function setDemo(on,silent){
      if(on===demoOn)return;demoOn=on;
      demoBtn.setAttribute('aria-pressed',on?'true':'false');
      demoBtn.textContent=on?'หยุดตัวอย่างบนจอ OBS':'แสดงตัวอย่างจริงบนจอ OBS';
      clearInterval(keepalive);clearTimeout(demoTimer);demoPending=false;
      if(on){emit(demoPayload('demo_start'));keepalive=setInterval(()=>emit(demoPayload('demo_layout')),20000);demoStatus.textContent='กำลังแสดงบนจอ OBS ลองปรับขนาดหรือตำแหน่งได้เลย เห็นผลทันที กดปุ่มอีกครั้งเมื่อพอใจ';}
      else{emit({type:'randomizer_spin',action:'demo_stop'});demoStatus.textContent=silent||OFF_TEXT;}
    }
    demoBtn.addEventListener('click',()=>setDemo(!demoOn));
    window.BP3RandomizerStopDemo=()=>{if(demoOn)setDemo(false,'ปิดอัตโนมัติเพราะปิดหน้าต่างสุ่มแล้ว');};
    window.addEventListener('pagehide',()=>{if(demoOn)emit({type:'randomizer_spin',action:'demo_stop'});});
    const win=$('win-randomizer');
    if(win&&window.MutationObserver)new MutationObserver(()=>{if(demoOn&&getComputedStyle(win).display==='none')setDemo(false,'ปิดอัตโนมัติเพราะปิดหน้าต่างสุ่มแล้ว');}).observe(win,{attributes:true,attributeFilter:['class','style']});

    /* ---- change wiring ---- */
    const onSetting=(rebuild)=>{persist();drawLocator();demoSync();if(rebuild)refreshSoon();};
    const syncPair=(rangeId,numId,key,min,max)=>{
      const r=$(rangeId),n=$(numId);
      const put=(v)=>{st[key]=clamp(Math.round(v),min,max);r.value=clamp(st[key],Number(r.min),Number(r.max));n.value=st[key];};
      put(st[key]);
      r.addEventListener('input',()=>{put(toNum(r.value,st[key]));onSetting(false);});
      n.addEventListener('input',()=>{if(n.value==='')return;put(toNum(n.value,st[key]));onSetting(false);});
      n.addEventListener('change',()=>{put(toNum(n.value,st[key]));onSetting(false);});
      return put;
    };
    const putScale=syncPair('randScale','randScaleNum','scale',20,300);
    const putOx=syncPair('randOx','randOxNum','ox',-1920,1920);
    const putOy=syncPair('randOy','randOyNum','oy',-1080,1080);
    const hold=$('randHold');if(![...hold.options].some(o=>Number(o.value)===st.hold))hold.add(new Option(st.hold+' วินาที',String(st.hold)));hold.value=String(st.hold);
    hold.addEventListener('change',()=>{st.hold=toNum(hold.value,5);onSetting(false);});
    $('chkRandRemove').checked=st.remove;$('chkRandRemove').addEventListener('change',()=>{st.remove=$('chkRandRemove').checked;persist();});
    $('chkRandCalm').checked=st.calm;$('chkRandCalm').addEventListener('change',()=>{st.calm=$('chkRandCalm').checked;onSetting(true);});
    pane.addEventListener('change',(e)=>{
      const t=e.target;if(!t||t.type!=='radio')return;
      if(t.name==='randStyle')st.style=t.value;
      else if(t.name==='randTheme')st.theme=t.value;
      else if(t.name==='randSpeed')st.spin=toNum(t.value,4);
      else if(t.name==='randAnchorPos')st.anchor=t.value;
      else return;
      onSetting(t.name!=='randAnchorPos');
    });
    $('btnRandLayoutReset').addEventListener('click',()=>{
      putScale(100);putOx(0);putOy(0);st.anchor='center';
      const c=pane.querySelector('input[name="randAnchorPos"][value="center"]');if(c)c.checked=true;
      onSetting(false);
      demoStatus.textContent=demoOn?'คืนค่าตำแหน่งและขนาดเริ่มต้นแล้ว':OFF_TEXT;
    });
    const onItems=()=>{showCount();setError('');try{write(LAST,{title:title.value,items:text.value});}catch(_){}refreshSoon();demoSync();};
    text.addEventListener('input',onItems);title.addEventListener('input',onItems);
    const preset=$('randomizerPresetSelect');
    if(preset)preset.addEventListener('change',onItems);
    const buttons=preset?preset.parentElement.querySelectorAll('button'):[];
    if(buttons[1])buttons[1].addEventListener('click',onItems);
    btnSpin.addEventListener('click',()=>{
      if(!ctl)return;
      if(ctl.running){ctl.stop();btnSpin.textContent='ทดลองหมุนในช่องตัวอย่าง';fit();return;}
      const items=readItems();const idx=items.length?Math.floor(Math.random()*items.length):0;
      ctl.setLook(lookPayload(idx));fit();ctl.start();btnSpin.textContent='หยุดตัวอย่าง';
    });
    if(window.ResizeObserver)new ResizeObserver(()=>{fit();drawLocator();}).observe(stage);

    /* ---- real spin ---- */
    let busy=false;
    const runBtn=$('btnRandRun'),result=$('randWinnerResult');
    function spin(){
      if(busy)return;
      const items=readItems();
      if(!items.length){setError('ยังไม่มีตัวเลือก กรุณาพิมพ์ตัวเลือกอย่างน้อย 1 อย่างที่ขั้นตอนที่ 1');text.focus();return;}
      setError('');
      if(demoOn)setDemo(false);
      const idx=Math.floor(Math.random()*items.length),chosen=items[idx],ttl=title.value.trim()||'สุ่มกิจกรรม';
      const payload={type:'randomizer_spin',action:'spin',title:ttl,items,winner:chosen,winnerIndex:idx,duration:st.hold,settings:settingsObj()};
      emit(payload);
      // play the same spin in the panel's stage so the suspense is visible even when OBS is not on screen
      try{if(ctl){if(ctl.running)ctl.stop();ctl.setLook(lookPayload(idx));fit();ctl.start();btnSpin.textContent='หยุดตัวอย่าง';if(stage.scrollIntoView)stage.scrollIntoView({block:'nearest',behavior:'auto'});}}catch(e){console.warn('randomizer panel spin',e);}
      busy=true;runBtn.setAttribute('aria-disabled','true');runBtn.textContent='กำลังสุ่ม...';
      result.textContent='กำลังสุ่ม...';
      const calm=calmNow();
      setTimeout(()=>{
        result.replaceChildren();
        const small=document.createElement('span');small.textContent='ผลการสุ่มล่าสุด '+ttl;const b=document.createElement('b');b.textContent=chosen;result.append(small,b);
        if(st.remove){const rest=items.slice();rest.splice(idx,1);setItemsText(rest);}
        busy=false;runBtn.removeAttribute('aria-disabled');runBtn.textContent='เริ่มสุ่มบนจอ OBS ทันที';
        try{showToast('ผลการสุ่ม '+chosen);}catch(_){}
        try{if(typeof appendAskChatSystemMessage==='function')appendAskChatSystemMessage(`🎰 [สุ่มกิจกรรมด่วน] <b>${esc(ttl)}</b> ➔ ผลลัพธ์: <b style="color:#34d399;">${esc(chosen)}</b>`);}catch(_){}
      },calm?600:Math.round(st.spin*1000+700));
      return payload;
    }
    runBtn.addEventListener('click',(e)=>{if(busy){e.preventDefault();e.stopImmediatePropagation();}},true);

    function shuffle(){const a=readItems();for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}setItemsText(a);countEl.textContent=`สลับลำดับแล้ว มี ${a.length} ตัวเลือก`;}
    function clear(){setItemsText([]);text.focus();countEl.textContent='ล้างตัวเลือกทั้งหมดแล้ว';}
    function pullChatters(){
      const names=Array.from(window._activeChattersSet||[]).map(String).filter(Boolean);
      if(!names.length){setError('ยังไม่มีคนดูที่พิมพ์ในแชทสด ลองรอให้มีคนพิมพ์ก่อน หรือพิมพ์ชื่อเองก็ได้');return;}
      setItemsText(names.slice(0,200));countEl.textContent=`ดึงชื่อคนที่พิมพ์ในแชทมา ${Math.min(names.length,200)} คนแล้ว`;
    }

    window.BP3RandomizerUI={spin,shuffle,clear,pullChatters,state:st,get preview(){return ctl;},get demoOn(){return demoOn;}};
    showCount();mount();drawLocator();
    // popout/hidden windows have no width until shown: refit on the first visible frame
    if(window.requestAnimationFrame)requestAnimationFrame(()=>{fit();drawLocator();});
  }
  function init(){
    const doc=getToolDocument('replie');
    const add=doc.querySelector('#paneReplieTab1 button.primary');if(add)add.onclick=()=>editReplieCommand();
    const save=doc.querySelector('#win-replie .floating-footer button.primary');if(save)save.onclick=()=>{saveReplieSettings();closeToolWindow('replie');};
    const loop=doc.querySelector('#paneReplieTab1 input[type="checkbox"]');if(loop)loop.onchange=()=>{if(!loop.checked)window.BP3_BUS?.emit('REPLIE_DISMISS',{});};
    const settings=read('bp3_replie_settings',null);
    if(settings){const dur=doc.querySelector('#paneReplieTab2 input[type="number"]');if(dur)dur.value=settings.duration;const scale=doc.querySelector('#paneReplieTab2 input[type="range"]');if(scale){scale.value=settings.scale;doc.getElementById('lblReplieScale').textContent=settings.scale+'%';}doc.querySelectorAll('.pos-btn').forEach(btn=>btn.classList.toggle('active',posMap[btn.textContent.trim()]===settings.anchor));}
    const select=getToolDocument('playroom').getElementById('selPlayroomTrigger');
    if(select)Object.keys(savedClips).forEach(command=>{if(!Array.from(select.options).some(option=>option.value===command))select.add(new Option(command,command));});
    const playroom=getToolDocument('playroom');
    const addLink=playroom.querySelector('[onclick="addPlayroomClipRow()"]');
    if(addLink){
      addLink.textContent='+ เพิ่มลิงก์';const importButton=playroom.createElement('button');importButton.id='btnPlayroomImportLocal';importButton.className='btn-topbar-action';importButton.textContent='เลือกไฟล์จากเครื่อง';addLink.after(importButton);
      importButton.onclick=()=>{const fileDocument=getToolDocument('playroom');const picker=fileDocument.createElement('input');picker.type='file';picker.multiple=true;picker.accept='image/*,video/mp4,video/webm,video/quicktime,audio/*';picker.style.display='none';fileDocument.body.append(picker);picker.oncancel=()=>picker.remove();picker.onchange=async()=>{importButton.disabled=true;try{for(const file of picker.files){const response=await fetch('/api/playroom/import',{method:'POST',headers:{'Content-Type':'application/octet-stream','X-Filename':encodeURIComponent(file.name)},body:file});const clip=await response.json();if(!response.ok)throw new Error(clip.error || 'นำเข้าไฟล์ไม่สำเร็จ');_activePlayroomClips.push({...clip,weight:50,vol:100});saveClips();}renderPlayroomClipsTable();}catch(error){showToast(error.message);}finally{importButton.disabled=false;picker.remove();}};picker.click();};
    }
    const playroomDoc=getToolDocument('playroom');
    const daily=playroomDoc.createElement('input');daily.id='playroomDailyLimit';daily.type='number';daily.min='0';daily.value=window._playroomTriggerMeta[_activePlayroomTrigger]?.daily_limit || 0;daily.className='modal-input';daily.style.width='70px';
    const label=playroomDoc.createElement('label');label.style.cssText='display:flex;align-items:center;gap:6px;font-size:12px';label.append('ครั้งต่อคน/วัน (0 ไม่จำกัด)',daily);playroomDoc.getElementById('selPlayroomTrigger')?.parentElement.append(label);
    daily.oninput=()=>{const meta=window._playroomTriggerMeta[_activePlayroomTrigger] ||= {};meta.daily_limit=Math.max(0,Number(daily.value)||0);write('bp3_playroom_trigger_meta',window._playroomTriggerMeta);};
    renderReplieCommands();renderPlayroomClipsTable();renderGwTable();
    setupPresets('ask',document.getElementById('paneAskTab1'));
    setupPresets('randomizer',document.getElementById('paneRandTab1'));
    try{setupRandomizerUI();}catch(error){console.warn('randomizer ui',error);}
    if(new URLSearchParams(location.search).get('tool')==='composer') setTimeout(()=>openToolWindow('composer'),100);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
