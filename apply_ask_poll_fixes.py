import os

path = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update popoutToolWindow to bridge BP3_BUS and state objects
old_popout_mirror = """      // Forward all global helper functions and properties from parent window to popup
      try {
        pop.opener = window;
        const copyProps = (src) => {
          for (const key of Object.getOwnPropertyNames(src)) {
            if (typeof src[key] === 'function' && !(key in pop)) {
              try { pop[key] = src[key].bind(window); } catch (e) { pop[key] = src[key]; }
            }
          }
        };
        copyProps(window);
        for (const key in window) {
          if (typeof window[key] === 'function' && !(key in pop)) {
            try { pop[key] = window[key].bind(window); } catch (e) { pop[key] = window[key]; }
          }
        }
      } catch (e) {
        console.warn('Could not mirror window functions to popup:', e);
      }"""

new_popout_mirror = """      // Forward all global helper functions, bus, and state objects from parent window to popup
      try {
        pop.opener = window;
        pop.parentWindow = window;
        pop.BP3_BUS = window.BP3_BUS;
        pop.composerStudio = window.composerStudio;
        pop.ComposerStudio = window.ComposerStudio;

        // Bridge state objects via getters/setters
        const bridgeKeys = [
          'BP3_BUS', '_askPollState', '_liveAskState', '_askVotes', '_askPollActive',
          '_liveGwState', '_gwState', '_randomizerState', 'ComposerStudio', 'composerStudio'
        ];
        bridgeKeys.forEach(k => {
          try {
            Object.defineProperty(pop, k, {
              get: () => window[k],
              set: (val) => { window[k] = val; },
              configurable: true,
              enumerable: true
            });
          } catch(e) {
            pop[k] = window[k];
          }
        });

        const copyProps = (src) => {
          for (const key of Object.getOwnPropertyNames(src)) {
            if (typeof src[key] === 'function' && !(key in pop)) {
              try { pop[key] = src[key].bind(window); } catch (e) { pop[key] = src[key]; }
            }
          }
        };
        copyProps(window);
        for (const key in window) {
          if (typeof window[key] === 'function' && !(key in pop)) {
            try { pop[key] = window[key].bind(window); } catch (e) { pop[key] = window[key]; }
          }
        }
      } catch (e) {
        console.warn('Could not mirror window functions to popup:', e);
      }"""

if old_popout_mirror in code:
    code = code.replace(old_popout_mirror, new_popout_mirror, 1)
    print("Updated popoutToolWindow bridging")
else:
    print("Warning: old_popout_mirror not found")

# 2. Add ask element helpers and update startAskPoll, endAskPoll, closeAskOverlay, resetAskPoll, updateAskUIState, emitAskState
old_ask_block_start = """    // ----------------------------------------------------
    // REAL ASK POLL SYSTEM (FULL LIFECYCLE: IDLE -> VOTING -> PAUSED -> ENDED)
    // ----------------------------------------------------
    window._askPollState = {"""

new_ask_helpers = """    // ----------------------------------------------------
    // REAL ASK POLL SYSTEM (FULL LIFECYCLE: IDLE -> VOTING -> PAUSED -> ENDED)
    // ----------------------------------------------------
    function getAskDoc() {
      if (window._popoutWindows && window._popoutWindows['ask'] && !window._popoutWindows['ask'].closed) {
        try {
          if (window._popoutWindows['ask'].document) return window._popoutWindows['ask'].document;
        } catch(e) {}
      }
      return document;
    }

    function getAskEl(id) {
      let el = null;
      if (window._popoutWindows && window._popoutWindows['ask'] && !window._popoutWindows['ask'].closed) {
        try {
          el = window._popoutWindows['ask'].document.getElementById(id);
        } catch(e) {}
      }
      if (!el) el = document.getElementById(id);
      return el;
    }

    function queryAskAll(selector) {
      let list = null;
      if (window._popoutWindows && window._popoutWindows['ask'] && !window._popoutWindows['ask'].closed) {
        try {
          list = window._popoutWindows['ask'].document.querySelectorAll(selector);
        } catch(e) {}
      }
      if (!list || list.length === 0) list = document.querySelectorAll(selector);
      return list;
    }

    window._askPollState = {"""

if old_ask_block_start in code:
    code = code.replace(old_ask_block_start, new_ask_helpers, 1)
    print("Added getAskDoc, getAskEl, queryAskAll helpers")
else:
    print("Warning: old_ask_block_start not found")

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/index.html', 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved preliminary changes.")
