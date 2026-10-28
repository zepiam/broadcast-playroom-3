import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert';
const html = fs.readFileSync('src/index.html', 'utf8');
const start = html.indexOf("    let _ttsServerHealthState = 'unknown';");
const end = html.indexOf('    function installObsDockAuto()', start);
const initStart = html.indexOf("    window.addEventListener('DOMContentLoaded', () => {", end);
const initEnd = html.indexOf('    });', initStart) + 7;
assert(start >= 0 && end > start && initStart > end);
const nodes = Object.fromEntries(['serverStatusDot', 'serverStatusText', 'topbarServerStatus'].map(id => [id, {}]));
let now = 0, mode = 'ok', requests = 0, startup, interval, listener;
const context = { document: {getElementById: id => nodes[id]}, performance: {now: () => now}, AbortController,
  fetch: async () => { requests++; if (mode === 'fail') throw Error('offline'); now += mode === 'slow' ? 2300 : 100; return {ok: true, arrayBuffer: async () => new Uint8Array([1]).buffer}; },
  setTimeout: (fn, ms) => { if (ms === 600) startup = fn; return 1; }, clearTimeout: () => {},
  setInterval: (fn, ms) => { assert.equal(ms, 60000); interval = fn; },
  window: {addEventListener: (event, fn) => { assert.equal(event, 'DOMContentLoaded'); listener = fn; }} };
vm.createContext(context);
vm.runInContext(html.slice(start, end) + html.slice(initStart, initEnd), context);
(async () => {
  listener(); assert(startup && interval);
  await startup(); await new Promise(setImmediate);
  assert.equal(nodes.serverStatusDot.className, 'server-status-dot green');
  mode = 'slow'; await interval(); await new Promise(setImmediate);
  assert.equal(nodes.serverStatusDot.className, 'server-status-dot yellow');
  mode = 'fail'; await interval(); await new Promise(setImmediate);
  assert.equal(nodes.serverStatusDot.className, 'server-status-dot red');
  mode = 'ok'; await context.checkTtsServerHealth(true);
  assert.equal(nodes.serverStatusDot.className, 'server-status-dot green');
  assert.equal(requests, 4);
  console.log('TTS health startup, one-minute schedule, slow, failure and recovery: PASS');
})().catch(err => { console.error(err); process.exitCode = 1; });
