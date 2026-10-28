/* Visuals for user-selected Randomizer modes, shared by Studio and OBS. */
(() => {
  window.BP3RandomizerVisual = {
    mount(container, data, duration) {
      const mode=data.settings?.mode || 'viewers';
      if(mode!=='wheel' && mode!=='box') return {finish(){}};
      const doc=container.ownerDocument, wrapper=doc.createElement('div');
      wrapper.dataset.randomizerMode=mode;
      wrapper.style.cssText='display:flex;align-items:center;justify-content:center;margin:0 auto 12px;height:136px;position:relative;';
      if(mode==='box') {
        const box=doc.createElement('div');box.textContent='📦';box.style.cssText='font-size:90px;line-height:1;';wrapper.append(box);
        container.prepend(wrapper);
        return {finish(){box.textContent='🎉';}};
      }
      const items=Array.isArray(data.items)&&data.items.length?data.items:[''];
      const wheel=doc.createElement('div');wheel.style.cssText='width:128px;height:128px;border:4px solid #f8fafc;border-radius:50%;box-shadow:0 4px 12px #0008;';
      const colors=['#60a5fa','#f472b6','#34d399','#fbbf24','#a78bfa','#fb7185'];
      wheel.style.background='conic-gradient('+items.map((_,i)=>`${colors[i%colors.length]} ${i*100/items.length}% ${(i+1)*100/items.length}%`).join(',')+')';
      if(items.length<=16) {
        const ns='http://www.w3.org/2000/svg',svg=doc.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 128 128');svg.setAttribute('width','128');svg.setAttribute('height','128');
        items.forEach((item,i)=>{const label=doc.createElementNS(ns,'text');label.setAttribute('x','64');label.setAttribute('y','15');label.setAttribute('text-anchor','middle');label.setAttribute('font-size',items.length>8?'7':'9');label.setAttribute('font-weight','700');label.setAttribute('fill','#111827');label.setAttribute('transform',`rotate(${(i+.5)*360/items.length} 64 64)`);label.textContent=String(item).slice(0,10);svg.append(label);});wheel.append(svg);
      }
      const pointer=doc.createElement('div');pointer.textContent='▼';pointer.style.cssText='position:absolute;top:-8px;color:white;text-shadow:0 1px 4px #000;font-size:22px;z-index:1;';
      wrapper.append(wheel,pointer);container.prepend(wrapper);
      const index=Math.max(0,items.indexOf(data.winner));
      const angle=1800+360-(index+.5)*360/items.length;
      requestAnimationFrame(()=>{wheel.style.transition=`transform ${duration}s cubic-bezier(.16,.64,.25,1)`;wheel.style.transform=`rotate(${angle}deg)`;});
      return {finish(){}};
    }
  };
})();
