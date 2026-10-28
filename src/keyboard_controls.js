/* One option per arrow key, with normal input/change events in every app window. */
(()=>{'use strict';const installed=new WeakSet();
function install(doc){if(installed.has(doc))return;installed.add(doc);doc.addEventListener('keydown',event=>{
 const select=event.target?.closest?.('select');
 if(!select || select.disabled || select.multiple || event.altKey || event.ctrlKey || event.metaKey || !['ArrowUp','ArrowDown'].includes(event.key))return;
 event.preventDefault();event.stopImmediatePropagation();
 const step=event.key==='ArrowDown'?1:-1,options=[...select.options];let index=select.selectedIndex+step;
 while(index>=0 && index<options.length && (options[index].disabled || options[index].hidden || options[index].parentElement?.disabled || options[index].parentElement?.hidden))index+=step;
 if(index<0 || index>=options.length)return;
 select.selectedIndex=index;const view=select.ownerDocument.defaultView;select.dispatchEvent(new view.Event('input',{bubbles:true}));select.dispatchEvent(new view.Event('change',{bubbles:true}));
 if(!select.isConnected && select.id)select.ownerDocument.getElementById(select.id)?.focus();
},true);}
window.BP3KeyboardControls={install};install(document);
})();
