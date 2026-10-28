/* Custom DNS is scoped to the program's TTS connector. */
(() => {
 let state={enabled:false,service:'cloudflare_doh',custom:''},saveQueue=Promise.resolve();
 const doc=()=>typeof getToolDocument==='function'?getToolDocument('settings'):document;
 function render(){
  const d=doc(),enabled=d.getElementById('chkEnableDns'),provider=d.getElementById('selDnsProvider'),custom=d.getElementById('txtCustomDns'),group=d.getElementById('groupCustomDnsInput'),badge=d.getElementById('lblDnsStatusBadge');
  if(enabled)enabled.checked=state.enabled;if(provider)provider.value=state.service;if(custom)custom.value=state.custom;if(group)group.style.display=state.service==='custom'?'block':'none';
  if(badge)badge.textContent=state.enabled?'● ใช้ Custom DNS สำหรับ TTS (หากล้มเหลวจะใช้ DNS ระบบ)':'● ใช้ DNS ระบบ';
 }
 async function save(){
  const d=doc(),enabled=d.getElementById('chkEnableDns'),provider=d.getElementById('selDnsProvider'),custom=d.getElementById('txtCustomDns');
  const data={enabled:enabled.checked,service:provider.value,custom:custom.value.trim()};
  if(data.service==='custom' && !data.custom){d.getElementById('groupCustomDnsInput').style.display='block';enabled.checked=state.enabled;d.getElementById('dnsTestResult').textContent='กรุณาระบุที่อยู่ DNS ก่อนบันทึก';return;}
  saveQueue=saveQueue.catch(()=>{}).then(async()=>{try{const response=await fetch('/api/dns/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});const result=await response.json();if(!response.ok)throw Error(result.error);state=result;render();}catch(error){d.defaultView.alert(error.message || 'บันทึก DNS ไม่สำเร็จ');render();}});
  return saveQueue;
 }
 window.testCustomDns=async()=>{
  const d=doc(),status=d.getElementById('dnsTestResult');status.textContent='กำลังทดสอบ...';
  try{const response=await fetch('/api/dns/test',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({enabled:true,service:d.getElementById('selDnsProvider').value,custom:d.getElementById('txtCustomDns').value.trim()})});const data=await response.json();if(!response.ok)throw Error(data.error);status.textContent=data.ok?data.message+' ('+data.latency_ms+' ms รวมเวลาสร้างเสียง)':data.message;}
  catch(error){status.textContent=error.message || 'ทดสอบไม่สำเร็จ';}
 };
 window.clearCustomDnsCache=async()=>{
  const d=doc(),status=d.getElementById('dnsTestResult');try{const response=await fetch('/api/dns/clear',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});if(!response.ok)throw Error();status.textContent='ล้างแคช DNS ของโปรแกรมแล้ว';}catch(_){status.textContent='ล้างแคชไม่สำเร็จ';}
 };
 function init(){
  for(const id of ['chkEnableDns','selDnsProvider','txtCustomDns']){const node=document.getElementById(id);node?.addEventListener('change',save);}
  Promise.all([fetch('/api/dns/settings').then(r=>r.json()),fetch('/api/legacy/user-filters').then(r=>r.json())]).then(async([data,legacy])=>{
   state=data;render();
   if(!data.has_saved && typeof legacy.dns_enabled==='boolean'){
    const d=doc();d.getElementById('chkEnableDns').checked=legacy.dns_enabled;d.getElementById('selDnsProvider').value=legacy.dns_service || 'cloudflare_doh';d.getElementById('txtCustomDns').value=legacy.dns_custom || '';await save();
   }
  }).catch(()=>render());
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
