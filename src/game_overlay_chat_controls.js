/* Game Overlay has its own legacy-compatible appearance settings. */
(()=>{'use strict';
 const modes=[['default','Default'],['theme','Theme'],['special','Balloon'],['character','Character Talk']];
 const choices={layout:[['inline','1 บรรทัด (ชื่อ: ข้อความ)'],['stacked','2 บรรทัด'],['message_only','เฉพาะข้อความ'],['inline_no_logo','1 บรรทัด ไม่มีโลโก้'],['stacked_no_logo','2 บรรทัด ไม่มีโลโก้']],font_family:['Kanit','Prompt','Sarabun','Mitr','Bai Jamjuree','Noto Sans Thai','IBM Plex Sans Thai','Plus Jakarta Sans'],font_weight:['300','400','500','600','700'],anim_in:['minimal','fade','slide_left','slide_up','zoom','bounce','pop','flip','glow','typewriter','slide_pop','card_flip','liquid','neon_pulse','glassy','elastic'],anim_out:['fade_out','slide_right','slide_down','shrink','blur_out','dissolve']};
 const groups=[
  ['📝 เนื้อหาและการจัดวาง',[['show_logo','แสดงโลโก้แพลตฟอร์ม','checkbox'],['show_timestamp','แสดงเวลา','checkbox'],['layout','รูปแบบข้อความ','select'],['font_size','ขนาดตัวอักษร (px)','number',10,64],['emote_size','ขนาด Emote (px)','number',12,64],['animated_emotes','แสดง Twitch Emote แบบเคลื่อนไหว','checkbox'],['max_rows','จำนวนข้อความสูงสุด','number',1,100],['max_msg_length','ความยาวข้อความสูงสุด (0 = ไม่จำกัด)','number',0,500],['msg_spacing','ระยะห่างข้อความ (px)','number',0,30,0.5],['demo_interval','ช่วงเวลา Loop Demo (วินาที)','number',1,60,0.5]]],
  ['🔤 ฟอนต์และสี',[['font_family','ฟอนต์','select'],['font_weight','น้ำหนักฟอนต์','select'],['text_color','สีข้อความ','color'],['text_stroke','เส้นขอบตัวอักษร','checkbox'],['text_stroke_color','สีเส้นขอบ','color'],['text_stroke_width','ความหนาเส้นขอบ','number',0,6],['text_shadow','เงาตัวอักษร','checkbox'],['text_shadow_color','สีเงา','color'],['text_shadow_blur','ความฟุ้งเงา','number',0,10]]],
  ['🎬 การเคลื่อนไหว',[['anim_in','เมื่อข้อความเข้า','select'],['anim_out','เมื่อข้อความออก','select'],['auto_hide','ซ่อนข้อความเมื่อหมดเวลา','checkbox'],['hide_after','ซ่อนหลัง (วินาที)','number',3,60]]],
  ['📦 กล่องข้อความ',[['box_enabled','แสดงกล่องข้อความ','checkbox'],['box_bg_color','สีพื้นหลัง','color'],['box_bg_opacity','ความทึบพื้นหลัง','number',0,1,0.05],['box_radius','มุมโค้ง','number',0,30],['box_border','แสดงเส้นขอบกล่อง','checkbox'],['box_border_color','สีขอบกล่อง','color'],['box_border_width','ความหนาขอบกล่อง','number',0,6],['box_shadow','เงากล่อง','checkbox'],['box_glow','แสงรอบกล่อง','checkbox'],['box_glow_color','สีแสง','color']]],
  ['🎈 Balloon',[['balloon_hide_after','เวลาข้อความหาย (วินาที)','number',2,30],['balloon_bg_opacity','ความทึบพื้นหลัง','number',0.1,1,0.05]],'special'],
  ['🎭 Character Talk',[['character_hide_after','เวลาข้อความหาย (วินาที)','number',2,60],['character_size','ขนาดตัวละคร (px)','number',40,400],['character_max_on_screen','จำนวนตัวละครสูงสุด','number',1,30],['character_random_pos','สุ่มตำแหน่ง','checkbox'],['character_bubble_width','ความกว้างกล่องข้อความ','number',200,800],['character_name_size','ขนาดชื่อตัวละคร','number',8,24],['character_name_stroke','เส้นขอบชื่อ','checkbox'],['character_name_stroke_color','สีเส้นขอบชื่อ','color'],['character_name_stroke_width','ความหนาเส้นขอบชื่อ','number',1,4],['character_name_shadow','เงาชื่อ','checkbox'],['character_name_shadow_color','สีเงาชื่อ','color'],['character_name_shadow_blur','ความฟุ้งเงาชื่อ','number',0,8]],'character']
 ];
 let state=null, targetDoc=null, chain=Promise.resolve(), timer=null, themePage=0;
 const THEMES_PER_PAGE=10;
 const el=(doc,tag,cls,text)=>{const n=doc.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n};
 function status(message,error=false){const n=targetDoc?.getElementById('gameChatSaveStatus');if(n){n.textContent=message;n.classList.toggle('error',error)}}
 function post(mode,key,value,rerender=false){
  chain=chain.catch(()=>{}).then(async()=>{status('กำลังบันทึก...');const r=await fetch('/api/game-chat-settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode,key,value})});const result=await r.json();if(!r.ok)throw Error(result.error || 'บันทึกไม่สำเร็จ');state=result;status('บันทึกแล้ว');if(rerender)render();}).catch(e=>{status('บันทึกไม่สำเร็จ: '+e.message,true);throw e});
  return chain;
 }
 function renderThemeCards(){
  const doc=targetDoc, grid=doc?.getElementById('gameChatThemeGrid');
  if(!grid||!state)return;
  const themes=state.themes||[], total=Math.max(1,Math.ceil(themes.length/THEMES_PER_PAGE));
  themePage=Math.max(0,Math.min(themePage,total-1));
  grid.replaceChildren();
  themes.slice(themePage*THEMES_PER_PAGE,themePage*THEMES_PER_PAGE+THEMES_PER_PAGE).forEach(([key,label])=>{
   const name=label.replace(/\s*\([^)]*[\u0E00-\u0E7F][^)]*\)/g,'').trim();
   const button=el(doc,'button','game-chat-theme-card'+(state.values.theme===key?' active':''),name);
   button.type='button';button.dataset.theme=key;button.setAttribute('aria-pressed',String(state.values.theme===key));
   button.onclick=()=>post(state.mode,'theme',key).then(()=>renderThemeCards()).catch(()=>{});
   grid.append(button);
  });
  const page=doc.getElementById('gameChatThemePage'),prev=doc.getElementById('gameChatThemePrev'),next=doc.getElementById('gameChatThemeNext');
  if(page)page.textContent=`หน้า ${themePage+1} / ${total}`;
  if(prev)prev.disabled=themePage===0;
  if(next)next.disabled=themePage>=total-1;
  const custom=doc.getElementById('gameChatCustomCss');if(custom)custom.hidden=state.values.theme!=='custom';
 }
 function renderHotkeys(){
  const doc=targetDoc, root=doc?.getElementById('gameOverlayHotkeys');if(!root||!state)return;
  root.replaceChildren();const card=el(doc,'div','voice-setting-card game-hotkey-card');
  const title=el(doc,'div','voice-setting-card-title');title.append(el(doc,'span','','🔑 ปุ่มลัด Game Overlay'));card.append(title);
  const rows=el(doc,'div','game-hotkey-fields');
  for(const [key,label] of [['hotkey','เปิด / ปิด Game Overlay'],['hotkey_edit','สลับโหมดปรับตำแหน่ง']]){
   const row=el(doc,'div','game-hotkey-row');row.append(el(doc,'span','',label));const button=el(doc,'button','game-chat-mode',String(state.values[key]||''));button.type='button';button.title='คลิกแล้วกดชุดคีย์ลัดใหม่';
   button.onclick=()=>{button.dataset.capturing='true';button.textContent='กดคีย์ลัดใหม่ (Esc เพื่อยกเลิก)';button.focus()};
   button.onkeydown=e=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();delete button.dataset.capturing;button.textContent=state.values[key]||'';button.blur();return}const modifiers=[e.ctrlKey?'ctrl':'',e.shiftKey?'shift':'',e.altKey?'alt':'',e.metaKey?'win':''].filter(Boolean),main=e.key.toLowerCase();if(!modifiers.length||!/^([a-z0-9]|f(?:[1-9]|1\d|2[0-4]))$/.test(main))return;e.preventDefault();e.stopPropagation();delete button.dataset.capturing;const chord=[...modifiers,main].join('+');post(state.mode,key,chord).then(()=>renderHotkeys()).catch(()=>{button.textContent=state.values[key]||''})};row.append(button);rows.append(row)
  }card.append(rows);root.append(card);
 }
 function render(){
  const doc=targetDoc, root=doc?.getElementById('gameChatCustomizer');if(!root||!state)return;root.replaceChildren();
  renderHotkeys();
  const heading=el(doc,'div','game-chat-head');heading.append(el(doc,'strong','', '🎮 ปรับแต่งแชท Game Overlay'),el(doc,'span','', 'แยกจาก Chat Widget ใน Composer'));root.append(heading);
  const modeRow=el(doc,'div','game-chat-modes');for(const [key,label] of modes){const b=el(doc,'button','game-chat-mode'+(state.mode===key?' active':''),label);b.type='button';b.setAttribute('aria-pressed',String(state.mode===key));b.onclick=()=>post(key,'mode',key,true).catch(()=>{});modeRow.append(b)}root.append(modeRow);
  const saved=el(doc,'div','game-chat-status','ปรับค่าแล้วบันทึกทันที');saved.id='gameChatSaveStatus';saved.setAttribute('role','status');root.append(saved);
  if(state.mode==='theme'){
   const card=el(doc,'div','game-chat-panel');card.append(el(doc,'div','game-chat-theme-title','🎨 Theme'));
   const grid=el(doc,'div','game-chat-theme-grid');grid.id='gameChatThemeGrid';card.append(grid);
   const pager=el(doc,'div','game-chat-theme-pagination');const prev=el(doc,'button','game-chat-page-btn','◀ ก่อนหน้า');prev.type='button';prev.id='gameChatThemePrev';prev.onclick=()=>{themePage--;renderThemeCards()};const page=el(doc,'span','game-chat-page-indicator');page.id='gameChatThemePage';const next=el(doc,'button','game-chat-page-btn','ถัดไป ▶');next.type='button';next.id='gameChatThemeNext';next.onclick=()=>{themePage++;renderThemeCards()};pager.append(prev,page,next);card.append(pager);
   {const caption=el(doc,'label','game-chat-custom-css','Custom CSS');caption.id='gameChatCustomCss';caption.hidden=state.values.theme!=='custom';const area=el(doc,'textarea','modal-input');area.rows=5;area.value=state.values.custom_css||'';area.onchange=()=>post(state.mode,'custom_css',area.value).catch(()=>{});caption.append(area);card.append(caption)}root.append(card);
   const selected=Math.max(0,(state.themes||[]).findIndex(([key])=>key===state.values.theme));themePage=Math.floor(selected/THEMES_PER_PAGE);renderThemeCards();
  }
  if(state.mode==='character'){
   const panel=el(doc,'div','game-chat-panel'),row=el(doc,'label','game-chat-row');row.append(el(doc,'span','','🖼️ ภาพตัวละครเริ่มต้นสำหรับ Game Overlay'));
   const input=el(doc,'input','modal-input');input.type='file';input.accept='image/png,image/jpeg,image/webp,image/gif,image/bmp';input.onchange=async()=>{const file=input.files?.[0];if(!file)return;try{status('กำลังนำเข้าภาพ...');const r=await fetch('/api/playroom/import',{method:'POST',headers:{'X-Filename':encodeURIComponent(file.name),'Content-Type':'application/octet-stream'},body:file});const result=await r.json();if(!r.ok||result.type!=='image')throw Error(result.error||'นำเข้าภาพไม่สำเร็จ');await post('character','default_image_url',result.url,true)}catch(e){status(e.message,true)}};row.append(input);panel.append(row);
   if(state.values.default_image_url){const image=el(doc,'img','game-chat-character-preview');image.src=state.values.default_image_url;image.alt='ภาพตัวละครเริ่มต้น';panel.append(image);const clear=el(doc,'button','game-chat-mode','ใช้ภาพเริ่มต้นของโปรแกรม');clear.type='button';clear.onclick=()=>post('character','default_image_url','',true).catch(()=>{});panel.append(clear)}root.append(panel);
  }
  for(const [title,fields,only] of groups){if(only && state.mode!==only)continue;const panel=el(doc,'details','game-chat-panel');panel.open=!only && title.startsWith('📝');panel.append(el(doc,'summary','',title));const content=el(doc,'div','game-chat-fields');
   for(const [key,label,type,min,max,step] of fields){if(key==='show_timestamp')continue;const row=el(doc,'label','game-chat-row');row.append(el(doc,'span','',label));let control;
    if(type==='select'){control=el(doc,'select','modal-input');for(const option of choices[key]||[]){const [value,text]=Array.isArray(option)?option:[option,option];const item=el(doc,'option','',text);item.value=value;control.append(item)}}
    else{control=el(doc,'input',type==='number'?'game-range-input':'modal-input');control.type=type==='number'?'range':type;if(type==='number'){control.min=min;control.max=max;control.step=step||1}}
    control.dataset.gameChatKey=key;if(type==='checkbox')control.checked=!!state.values[key];else control.value=state.values[key] ?? '';
    control.addEventListener('change',()=>{const value=type==='checkbox'?control.checked:type==='number'?Number(control.value):control.value;if(type==='number'&&(!control.validity.valid||!control.value)){status('กรุณากรอกค่าในช่วงที่กำหนด',true);return}post(state.mode,key,value).catch(()=>{})});
    if(type==='number'){const wrap=el(doc,'div','game-range-wrap'),output=el(doc,'output','game-range-value');const format=()=>{const isOpacity=key==='box_bg_opacity'||key==='balloon_bg_opacity';output.textContent=isOpacity?Math.round(Number(control.value)*100)+'%':control.value;};control.addEventListener('input',format);format();wrap.append(control,output);row.append(wrap)}else row.append(control);content.append(row);
   }panel.append(content);root.append(panel);
  }
 }
 window.BP3GameChatSettings={async init(doc){targetDoc=doc;const root=doc?.getElementById('gameChatCustomizer');if(!root)return;root.textContent='กำลังโหลดการตั้งค่าแชท...';try{const r=await fetch('/api/game-chat-settings',{cache:'no-store'});if(!r.ok)throw Error('ไม่สามารถโหลดการตั้งค่าได้');state=await r.json();render()}catch(e){root.textContent='ไม่สามารถโหลดการตั้งค่า Game Overlay: '+e.message}},flush:()=>chain};
 let viewerQueue=Promise.resolve();
 window.BP3GameSliders={init(doc){doc.querySelectorAll('#win-game-overlay input[type="range"][data-output]').forEach(control=>{const output=doc.getElementById(control.dataset.output);if(!output)return;const update=()=>{output.textContent=control.dataset.percent==='true'?Math.round(Number(control.value)*100)+'%':control.value+(control.dataset.unit||'')};if(!control.dataset.sliderLabelBound){control.addEventListener('input',update);control.dataset.sliderLabelBound='1'}update()})}};
 const viewerFields={goViewerMode:'mode',goViewerAlign:'align',goViewerWidth:'width',goViewerHeight:'height',goViewerAlpha:'alpha',goViewerFontSize:'font_size',goViewerIconSize:'icon_size',goViewerFontColor:'font_color',goViewerTextStroke:'text_stroke',goViewerTextStrokeColor:'text_stroke_color',goViewerTextStrokeWidth:'text_stroke_width',goViewerTextShadow:'text_shadow',goViewerTextShadowColor:'text_shadow_color',goViewerTextShadowBlur:'text_shadow_blur'};
 window.BP3ViewerOverlaySettings={init(doc){for(const [id,key] of Object.entries(viewerFields)){const control=doc.getElementById(id);if(!control||control.dataset.viewerLiveBound)continue;control.dataset.viewerLiveBound='1';control.addEventListener('change',()=>{const badge=doc.getElementById('viewerOverlaySaveStatus');const show=(text,error=false)=>{if(badge){badge.textContent=text;badge.classList.toggle('error',error)}};const numeric=control.type==='number'||control.type==='range';const value=control.type==='checkbox'?control.checked:numeric?Number(control.value):control.value;if(numeric&&(!control.value||!control.validity.valid)){show('กรุณากรอกค่าในช่วงที่กำหนด',true);return}viewerQueue=viewerQueue.catch(()=>{}).then(async()=>{show('กำลังบันทึก...');const r=await fetch('/api/viewer-overlay-settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({[key]:value})});if(!r.ok)throw Error('บันทึก Viewer Overlay ไม่สำเร็จ');show('บันทึกแล้ว')}).catch(e=>{show(e.message,true);throw e})})}},flush:()=>viewerQueue};
})();
