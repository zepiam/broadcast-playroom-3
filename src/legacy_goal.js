// Original Donate Goal presentation. Amounts come from the legacy watcher.
(()=>{'use strict';const config={font_family:'Kanit'};let _lastDonateGoalData={};let busy=false;
function setupDonateGoalWidget(inner, w) {
  const signature=JSON.stringify([w,_lastDonateGoalData[w.id]]);if(inner._bpGoalConfig===signature)return;inner._bpGoalConfig=signature;
  const previous=inner.cloneNode(false);
  // Build markup detached, then patch the existing presentation.
  const target=inner;inner=previous;
  inner.innerHTML = '';
  const theme = w.dg_theme || 'neon';
  const barColor = w.dg_bar_color || '#10b981';
  const bgColor = w.dg_bg_color || '#1a1a2e';
  const fontColor = w.dg_font_color || '#e5e7eb';
  const currentColor = w.dg_current_color || '#10b981';
  const goalColor = w.dg_goal_color || '#9ca3af';
  const currency = w.dg_currency || '฿';
  const goal = w.dg_goal_amount || 1000;
  const goalTitle = w.dg_goal_title || '';
  const fs = w.dg_font_size || 16;
  const opacity = (w.dg_opacity != null ? w.dg_opacity : 100) / 100;
  const showDonor = w.dg_show_donor !== false;

  // ★ restore จาก last data
  const startAmount = w.dg_start_amount || 0;
  const lastData = _lastDonateGoalData[w.id];
  const donated = lastData ? lastData.current : 0;
  const current = startAmount + donated;  // ★ ยอดเริ่มต้น + ยอดโดเนทใหม่
  const percent = (current / Math.max(1, goal)) * 100;
  const lastDonor = lastData ? lastData.last_donor : '';
  const lastAmount = lastData ? lastData.last_amount : 0;
  const achieved = current >= goal;
  const overflow = current > goal ? current - goal : 0;

  // ★ gradient bar color (สวยกว่า solid)
  const gradFrom = barColor;
  const gradTo = achieved ? '#fbbf24' : _lightenColor(barColor, 20);

  const wrap = document.createElement('div');
  wrap.className = `dg-wrap dg-theme-${theme} ${achieved ? 'dg-achieved' : ''}`;
  // ★ default theme ใช้สีจาก settings, theme อื่นๆ ใช้ CSS class (override ใน <style>)
  wrap.style.cssText = `--dg-bar:${barColor};--dg-bg:${bgColor};width:100%;height:100%;display:flex;flex-direction:column;justify-content:center;gap:6px;padding:10px 14px;background:${bgColor};border-radius:10px;box-sizing:border-box;font-family:${config.font_family || 'Kanit'},sans-serif;opacity:${opacity};${achieved ? `box-shadow:0 0 16px ${barColor}44;` : ''}`;

  // ★ header — title + percent
  const header = document.createElement('div');
  header.className = 'dg-header';
  const titleAlign = w.dg_title_align || 'left';
  const titleAlignMap = { left: 'flex-start', center: 'center', right: 'flex-end' };
  header.style.cssText = `display:flex;justify-content:${titleAlignMap[titleAlign] || 'flex-start'};align-items:center;font-size:${fs}px;color:${fontColor || 'inherit'};font-weight:600;`;
  const titleEl = document.createElement('span');
  titleEl.className = 'dg-title';
  if (achieved) {
    titleEl.innerHTML = overflow > 0
      ? `🎉 ${goalTitle || 'ครบเป้าหมาย'}! <span style="font-size:0.8em;color:#fbbf24;">(+${overflow.toLocaleString()}${currency})</span>`
      : `🎉 ${goalTitle || 'ครบเป้าหมายแล้ว'}!`;
  } else {
    titleEl.textContent = goalTitle || 'เป้าหมาย';
  }
  header.appendChild(titleEl);
  wrap.appendChild(header);

  // ★ progress bar — แต่ละ theme มีความสูงต่างกัน
  const barHeight = theme === 'minimal' ? 6 : (theme === 'cute' ? 18 : (theme === 'liquid' ? 22 : 14));
  const barBg = document.createElement('div');
  barBg.className = 'dg-bar-bg';
  barBg.style.cssText = `position:relative;width:100%;height:${barHeight}px;background:rgba(255,255,255,0.1);overflow:hidden;`;
  const barFill = document.createElement('div');
  barFill.className = 'dg-bar-fill';
  barFill.style.cssText = `height:100%;width:${Math.min(100, percent)}%;background:linear-gradient(90deg, ${gradFrom}, ${gradTo});transition:width 0.6s cubic-bezier(0.4,0,0.2,1);position:relative;`;
  barBg.appendChild(barFill);
  wrap.appendChild(barBg);

  // ★ footer — amounts (พร้อม %) + last donor
  const amountAlign = w.dg_amount_align || 'left';
  const footer = document.createElement('div');
  const alignMap = { left: 'flex-start', center: 'center', right: 'flex-end' };
  footer.style.cssText = `display:flex;justify-content:${alignMap[amountAlign] || 'flex-start'};align-items:center;gap:12px;font-size:${Math.max(11, fs - 3)}px;color:${fontColor || 'inherit'};font-weight:600;`;
  const amountEl = document.createElement('span');
  amountEl.className = 'dg-amount';
  amountEl.innerHTML = `<b style="${currentColor ? `color:${achieved ? '#fbbf24' : currentColor};` : ''}font-size:${fs}px;font-weight:800;">${current.toLocaleString()}</b> <span style="${goalColor ? `color:${goalColor};` : ''}font-weight:600;">/ ${goal.toLocaleString()} ${currency}</span> <span style="font-weight:700;opacity:0.9;">(${percent.toFixed(0)}%)</span>`;
  footer.appendChild(amountEl);
  if (showDonor && lastDonor) {
    const donorEl = document.createElement('span');
    donorEl.className = 'dg-donor';
    donorEl.style.cssText = 'opacity:0.7;';
    donorEl.append(document.createTextNode('• ล่าสุด: '));
    const donorName=document.createElement('b');donorName.style.color='#cbd5e1';donorName.textContent=lastDonor;donorEl.append(donorName);
    const donationAmount=document.createElement('span');donationAmount.style.color=barColor;donationAmount.textContent=` +${lastAmount}${currency}`;donorEl.append(donationAmount);
    footer.appendChild(donorEl);
  }
  wrap.appendChild(footer);

  inner.appendChild(wrap);
  if(window.BP3PatchWidget)window.BP3PatchWidget(target,inner,true);else target.replaceChildren(...inner.childNodes);
}

// ★ helper — ทำสีอ่อนขึ้น (สำหรับ gradient)
function _lightenColor(hex, percent) {
  const num = parseInt(hex.replace('#', ''), 16);
  const r = Math.min(255, (num >> 16) + Math.round(255 * percent / 100));
  const g = Math.min(255, ((num >> 8) & 0xff) + Math.round(255 * percent / 100));
  const b = Math.min(255, (num & 0xff) + Math.round(255 * percent / 100));
  return '#' + ((r << 16) | (g << 8) | b).toString(16).padStart(6, '0');
}


function mount(){(window._overlayWidgets || window.ComposerStudio?.getActivePage?.()?.widgets || []).filter(w=>w.type==='donate_goal' && !w.hidden).forEach(w=>{const inner=(document.getElementById('widget-'+w.id)?.querySelector('.composer-widget-inner') || document.querySelector('.widget[data-id="'+CSS.escape(String(w.id))+'"] .composer-widget-inner'));if(inner)setupDonateGoalWidget(inner,w);});}
async function refresh(){if(busy || !(window._overlayWidgets || window.ComposerStudio?.getActivePage?.()?.widgets || []).some(w=>w.type==='donate_goal' && !w.hidden))return;busy=true;try{const response=await fetch('/api/donation-goals',{cache:'no-store'});if(response.ok){_lastDonateGoalData=await response.json();mount();}}catch{}finally{busy=false;}}
window.BP3LegacyGoals={mount(){mount();refresh();},refresh};setInterval(refresh,3000);
})();
