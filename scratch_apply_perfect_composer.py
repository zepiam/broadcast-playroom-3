# -*- coding: utf-8 -*-
"""
Updater script for src/composer_studio.js
"""
import sys, io, re

file_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

print("Initial code length:", len(code))

# 1. Insert Number Ticker & People Icon helpers if not present
if 'function updateNumberTicker(' not in code:
    ticker_helpers = """
  // ── Vertical Ticker Helper for Viewer Widget ──
  const _VT_DIGITS = [];
  for (let loop = 0; loop < 3; loop++) {
    for (let d = 0; d <= 9; d++) {
      _VT_DIGITS.push(d);
    }
  }
  const _VT_TOTAL_ITEMS = _VT_DIGITS.length;
  const _VT_STEP_PCT = 100 / _VT_TOTAL_ITEMS;

  function createVtDigitColumn(initDigit) {
    const col = document.createElement('span');
    col.className = 'vt-col';
    col.dataset.digit = initDigit;
    col.dataset.idx = 10 + initDigit;

    const track = document.createElement('span');
    track.className = 'vt-track';
    for (let i = 0; i < _VT_TOTAL_ITEMS; i++) {
      const item = document.createElement('span');
      item.className = 'vt-num';
      item.textContent = _VT_DIGITS[i];
      track.appendChild(item);
    }

    const initIdx = 10 + initDigit;
    track.style.transform = `translateY(-${(initIdx * _VT_STEP_PCT).toFixed(4)}%)`;
    col.appendChild(track);

    track.addEventListener('transitionend', (e) => {
      if (e.propertyName !== 'transform') return;
      const curIdx = parseInt(col.dataset.idx, 10);
      const normDigit = ((curIdx % 10) + 10) % 10;
      const normIdx = 10 + normDigit;
      col.dataset.idx = normIdx;
      col.dataset.digit = normDigit;
      track.classList.remove('animated');
      track.style.transform = `translateY(-${(normIdx * _VT_STEP_PCT).toFixed(4)}%)`;
      void track.offsetHeight;
    });

    return col;
  }

  function createVtCharSpan(char) {
    const sp = document.createElement('span');
    sp.className = 'vt-char';
    sp.textContent = char;
    return sp;
  }

  function updateNumberTicker(tickerEl, targetNumber) {
    if (!tickerEl) return;
    const targetVal = targetNumber || 0;
    const formatted = targetVal.toLocaleString();
    const targetChars = formatted.split('');
    const prevVal = tickerEl._lastVal != null ? tickerEl._lastVal : null;
    const isIncrease = prevVal == null || targetVal >= prevVal;
    tickerEl._lastVal = targetVal;

    let curCols = Array.from(tickerEl.children);

    while (curCols.length < targetChars.length) {
      const c = targetChars[targetChars.length - curCols.length - 1];
      let newEl;
      if (c >= '0' && c <= '9') {
        newEl = createVtDigitColumn(parseInt(c, 10));
      } else {
        newEl = createVtCharSpan(c);
      }
      tickerEl.insertBefore(newEl, tickerEl.firstChild);
      curCols.unshift(newEl);
    }
    while (curCols.length > targetChars.length) {
      const rem = curCols.shift();
      if (rem) rem.remove();
    }

    targetChars.forEach((c, i) => {
      const el = curCols[i];
      if (c >= '0' && c <= '9') {
        if (!el.classList.contains('vt-col')) {
          const col = createVtDigitColumn(parseInt(c, 10));
          tickerEl.replaceChild(col, el);
          curCols[i] = col;
          return;
        }
        const targetDigit = parseInt(c, 10);
        const curDigit = parseInt(el.dataset.digit || 0, 10);
        let curIdx = parseInt(el.dataset.idx || 10, 10);

        if (curDigit === targetDigit && curIdx >= 10 && curIdx < 20) {
          return;
        }

        let nextIdx;
        if (isIncrease) {
          if (targetDigit >= curDigit) {
            nextIdx = curIdx + (targetDigit - curDigit);
          } else {
            nextIdx = curIdx + (10 + targetDigit - curDigit);
          }
        } else {
          if (targetDigit <= curDigit) {
            nextIdx = curIdx - (curDigit - targetDigit);
          } else {
            nextIdx = curIdx - (10 + curDigit - targetDigit);
          }
        }

        el.dataset.digit = targetDigit;
        el.dataset.idx = nextIdx;

        const track = el.querySelector('.vt-track');
        if (track) {
          track.classList.add('animated');
          track.style.transform = `translateY(-${(nextIdx * _VT_STEP_PCT).toFixed(4)}%)`;
        }
      } else {
        if (!el.classList.contains('vt-char')) {
          const sp = createVtCharSpan(c);
          tickerEl.replaceChild(sp, el);
          curCols[i] = sp;
        } else {
          el.textContent = c;
        }
      }
    });
  }

  const PEOPLE_ICON_SVG = `<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;">
    <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
  </svg>`;
  function peopleIconSpan(iconSize = 20) {
    return `<span style="display:inline-flex;align-items:center;width:${iconSize}px;height:${iconSize}px;flex-shrink:0;">${PEOPLE_ICON_SVG}</span>`;
  }
"""
    # Insert right before const ComposerDemoManager
    ins_idx = code.find('const ComposerDemoManager = {')
    code = code[:ins_idx] + ticker_helpers + "\n  " + code[ins_idx:]
    print("Added ticker helpers and PEOPLE_ICON_SVG.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated composer_studio.js with helpers.")
