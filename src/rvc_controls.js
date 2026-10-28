(() => {
 'use strict';
 let capability=null,latest=null,models=[],lastState='',polling=false,pendingRefresh=false;
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
  const labels={idle:'ยังไม่ได้เปิดใช้โมเดล',loading:'กำลังโหลดโมเดล',downloading:`กำลังดาวน์โหลด ${status.progress || 0}%`,ready:'พร้อมใช้งาน',error:'ไม่สำเร็จ: '+(status.error || '')};
  for(const d of allDocs()){
   d.querySelectorAll('#rvcStatusLabel,#rvcDownloadStatus').forEach(el=>el.textContent=labels[status.state] || status.state);
   d.querySelectorAll('#chkEnableRvc,#chkEnableRvcSettings').forEach(el=>{el.checked=Boolean(status.enabled && status.loaded);el.disabled=busy;});
   const device=d.getElementById('rvcDeviceLabel');if(device)device.textContent=!status.loaded?'ยังไม่ได้โหลดโมเดล':status.device?(status.device.startsWith('cuda')?'GPU':'CPU'):'โมเดลพร้อมใช้';
   const select=d.getElementById('winRvcSelect');if(select){select.disabled=busy;if(status.selected && models.some(m=>m.id===status.selected))select.value=status.selected;}
   const progress=d.getElementById('rvcDownloadProgress');if(progress)progress.value=status.progress || 0;
   const download=d.getElementById('btnRvcDownload');if(download)download.disabled=busy;
  }
  if(window.updateVoiceSummary)window.updateVoiceSummary();
 }
 async function refresh(){
  const result=await api('/api/rvc/models');models=result.models || [];
  const select=doc().getElementById('winRvcSelect');
  if(select){select.replaceChildren(new Option('ไม่ใช้ RVC','none'));models.forEach(model=>select.add(new Option(model.name,model.id)));if(!models.length)select.add(new Option('ยังไม่มีไฟล์โมเดล — เลือกนำเข้าหรือดาวน์โหลด','none'));}
  showStatus(result.status);return result;
 }
 window.rescanRvcModels=()=>refresh().catch(error=>message(error.message));
 window.changeRvcModel=async id=>{
  try{pendingRefresh=true;showStatus(await api('/api/rvc/select',{id,enabled:id!=='none'}));}catch(error){message(error.message);}
 };
 window.toggleRvcStatus=async enabled=>{
  const select=doc().getElementById('winRvcSelect');const id=select?.value;
  if(enabled && (!id || id==='none')){message('กรุณาเลือกโมเดลก่อนเปิดใช้');if(latest)showStatus(latest);return;}
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
 window.openRvcDownloader=async()=>{
  if(!capability?.rvc)return;
  try{
   const result=await api('/api/rvc/catalog');const d=doc();
   d.getElementById('rvcDownloadDialog')?.remove();
   const panel=d.createElement('dialog');panel.id='rvcDownloadDialog';
   panel.style.cssText='width:min(620px,90vw);margin:auto;padding:22px;background:#232428;color:#f2f3f5;border:1px solid #475569;border-radius:12px;';
   const title=d.createElement('h3');title.textContent='ดาวน์โหลดโมเดล RVC';
   const search=d.createElement('input');search.className='modal-input';search.placeholder='ค้นหาโมเดล';search.id='rvcModelSearch';search.style.width='100%';
   const select=d.createElement('select');select.id='rvcCatalogSelect';select.className='voice-select-box';select.style.cssText='width:100%;margin:12px 0;';
   function filter(){select.replaceChildren();(result.models || []).filter(model=>model.name.toLowerCase().includes(search.value.toLowerCase())).forEach(model=>select.add(new Option(`${model.name} • ${model.category} • ประมาณ ${Math.round(model.size/1048576)} MB`,model.id)));}
   search.oninput=filter;filter();
   const progress=d.createElement('progress');progress.id='rvcDownloadProgress';progress.max=100;progress.value=0;progress.style.width='100%';
   const status=d.createElement('div');status.id='rvcDownloadStatus';status.style.margin='10px 0';
   const buttons=d.createElement('div');buttons.style.cssText='display:flex;gap:8px;justify-content:flex-end;';
   const download=d.createElement('button');download.id='btnRvcDownload';download.className='btn-topbar-action primary';download.textContent='ดาวน์โหลด';
   download.onclick=async()=>{try{pendingRefresh=true;showStatus(await api('/api/rvc/download',{id:select.value}));}catch(error){status.textContent=error.message;}};
   const cancel=d.createElement('button');cancel.id='btnRvcCancel';cancel.className='btn-topbar-action';cancel.textContent='ยกเลิกดาวน์โหลด';cancel.onclick=()=>api('/api/rvc/cancel',{}).then(showStatus).catch(error=>status.textContent=error.message);
   const close=d.createElement('button');close.className='btn-topbar-action';close.textContent='ปิด';close.onclick=()=>panel.close();
   buttons.append(download,cancel,close);panel.append(title,search,select,progress,status,buttons);d.body.append(panel);panel.showModal();if(latest)showStatus(latest);
  }catch(error){message(error.message);}
 };
 async function init(){
  try{
   capability=await api('/api/capabilities');window.BP3Capabilities=capability;
   for(const d of allDocs())d.querySelectorAll('[data-feature="rvc"]').forEach(el=>{if(capability.rvc)el.style.display='';else el.remove();});
   if(!capability.rvc){const subtitle=document.getElementById('voiceSettingsSubtitle');if(subtitle)subtitle.textContent='ปรับแต่งเสียงอ่านแชท ระดับเสียง ความเร็ว และ Pitch';return;}
   await refresh();
   setInterval(async()=>{
    if(polling)return;
    const visible=doc().getElementById('rvcVoiceCard')?.getClientRects().length || doc().getElementById('rvcDownloadDialog')?.open;
    if(!visible)return;
    polling=true;
    try{const state=await api('/api/rvc/status');showStatus(state);if((pendingRefresh || state.state!==lastState) && !['loading','downloading'].includes(state.state)){await refresh();pendingRefresh=false;}lastState=state.state;}catch(error){message(error.message);}finally{polling=false;}
   },400);
  }catch(error){message('ตรวจรุ่นโปรแกรมไม่สำเร็จ: '+error.message);}
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
