/* Patch authored markup in place. Existing live nodes are never detached. */
(()=>{'use strict';function patch(old,next,force=false){if(old.nodeType!==next.nodeType || old.nodeName!==next.nodeName){old.replaceWith(next);return next;}if(old.nodeType!==1){if(old.nodeValue!==next.nodeValue)old.nodeValue=next.nodeValue;return old;}
if(old.matches('iframe[data-legacy-chat]'))return old;
const live=old.matches('[data-live-replie], [id^="compPlayroomStage_"], [id^="compAskPanel_"], [id^="compGwPanel_"], [id^="widget-emote-party-"]');
const display=live?old.style.display:null;
for(const attr of [...old.attributes])if(!next.hasAttribute(attr.name))old.removeAttribute(attr.name);
for(const attr of next.attributes)if(old.getAttribute(attr.name)!==attr.value)old.setAttribute(attr.name,attr.value);
if(live && display!==null)old.style.display=display;
if(live || (!force && (old._bpAvatarConfig || old._bpGoalConfig || old._bpRuntimeConfig)) || (old.matches('.widget-inner') && old.querySelector('.replie-wrapper')) || old.matches('[data-live-media],video,audio') || (!next.childNodes.length && old.querySelector('[data-live-media],.replie-wrapper')))return old;
let index=0;for(const desired of [...next.childNodes]){let existing=old.childNodes[index];if(desired.nodeType===1 && desired.id){const found=[...old.children].find(el=>el.id===desired.id);if(found && found!==existing){old.insertBefore(found,existing || null);existing=found;}}
if(!existing)old.append(desired);else patch(existing,desired,force);index++;}
while(old.childNodes.length>index){const stale=old.childNodes[index];if(stale.nodeType===1 && stale.matches('[data-video-color-key],[data-live-media]')){index++;continue;}stale.remove();}return old;}
window.BP3PatchWidget=patch;
})();
