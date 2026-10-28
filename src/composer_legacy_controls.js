/* Actual legacy avatar and donation controls; values remain profile-compatible. */
(()=>{'use strict';const VIEWER_THEMES=[["default", "⚪ Default (น้ำเงิน)"], ["neon", "🌈 Neon (ฟ้าเรืองแสง)"], ["glass", "🪟 Glass (กระจก)"], ["pill", "💊 Pill (ยาวกลม)"], ["dark", "🖤 Dark (เข้ม)"], ["cyberpunk", "🌃 Cyberpunk"], ["gold", "✨ Gold (ทอง)"], ["retro", "📺 Retro"], ["aqua", "💧 Aqua (ฟ้าน้ำทะเล)"], ["magma", "🌋 Magma (แดงส้ม)"], ["forest", "🌲 Forest (เขียวเข้ม)"], ["sapphire", "💎 Sapphire (น้ำเงินกลม)"], ["neon-purple", "🟣 Neon Purple"], ["sunset-orange", "🌅 Sunset Orange"], ["mono", "⬜ Mono (ขาวดำ)"], ["rainbow", "🏳️ Rainbow (สายรุ้ง)"], ["carbon", "🪨 Carbon (คาร์บอน)"], ["vapor", "💜 Vaporwave"], ["ice", "🧊 Ice (น้ำแข็ง)"], ["rose-gold", "🌹 Rose Gold (ทองกุหลาบ)"], ["emerald", "💚 Emerald (มรกต)"], ["sakura", "🌸 Sakura (ซากุระ)"], ["toxic", "☣️ Toxic (พิษเรืองแสง)"], ["blood-moon", "🌑 Blood Moon (จันทร์เลือด)"], ["chrome", "⚙️ Chrome (โครเมียม)"], ["coral", "🪸 Coral (ปะการัง)"], ["galaxy", "🌌 Galaxy (กาแล็กซี่)"], ["amber", "🟠 Amber (อำพัน)"]];
window.BP3LegacyControls={mount(body,w,save){
 if(!['avatar','donate_goal','viewer'].includes(w.type))return;
 const d=body.ownerDocument;let panel;
 function section(title){const card=d.createElement('section');card.className='comp-card-section';const header=d.createElement('div');header.className='comp-card-header';const text=d.createElement('span');text.className='comp-card-title';text.textContent=title;header.append(text);panel=d.createElement('div');panel.className='comp-card-body';card.append(header,panel);body.append(card);}
 section(w.type==='viewer'?'👥 รูปแบบยอดผู้ชม':w.type==='avatar'?'😊 ตัวละครและเสียง':'🎯 เป้าหมายโดเนต');
 function field(key,label,type='text',fallback='',options,id){
  const row=d.createElement('div');row.className='comp-field-row';const text=d.createElement('label');text.className='comp-field-label';text.textContent=label;row.append(text);
  const input=d.createElement(options?'select':'input');input.id=id || 'compLegacy_'+key;text.htmlFor=input.id;input.className=options?'cwc-select':type==='color'?'cwc-color-pick':'cwc-input';
  if(options)for(const [value,text] of options.map(x=>Array.isArray(x)?x:[x,x])){const o=d.createElement('option');o.value=value;o.textContent=text;input.append(o);}
  else input.type=type;
  if(options && w[key]!=null && ![...input.options].some(option=>option.value===String(w[key]))){const option=d.createElement('option');option.value=String(w[key]);option.textContent=String(w[key]);input.append(option);}
  if(type==='checkbox')input.checked=w[key] ?? fallback;else input.value=w[key] ?? fallback;
  input.onchange=()=>{const value=type==='checkbox'?input.checked:type==='number'?Number(input.value):input.value;w[key]=value;const aliases={showIcon:'viewer_show_icon',iconSize:'viewer_icon_size',strokeColor:'text_stroke_color'};const raw=aliases[key] || key.replace(/[A-Z]/g,c=>'_'+c.toLowerCase());w[raw]=value;if(key==='strokeColor')w.textStrokeColor=value;save();};
  if(type==='checkbox'){const toggle=d.createElement('label');toggle.className='cwc-switch';const slider=d.createElement('span');slider.className='cwc-switch-slider';toggle.append(input,slider);row.append(toggle);}else row.append(input);panel.append(row);return row;
 }
 if(w.type==='viewer'){
  field('viewerTheme','ธีม','text','default',VIEWER_THEMES,'compViewerTheme');
  field('viewerMode','แสดงยอด','text','both',[['both','รวมและรายแพลตฟอร์ม'],['total','ยอดรวม'],['per_platform','รายแพลตฟอร์ม']],'compViewerMode');
  field('viewerDirection','ทิศทาง','text','horizontal',[['horizontal','แนวนอน'],['vertical','แนวตั้ง']],'compViewerDirection');
  field('viewerAlign','จัดวาง','text','left',[['left','ซ้าย'],['center','กลาง'],['right','ขวา']],'compViewerAlign');
  field('showIcon','แสดงไอคอน','checkbox',true,null,'compViewerShowIcon');field('iconSize','ขนาดไอคอน','number',20,null,'compViewerIconSize');
  section('🔤 ตัวอักษร');field('fontFamily','ฟอนต์','text','Kanit',["Kanit", "Noto Sans Thai Looped", "Sarabun", "Prompt", "Mitr", "Chonburi", "Mali", "Bai Jamjuree", "Krub", "Taviraj", "Pattaya", "Itim", "Pridi", "Athiti", "Chakra Petch", "Kavivanar", "Charmonman", "Sriracha", "KoHo", "Fahkwang", "Roboto", "Inter", "Outfit", "Fredoka", "Bebas Neue", "Montserrat", "Poppins", "Open Sans", "Press Start 2P", "Arial", "Tahoma", "Segoe UI"],'compViewerFontFamily');field('fontSize','ขนาดตัวอักษร','number',18,null,'compViewerFontSize');field('fontWeight','ความหนา','text','600',['400','500','600','700','800'],'compViewerFontWeight');field('fontColor','สีตัวอักษร','color','#ffffff',null,'compViewerFontColor');
  section('✨ เส้นขอบและเงา');field('textStroke','เส้นขอบข้อความ','checkbox',false,null,'compViewerTextStroke');field('textStrokeWidth','ความหนาเส้นขอบ','number',2,null,'compViewerTextStrokeWidth');field('strokeColor','สีเส้นขอบ','color','#000000',null,'compViewerTextStrokeColor');field('textShadow','เงาข้อความ','checkbox',true,null,'compViewerTextShadow');field('textShadowBlur','ความฟุ้งเงา','number',3,null,'compViewerTextShadowBlur');field('textShadowColor','สีเงา','color','#000000',null,'compViewerTextShadowColor');
  section('📡 แพลตฟอร์มที่เชื่อมต่อ');const status=d.createElement('p');status.className='comp-settings-hint';status.textContent='แสดงเฉพาะแพลตฟอร์มที่เชื่อมต่อแชทอยู่โดยอัตโนมัติ';panel.append(status);
  const hint=d.createElement('p');hint.className='comp-settings-hint';hint.textContent='ปุ่มทดสอบเปลี่ยนเฉพาะตัวอย่างใน Composer กด “กลับไปใช้ยอดจริง” เพื่อยกเลิก เมื่อมีข้อมูลสดเข้ามาจะกลับเป็นยอดจริงอัตโนมัติ';panel.append(hint);
 }else if(w.type==='donate_goal'){
  /* EasyDonate setup hidden until planned; saved credentials retained. */field('dg_goal_title','ชื่อเป้าหมาย','text','เป้าหมายโดเนต');
  field('dg_goal_amount','ยอดเป้าหมาย','number',1000);field('dg_start_amount','ยอดเริ่มต้น','number',0);field('dg_currency','สกุลเงิน','text','฿');
  section('🎨 รูปแบบและสี');field('dg_theme','รูปแบบ','text','neon',['neon','minimal','cute','liquid','segment']);
  for(const [key,label,color] of [['bar','สีแถบ','#10b981'],['bg','สีพื้น','#1a1a2e'],['font','สีข้อความ','#e5e7eb'],['current','สียอดปัจจุบัน','#10b981'],['goal','สียอดเป้าหมาย','#9ca3af']])field('dg_'+key+'_color',label,'color',color);
  field('dg_font_size','ขนาดตัวอักษร','number',16);field('dg_opacity','ความทึบ (0–100)','number',100);field('dg_title_align','ตำแหน่งชื่อ','text','left',['left','center','right']);field('dg_show_donor','แสดงผู้โดเนตล่าสุด','checkbox',true);
 }else{
  field('avatar_preset','ตัวละคร','text','',[['','รูปภาพของฉัน'],['man','ชาย'],['girl','หญิง']]);
  field('avatar_mode','ตอบสนองเสียง','text','tts',[['tts','TTS'],['mic','ไมโครโฟน']]);
  section('🖼️ ภาพตัวละคร');for(const [role,label] of [['idle','ปกติ'],['talk','พูด'],['blink_idle','หลับตาปกติ'],['blink_talk','หลับตาพูด']]){
   const key='avatar_'+role+'_url',row=field(key,label);row.classList.add('comp-field-row-stack');const button=d.createElement('button');button.type='button';button.textContent='เลือกไฟล์';button.className='btn-comp-demo-action';button.id='compLegacyUpload_'+role;row.append(button);
   button.onclick=()=>{const picker=d.createElement('input');picker.type='file';picker.accept='image/*';picker.style.display='none';body.append(picker);picker.onchange=async()=>{try{const file=picker.files?.[0];if(!file)return;const response=await fetch('/api/playroom/import',{method:'POST',headers:{'Content-Type':'application/octet-stream','X-Filename':encodeURIComponent(file.name)},body:file});const data=await response.json();if(!response.ok || !data.url)throw Error(data.error || 'นำเข้าไม่สำเร็จ');w[key]=data.url;w.avatar_preset='';d.getElementById('compLegacy_'+key).value=data.url;d.getElementById('compLegacy_avatar_preset').value='';save();}catch(error){window.showToast?.(error.message);}finally{picker.remove();}};picker.click();};
  }
  section('⚙️ ภาพและการขยับ');field('avatar_fit_mode','การจัดภาพ','text','contain',['contain','cover','fill']);field('avatar_blink_rate','ช่วงกระพริบตา (วินาที)','number',4);
  field('avatar_mic_threshold','ระดับตรวจจับไมค์ (dB)','number',-35);field('avatar_mic_gain','ความดังไมค์ (%)','number',100);field('avatar_mic_device','อุปกรณ์ไมค์ (ว่าง = ค่าเริ่มต้น)');
  for(const [key,label,fallback] of [['bounce','ขยับเมื่อพูด',true],['breathing','หายใจ',true],['sway','โยกตัว',true],['flip_h','กลับภาพแนวนอน',false],['flip_v','กลับภาพแนวตั้ง',false]])field('avatar_'+key,label,'checkbox',fallback);
 }
},polish(body,type){
 if(!['avatar','donate_goal','viewer','image','video','alert','webcam'].includes(type))return;
 const d=body.ownerDocument;
 for(const panel of body.querySelectorAll('.comp-card-section')){
  let header=panel.querySelector(':scope > .comp-card-header'),content=panel.querySelector(':scope > .comp-card-body');
  if(!header)continue;if(!header.querySelector('.comp-card-title')){const title=d.createElement('span');title.className='comp-card-title';title.textContent=header.textContent;header.replaceChildren(title);}
  if(!content){content=d.createElement('div');content.className='comp-card-body';for(const node of [...panel.childNodes])if(node!==header)content.append(node);panel.append(content);}
  for(const field of [...content.children]){
   if(field.matches('input,select')){const row=d.createElement('div');row.className='comp-field-row'+(field.type==='text'?' comp-field-row-stack':'');const label=d.createElement('label');label.className='comp-field-label';label.htmlFor=field.id;label.textContent=field.tagName==='SELECT'?'การจัดภาพ':field.type==='text'?'URL ไฟล์หรือหน้าเว็บ':'ค่า';field.before(row);row.append(label,field);field.classList.add(field.tagName==='SELECT'?'cwc-select':'cwc-input');}
   else if(field.matches('label') && !field.querySelector('.comp-field-label')){field.className='comp-field-row';field.removeAttribute('style');const text=[...field.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent).join('').trim();[...field.childNodes].filter(n=>n.nodeType===3).forEach(n=>n.remove());const label=d.createElement('span');label.className='comp-field-label';label.textContent=text;field.prepend(label);const input=field.querySelector('input,select');if(input){input.className=input.tagName==='SELECT'?'cwc-select':input.type==='color'?'cwc-color-pick':'cwc-input';if(input.type==='checkbox'){const toggle=d.createElement('span');toggle.className='cwc-switch';input.before(toggle);toggle.append(input);const slider=d.createElement('span');slider.className='cwc-switch-slider';toggle.append(slider);}}}
   else if(field.tagName==='BUTTON')field.classList.add('comp-file-import-button');
  }
 }
}};
})();
