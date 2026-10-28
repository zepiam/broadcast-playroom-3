/* Editable local bot configuration. Message delivery remains unavailable until account integration is complete. */
(()=>{'use strict';
 const key='bp3_bot_settings_v1';let askChoiceSaved=false,askTouched=false;let state={commands:[],timers:[],enabled:false,platforms:[],postAsk:false};
 try{const saved=JSON.parse(localStorage.getItem(key));if(saved && Array.isArray(saved.commands) && Array.isArray(saved.timers)){state=saved;askChoiceSaved=Object.prototype.hasOwnProperty.call(saved,'postAsk');}}catch(_){}
 const doc=()=>getToolDocument('settings');
 const save=()=>{localStorage.setItem(key,JSON.stringify(state));fetch('/api/chatbot/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...state,platforms:(state.platforms || []).filter(platform=>platform!=='kick')})}).catch(()=>showToast('ไม่สามารถส่งการตั้งค่า Chat Bot ไปยังโปรแกรม'));};
 const element=(d,tag,text)=>{const node=d.createElement(tag);if(text!=null)node.textContent=String(text);return node;};
 function render(){const d=doc(),body=d.getElementById('botCommandsList'),timers=d.getElementById('botTimerList');if(!body || !timers)return;body.replaceChildren();timers.replaceChildren();
  for(const item of state.commands){const tr=element(d,'tr');for(const value of [item.command,item.response,item.cooldown+' วิ'])tr.append(element(d,'td',value));const td=element(d,'td'),button=element(d,'button','ลบ');button.type='button';button.className='btn-topbar-action';button.onclick=()=>{state.commands=state.commands.filter(x=>x.id!==item.id);save();render();};td.append(button);tr.append(td);body.append(tr);}
  for(const item of state.timers){const row=element(d,'div');row.className='clean-row';row.style.cssText='gap:10px;padding:8px 10px;margin:6px 0;background:#1e1f22;border-radius:6px;flex-wrap:wrap';const info=element(d,'div',`${item.text} · ทุก ${item.minutes} นาที · แชทอย่างน้อย ${item.minChat} ข้อความ`),button=element(d,'button','ลบ');button.type='button';button.className='btn-topbar-action';button.onclick=()=>{state.timers=state.timers.filter(x=>x.id!==item.id);save();render();};row.append(info,button);timers.append(row);}
 }
 function form(id,open){const d=doc(),node=d.getElementById(id);if(node)node.hidden=!open;}
 window.addBotCommandPrompt=()=>{form('botCommandForm',true);doc().getElementById('botCommandName')?.focus();};
 window.closeBotCommandForm=()=>form('botCommandForm',false);
 window.openBotTimerForm=()=>{form('botTimerForm',true);doc().getElementById('botTimerText')?.focus();};
 window.closeBotTimerForm=()=>form('botTimerForm',false);
 window.saveBotCommand=()=>{const d=doc(),name=d.getElementById('botCommandName'),response=d.getElementById('botCommandResponse'),cooldown=d.getElementById('botCommandCooldown');const command=name.value.trim(),reply=response.value.trim();if(!/^![^\s]+$/.test(command)||!reply){showToast('กรุณากรอกคำสั่งที่ขึ้นต้นด้วย ! และข้อความตอบกลับ');return;}if(state.commands.some(item=>item.command.toLowerCase()===command.toLowerCase())){showToast('มีคำสั่งนี้อยู่แล้ว');return;}state.commands.push({id:crypto.randomUUID(),command,response:reply,cooldown:Math.max(1,Number(cooldown.value)||5)});save();render();name.value='';response.value='';form('botCommandForm',false);showToast('บันทึกคำสั่งแล้ว');};
 window.saveBotTimer=()=>{const d=doc(),text=d.getElementById('botTimerText'),interval=d.getElementById('botTimerInterval'),min=d.getElementById('botTimerMinChat');if(!text.value.trim()){showToast('กรุณากรอกข้อความ Timer');return;}state.timers.push({id:crypto.randomUUID(),text:text.value.trim(),minutes:Math.max(1,Number(interval.value)||1),minChat:Math.max(0,Number(min.value)||0)});save();render();text.value='';form('botTimerForm',false);showToast('บันทึก Timer แล้ว');};
 async function updateAuth(){
  try{const response=await fetch('/api/chatbot/auth/status');if(!response.ok)return;const statuses=await response.json(),d=doc();window._botAuthStatuses=statuses;let ready=0;
   for(const platform of ['twitch','kick']){const info=statuses[platform] || {},label=platform==='twitch'?'Twitch':'KICK',capital=platform==='twitch'?'Twitch':'Kick';if(info.ready)ready++;
    const message=info.ready?'🟢 พร้อมส่งแชท':info.state==='authorizing'?'กำลังรอเข้าสู่ระบบ':info.state==='saved'?'เชื่อมบัญชีแล้ว · รอเชื่อมแชท':info.state==='error'?(info.error || 'เชื่อมต่อไม่สำเร็จ'):'ยังไม่ได้เชื่อมบัญชี';
    const status=d.getElementById('botAuth'+capital+'Status'),name=d.getElementById('botAuth'+capital+'Name'),badge=d.getElementById(platform==='twitch'?'twitchBotBadge':'kickBotBadge');
    const connect=d.getElementById(platform+'BotConnect'),disconnect=d.getElementById(platform+'BotDisconnect'),hasAccount=!!info.username;if(connect){connect.textContent=info.state==='authorizing'?'กำลังเชื่อมต่อ…':hasAccount?'สลับบัญชี':'เชื่อมต่อ Chatbot';connect.disabled=info.state==='authorizing';}if(disconnect){disconnect.hidden=!hasAccount;disconnect.style.setProperty('display',hasAccount?'':'none',hasAccount?'':'important');}const chip=window.document.getElementById('chipSend'+capital);if(chip){const visible=platform==='twitch' && info.ready;chip.hidden=!visible;chip.style.setProperty('display',visible?'':'none',visible?'':'important');}if(status)status.textContent=message;if(name)name.textContent=info.username?'@'+info.username:'ยังไม่ได้เชื่อมต่อ';if(badge)badge.textContent=label+': '+message;
   }const summary=d.getElementById('botAuthSummary');if(summary)summary.textContent=ready?'พร้อมใช้งาน '+ready+' ช่องทาง':'ยังไม่มีบัญชีพร้อมส่งข้อความ';
   const chatLabel=window.document.getElementById('chatBotAccountName');if(chatLabel){const active=['twitch','kick'].filter(platform=>statuses[platform]?.ready);chatLabel.textContent=active.length?active.map(platform=>(platform==='kick'?'KICK':'Twitch')+' (@'+statuses[platform].username+')').join(' · '):'ยังไม่มีบัญชีพร้อมส่งข้อความ';}
   const available=!!statuses.twitch?.ready;const input=window.document.getElementById('chatInputContainer'),notice=window.document.getElementById('chatInputUnavailable');if(input)input.style.display=available?'':'none';if(notice)notice.style.display=available?'none':'';
   window.updateChatTargetChipsUi?.();
  }catch(_){}
 }
 async function authAction(platform,action){try{const response=await fetch('/api/chatbot/auth',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({platform,action})});if(!response.ok){const result=await response.json().catch(()=>({}));throw Error(result.error || 'ไม่สามารถเริ่มเชื่อมบัญชีได้');}await updateAuth();if(action==='start')showToast('เปิดหน้าล็อกอินในเบราว์เซอร์แล้ว');}catch(error){showToast(error.message);}}
 window.refreshBotAuthStatus=updateAuth;
 window.toggleTwitchBotAuth=()=>authAction('twitch','start');window.toggleKickBotAuth=()=>authAction('kick','start');window.disconnectBotAccount=platform=>authAction(platform,'disconnect');
 window.BP3BotPostAskResult=async poll=>{
  if(!state.enabled || !state.platforms.includes('twitch') || state.postAsk!==true || !window._botAuthStatuses?.twitch?.ready)return;
  const choices=Array.isArray(poll?.choices)?poll.choices:[], total=Object.keys(poll?.voters || {}).length;if(!total)return;
  const ranked=choices.map((choice,index)=>({choice,index})).sort((a,b)=>(Number(b.choice.votes)||0)-(Number(a.choice.votes)||0)||a.index-b.index);
  const result=ranked.map(({choice})=>`[${choice.key || choice.label}- ${choice.text} ${Number(choice.votes)||0} โหวต]`).join(' ');
  const message=`[ผลสรุปการโหวต] หัวข้อ : ${poll.question || ''} | จาก ${total} คนโหวต | ผลออกมาดังนี้ ${result}`.slice(0,480);
  try{const response=await fetch('/api/chatbot/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message,targets:['twitch']})});const result=await response.json();if(!response.ok || !result.results?.twitch?.ok)throw Error();showToast('ส่งผลโหวตไป Twitch แล้ว');}catch(_){showToast('ส่งผลโหวตไป Twitch ไม่สำเร็จ');}
 };
 function init(){
  const d=doc(),master=d.getElementById('cfgMasterBotEnabled'),twitch=d.getElementById('cfgBotPlatTwitch'),kick=d.getElementById('cfgBotPlatKick'),twitchCard=d.getElementById('cfgTwitchBotEnabled'),ask=d.getElementById('cfgBotAskPostGlobal'),askCard=d.getElementById('cfgTwitchBotAskPost');
  state.enabled=state.enabled===true;state.platforms=Array.isArray(state.platforms)?state.platforms:[];state.postAsk=state.postAsk===true;
  const sync=()=>{if(master)master.checked=state.enabled;if(twitch)twitch.checked=state.platforms.includes('twitch');if(kick)kick.checked=state.platforms.includes('kick');if(twitchCard)twitchCard.checked=state.enabled && state.platforms.includes('twitch');if(ask)ask.checked=state.postAsk;if(askCard)askCard.checked=state.postAsk;};
  sync();
  master?.addEventListener('change',()=>{state.enabled=master.checked;sync();save();});
  twitch?.addEventListener('change',()=>{state.platforms=[...state.platforms.filter(p=>p!=='twitch'),...(twitch.checked?['twitch']:[])];sync();save();});
  kick?.addEventListener('change',()=>{state.platforms=[...state.platforms.filter(p=>p!=='kick'),...(kick.checked?['kick']:[])];sync();save();});
  twitchCard?.addEventListener('change',()=>{state.enabled=twitchCard.checked;state.platforms=[...state.platforms.filter(p=>p!=='twitch'),...(twitchCard.checked?['twitch']:[])];sync();save();});
  for(const checkbox of [ask,askCard])checkbox?.addEventListener('change',()=>{askTouched=true;state.postAsk=checkbox.checked;sync();save();});
  if(!askChoiceSaved)fetch('/api/legacy/user-filters').then(r=>r.ok?r.json():{}).then(data=>{if(!askTouched && typeof data.ask_post_result==='boolean'){state.postAsk=data.ask_post_result;sync();save();}}).catch(()=>{});
  render();save();updateAuth();setInterval(updateAuth,3000);
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
