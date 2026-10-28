/* Original Dock actions operate the same main-app tools and shared overlay bus. */
(()=>{'use strict';let hidden=false,chatHidden=false,currentReplie=null;const schedules=new Map();let syncing=false;
const page=()=>ComposerStudio.getActivePage();
function persist(){ComposerStudio.renderCanvasWidgets();ComposerStudio.renderLayersList();return ComposerStudio.saveState(true);}
function presets(){try{return JSON.parse(localStorage.getItem('bp3_ask_presets') || '{}');}catch{return {};}}
function putPresets(value){localStorage.setItem('bp3_ask_presets',JSON.stringify(value));}
function setHidden(all,value){for(const w of page()?.widgets || []){if(!all && w.type!=='chat')continue;if(value){w._dockHiddenBefore=w.hidden;w.hidden=true;}else if('_dockHiddenBefore' in w){w.hidden=w._dockHiddenBefore;delete w._dockHiddenBefore;}}return persist();}
async function snapshot(){if(syncing)return;syncing=true;try{const st=window._liveAskState || {},choice=st.choices || [],rules=window._replieCommands || {},scheduled=[...schedules.keys()];const state={tts_reading:_masterTtsEnabled,translate_mode:typeof _currentTranslateMode==='undefined'?'translate':_currentTranslateMode,voice_gender:typeof _currentVoiceGender==='undefined'?'female':_currentVoiceGender,overlay_hidden:hidden,chat_hidden:chatHidden,ask:{...st,choices:choice.map(c=>c.text),keys:choice.map(c=>c.key || c.label),counts:choice.map(c=>c.votes || 0),remaining_sec:st.remainingSec},ask_presets:Object.entries(presets()).map(([name,preset])=>({name,...preset})),giveaway:window._liveGwState || {active:window._isGwCodeBroadcasting,participants:window._gwParticipants || []},replie:{commands:Object.entries(rules).map(([name,rule])=>({name,title:rule.title || '',enabled:rule.enabled!==false,duration_sec:rule.duration || 8,type:rule.legacyPayload?.display_mode || (rule.text && rule.imageUrl?'combo':rule.imageUrl?'image':'ticker'),scheduled:scheduled.includes(name),sched_interval_min:schedules.get(name)?.minutes,sched_next_ts:schedules.get(name)?.next/1000})),is_active:!!currentReplie,active_command:currentReplie?.cmd,duration_sec:currentReplie?.duration || 8,rem_active_sec:currentReplie?Math.max(0,(currentReplie.until-Date.now())/1000):0,loop_active:!!currentReplie?.isLoop}};await fetch('/api/dock/state',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(state)});}catch(error){console.warn('Dock status update failed',error);}finally{syncing=false;}}
function startAsk(data){const doc=getToolDocument('ask');doc.getElementById('askQuestion').value=data.question || '';const rows=doc.querySelector('#askChoicesList');rows.replaceChildren();for(const [index,value] of (data.choices || []).entries()){const row=doc.createElement('div');row.className='ask-choice-row';const input=doc.createElement('input');input.value=typeof value==='object'?value.text:value;row.append(input);rows.append(row);}doc.getElementById('askAnswerMode').value=data.answer_mode || 'letters';const select=doc.getElementById('askDurationSelect'),duration=data.no_limit?0:Number(data.duration_sec)||30;if(![...select.options].some(o=>Number(o.value)===duration)){const o=doc.createElement('option');o.value=duration;o.textContent=String(duration);select.append(o);}select.value=String(duration);startAskPoll();if(window._askPollState){_askPollState.realtime=data.realtime!==false;emitAskState();}}
async function action(data){const a=data.action,p=data.payload || data;
 switch(a){
 case 'dock_get_status':break;
 case 'toggle_tts':{const desired=typeof p.reading==='boolean'?p.reading:!_masterTtsEnabled;if(desired!==_masterTtsEnabled)toggleMasterTts();break;}
 case 'set_master_tts':if(Boolean(p.enabled)!==_masterTtsEnabled)toggleMasterTts();break;
 case 'toggle_translate':setTranslateMode(p.mode || ( _currentTranslateMode==='translate'?'multilang':'translate'));break;
 case 'toggle_voice_gender':case 'set_gender':selectVoiceGender(document.getElementById(p.gender==='male'?'tbGenderMale':'tbGenderFemale'),p.gender);break;
 case 'set_volume':syncMasterVolume(p.volume);break;
 case 'clear_tts_queue':clearChatTtsQueue();break;
 case 'toggle_hide_chat':chatHidden=Boolean(p.hidden);await setHidden(false,chatHidden);break;
 case 'toggle_hide_all_overlay':hidden=Boolean(p.hidden);await setHidden(true,hidden);break;
 case 'switch_overlay_page':ComposerStudio.switchPage(p.page_id);break;
 case 'toggle_widget_visibility':{const target=ComposerStudio.state.pages.find(pg=>pg.id===p.page_id) || page(),w=target?.widgets.find(w=>w.id===p.widget_id);if(w){w.hidden=!p.enabled;await persist();}break;}
 case 'open_composer':if(p.page_id)ComposerStudio.switchPage(p.page_id);openToolWindow('composer');break;
 case 'open_ask_tool':openToolWindow('ask');break;
 case 'open_giveaway_tool':openToolWindow('giveaway');break;
 case 'open_replie_tool':openToolWindow('replie');break;
 case 'ask_start':if(p.question)startAsk(p);else sendAskPollToObs();break;
 case 'ask_poll':case 'trigger_ask':sendAskPollToObs();break;
 case 'ask_end':endAskPoll();break;
 case 'ask_close':closeAskOverlay();break;
 case 'ask_save_preset':{const value=presets();value[p.preset.name]=p.preset;putPresets(value);break;}
 case 'ask_delete_preset':{const value=presets();delete value[p.name];putPresets(value);break;}
 case 'giveaway_roll':case 'trigger_giveaway':rerollGwWinner();break;
 case 'giveaway_confirm':BP3_BUS.emit('GIVEAWAY_UPDATE',{active:false,phase:'idle'});break;
 case 'playroom_clip':case 'trigger_playroom':playroomFireActiveClip();break;
 case 'replie_action':{const name=Object.keys(window._replieCommands || {})[0];if(name)demoReplieAction(name);break;}
 case 'replie_trigger':if(window._replieCommands[p.name])demoReplieAction(p.name);break;
 case 'replie_dismiss':BP3_BUS.emit('REPLIE_DISMISS',{});break;
 case 'replie_toggle':{const rule=window._replieCommands[p.name];if(rule){rule.enabled=rule.enabled===false;localStorage.setItem('bp3_replie_commands',JSON.stringify(window._replieCommands));renderReplieCommands();}break;}
 case 'replie_schedule_start':{const prior=schedules.get(p.name);if(prior)clearInterval(prior.timer);const minutes=Math.max(1,Number(p.interval_min)||5),entry={minutes,next:Date.now()+minutes*60000};entry.timer=setInterval(()=>{demoReplieAction(p.name);entry.next=Date.now()+minutes*60000;},minutes*60000);schedules.set(p.name,entry);break;}
 case 'replie_schedule_stop':clearInterval(schedules.get(p.name)?.timer);schedules.delete(p.name);break;
 case 'open_author_modal':openAuthorModal(p.raw_author || p.author,'','','');break;
 case 'block_user':{const name=String(p.raw_author || p.author).toLowerCase();window._blockedUsers[name]=true;localStorage.setItem('bp3_blocked_users',JSON.stringify(window._blockedUsers));break;}
 case 'delete_chat_message':document.querySelectorAll('#chatList .chat-row').forEach(row=>{if(row.dataset.messageId===String(p.id))row.remove();});await fetch('/api/chat/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:p.id})});break;
 case 'simulate_chat':toggleSimulateLiveChats();break;
 case 'clear_chat':clearChat();break;
 default:showToast('ไม่รู้จักคำสั่ง Dock: '+a);
 }snapshot();}
function init(){if(!window.BP3_BUS)return setTimeout(init,100);BP3_BUS.on('CHAT_DELETE',data=>document.querySelectorAll('#chatList .chat-row').forEach(row=>{if(row.dataset.messageId===String(data.id))row.remove();}));BP3_BUS.on('DOCK_CONTROL',data=>action(data).catch(error=>{console.error('Dock action failed',error);showToast('คำสั่ง Dock ทำงานไม่สำเร็จ');}));BP3_BUS.on('REPLIE_ACTION',data=>{currentReplie={...data,isLoop:data.legacyPayload?.is_loop ?? data.isLoop,duration:data.legacyPayload?.duration_sec || data.duration || 8,until:Date.now()+(Number(data.legacyPayload?.duration_sec || data.duration)||8)*1000};snapshot();});BP3_BUS.on('REPLIE_DISMISS',()=>{currentReplie=null;snapshot();});setInterval(()=>{if(currentReplie && !currentReplie.isLoop && currentReplie.until<Date.now())currentReplie=null;snapshot();},1000);snapshot();}
window.addEventListener('pagehide',()=>{for(const entry of schedules.values())clearInterval(entry.timer);});window.BP3Dock={action,snapshot};init();
})();
