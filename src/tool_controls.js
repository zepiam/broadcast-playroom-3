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
    const randSettings=read('bp3_randomizer_display',{});
    for(const id of ['randAnchor','randHoldDuration','randSpinDuration','randColorTheme','randDisplayMode']){
      const field=document.getElementById(id);if(!field)continue;
      if(typeof randSettings[id]==='string' && [...field.options].some(option=>option.value===randSettings[id]))field.value=randSettings[id];
      field.addEventListener('change',()=>{randSettings[id]=field.value;write('bp3_randomizer_display',randSettings);});
    }
    if(new URLSearchParams(location.search).get('tool')==='composer') setTimeout(()=>openToolWindow('composer'),100);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
