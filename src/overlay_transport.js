(() => {
  'use strict';
  try {if(window.opener?.BP3Transport){window.BP3Transport=window.opener.BP3Transport;return;}} catch (_) {}
  if (!/^https?:$/.test(location.protocol)) return;
  const client = (crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`);
  let cursor = null, epoch = null, stopped = false;
  const pending = new Map();
  let flushing = null;
  function flush() {
    if (flushing) return flushing;
    flushing = (async () => {
      for (const [id, item] of pending) {
        const response = await fetch('/api/overlay/events', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(item)});
        if (!response.ok) break;
        pending.delete(id);
      }
    })().finally(() => {flushing = null;});
    return flushing;
  }
  const supported = new Set(['ASK_UPDATE','GIVEAWAY_UPDATE','CHAT_MESSAGE','CHAT_CLEAR','CHAT_DELETE','RANDOMIZER_SPIN','REPLIE_ACTION','REPLIE_DISMISS','PLAYROOM_PLAY_CLIP','AVATAR_STATE','VIEWERS_UPDATE','DOCK_CONTROL','CANVAS_LAYOUT_SAVED']);
  window.BP3Transport = {
    publish(event, payload) {
      if (!supported.has(event)) return;
      const item = { id: `${client}:${Date.now()}:${Math.random()}`, client, event, payload };
      pending.set(item.id, item);
      flush().catch(() => {});

    }
  };
  async function poll() {
    try {
      // Retain failed sends for a bounded retry window, preserving event order.
      if (pending.size > 200) pending.delete(pending.keys().next().value);
      await flush();
      const query = cursor === null ? '' : `?after=${cursor}&epoch=${encodeURIComponent(epoch || '')}`;
      const response = await fetch('/api/overlay/events' + query, {cache:'no-store'});
      if (!response.ok) throw new Error('Overlay relay unavailable');
      const data = await response.json();
      epoch = data.epoch;
      cursor = data.cursor;
      for (const item of data.events || []) {
        if (item.client === client) continue;
        window.dispatchEvent(new CustomEvent('bp3:remote-event', {detail:item}));
        const bus = window.BP3_BUS;
        if (bus && bus.listeners && bus.listeners[item.event]) {
          bus.listeners[item.event].forEach(fn => {try {fn(item.payload);} catch (error) {console.error(error);}});
        }
      }
    } catch (_) {}
    if (!stopped) setTimeout(poll, 250);
  }
  window.addEventListener('pagehide', () => {stopped = true;});
  window.addEventListener('pageshow', () => {if (stopped) {stopped = false;poll();}});
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', poll, {once:true});
  else poll();
})();
