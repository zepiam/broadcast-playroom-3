(() => {
 'use strict';
 let capability=null,latest=null,models=[],lastState='',polling=false,pendingRefresh=false,catalogView=null;
 const doc=()=>getToolDocument('voice-settings');
 const allDocs=()=>Array.from(new Set([document,doc(),getToolDocument('settings')]));
 async function api(path,body){
  const response=await fetch(path,body===undefined?{cache:'no-store'}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const value=await response.json();if(!response.ok)throw new Error(value.error || 'ทำรายการไม่สำเร็จ');return value;
 }
 function message(text){if(window.showToast)window.showToast(text);}
 function showStatus(status){
  latest=status;
  const busy=['loading','downloading'].includes(status.state);
  const labels={idle:'ยังไม่ได้เปิดใช้โมเดล',loading:'กำลังโหลดโมเดล...',downloading:'กำลังดาวน์โหลด...',ready:'พร้อมใช้งาน',error:'ไม่สำเร็จ: '+(status.error || '')};
  const isReady = (status.state === 'ready' && status.enabled && status.loaded);
  const badgeClass = isReady ? 'ready' : ((status.state === 'loading' || status.state === 'downloading') ? 'loading' : (status.state === 'error' ? 'error' : 'idle'));
  const labelText = labels[status.state] || status.state;
  for(const d of allDocs()){
   d.querySelectorAll('#rvcStatusLabel,#secRvcStatusLabel').forEach(el=>{
    if(el.textContent !== labelText) el.textContent = labelText;
    const targetClass = 'badge rvc-status-badge ' + badgeClass;
    if(el.className !== targetClass) el.className = targetClass;
    if(el.style.fontSize) el.style.fontSize = '';
    if(el.style.padding) el.style.padding = '';
   });
   d.querySelectorAll('#rvcDownloadStatus').forEach(el=>el.textContent=labels[status.state] || status.state);
   d.querySelectorAll('#chkEnableRvc,#chkEnableRvcSettings').forEach(el=>{
    if(status.state==='loading'){
     el.checked=true;
     el.disabled=true;
    }else{
     el.checked=Boolean(status.enabled && status.loaded);
     el.disabled=busy;
    }
   });
   d.querySelectorAll('.rvc-loading-progress-box').forEach(box=>{
    if(status.state==='loading'){
     box.style.display='block';
     const text=box.querySelector('.rvc-loading-text');if(text)text.textContent='กำลังโหลดโมเดลเข้าหน่วยความจำ (GPU/RAM)...';
     const pct=box.querySelector('.rvc-loading-pct');if(pct)pct.textContent='กรุณารอสักครู่';
     const fill=box.querySelector('.rvc-progress-bar-fill');if(fill){fill.style.width='100%';fill.style.animation='rvc-shimmer 1.5s infinite linear';}
    }else if(status.state==='downloading'){
     box.style.display='block';
     const text=box.querySelector('.rvc-loading-text');if(text)text.textContent='กำลังดาวน์โหลดโมเดลจากคลาวด์...';
     const pct=box.querySelector('.rvc-loading-pct');if(pct)pct.textContent=(status.progress || 0) + '%';
     const fill=box.querySelector('.rvc-progress-bar-fill');if(fill){fill.style.width=(status.progress || 0) + '%';fill.style.animation='none';}
    }else{
     box.style.display='none';
    }
   });
   d.querySelectorAll('#rvcDeviceLabel,#secRvcDeviceLabel').forEach(device=>{device.textContent=!status.loaded?'ยังไม่ได้โหลดโมเดล':status.device?(status.device.startsWith('cuda')?'GPU':'CPU'):'โมเดลพร้อมใช้';});
   d.querySelectorAll('#winRvcSelect,#secRvcSelect').forEach(select=>{
    select.disabled=busy;
    if(status.selected && models.some(m=>m.id===status.selected))select.value=status.selected;
   });
   const progress=d.getElementById('rvcDownloadProgress');if(progress)progress.value=status.progress || 0;
   const download=d.getElementById('btnRvcDownload');if(download)download.disabled=busy;
  }
  if(catalogView)catalogView(status);
  if(window.updateVoiceSummary)window.updateVoiceSummary();
 
  updateTopbarBadge(status);
 }
 function updateTopbarBadge(status){
  const badge=document.getElementById('topbarRvcBadge');
  if(!badge)return;
  const textEl=badge.querySelector('.rvc-badge-text') || badge;
  badge.classList.remove('rvc-loading','rvc-ready','rvc-off');
  if(status.state==='loading' || status.state==='downloading'){
   badge.classList.add('rvc-loading');
   badge.title='กำลังเตรียมโมเดล RVC';
   if(textEl)textEl.textContent='RVC โหลด...';
  }else if(status.state==='ready' && status.enabled && status.loaded){
   badge.classList.add('rvc-ready');
   const curModel=models.find(m=>m.id===status.selected);
   const modelName=curModel?curModel.name:(status.selected || '');
   badge.title=modelName ? ('RVC พร้อมใช้งาน: ' + modelName) : 'RVC พร้อมใช้งาน';
   if(textEl)textEl.textContent=modelName ? modelName : 'พร้อม';
  }else{
   badge.classList.add('rvc-off');
   badge.title='RVC ปิดใช้งาน (คลิกเพื่อตั้งค่า)';
   if(textEl)textEl.textContent='RVC: ปิด';
  }
 }
  async function refresh(){
  const result=await api('/api/rvc/models');models=result.models || [];
  for(const d of allDocs()){
   d.querySelectorAll('#winRvcSelect,#secRvcSelect').forEach(select=>{
    select.replaceChildren(new Option('ไม่ใช้ RVC','none'));
    models.forEach(model=>select.add(new Option(model.name,model.id)));
    if(!models.length)select.add(new Option('ยังไม่มีไฟล์โมเดล — เลือกนำเข้าหรือดาวน์โหลด','none'));
    if(latest?.selected && models.some(m=>m.id===latest.selected))select.value=latest.selected;
   });
  }
  showStatus(result.status);return result;
 }
 window.rescanRvcModels=()=>refresh().catch(error=>message(error.message));
 window.changeRvcModel=async id=>{
  for(const d of allDocs()){
   d.querySelectorAll('#winRvcSelect,#secRvcSelect').forEach(s=>{s.value=id;});
  }
  try{pendingRefresh=true;showStatus(await api('/api/rvc/select',{id,enabled:id!=='none'}));}catch(error){message(error.message);}
 };
 window.toggleRvcStatus=async enabled=>{
  for(const d of allDocs()){
   d.querySelectorAll('#chkEnableRvc,#chkEnableRvcSettings').forEach(c=>{c.checked=enabled;});
  }
  const select=doc().getElementById('winRvcSelect') || document.getElementById('secRvcSelect');
  let id=select?.value;
  if(enabled && (!id || id==='none')){
   const validModel=models.find(m=>m.id && m.id!=='none');
   if(validModel){
    id=validModel.id;
    for(const d of allDocs()){d.querySelectorAll('#winRvcSelect,#secRvcSelect').forEach(s=>{s.value=id;});}
   }else{
    message('ยังไม่มีโมเดลเสียง RVC ในเครื่อง กำลังเปิดหน้าต่างดาวน์โหลดโมเดลเสียง...');
    if(latest)showStatus(latest);
    if(window.openRvcDownloader)window.openRvcDownloader();
    return;
   }
  }
  try{pendingRefresh=true;showStatus(await api('/api/rvc/select',{id,enabled}));}catch(error){message(error.message);}
 };
 window.openRvcModelFolder=()=>api('/api/rvc/open-folder',{}).catch(error=>message(error.message));
 window.importRvcModelFile=()=>{
  if(!capability?.rvc)return;
  const d=doc();const input=d.createElement('input');input.type='file';input.accept='.pth,.index';input.multiple=true;
  input.onchange=async()=>{
   try{
    for(const file of Array.from(input.files || [])){
     const response=await fetch('/api/rvc/import',{method:'POST',headers:{'Content-Type':'application/octet-stream','X-Filename':encodeURIComponent(file.name)},body:file});
     const data=await response.json();if(!response.ok)throw new Error(data.error || 'นำเข้าไม่สำเร็จ');
    }
    await refresh();message('นำเข้าไฟล์โมเดลแล้ว');
   }catch(error){message(error.message);}
  };
  input.click();
 };
 // Model catalog: searchable list with category chips. Downloaded models show a green check and
 // a "use" action instead of a download button.
 const CATALOG_CSS=`
#rvcDownloadDialog{width:min(640px,92vw);margin:auto;padding:20px;background:#232428;color:#f2f3f5;border:1px solid #475569;border-radius:12px;}
#rvcDownloadDialog::backdrop{background:rgba(0,0,0,.55);}
#rvcDownloadDialog h3{margin:0 0 12px;font-size:16px;}
#rvcDownloadDialog .rvc-cat-tools{display:flex;flex-direction:column;gap:8px;margin-bottom:10px;}
#rvcDownloadDialog .rvc-cat-chips{display:flex;flex-wrap:wrap;gap:6px;}
#rvcDownloadDialog .rvc-cat-chip{background:#2b2d31;color:#b5bac1;border:1px solid #3f4147;border-radius:999px;padding:4px 12px;font-size:12px;cursor:pointer;}
#rvcDownloadDialog .rvc-cat-chip:hover{color:#f2f3f5;border-color:#5c5f66;}
#rvcDownloadDialog .rvc-cat-chip.active{background:#5865f2;border-color:#5865f2;color:#fff;}
#rvcDownloadDialog .rvc-cat-list{display:flex;flex-direction:column;gap:6px;max-height:min(52vh,460px);overflow-y:auto;padding-right:4px;contain:content;}
#rvcDownloadDialog .rvc-cat-row{display:flex;align-items:center;gap:12px;padding:10px 12px;background:#2b2d31;border:1px solid #3a3c42;border-radius:8px;}
#rvcDownloadDialog .rvc-cat-row.installed{border-color:rgba(35,165,90,.45);}
#rvcDownloadDialog .rvc-cat-row.active{background:rgba(35,165,90,.12);}
#rvcDownloadDialog .rvc-cat-icon{flex:0 0 24px;width:24px;height:24px;display:flex;align-items:center;justify-content:center;}
#rvcDownloadDialog .rvc-cat-info{flex:1;min-width:0;}
#rvcDownloadDialog .rvc-cat-name{font-weight:600;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
#rvcDownloadDialog .rvc-cat-meta{font-size:12px;color:#949ba4;margin-top:2px;}
#rvcDownloadDialog .rvc-cat-action{flex:0 0 auto;display:flex;align-items:center;gap:8px;font-size:12px;}
#rvcDownloadDialog .rvc-cat-delete{display:flex;align-items:center;justify-content:center;width:32px;height:32px;padding:0;background:transparent;color:#949ba4;border:1px solid #3f4147;border-radius:6px;cursor:pointer;}
#rvcDownloadDialog .rvc-cat-delete:hover:not(:disabled){color:#f23f43;border-color:#f23f43;background:rgba(242,63,67,.1);}
#rvcDownloadDialog .rvc-cat-delete:disabled{opacity:.4;cursor:default;}
#rvcDownloadDialog .rvc-cat-using{color:#23a55a;font-weight:600;}
#rvcDownloadDialog .rvc-cat-pct{color:#b5bac1;min-width:36px;text-align:right;}
#rvcDownloadDialog .rvc-cat-empty{padding:24px;text-align:center;color:#949ba4;font-size:13px;}
#rvcDownloadDialog .rvc-cat-footer{display:flex;align-items:center;gap:12px;margin-top:12px;}
#rvcDownloadDialog #rvcCatalogStatus{flex:1;font-size:12px;color:#b5bac1;}
#rvcDownloadDialog #rvcDownloadProgress{width:100%;margin-top:10px;}
`;
 const ICON_INSTALLED='<svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="11" fill="#23a55a"/><path d="M7 12.5l3.2 3.2L17 9" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>';
 const ICON_TRASH='<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/></svg>';
 const ICON_REMOTE='<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="#80848e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"/><path d="M7 10l5 5 5-5"/><path d="M5 21h14"/></svg>';
 window.openRvcDownloader=async()=>{
  if(!capability?.rvc)return;
  try{
   let catalog=(await api('/api/rvc/catalog')).models || [];const d=doc();
   d.getElementById('rvcDownloadDialog')?.remove();
   const panel=d.createElement('dialog');panel.id='rvcDownloadDialog';
   const style=d.createElement('style');style.textContent=CATALOG_CSS;
   const title=d.createElement('h3');title.textContent='โมเดลเสียง RVC';
   const tools=d.createElement('div');tools.className='rvc-cat-tools';
   const search=d.createElement('input');search.className='modal-input';search.placeholder='ค้นหาโมเดล';search.id='rvcModelSearch';search.style.width='100%';
   const chips=d.createElement('div');chips.className='rvc-cat-chips';
   const CATEGORY_LABELS={genshin:'Genshin',vtuber:'VTuber',anime:'Anime'};
   const filters=[['all','ทั้งหมด'],['installed','โหลดแล้ว'],...Object.entries(CATEGORY_LABELS)];
   let activeFilter='all';
   filters.forEach(([key,label])=>{const chip=d.createElement('button');chip.type='button';chip.className='rvc-cat-chip'+(key===activeFilter?' active':'');chip.dataset.filter=key;chip.textContent=label;chip.onclick=()=>{activeFilter=key;chips.querySelectorAll('.rvc-cat-chip').forEach(c=>c.classList.toggle('active',c===chip));render(true);};chips.append(chip);});
   tools.append(search,chips);
   const list=d.createElement('div');list.className='rvc-cat-list';list.id='rvcCatalogList';
   const progress=d.createElement('progress');progress.id='rvcDownloadProgress';progress.max=100;progress.value=0;progress.hidden=true;
   const footer=d.createElement('div');footer.className='rvc-cat-footer';
   const statusLine=d.createElement('div');statusLine.id='rvcCatalogStatus';
   const close=d.createElement('button');close.className='btn-topbar-action';close.textContent='ปิด';close.onclick=()=>panel.close();
   footer.append(statusLine,close);
   panel.append(style,title,tools,list,progress,footer);d.body.append(panel);
   let downloadingId=null,lastSig='',lastState=latest?.state || '',note='';
   const isActive=item=>item.model_id && latest && latest.selected===item.model_id && latest.state==='ready' && latest.enabled && latest.loaded;
   const isLoading=item=>item.model_id && latest && latest.selected===item.model_id && latest.state==='loading';
   async function reloadCatalog(){try{catalog=(await api('/api/rvc/catalog')).models || [];render(true);}catch(error){statusLine.textContent=note=error.message;}}
   function actionFor(item,busy){
    const box=d.createElement('div');box.className='rvc-cat-action';
    if(item.installed){
     if(isActive(item)){const s=d.createElement('span');s.className='rvc-cat-using';s.textContent='กำลังใช้งาน';box.append(s);}
     else if(isLoading(item)){const s=d.createElement('span');s.className='rvc-cat-pct';s.textContent='กำลังโหลด...';box.append(s);}
     else if(item.model_id){const b=d.createElement('button');b.type='button';b.className='btn-topbar-action rvc-cat-use';b.textContent='ใช้โมเดลนี้';b.disabled=busy;b.onclick=()=>window.changeRvcModel(item.model_id);box.append(b);}
     if(item.model_id && !isLoading(item)){
      const del=d.createElement('button');del.type='button';del.className='rvc-cat-delete';del.title='ลบโมเดล';del.setAttribute('aria-label','ลบโมเดล '+item.name);del.innerHTML=ICON_TRASH;del.disabled=busy;
      del.onclick=async()=>{
       const warn=isActive(item)?'\nโมเดลนี้กำลังใช้งานอยู่ จะถูกปิดก่อนลบ':'';
       if(!(d.defaultView || window).confirm(`ลบโมเดล "${item.name}" ใช่ไหม?${warn}\nไฟล์จะถูกย้ายไปถังขยะของ Windows กู้คืนได้`))return;
       try{const st=await api('/api/rvc/delete',{id:item.model_id});note='ลบโมเดล '+item.name+' แล้ว';pendingRefresh=true;showStatus(st);await refresh();await reloadCatalog();}
       catch(error){statusLine.textContent=note=error.message;}
      };
      box.append(del);
     }
    }else if(latest?.state==='downloading' && downloadingId===item.id){
     const pct=d.createElement('span');pct.className='rvc-cat-pct';pct.dataset.pct='1';pct.textContent=(latest.progress || 0)+'%';
     const c=d.createElement('button');c.type='button';c.className='btn-topbar-action';c.id='btnRvcCancel';c.textContent='ยกเลิก';
     c.onclick=()=>api('/api/rvc/cancel',{}).then(showStatus).catch(error=>statusLine.textContent=note=error.message);
     box.append(pct,c);
    }else{
     const b=d.createElement('button');b.type='button';b.className='btn-topbar-action primary rvc-cat-download';b.textContent='ดาวน์โหลด';b.disabled=busy;
     b.onclick=async()=>{try{downloadingId=item.id;pendingRefresh=true;showStatus(await api('/api/rvc/download',{id:item.id}));}catch(error){downloadingId=null;statusLine.textContent=note=error.message;render(true);}};
     box.append(b);
    }
    return box;
   }
   function render(force){
    const busy=['loading','downloading'].includes(latest?.state);
    const sig=[activeFilter,search.value,latest?.state,latest?.selected,latest?.enabled,latest?.loaded,downloadingId,catalog.map(i=>i.installed?1:0).join('')].join('|');
    if(!force && sig===lastSig)return;lastSig=sig;
    const q=search.value.trim().toLowerCase();
    const items=catalog.filter(item=>(!q || item.name.toLowerCase().includes(q)) && (activeFilter==='all' || (activeFilter==='installed'?item.installed:item.category===activeFilter)))
     .sort((a,b)=>(b.installed?1:0)-(a.installed?1:0));
    list.replaceChildren();
    if(!items.length){const empty=d.createElement('div');empty.className='rvc-cat-empty';empty.textContent=activeFilter==='installed'?'ยังไม่มีโมเดลที่ดาวน์โหลดไว้':'ไม่พบโมเดลที่ค้นหา';list.append(empty);return;}
    for(const item of items){
     const row=d.createElement('div');row.className='rvc-cat-row'+(item.installed?' installed':'')+(isActive(item)?' active':'');row.dataset.id=item.id;
     const icon=d.createElement('div');icon.className='rvc-cat-icon';icon.innerHTML=item.installed?ICON_INSTALLED:ICON_REMOTE;icon.title=item.installed?'ดาวน์โหลดแล้ว':'ยังไม่ได้ดาวน์โหลด';
     const info=d.createElement('div');info.className='rvc-cat-info';
     const name=d.createElement('div');name.className='rvc-cat-name';name.textContent=item.name;
     const meta=d.createElement('div');meta.className='rvc-cat-meta';
     meta.textContent=[CATEGORY_LABELS[item.category] || item.category,item.tag?('เสียง'+item.tag):'',item.installed?'ดาวน์โหลดแล้ว':`ประมาณ ${Math.round(item.size/1048576)} MB`].filter(Boolean).join(' • ');
     info.append(name,meta);row.append(icon,info,actionFor(item,busy));list.append(row);
    }
   }
   catalogView=status=>{
    if(!panel.isConnected){catalogView=null;return;}
    if(lastState==='downloading' && status.state!=='downloading'){
     if(status.state==='error')note='ดาวน์โหลดไม่สำเร็จ: '+(status.error || '');
     else if(status.error==='Download cancelled')note='ยกเลิกการดาวน์โหลดแล้ว';
     else note='ดาวน์โหลดเสร็จแล้ว กด "ใช้โมเดลนี้" เพื่อเริ่มใช้งาน';
     downloadingId=null;reloadCatalog();
    }else if(status.state!==lastState && status.state!=='idle'){note='';}
    let text=note;
    if(status.state==='downloading')text='กำลังดาวน์โหลด... '+(status.progress || 0)+'%';
    else if(status.state==='loading')text='กำลังโหลดโมเดลเข้าหน่วยความจำ...';
    else if(status.state==='error' && status.error)text='ไม่สำเร็จ: '+status.error;
    else if(!text && status.state==='ready' && status.enabled && status.loaded){const cur=models.find(m=>m.id===status.selected);text='กำลังใช้งาน: '+(cur?cur.name:'โมเดลที่เลือก');}
    if(statusLine.textContent!==text)statusLine.textContent=text;
    lastState=status.state;
    progress.hidden=status.state!=='downloading';
    render(false);
    const pct=list.querySelector('[data-pct]');if(pct)pct.textContent=(status.progress || 0)+'%';
   };
   search.oninput=()=>render(true);
   panel.addEventListener('close',()=>{panel.remove();catalogView=null;});
   render(true);panel.showModal();if(latest)showStatus(latest);
  }catch(error){message(error.message);}
 };
 async function init(){
  try{
   capability=await api('/api/capabilities');window.BP3Capabilities=capability;
   for(const d of allDocs()){
    d.querySelectorAll('[data-feature="rvc"]').forEach(el=>{if(capability.rvc)el.style.display='';else el.remove();});
    d.querySelectorAll('[data-feature="pitch"]').forEach(el=>{if(capability.edition==='full')el.style.display='';else el.remove();});
   }
   if(!capability.rvc){
    const subtitle=document.getElementById('voiceSettingsSubtitle');
    if(subtitle)subtitle.textContent='ปรับแต่งเสียงอ่านแชท ระดับเสียง และความเร็ว';
    return;
   }
   await refresh();
   setInterval(async()=>{
    if(polling)return;
    const visible=doc().getElementById('rvcVoiceCard')?.getClientRects().length || doc().getElementById('rvcDownloadDialog')?.open || document.getElementById('secRvcVoiceCard')?.getClientRects().length;
    const isRvcBusy=['loading','downloading'].includes(latest?.state);
   if(!visible && !isRvcBusy)return;
    polling=true;
    try{const state=await api('/api/rvc/status');showStatus(state);if((pendingRefresh || state.state!==lastState) && !['loading','downloading'].includes(state.state)){await refresh();pendingRefresh=false;}lastState=state.state;}catch(error){message(error.message);}finally{polling=false;}
   },400);
  }catch(error){message('ตรวจรุ่นโปรแกรมไม่สำเร็จ: '+error.message);}
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
