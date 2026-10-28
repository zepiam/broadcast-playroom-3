/**
 * BROADCAST PLAYROOM 3.0 - IN-APP OVERLAY COMPOSER CANVAS STUDIO
 * Unified Canvas Studio & Full Widget Customizer with Real-Time Live Preview,
 * Interactive Demos, Context Menu Add, and Duplicate Prevention
 */

(function () {
  'use strict';

  let CANVAS_WIDTH = 1920;
  let CANVAS_HEIGHT = 1080;
  const STORAGE_KEY = 'bp_composer_studio_v3';

  // Application State
  const state = {
    pages: [
      {
        id: 'page-1',
        name: 'ฉากหลักสตรีม',
        widgets: [
          {
            id: 'w-chat-1',
            type: 'chat',
            title: 'กล่องแชทมาตรฐาน',
            chatMode: 'default',
            chatTheme: 'default',
            x: 60,
            y: 400,
            width: 440,
            height: 600,
            z: 1,
            opacity: 1,
            locked: false,
            hidden: false,
            fontSize: 15,
            fontColor: '#ffffff',
            bgColor: '#1e1f22',
            bgOpacity: 0.85,
            boxRadius: 8
          },
          {
            id: 'w-clock-1',
            type: 'clock',
            title: 'นาฬิกาสตรีม',
            clockTheme: 'cyberpunk',
            clockFormat: '24',
            showSeconds: true,
            x: 1560,
            y: 50,
            width: 280,
            height: 80,
            z: 2,
            opacity: 1,
            locked: false,
            hidden: false,
            fontSize: 26,
            fontColor: '#38bdf8'
          },
          {
            id: 'w-text-1',
            type: 'text',
            title: 'แถบข้อความประกาศ',
            text: 'ยินดีต้อนรับทุกคนเข้าสู่ไลฟ์สตรีมสดวันนี้ครับ! กดติดตามและพูดคุยในแชทได้เลย',
            textMode: 'ticker',
            x: 560,
            y: 1000,
            width: 800,
            height: 50,
            z: 3,
            opacity: 1,
            locked: false,
            hidden: false,
            fontSize: 18,
            fontColor: '#ffffff',
            bgColor: '#141923'
          }
        ]
      }
    ],
    activePageId: 'page-1',
    selectedWidgetId: null,
    zoom: 0.45,
    snapGuides: true,
    isDragging: false,
    isResizing: false,
    activeResizeHandle: null,
    dragStartMouseX: 0,
    dragStartMouseY: 0,
    dragStartWidgetX: 0,
    dragStartWidgetY: 0,
    dragStartWidgetW: 0,
    dragStartWidgetH: 0,
    customizerManuallyCollapsed: false,
    chatSubTab: 'standard',
    chatThemePage: 1
  };

  let clockInterval = null;

  // ========================================================
  // COMPOSER LIVE DEMO SIMULATION MANAGER
  // ========================================================
  
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
  const PLATFORM_LOGOS = {"youtube": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAKMWlDQ1BJQ0MgUHJvZmlsZQAAeJydlndUU9kWh8+9N71QkhCKlNBraFICSA29SJEuKjEJEErAkAAiNkRUcERRkaYIMijggKNDkbEiioUBUbHrBBlE1HFwFBuWSWStGd+8ee/Nm98f935rn73P3Wfvfda6AJD8gwXCTFgJgAyhWBTh58WIjYtnYAcBDPAAA2wA4HCzs0IW+EYCmQJ82IxsmRP4F726DiD5+yrTP4zBAP+flLlZIjEAUJiM5/L42VwZF8k4PVecJbdPyZi2NE3OMErOIlmCMlaTc/IsW3z2mWUPOfMyhDwZy3PO4mXw5Nwn4405Er6MkWAZF+cI+LkyviZjg3RJhkDGb+SxGXxONgAoktwu5nNTZGwtY5IoMoIt43kA4EjJX/DSL1jMzxPLD8XOzFouEiSniBkmXFOGjZMTi+HPz03ni8XMMA43jSPiMdiZGVkc4XIAZs/8WRR5bRmyIjvYODk4MG0tbb4o1H9d/JuS93aWXoR/7hlEH/jD9ld+mQ0AsKZltdn6h21pFQBd6wFQu/2HzWAvAIqyvnUOfXEeunxeUsTiLGcrq9zcXEsBn2spL+jv+p8Of0NffM9Svt3v5WF485M4knQxQ143bmZ6pkTEyM7icPkM5p+H+B8H/nUeFhH8JL6IL5RFRMumTCBMlrVbyBOIBZlChkD4n5r4D8P+pNm5lona+BHQllgCpSEaQH4eACgqESAJe2Qr0O99C8ZHA/nNi9GZmJ37z4L+fVe4TP7IFiR/jmNHRDK4ElHO7Jr8WgI0IABFQAPqQBvoAxPABLbAEbgAD+ADAkEoiARxYDHgghSQAUQgFxSAtaAYlIKtYCeoBnWgETSDNnAYdIFj4DQ4By6By2AE3AFSMA6egCnwCsxAEISFyBAVUod0IEPIHLKFWJAb5AMFQxFQHJQIJUNCSAIVQOugUqgcqobqoWboW+godBq6AA1Dt6BRaBL6FXoHIzAJpsFasBFsBbNgTzgIjoQXwcnwMjgfLoK3wJVwA3wQ7oRPw5fgEVgKP4GnEYAQETqiizARFsJGQpF4JAkRIauQEqQCaUDakB6kH7mKSJGnyFsUBkVFMVBMlAvKHxWF4qKWoVahNqOqUQdQnag+1FXUKGoK9RFNRmuizdHO6AB0LDoZnYsuRlegm9Ad6LPoEfQ4+hUGg6FjjDGOGH9MHCYVswKzGbMb0445hRnGjGGmsVisOtYc64oNxXKwYmwxtgp7EHsSewU7jn2DI+J0cLY4X1w8TogrxFXgWnAncFdwE7gZvBLeEO+MD8Xz8MvxZfhGfA9+CD+OnyEoE4wJroRIQiphLaGS0EY4S7hLeEEkEvWITsRwooC4hlhJPEQ8TxwlviVRSGYkNimBJCFtIe0nnSLdIr0gk8lGZA9yPFlM3kJuJp8h3ye/UaAqWCoEKPAUVivUKHQqXFF4pohXNFT0VFysmK9YoXhEcUjxqRJeyUiJrcRRWqVUo3RU6YbStDJV2UY5VDlDebNyi/IF5UcULMWI4kPhUYoo+yhnKGNUhKpPZVO51HXURupZ6jgNQzOmBdBSaaW0b2iDtCkVioqdSrRKnkqNynEVKR2hG9ED6On0Mvph+nX6O1UtVU9Vvuom1TbVK6qv1eaoeajx1UrU2tVG1N6pM9R91NPUt6l3qd/TQGmYaYRr5Grs0Tir8XQObY7LHO6ckjmH59zWhDXNNCM0V2ju0xzQnNbS1vLTytKq0jqj9VSbru2hnaq9Q/uE9qQOVcdNR6CzQ+ekzmOGCsOTkc6oZPQxpnQ1df11Jbr1uoO6M3rGelF6hXrtevf0Cfos/ST9Hfq9+lMGOgYhBgUGrQa3DfGGLMMUw12G/YavjYyNYow2GHUZPTJWMw4wzjduNb5rQjZxN1lm0mByzRRjyjJNM91tetkMNrM3SzGrMRsyh80dzAXmu82HLdAWThZCiwaLG0wS05OZw2xljlrSLYMtCy27LJ9ZGVjFW22z6rf6aG1vnW7daH3HhmITaFNo02Pzq62ZLde2xvbaXPJc37mr53bPfW5nbse322N3055qH2K/wb7X/oODo4PIoc1h0tHAMdGx1vEGi8YKY21mnXdCO3k5rXY65vTW2cFZ7HzY+RcXpkuaS4vLo3nG8/jzGueNueq5clzrXaVuDLdEt71uUnddd457g/sDD30PnkeTx4SnqWeq50HPZ17WXiKvDq/XbGf2SvYpb8Tbz7vEe9CH4hPlU+1z31fPN9m31XfKz95vhd8pf7R/kP82/xsBWgHcgOaAqUDHwJWBfUGkoAVB1UEPgs2CRcE9IXBIYMj2kLvzDecL53eFgtCA0O2h98KMw5aFfR+OCQ8Lrwl/GGETURDRv4C6YMmClgWvIr0iyyLvRJlESaJ6oxWjE6Kbo1/HeMeUx0hjrWJXxl6K04gTxHXHY+Oj45vipxf6LNy5cDzBPqE44foi40V5iy4s1licvvj4EsUlnCVHEtGJMYktie85oZwGzvTSgKW1S6e4bO4u7hOeB28Hb5Lvyi/nTyS5JpUnPUp2Td6ePJninlKR8lTAFlQLnqf6p9alvk4LTduf9ik9Jr09A5eRmHFUSBGmCfsytTPzMoezzLOKs6TLnJftXDYlChI1ZUPZi7K7xTTZz9SAxESyXjKa45ZTk/MmNzr3SJ5ynjBvYLnZ8k3LJ/J9879egVrBXdFboFuwtmB0pefK+lXQqqWrelfrry5aPb7Gb82BtYS1aWt/KLQuLC98uS5mXU+RVtGaorH1futbixWKRcU3NrhsqNuI2ijYOLhp7qaqTR9LeCUXS61LK0rfb+ZuvviVzVeVX33akrRlsMyhbM9WzFbh1uvb3LcdKFcuzy8f2x6yvXMHY0fJjpc7l+y8UGFXUbeLsEuyS1oZXNldZVC1tep9dUr1SI1XTXutZu2m2te7ebuv7PHY01anVVda926vYO/Ner/6zgajhop9mH05+x42Rjf2f836urlJo6m06cN+4X7pgYgDfc2Ozc0tmi1lrXCrpHXyYMLBy994f9Pdxmyrb6e3lx4ChySHHn+b+O31w0GHe4+wjrR9Z/hdbQe1o6QT6lzeOdWV0iXtjusePhp4tLfHpafje8vv9x/TPVZzXOV42QnCiaITn07mn5w+lXXq6enk02O9S3rvnIk9c60vvG/wbNDZ8+d8z53p9+w/ed71/LELzheOXmRd7LrkcKlzwH6g4wf7HzoGHQY7hxyHui87Xe4Znjd84or7ldNXva+euxZw7dLI/JHh61HXb95IuCG9ybv56Fb6ree3c27P3FlzF3235J7SvYr7mvcbfjT9sV3qID0+6j068GDBgztj3LEnP2X/9H686CH5YcWEzkTzI9tHxyZ9Jy8/Xvh4/EnWk5mnxT8r/1z7zOTZd794/DIwFTs1/lz0/NOvm1+ov9j/0u5l73TY9P1XGa9mXpe8UX9z4C3rbf+7mHcTM7nvse8rP5h+6PkY9PHup4xPn34D94Tz+6TMXDkAAAbXSURBVHic7ZttiFRlFMd/z713319FM9deDd8QM1+goBAlkSD7EqVIH7KIMKhPEX2Rkk0Jwz6pWFFmKZQh+iGNoIK0pZTMFE1BXJWyNxfLfVF3d2bufeLc57k6jjPjLnlnZnfnD5eZvTNzn/M/zznnOc95zkIZZZRRRhlljFiom/EQff1z8jx38Q3G3K7zD3XNIPm+OyCoARBTRugOBWMzBtyuFQQUERqc65UayRoqU+dTlMr+0MXuYMhpplUC9qqrBF0BjgcJD5QHrgspFzwHAgeUm+NJPjgB+D649lWnoDIFQQpUEi4lgPBSHE8MRkmK7X5eBWg74xFxzYw6qJoE/u1ACzjjQY8FRoNuAhqBWlDVoK0ClLxWgPYAqwCEsBAfiLyRpYsMKXOJYpS8T4BOgLJK0H3AZaAbVBfwL6gOCP4E/gLvLPS1K45cSuN3jeuodPLRB5o5C0E9C3oucCu4Fear2Swp/V7m51ktLzTLLNYX3cuipXwhJptSI1n9JHAOVBvozYqDX2dyVek3NFMaoGE9qGXmoyCS188htDWYvNLe6H4u6IHd17lmRRlXk2EdeyvYCl0vKdq7I87KmMVKBburQX0B7nxI+mnkcszKkIC1tkhJFRKL9gKPwmN90KodIa9olal+25BPJa3mrN8OWfICO/0RH+HmzQP9luG80piv5r6ZUHEQAjGIoU46H0I/ACXXLMWBY0JWgvUz4EaOMlzJC2zscyogeEpuOJo5FcBDJuCFsz8SIFqYK/mB+Mc4YFL6qjC8IZMcCM+pMP0WB/RdQNPIUcCVPGgM1NwhCph4NR2Ia0hZkktKtzYNCCaLAibYzCmIT+GSzabMlqA0EGXF9zjgjIvN8sPHpqC5GcaMBv+CUXy44BQTkhiFwrWIJGNjs/5wUemHyXfCga3w9FLQSfAvGiUU3S30WHGBUVba+MwgkYS7W+DjN+DbTTD3AfB7zMZO3KLgioj2Qmq0TEO0AsQ7niSZfgDz58CeD+Hd1XBbi3ELCT8Fjw8h5yaxgMZIzFjHc6zvixLk/fIn4PA2eOUFqHbB7zZpiVzxI+LaKBZQTSERBUAp9oxphrUvw/dbYNFCCC5D0FtAt9A1Ik1N7C6QDUJSgrEoYvZU2L0Odq6D6VPA7yzUslktLhBZQOFDcrgkuhAEJkY8/jDs2wKrX4VRDUYR8SybURCsKbwLZEPo+8rEh/paWPEcHNwGy5aYlULiQzyoKa29v8x05BYTxsNHq+Cb9+GRBWF5NQZJVbFTshz7BgeSUgQGFtwPTy6ESgmMWY5g/ic8Sgky+xIPJC7IsULbIVixHtr2m1gdgwl49pBBavnFRXgW4prr17/hzQ9g007w+8CpN4q5+Uh45nAhPMwoDiT6C4R4fxI2fAprNsN5OdtoiJO8oFdObnpBNdrSceECYhjsAvDsWv/5d9C6EX4+LMszuM3GKuIhH9UDesUF5HipOOYu5I+dgpUbYcdXRi63yZCW78SPPlFAeG5WEET7ACH/Txes3QIbPoFLF8BpMAZYGOIRLooCumxFKD4XuBLd7aq7ZRe0vgenTwJ1ZtZD4gVLya0L0CVBsPOqlHHw18bUJdtrOwyvb4Q9beYA2RM/L5i5p8tkNa06JQiejy/2yTgu9FyGF9fAO5+B7rfmLtWyQhNPR2j1HeICHfEucVVw4gycOG5aCVzZ5BSTeDrUOXGBs3ZnFN8SKKmtzHpYFSoF8iJQeHB8VizglG0IiW9fEPYqFLWVKNd2+KQD3mlTfRgxsAEw6IPgjMz678BvNhCW1DTFBNMzhToDVX84ih+l2nA0PCjO3m4yzCAl6HBffVixv9f6vd6R1lk03GFbfvRO+UOmXUHjdkgdA1dWhVII0zFBuEke7h+Frl22HUb6ZPb2gX7eZimuDYrDyRrEvVOWWwKc5Yr2fuHuSLOQZqWjOLQP/CVAJ3he2rGub60iSO+bo/QQyWXljOQOJ1NZTt0QLFUc2Gc4t4adEvbXi11pJdXMnAbuKlCLwKm6/vnR+8wWtAEJOBgMMDFLb+WLfpLZ2Rf0A18Cryl++iXiSpZWWedqm+ysGeA8CMwGJpqOCukkkTIN9aBs9+ggZL3pSJ8QMe1wa99jrJjzQDtwCIIfFIeOZHLMKrldJOWDa3ICEyzvbYZKyWnrwJEqZa1RSlBve4ZrwKmVI6ervcO6ynRlSf1R+ofD/sNcxdj0vmBpkE7rC5ZXqV7J+ZnuNT3CzkWznceeqTmXINEDRzszO8Rz8coJ+YFmnifmEv14KMHIL7ILh9zyq0E8MMPe8/3jg/Trx4HM/1eIME1Da/RH1O1VioG6jDLKKKOMMigh/Af9BnGlHzwxqAAAAABJRU5ErkJggg==", "twitch": "data:image/png;base64,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", "tiktok": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAANVUlEQVR4nOWbiVMbSZbGf5VVpVsCSSBOc/ka4wO3Cbt7e7wxERsxsbH/8MbEbOzsRuxu99gzxvjoNjY2NggECAkJHUgl1bGRqRKWvV6bxshutx9RSOiozHz5ju99L9EAl45ofIUi+MpF8JWL4CsXwVcuxueeANr/E3u9o1+/YQVoGpomOkro1YPnqUs+dH71cQp85WnQ4Fci2lvPu397aHjq5zeoAM00EaEwnmkemaF0B89uQ7MJ7Ra4/XUBg08t0t89D01oGKk0obPnEJlRXF2AkJeOfVDC2ljH3d6CSqWjBBULpF14vw0FgIaeTBK7dp305SukI2GiwQCabmDv7mIt3ae4dI/txirlZh27m7SPTOVLU4DWWbjQNLUG6dtaLE707BwXb97ku6E0U7EIuqHj7RZw4ilWLfivvQMeWq8oAI7Q8KT1eJ248OUHQcPAjMUZHR5mcXKcKwEdXeoqMQAtmMrmqSw/Znc3yz42th8eBRrOKSlA8LnE9wTN9Qh6LoO6YBhIAUlTJzlzhtlLF7l0ZobpcIoIAqEJhJDYQTu1nC34nOK6eK0Wnoz48rJtPHnJ1+Mh4uemuLBwlQszc8Q1A7dt4zq+AykQJQGU9gW7gPAXIHTQdZUFehcVmTnDhT/8A9fKBf5a2mZ7Z10FQ2HoKhl40oqkslyJGt0vFAhpnQWrffWfOz4UNgaipBYuMV8rc6u0Q/FHh9VinlardWrDG/xKRIW3rjmrSO8pq9DHM5y9/R3/rDnY6UHaP/w3z1efQY8SZOBUXztBljT4lYoMTjLleYbOwOQ4129/jx2L0h6IE50YJ7e5Se2gQqNWxbEssJonwkgG/ZLubvY+uu7xrUEItR7p40IIhsZG+TYSITYxzsXf3+bvL9ZYWVsju/qM8toLrOzGa6uQFaYKEt4nVoD22oSPBu+ZRLfIORag9e8luo+6TjqV5OZgkrHzF5i4lOPCizVe3FtiQw+xUapS2N+jiovrD3CccYyTr/YdE9ZkFOe1H/s73puoJIiRKPC9ovTXSXU9L6lvhYGZWITBmSkWEwl2MXm6V+fHpxv8ff+AJzQ51DxVP3TQwvsxo8FHi69ntetv4jP1XBY4XdLDtXF8IPxe83QcqDZxrZb6voiE0KLho+BgAsPBAMNjGWb3KoxkxmlEkuQweSEV4N9GOoLzgdkbH7f2bs4W4L4eSg6shUJ4sRieX+4qbdSrUKtAw5LO3aOszo4d3bZlo+X3sTZ2aFarGMMpovNn0VIDb47vh5SY0EkIgzCGj+yOHw2Nj1p8j68rc5WLlTg+mcQcGiaYThGKJwiGw+iOg5PdwFp5Qi27ieUDl3dNVaXAWgPr+TrbT55RDRsEdi6TunKR4cQg4UgETAMabThoEGq2CaFhSqj8CzOBcWIFSNOWPi59FQik0+jTsxgXLxGYnSUxNkE6nSaTiDEUjRBrtXHuLVOqO6xuFXnpNqjLTXzL15UC5L3RaO2XyS494OHuFqX7d5lYuMy3M+e5NDNLOJ1EcwVsFTBKNXTbUdkCp1tuHy/aGifeeemnUg+hEGI4gzF/mdiVa2SuXGVkZoapzAgTAwnGwkGGw2FiVgv30GHnzk9EzceUWm2qyorfERLlQnRdpcCD4j5PV1d4nF1hcGON/Jk5crPnSA8PkdFDhMqHFF+skTusUhUejiNULDquGCdWgFp8kPDZc5jXbxD/9jvGLs1zdXycq4MJLsViTASDDOoaIV3H0AROOMpOaID9QIKldo0NPF8B78gKnocuawOh08RhvVnh57VDnuU2uPP4AZlIjAkjQgqdVqPJy0qRnNam3bPrykNPXQG+CMnnjU8QWLxJ8vYfmP3mOlfGx7gVi3HZ0JgNBkjIAqcrQQNME88IktIDBPxFv2+CQjcwQyF0I0zLrVJpWerKVUrIcDiEwSBBhGFQ1Vz2aNPqueNxYJdxjM+85u19bk4zDIJj4xgLN4h//4/MLS5ye2Kc7yMhLkfCpGQ8lJXeG/eQoF3QxsP2XLXzH5JOW8DFcxyFC7rSBCyghI0paRJbw9U0VSm2ez53HNbI4NjiZ1U5QDSGcf4i8cWbTF6+zLWxUb6PhrkhIK37O+u6OM0Wot5E2A7UmpDN49UbavGq8vugBjoKlyObmoZuaAi3Q4q0PI8WLq0uYXrCBopxbBZXPnRzfCaDefUao9cWuD42xnfREFdCwaPFS0txCyW0jV3EyxzsV6FSo/1qi1a+iC0V4PN70jQ+NHdV5XmeMkDXddAlJ9it/z+SGTOO/1EJrjUV+PSxMRX8JqamWIjHWNA1hqWCZC1vtfB29hEPn2E/XKX4/CUHhX2KtQq1apW9/RLP2jXls1KZftlyvBn4UU15k3r6OnwqdzkBVWocO+pL9esCLTVMaHyS1NgYM0Mp5mNRpkMGhqzebBu2C4i//Uz7335k9/5PPNrb4pFV4UWzSsluUfUcdqwyec1FR8OQjZBfWMW/rvvfXLDXdwswDLR0msjICCMDA5wJBhkzdYJ+6erUG2jPs7TuPmLnzjIPnq3w7808S8Ji3W1Qkz4rBLasCXSd4EeSkqfBCxvvfdcnHo96MoYBiQSRZIrReJyJYIgB2dHpBvmDBtqzLAcrz3mQ3+TPVoG/UCLrOjS6kz5yeO81J9j/Lvgp4QBdh1CIUCTCUFDmc6Fu4HaDY72Bl9ujuLPLQ+uAvwVaPLc9HLVIDVOymNICHLsTuCWU7nPv73QVoIEnBIauEzcM4oZQPnxkxraN3WqxbzV42aqz2W7gyGjtxxFVLMsIrpjgTi9Q9gj/D7WtYo7r1xo9g/fBVMQv+rRMb20bzbExNQ9TNil63zcNvFCAuq5RtC1qrqUIEFMYqlBRbJDrdi7pXrrZKZV7EaOUbq3Rto9No/VNAV5PYYXj4jYOceuHuO22/17PrkTDiKEkWnJAkZnqHbk401DoURU4SmkaRjxBIJkiEE9gBoPoXeQob6qAUwOnfki71cLuQKeeSX1CBbwhsmtTLtMql2hYlmzfvYnoEjHEhWkS8+dIZ4ZVO8u1bdqNhmJuHVt2dhxcyRtMz2DMnSWaThMzTULde3TJ04MaTqmCZVkK9rqfJQZ4HXhxtMR2G/aLHO7uUi6VqTSbtI1IJwjKicdCiKvnGTrY4+z2C87U9ynmt44mLw1dGCbu9DTBxZsMfHODidFRxg2duHLxDtjyDpuwU6SxU6DcPKSC22mM+ubofdog6L1JgFQq1HNb7ORy7FUqtOPRjhlJDl8CpdE0wzeusFgukA+ZHD59zGaxiGU7iibTU0MY8/Okbn7L2Yu/YyGd4nzQJKG4Q7/9Xa7BZp7mdp69wxoF4dA6fol/ygrwOoWL11WA1aS+lSW78oRXF85RTg2QCYVxXVnhSTfXiU9Psvgvf0ScnyP4dIWlzRzbjSaHoRDmUIbE1BRnpqe4MZLh94kY86EgETmGLKAOqhjr27TXNinu5sk2a+wIm5bjNwN9DsH71GnQ6+HrWoUCW8vLrE6dITs1yczUFAFdV9Fdlq56IMDI1BkWRzKYc7NM5gtkD5tUJIeQSDAYjzMVDqqFz4eDDAUkzwtes4X+IgcPVznY2CRbLbPePqQkZBjsywERjqcAaQUydfm+7lSrFB8s8ySd5MHcHJMDSc4NxDunP6QlOI7CChIs3Zqc4FwmQ8l2OJSbqOtEhCApNFJCI+ojyba893YB/c5jqneWeZbL8qhdZd1t0vTUARlFeHai0qdWgJRuk0Ny/K6Dnd8he/8+P0yeIRUMEru+wEQ6hSHTnb9TUmEdwGQw7XP08nX5iTfORTZbmDtFuPsz7p1H5J6ucre8zT2vxp4snvt4WNL45VXY68mUXr3kxz/9K2a9RrLZJHTrpiIru+K8NYDMAm9BHuymhf50A/76CPeHB+SWf2Ipv8V/1vdY8qrUcBRu8E7Z90/MCbp+qtJV7W+RW1nhbtsmKdHrQYUbV6+SyWQUdy+5OsXfH6FYH+TIUx7NFlTrGK+2Yfkptf9ZYvOnFZbym/ylUeCBU6PgdZqdeo/1/GqOygrkoYbOfphmgMnRMb45f4F/Wljk1vxlLs6eI5EZhkQcTL0DcCRfUG9AqQq5PLzcxn76ktLaOquvXnJ3f5v/ONxj2amScyzFHHXG6h8Q0k6qAFUFCK0TFP0ewVAgzOLMWW6d/x3X5y4yNTZOOpkkGA4S1HRE28Gt1XGKB1ibOxy+2qSwvslGucij5gH33BpLdpWC21Sz0nsm530ph6UTRoCRaIKZeFJdU9EOThgUJgFZ3Fltmo0G5VqVfPWAjfoB661DFe3ztKn0tDP7U//1QQFCdnCFht1hLdVrASADjBFmWAQZEAYBhDrQZHmOWugejgI5MtJbMtX5MzF89+pvHXiaFqD5nfi30pV8LeQrw+wZQA4oM7sMce8qdD7FzvfFBTRJjvg0mmxUdIJkl7N/a0nqzw4dJnpATj9S3SeNAZpfHh/VbcdcTS+9/SlF69d/jHTOAklrePfNj44Q+Tv+uZhBrd//MvOhm35eSpT+nxP83Av8kAi+chF85WJ8QdbaFxGfewKfW/4XfRL1lgcnqawAAAAASUVORK5CYII=", "kick": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAADNElEQVR4nO2bS0hUYRTH//fM3Dv4HPNRaJGPTCfB1B60KrBFtIqKKKIgamVEhG3KkqigtLRCKALbGNQiDNsE1a5V7czIirFmTMUwlAy1prmPuTEjQqXfKDnPe/rBbOZxzzn/7/J95/4PIzmdThOMITCHwBwCcwjMITCHwBwCcwjMITCHwBwCcwjMITCHwBwCc+yRvFhNp4KcrbZZ7490GuitUxd8HUeBhA2PHUgplITfGWrX4W7QYLk7QMmTsP5R+OI/3zPgPrP44hNOAHmJhHVdClJLxcV/6TLwvl4FIuRjERIEewZQ81BBeoU4pdGnBnqPqjADkYtLSABsqUD1Awcyq8XpfH0ewJsjKkw9srEpspf7hwQcQNV9B7I2iVP59jKA1wf9CPijEB9xRJKBtR0KsreI05joCaBnvx+GLzo5EOKEZAMq2xXkbpt9bM4w9S6AV3tU6JPRy4MQByQCKm4qWLpDXPwPj4nu3Sq08eiOLQhxwNUqI3+vuHjfoInuXX6oo9Gf2RBiTNklGcsPiRtQ/0hw5f34ORybgRUhhqxqlLGyTly8Oja98r7+2E3rKFaBiuvtoVc4Pl7Q8L0vtqNKikWQ7FoKrf58FB6XQQqsJ4CSK+7tfyetTELRyfmFslQn+DdFJ+xIK1+YYJYUgBSgok0J9QoxiYc4MXhbhz4x94bn3EhYcTiiXk1iCeC9oqGvUYO3RfxoV3pODjlDlhPA26zBe3W68KE7uvDYs6UDrhbZWgJ4mv5cdVMD3A1irzBvuw3Ldopb5qQSwNOkob9Vn9PoGH1iCH9X3ixDzpKSW4CxZ8acxc/Qd1YTmh1Bk3T1RTm5BdAnwn/uGzAxcEssUMEBG7I3k7X7gE/XtbBPgK4bSsg+s6wAhg/4cF7s9acWSyg5JVtXgBnPf/yF2PMuPGZHRiVZV4Ag7tMaTMGhINmBNW1yyE+0rABTbwMYviveEDOrKKypkvQCBPFc1sOaoSUNctjZYdILoI2b8DSJ7wJbCuC6plhXgCDDHTome8UbYk4tIX/f4jcD6f//BZhDYA6BOQTmEJhDYA6BOQTmEJhDYA6BOQTmEJhDYA7FO4F48wvOIuBp+CZSdAAAAABJRU5ErkJggg==", "facebook": "data:image/png;base64,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", "soop": "data:image/png;base64,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", "obs_icon": "data:image/png;base64,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"};

  PLATFORM_LOGOS.mylive='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAACAAAAAgACAYAAACyp9MwAAEAAElEQVR4nOzdBZhd5bXG8Xfvo+Mad/dgwakApUVaKFKKF/fgUIq3hWLFpYW2QJGgxV1bCsVdQohPJhOZjMvxve+z9wQqtzKBJHvO+f6/PsOE3tuyus/ky8xZ77eWteX1z7gCAABAQXNdV67ryLZtdS6a43520/lOLpW0nXTS+uL/ZfXHF38PAAAAAAAAAOi7vng/94v3dB3vww64KAAAAKxPfhDg7x8AAAAAAAAAgMIRDroAAAAArHs9EdCeMKjrOJaTToXcbPpf/1+4/Q8AAAAAAAAA+eFf38/1L/8zAQAAAMAAPfP9e278ezf/nUzanwYAAAAAAAAAACgYNhMAAAAATAkAeGP/vV85Ocn11kEBAAAAAAAAAAoJEwAAAAAM4M/3d1cHAbwAAAAAAAAAAACg0LgEAAAAAExhubL8KQAAAAAAAAAAgAJEAAAAAMCsOQCSZfV8BgAAAAAAAAAUFIsJAAAAAMZwve4/AQAAAAAAAAAAKFAEAAAAAIxhyfVu/3+ZAWUSAAAAAAAAAAAUEgIAAAAAxrC8CIAs25LskGS5QRcEAAAAAAAAAFiLCAAAAAAYxAsA+EEA2/s2kAkAAAAAAAAAAFBICAAAAAAYxWv60/gHAAAAAAAAgEJEAAAAAMAwruvK+5f8DwAAAAAAAABAoSAAAAAAYBjLcmW5TAIAAAAAAAAAgEJDAAAAAMA4Fpf/AQAAAAAAAKAAEQAAAAAwkTcAAAAAAAAAAABQUAgAAAAAAAAAAAAAAABQAAgAAAAAAAAAAAAAAABQAAgAAAAAAAAAAAAAAABQAAgAAAAAAAAAAAAAAABQAAgAAAAAAAAAAAAAAABQAAgAAAAAAAAAAAAAAABQAAgAAAAAAAAAAAAAAABQAAgAAAAAAAAAAAAAAABQAAgAAAAAGMkNugAAAAAAAAAAwFpGAAAAAMBIBAAAAAAAAAAAoNAQAAAAAAAAAAAAAAAAoAAQAAAAADCSFXQBAAAAAAAAAIC1jAAAAAAAAAAAAAAAAAAFgAAAAACAkdygCwAAAAAAAAAArGUEAAAAAIzECgAAAAAAAAAAKDQEAAAAAEzEAAAAAAAAAAAAKDgEAAAAAAAAAAAAAAAAKAAEAAAAAAAAAAAAAAAAKAAEAAAAAEzECgAAAAAAAAAAKDgEAAAAAExkBV0AAAAAAAAAAGBtIwAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAAAAAAAAAAAAAEABIAAAAABgIjfoAgAAAAAAAAAAaxsBAAAAABNZQRcAAAAAAAAAAFjbCAAAAAAAAAAAAAAAAFAACAAAAAAAAAAAAAAAAFAACAAAAACYiBUAAAAAAAAAAFBwCAAAAAAYyQ26AAAAAAAAAADAWkYAAAAAwEiMAAAAAAAAAACAQkMAAAAAAAAAAAAAAACAAkAAAAAAwEisAAAAAAAAAACAQkMAAAAAAAAAAAAAAACAAkAAAAAAwEhW0AUAAAAAAAAAANYyAgAAAABGIgAAAAAAAAAAAIWGAAAAAAAAAAAAAAAAAAWAAAAAAAAAAAAAAAAAAAWAAAAAAAAAAAAAAAAAAAWAAAAAAAAAAAAAAAAAAAWAAAAAAAAAAAAAAAAAAAWAAAAAAAAAAAAAAAAAAAWAAAAAAAAAAAAAAAAAAAWAAAAAAAAAAAAAAAAAAAWAAAAAAAAAAAAAAAAAAAWAAAAAAAAAAAAAAAAAAAWAAAAAAAAAAAAAAAAAAAWAAAAAAAAAAAAAAAAAAAWAAAAAAAAAAAAAAAAAAAWAAAAAAAAAAAAAAAAAAAWAAAAAAAAAAAAAAAAAAAWAAAAAAAAAAAAAAAAAAAWAAAAAAAAAAAAAAAAAAAWAAAAAAAAAAAAAAAAAAAWAAAAAAICR3KALAAAAAAAAAACsZQQAAAAAjEQAAAAAAAAAAAAKDQEAAAAAAAAAAAAAAAAK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AAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAgOPbl0/nWlxePu775XLv/QAAAAAAAAAAf+AYY4y1+PkCAAAAAAAAAB6QKwAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAgAABAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAACAAAEAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAAAAAECAAAAAAAAAAAIEAAAAAAAAAAAQIAAAAAAAAAAAAACBAAAAAAAAAAAECAAAAAAAAAAAIAAAQAAAAAAAAAABAgAAAAAAAAAACBAAAAAAAAAAAAAAQIAAAAAAAAAAAgQAAAAAAAAAABAgAAAAAAAAAAAAAIEAAAAAAAAAAAQcMw5b4v1HvfeDQAAAAAAAADwW9a8fz3HGPutABj7bv4PAAAAAAAAAA9m7Pu2Zv/H/vR8G/yPYf4PAAAAAAAAAI9mzfvX7P8Yl8PkHwAAAAAAAAAe2Jr9H/75DwAAAAAAAACPbc3+j++vn8/14fL8Yd/Gfu89AQAAAAB/yZzrLtDh+s//3DzPbc7pewAAUDbP7f3r9TzO6+v569fAcB0AAAAAAETMec7L08sYx8vYttv53723xL+yznvXs+/rIHjO830O578AAFvWnPN8u54/AOICzjr4Yf9GAAAAAElFTkSuQmCC';

  function getPlatformLogoSrc(plat) {
    const p = (plat || '').toLowerCase().trim();
    return PLATFORM_LOGOS[p] || `assets/platforms/${p}.png`;
  }

  function getPlatformIconHtml(plat, size = 20, extraStyle = '') {
    const p = (plat || '').toLowerCase().trim();
    const src = getPlatformLogoSrc(p);
    return `<img src="${src}" class="plat-icon plat-icon-${p}" alt="${p}" style="width:${size}px; height:${size}px; object-fit:contain; vertical-align:middle; display:inline-block; flex-shrink:0; pointer-events:none; ${extraStyle}" onerror="this.src='assets/platforms/${p}.png'; this.onerror=function(){this.style.display='none';};">`;
  }

  const MUSIC_LOGOS = {
    spotify: `<svg viewBox="0 0 24 24" fill="#1ED760" style="width:14px;height:14px;vertical-align:middle;display:inline-block;flex-shrink:0;"><path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/></svg>`,
    ytmusic: `<svg viewBox="0 0 24 24" style="width:14px;height:14px;vertical-align:middle;display:inline-block;flex-shrink:0;"><circle cx="12" cy="12" r="12" fill="#FF0000"/><circle cx="12" cy="12" r="7" fill="none" stroke="#FFFFFF" stroke-width="2"/><polygon points="10,8 16,12 10,16" fill="#FFFFFF"/></svg>`,
    desktop_player: `<svg viewBox="0 0 24 24" fill="#60A5FA" style="width:14px;height:14px;vertical-align:middle;display:inline-block;flex-shrink:0;"><path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/></svg>`
  };

  function updateAllViewerTickers(container, w) {
    if (!container || !w) return;
    if(window.BP3ViewerPreview && !window.BP3ViewerPreview.active(w)){window.BP3ViewerPreview.render(container,w);return;}
    const count = window.BP3ViewerPreview?.count(w) ?? 0;
    const totalTicker = container.querySelector('.viewer-total .viewer-ticker');
    if (totalTicker) {
      updateNumberTicker(totalTicker, count);
    }
    const platWeights = {
      youtube: 0.45,
      twitch: 0.30,
      tiktok: 0.15,
      kick: 0.10,
      facebook: 0.08,
      soop: 0.05
    };
    const activePlats = ['youtube','twitch','tiktok','kick','soop','mylive'];
    let sumWeight = 0;
    activePlats.forEach(p => { sumWeight += (platWeights[p] || 0.1); });
    if (sumWeight <= 0) sumWeight = 1;

    activePlats.forEach(p => {
      const chipTicker = container.querySelector(`.viewer-chip[data-platform="${p}"] .viewer-ticker`);
      if (chipTicker) {
        const platShare = Math.round(count * ((platWeights[p] || 0.1) / sumWeight));
        updateNumberTicker(chipTicker, platShare);
      }
    });
  }


  const ComposerDemoManager = {
    timers: {},
    chatMockPool: [
      { user: 'Krit_Live', text: 'สวัสดีทุกคนในไลฟ์สตรีม ภาพคมชัดมากครับ! 🎮', platform: 'youtube', color: '#ef4444' },
      { user: 'Zack_Twitch', text: 'สตรีมภาพสวย 60fps ลื่นไหลดีมากครับ 🔥', platform: 'twitch', color: '#a855f7' },
      { user: 'น้องมุก_ยิ้มสดใส', text: 'ส่งดาว 100 ดวง เป็นกำลังใจให้สตรีมเมอร์นะคะ ⭐', platform: 'facebook', color: '#3b82f6' },
      { user: 'Boy_Gamer', text: 'วันนี้เล่นเกมเนื้อเรื่องสนุกสุดๆ เลยครับ 🚀', platform: 'kick', color: '#22c55e' },
      { user: 'Aom_Channel', text: 'ยินดีต้อนรับเพื่อนๆ ทุกคนที่แวะเข้ามาพูดคุยกันน้า 💖', platform: 'tiktok', color: '#ec4899' },
      { user: 'Captain_Soop', text: 'ภาพแสงและสีในเกมวันนี้ปรับได้สวยงามมากครับ ✨', platform: 'soop', color: '#06b6d4' }
    ],
    charMockPool: [
      'สวัสดีครับทุกคน! วันนี้ยินดีต้อนรับสู่ไลฟ์สตรีมนะครับ 🎮',
      'ขอบคุณทุกคนที่เข้ามาร่วมพูดคุยและส่งกำลังใจให้กันนะครับ ✨',
      'ขอให้ทุกคนมีความสุขและสนุกกับการรับชมสตรีมวันนี้น้า 💖',
      'อย่าลืมกดแชร์และคอมเมนต์พูดคุยกันได้ตลอดเลยนะครับ! 🚀'
    ],
    danmakuPool: [
      '🚀 สตรีมเมอร์สู้ๆ นะครับ!',
      '🎮 ภาพคมชัด 60fps ลื่นมาก',
      '💖 สวัสดีรอบห้องสตรีมจ้า',
      '🔥 คอมเมนต์ด่วน ดันมากุวิ่งบนจอสด',
      '⭐ ยินดีต้อนรับเพื่อนๆ ทุกคนครับ',
      '🎉 สตรีมสนุกมากครับวันนี้'
    ],

    // Default Chat Simulation with full scoped theme & box style support
    sendChatMsg(w, customText = null) {
      const feed = document.getElementById(`widget-chat-feed-${w.id}`);
      if (!feed) return;
      const msg = customText ? { user: 'สตรีมเมอร์', text: customText, platform: 'youtube', color: '#38bdf8' } : this.chatMockPool[Math.floor(Math.random() * this.chatMockPool.length)];
      
      const theme = w.chatTheme || 'default';
      const isTheme = w.chatMode === 'theme';
      const fFam = w.fontFamily || 'Kanit';
      const fSz = w.fontSize || 15;
      const fClr = w.fontColor || '#ffffff';
      const fWeight = w.fontWeight || '600';
      const uClr = w.usernameColor || '#38bdf8';
      const hex = w.bgColor || '#1e1f22';
      const r = parseInt(hex.slice(1, 3), 16) || 30;
      const g = parseInt(hex.slice(3, 5), 16) || 31;
      const b = parseInt(hex.slice(5, 7), 16) || 34;
      const bgOp = w.bgOpacity ?? 0.85;
      const radius = w.boxRadius ?? 8;
      const pad = w.boxPadding ?? 6;
      const boxEnabled = w.boxEnabled !== false;

      let boxStyle = '';
      if (isTheme) {
        boxStyle = 'background:transparent;';
      } else if (boxEnabled) {
        boxStyle = `background:rgba(${r}, ${g}, ${b}, ${bgOp}); border-radius:${radius}px; padding:${pad}px 12px;`;
        if (w.boxWidth === 'full') boxStyle += ' width:100%;';
        if (w.boxBorder) boxStyle += ` border:${w.boxBorderWidth || 2}px solid ${w.boxBorderColor || 'rgba(255,255,255,0.2)'};`;
        if (w.boxGlow) boxStyle += ` box-shadow:0 0 12px ${w.boxGlowColor || '#a855f7'};`;
        else if (w.boxShadow) boxStyle += ' box-shadow:0 4px 12px rgba(0,0,0,0.3);';
      } else {
        boxStyle = 'background:transparent; padding:2px 0;';
      }

      const strokeCss = w.textStroke ? `-webkit-text-stroke:${w.textStrokeWidth || 1.5}px ${w.strokeColor || '#000000'}; paint-order:stroke fill;` : '';
      const shadowCss = w.textShadow ? `text-shadow:0 1px ${w.textShadowBlur ?? 3}px ${w.textShadowColor || '#000000'};` : '';
      const alignCss = w.align === 'center' ? 'center' : (w.align === 'right' ? 'flex-end' : 'flex-start');

      const item = document.createElement('div');
      item.className = `cwc-msg-item msg chat-line theme-${theme}`;
      item.style.cssText = `align-self:${alignCss}; ${boxStyle} animation:cwc-item-pop 0.25s ease-out; margin-bottom:4px;`;
      item.innerHTML = `
        <div class="msg-bg"></div>
        ${getPlatformIconHtml(msg.platform, 16, 'margin-right:6px;')}
        <span class="author" style="color:${uClr}; font-weight:700; margin-right:6px;">${msg.user}:</span>
        <span class="text" style="font-family:'${fFam}',sans-serif; font-size:${fSz}px; font-weight:${fWeight}; color:${fClr}; ${strokeCss} ${shadowCss}">${msg.text}</span>
      `;
      feed.appendChild(item);
      feed.scrollTop = feed.scrollHeight;

      while (feed.children.length > 12) {
        feed.removeChild(feed.children[0]);
      }
    },

    toggleChatLoop(w, btn) {
      if (this.timers[w.id]) {
        clearInterval(this.timers[w.id]);
        delete this.timers[w.id];
        if (btn) {
          btn.innerHTML = '▶ เล่นจำลองแชทสด';
          btn.classList.remove('active');
        }
      } else {
        this.sendChatMsg(w);
        this.timers[w.id] = setInterval(() => this.sendChatMsg(w), 1600);
        if (btn) {
          btn.innerHTML = '⏹ หยุดจำลองแชท';
          btn.classList.add('active');
        }
      }
    },

    // Danmaku Simulation
    sendDanmakuMsg(w, customText = null) {
      const feed = document.getElementById(`widget-danmaku-feed-${w.id}`);
      if (!feed) return;
      const txt = customText || this.danmakuPool[Math.floor(Math.random() * this.danmakuPool.length)];
      const bullet = document.createElement('div');
      bullet.className = 'danmaku-bullet-item';

      const zone = w.slider_zone || 'middle';
      let minY = 0.05, maxY = 0.90;
      if (zone === 'top') { minY = 0.05; maxY = 0.45; }
      else if (zone === 'middle') { minY = 0.25; maxY = 0.70; }
      else if (zone === 'bottom') { minY = 0.55; maxY = 0.92; }

      const topPct = (minY + Math.random() * (maxY - minY)) * 100;
      const fsz = w.fontSize || 24;
      const clr = w.fontColor || '#ffffff';
      const stroke = w.textStroke === true ? `-webkit-text-stroke:${w.textStrokeWidth || 1.5}px ${w.strokeColor || '#000000'}; paint-order:stroke fill;` : '';
      const shadow = w.textShadow !== false ? `filter:drop-shadow(0 2px 4px ${w.textShadowColor || 'rgba(0,0,0,0.6)'});` : '';
      const dur = w.speed || 6;

      bullet.style.cssText = `top:${topPct}%; left:0; font-size:${fsz}px; color:${clr}; opacity:${w.opacity ?? 1}; ${stroke} ${shadow} animation:danmakuBulletRun ${dur}s linear forwards;`;
      bullet.textContent = txt;
      feed.appendChild(bullet);

      setTimeout(() => bullet.remove(), dur * 1000 + 500);
    },

    toggleDanmakuLoop(w, btn) {
      if (this.timers[w.id]) {
        clearInterval(this.timers[w.id]);
        delete this.timers[w.id];
        if (btn) {
          btn.innerHTML = '▶ เล่นกระสุนดันมากุสด';
          btn.classList.remove('active');
        }
      } else {
        this.sendDanmakuMsg(w);
        this.timers[w.id] = setInterval(() => this.sendDanmakuMsg(w), 1200);
        if (btn) {
          btn.innerHTML = '⏹ หยุดกระสุนดันมากุ';
          btn.classList.add('active');
        }
      }
    },

    // Balloon Simulation
    sendBalloonMsg(w) {
      const feed = document.getElementById(`widget-balloon-feed-${w.id}`);
      if (!feed) return;
      const msg = this.chatMockPool[Math.floor(Math.random() * this.chatMockPool.length)];
      const bubble = document.createElement('div');
      const bg = w.balloonBg || '#ffffff';
      const clr = w.balloonTextColor || '#0f172a';
      const radius = w.balloonRadius ?? 14;
      const fsz = w.fontSize || 15;
      const op = w.balloonOpacity ?? 0.95;

      bubble.style.cssText = `background:${bg}; color:${clr}; padding:10px 16px; border-radius:${radius}px; font-weight:600; font-size:${fsz}px; box-shadow:0 6px 18px rgba(0,0,0,0.35); position:relative; margin-bottom:12px; max-width:90%; opacity:${op}; animation:cwc-item-pop 0.25s ease-out;`;
      bubble.innerHTML = `
        <div style="font-weight:700; font-size:12px; color:${msg.color}; margin-bottom:3px;">${msg.user}:</div>
        <div>${msg.text}</div>
        <svg style="position:absolute; bottom:-11px; left:22px; width:18px; height:12px; fill:${bg};" viewBox="0 0 18 12">
          <path d="M0 0 L18 0 L6 12 Z"/>
        </svg>
      `;
      feed.appendChild(bubble);
      feed.scrollTop = feed.scrollHeight;
      while (feed.children.length > 8) {
        feed.removeChild(feed.children[0]);
      }
    },

    // Character Speech Simulation
    triggerCharacterTalk(w) {
      const textEl = document.getElementById(`widget-char-text-${w.id}`);
      const avatarEl = document.getElementById(`widget-char-avatar-${w.id}`);
      if (!textEl) return;
      const txt = this.charMockPool[Math.floor(Math.random() * this.charMockPool.length)];
      textEl.textContent = txt;
      if (avatarEl) {
        avatarEl.style.transform = 'scale(1.08) translateY(-4px)';
        setTimeout(() => avatarEl.style.transform = 'none', 300);
      }
    },

    // Goal Simulation
    triggerGoalPlus(w) {
      w.goalCurrent = (w.goalCurrent || 0) + 50;
      renderCanvasWidgets();
      saveState();
      renderWidgetCustomizerPanel(w.id);
      if (window.showToast) window.showToast(`🎉 เป้าหมายยอดเพิ่มขึ้นเป็น ${w.goalCurrent} แล้ว`);
    },

    triggerGoalReset(w) {
      w.goalCurrent = 0;
      renderCanvasWidgets();
      saveState();
      renderWidgetCustomizerPanel(w.id);
    },

    // Viewer Simulation with Smooth Column Rolling Ticker
    triggerViewerRandom(w) {
      window.BP3ViewerPreview?.begin(w);
      const target = Math.floor(800 + Math.random() * 3200);
      window.BP3ViewerPreview?.set(w,target);
      const el = document.getElementById(`widget-${w.id}`);
      if (el) {
        updateAllViewerTickers(el, w);
      }
      renderLayersList();
    },

    triggerViewerAdd(w, delta = 50) {
      window.BP3ViewerPreview?.begin(w);
      const current = window.BP3ViewerPreview?.count(w) ?? 0;
      const target = current + delta;
      window.BP3ViewerPreview?.set(w,target);
      const el = document.getElementById(`widget-${w.id}`);
      if (el) {
        updateAllViewerTickers(el, w);
      }
      renderLayersList();
    },

    triggerViewerSub(w, delta = 30) {
      window.BP3ViewerPreview?.begin(w);
      const current = window.BP3ViewerPreview?.count(w) ?? 0;
      const target = Math.max(0, current - delta);
      window.BP3ViewerPreview?.set(w,target);
      const el = document.getElementById(`widget-${w.id}`);
      if (el) {
        updateAllViewerTickers(el, w);
      }
      renderLayersList();
    },

    // Temporary preview events do not change live poll or participant state.
    triggerAskVote(w) {
      if (window._liveAskState?.active) { window.alert('กำลังมีโพลจริงอยู่ กรุณาปิดโพลก่อนทดสอบ'); return; }
      clearTimeout(this.askDemoTimer);
      window.BP3_BUS?.emit('ASK_UPDATE',{demo:true,active:true,phase:'voting',question:'[DEMO] ตัวอย่างโพล',choices:[{label:'A',text:'ตัวเลือกที่ 1',votes:3,pct:60},{label:'B',text:'ตัวเลือกที่ 2',votes:2,pct:40}],totalVotes:5,remainingSec:10});
      this.askDemoTimer=setTimeout(()=>{if(!window._liveAskState?.active)window.BP3_BUS?.emit('ASK_UPDATE',{demo:true,active:false,phase:'idle'});},10000);
    },
    triggerGiveawayDraw(w) {
      if (window._liveGwState?.active) { window.alert('กำลังมีกิจกรรมจริงอยู่ กรุณาปิดกิจกรรมก่อนทดสอบ'); return; }
      clearTimeout(this.giveawayDemoTimer);
      window.BP3_BUS?.emit('GIVEAWAY_UPDATE',{demo:true,active:true,phase:'winner',winner:'[DEMO] ตัวอย่างผู้ชม',candidates:['[DEMO] ตัวอย่างผู้ชม','[DEMO] ผู้ชม 2'],style:'gachapon',drawId:'demo-'+Date.now(),holdDuration:5});
      this.giveawayDemoTimer=setTimeout(()=>{if(!window._liveGwState?.active)window.BP3_BUS?.emit('GIVEAWAY_UPDATE',{demo:true,active:false});},12000);
    },

    // Emote Party Simulation
    triggerEmoteParty(w) {
      const container = document.getElementById(`widget-emote-party-${w.id}`) || document.getElementById(`widget-${w.id}`);
      if (!container) return;
      const emotes = ['🔥', '🎉', '💖', '⭐', '🚀', '👑', '🎮', '✨', '👏', '🥳', '😎', '💯'];
      const maxEmotes = w.epMaxEmotes || 15;
      const anim = w.epAnimation || 'float';
      const dur = w.epDuration || 4;
      const size = w.epEmoteSize || 48;

      for (let i = 0; i < maxEmotes; i++) {
        setTimeout(() => {
          const em = document.createElement('div');
          const emo = emotes[Math.floor(Math.random() * emotes.length)];
          const left = Math.random() * 85 + 5;
          em.style.cssText = `position: absolute; left: ${left}%; bottom: 0; font-size: ${size}px; pointer-events: none; user-select: none; animation: emoteFloatUp ${dur}s ease-out forwards; z-index: 100;`;
          em.textContent = emo;
          container.appendChild(em);
          setTimeout(() => em.remove(), dur * 1000 + 200);
        }, i * 120);
      }
    },

    // Refresh the actual Windows media session instead of fabricating a song.
    triggerNowPlayingNext(w) {
      window.BP3Live?.refreshNowPlaying?.();
    }

  };

  Object.assign(ComposerDemoManager,{
    sendChatMsg(w,text=null){window.sendSingleSimulatedChat?.(text);},
    sendDanmakuMsg(w,text=null){window.sendSingleSimulatedChat?.(text);},
    sendBalloonMsg(w){window.sendSingleSimulatedChat?.();},
    triggerCharacterTalk(w){window.sendSingleSimulatedChat?.();},
    toggleChatLoop(w,btn){window.toggleSimulateLiveChats?.();if(btn)btn.textContent=document.getElementById('lblSimChat')?.textContent || 'จำลองแชท';},
    toggleDanmakuLoop(w,btn){this.toggleChatLoop(w,btn);}
  });

  // ═══ V2/V3 Universal Schema Migration & Dual-Key Normalizer ═══
  // Helper to identify widgets that are forced to cover the full canvas (1920x1080)
  function isFullscreenWidget(w) {
    if (!w) return false;
    return !!(
      w.isDanmaku ||
      w.chatMode === 'danmaku' ||
      w.isFullScreen ||
      w.is_fullscreen ||
      w.type === 'ask' ||
      w.type === 'giveaway' ||
      w.type === 'replie' ||
      w.type === 'emote_party' ||
      w.type === 'randomizer'
    );
  }

  function normalizeWidget(w) {
    if (!w || typeof w !== 'object') return w;
    if (w.type === 'chat' && Object.prototype.hasOwnProperty.call(w, 'appearance_mode')) {
      w.chatMode ??= ({slider:'danmaku',theme2:'theme'})[w.appearance_mode] || w.appearance_mode;
      w.chatTheme ??= w.theme || 'default';
      w.appearance_mode = w.chatMode === 'danmaku' ? 'slider' : w.chatMode;
      w.theme = w.chatTheme;
    }
    if(w.type==='character'){w.type='replie';w.title='Replie';}
    // Standalone character is the legacy full-canvas Replie layer.
    w.opacity = Number(w.opacity ?? w.alpha ?? 1);
    w.hidden = w.hidden ?? (w.enabled === false);

    // Geometry
    if (isFullscreenWidget(w)) {
      w.x = 0;
      w.y = 0;
      w.width = CANVAS_WIDTH;
      w.w = CANVAS_WIDTH;
      w.height = CANVAS_HEIGHT;
      w.h = CANVAS_HEIGHT;
      w.noDrag = true;
      w.noResize = true;
      w.isFullScreen = true;
    } else {
      w.x = parseInt(w.x ?? 0, 10);
      w.y = parseInt(w.y ?? 0, 10);
      const widthVal = w.width ?? w.w ?? 300;
      const heightVal = w.height ?? w.h ?? 180;
      w.width = parseInt(widthVal, 10);
      w.w = w.width;
      w.height = parseInt(heightVal, 10);
      w.h = w.height;
    }

    // Typography & Styling (Dual-Key for V2/V3 compatibility)
    w.fontSize = parseInt(w.fontSize ?? w.font_size ?? 16, 10);
    w.font_size = w.fontSize;
    w.fontColor = w.fontColor || w.font_color || '#ffffff';
    w.font_color = w.fontColor;
    w.fontWeight = w.fontWeight || w.font_weight || '600';
    w.font_weight = w.fontWeight;
    w.fontFamily = w.fontFamily || w.font_family || 'Kanit';
    w.font_family = w.fontFamily;

    // Stroke & Shadow
    w.textStroke = w.textStroke ?? w.text_stroke ?? false;
    w.text_stroke = w.textStroke;
    w.textStrokeWidth = parseInt(w.textStrokeWidth ?? w.text_stroke_width ?? 2, 10);
    w.text_stroke_width = w.textStrokeWidth;
    w.textStrokeColor = w.textStrokeColor || w.text_stroke_color || w.strokeColor || '#000000';
    w.text_stroke_color = w.textStrokeColor;
    w.strokeColor = w.textStrokeColor;
    w.textShadow = w.textShadow ?? w.text_shadow ?? true;
    w.text_shadow = w.textShadow;
    w.textShadowBlur = parseInt(w.textShadowBlur ?? w.text_shadow_blur ?? 3, 10);
    w.text_shadow_blur = w.textShadowBlur;
    w.textShadowColor = w.textShadowColor || w.text_shadow_color || '#000000';
    w.text_shadow_color = w.textShadowColor;

    // Background
    w.bgColor = w.bgColor || w.bg_color || '#1e1f22';
    w.bg_color = w.bgColor;
    w.bgOpacity = parseFloat(w.bgOpacity ?? w.bg_opacity ?? 0.85);
    w.bg_opacity = w.bgOpacity;
    w.boxRadius = parseInt(w.boxRadius ?? w.box_radius ?? 8, 10);
    w.box_radius = w.boxRadius;

    if(w.type==='viewer')w.showIcon=w.showIcon ?? w.viewer_show_icon ?? true;
    // Viewer Widget
    w.viewerTheme = w.viewerTheme || w.viewer_theme || 'default';
    w.viewer_theme = w.viewerTheme;
    w.viewerMode = w.viewerMode || w.viewer_mode || 'both';
    w.viewer_mode = w.viewerMode;
    w.viewerDirection = w.viewerDirection || w.viewer_direction || 'horizontal';
    w.viewer_direction = w.viewerDirection;
    w.viewerAlign = w.viewerAlign || w.viewer_align || 'left';
    w.viewer_align = w.viewerAlign;
    w.iconSize = parseInt(w.iconSize ?? w.viewer_icon_size ?? 20, 10);
    w.viewer_icon_size = w.iconSize;
    w.viewerPlatforms = w.viewerPlatforms || w.viewer_platforms || ['youtube', 'twitch', 'tiktok', 'kick'];
    w.viewer_platforms = w.viewerPlatforms;

    // Chat Widget
    w.chatTheme = w.chatTheme || w.chat_theme || 'default';
    w.chat_theme = w.chatTheme;
    w.chatMode = w.chatMode || w.chat_mode || 'default';
    w.chat_mode = w.chatMode;

    // Chat Animation & Auto-Hide
    w.animation = w.animation || w.anim_in || w.animIn || 'slide';
    w.anim_in = w.animation;
    w.animIn = w.animation;
    w.exitAnimation = w.exitAnimation || w.exit_animation || w.anim_out || w.animOut || 'auto';
    w.exit_animation = w.exitAnimation;
    w.anim_out = w.exitAnimation;
    w.animOut = w.exitAnimation;
    w.autoHide = w.autoHide ?? w.auto_hide ?? false;
    w.auto_hide = w.autoHide;
    w.hideAfter = parseFloat(w.hideAfter ?? w.hide_after ?? 8);
    w.hide_after = w.hideAfter;

    // Chat Container Background Box (Default false: completely transparent, only message boxes visible)
    w.containerBgEnabled = w.containerBgEnabled ?? w.container_bg_enabled ?? false;
    w.container_bg_enabled = w.containerBgEnabled;
    w.containerBgColor = w.containerBgColor || w.container_bg_color || '#0a0e1a';
    w.container_bg_color = w.containerBgColor;
    w.containerBgOpacity = parseFloat(w.containerBgOpacity ?? w.container_bg_opacity ?? 0.75);
    w.container_bg_opacity = w.containerBgOpacity;
    w.containerRadius = parseInt(w.containerRadius ?? w.container_radius ?? 8, 10);
    w.container_radius = w.containerRadius;
    w.containerBorder = w.containerBorder ?? w.container_border ?? false;
    w.container_border = w.containerBorder;
    w.containerBorderWidth = parseInt(w.containerBorderWidth ?? w.container_border_width ?? 1, 10);
    w.container_border_width = w.containerBorderWidth;
    w.containerBorderColor = w.containerBorderColor || w.container_border_color || '#38bdf8';
    w.container_border_color = w.containerBorderColor;

    // Now Playing Widget
    w.npTheme = w.npTheme || w.np_theme || 'custom';
    w.np_theme = w.npTheme;
    w.npStyle = w.npStyle || w.np_style || 'flat';
    w.np_style = w.npStyle;
    w.npSource = w.npSource || w.np_source || 'auto';
    w.np_source = w.npSource;
    w.npSyncMode = w.npSyncMode || w.np_sync_mode || 'browser';w.np_sync_mode=w.npSyncMode;
    w.npShowArt = w.npShowArt ?? w.np_show_art ?? true;
    w.np_show_art = w.npShowArt;
    w.npShowProgress = w.npShowProgress ?? w.np_show_progress ?? true;
    w.np_show_progress = w.npShowProgress;
    w.npScrollTitle = w.npScrollTitle ?? w.np_scroll_title ?? true;
    w.np_scroll_title = w.npScrollTitle;
    w.npBgColor = w.npBgColor || w.np_bg_color || '#1a1a2e';
    w.np_bg_color = w.npBgColor;
    w.npBgOpacity = parseFloat(w.npBgOpacity ?? w.np_bg_opacity ?? 0.85);
    w.np_bg_opacity = w.npBgOpacity;
    w.npRadius = parseInt(w.npRadius ?? w.np_radius ?? 8, 10);
    w.np_radius = w.npRadius;
    w.npArtRadius = parseInt(w.npArtRadius ?? w.np_art_radius ?? 6, 10);
    w.np_art_radius = w.npArtRadius;
    w.npArtSize = parseInt(w.npArtSize ?? w.np_art_size ?? 48, 10);
    w.np_art_size = w.npArtSize;
    w.npAccentColor = w.npAccentColor || w.np_accent_color || '#1db954';
    w.np_accent_color = w.npAccentColor;
    w.npTextColor = w.npTextColor || w.np_text_color || '#ffffff';
    w.np_text_color = w.npTextColor;
    w.npFontSize = parseInt(w.npFontSize ?? w.np_font_size ?? 14, 10);
    w.np_font_size = w.npFontSize;
    w.npArtistFontSize = parseInt(w.npArtistFontSize ?? w.np_artist_font_size ?? 12, 10);
    w.np_artist_font_size = w.npArtistFontSize;
    w.npTimeFontSize = parseInt(w.npTimeFontSize ?? w.np_time_font_size ?? 10, 10);
    w.np_time_font_size = w.npTimeFontSize;

    // Webcam Widget
    w.webcamRatio = w.webcamRatio || w.webcam_ratio || '16:9';
    w.webcam_ratio = w.webcamRatio;
    w.webcamTheme = w.webcamTheme || w.webcam_theme || 'simple-white';
    w.webcam_theme = w.webcamTheme;
    w.borderWidth = parseInt(w.borderWidth ?? w.webcam_border_width ?? 4, 10);
    w.webcam_border_width = w.borderWidth;
    w.borderColor = w.borderColor || w.webcam_border_color || '#6366f1';
    w.webcam_border_color = w.borderColor;

    // Clock Widget
    w.clockMode = w.clockMode || w.clock_mode || (w.clock_style && w.clock_style !== 'none' ? 'style' : 'theme');
    w.clock_mode = w.clockMode;
    w.clockTheme = w.clockTheme || w.clock_theme || 'default';
    w.clock_theme = w.clockTheme;
    w.clockStyle = w.clockStyle || w.clock_style || 'none';
    w.clock_style = w.clockStyle;
    w.clockFormat = w.clockFormat || w.clock_format || 'HH:MM';
    w.clock_format = w.clockFormat;
    w.showDate = w.showDate ?? w.show_date ?? false;
    w.show_date = w.showDate;
    w.dateLang = w.dateLang || w.date_lang || 'th';
    w.date_lang = w.dateLang;
    w.dateFormat = w.dateFormat || w.date_format || 'short';
    w.date_format = w.dateFormat;
    w.dateFontSize = parseInt(w.dateFontSize ?? w.date_font_size ?? 14, 10);
    w.date_font_size = w.dateFontSize;
    w.dateColor = w.dateColor || w.date_color || '#cccccc';
    w.date_color = w.dateColor;
    w.timeColor = w.timeColor || w.time_color || '#ffffff';
    w.time_color = w.timeColor;
    w.themeOpacity = parseFloat(w.themeOpacity ?? w.theme_opacity ?? 1.0);
    w.theme_opacity = w.themeOpacity;
    w.styleOpacity = parseFloat(w.styleOpacity ?? w.style_opacity ?? 1.0);
    w.style_opacity = w.styleOpacity;

    // Media & Browser Source
    w.imageUrl = w.imageUrl || w.image_url || '';
    w.image_url = w.imageUrl;
    w.videoUrl = w.videoUrl || w.video_url || '';
    w.video_url = w.videoUrl;
    w.fitMode = w.fitMode || w.fit_mode || 'cover';
    w.fit_mode = w.fitMode;
    w.url = w.url || '';

    return w;
  }

  // Load saved state from localStorage (with full V2 fallback & migration)
  function loadSavedState() {
    try {
      let saved = localStorage.getItem(STORAGE_KEY);
      if (!saved) {
        saved = localStorage.getItem('composer_pages') || localStorage.getItem('composer_layout');
      }
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          if (parsed[0].widgets) {
            state.pages = parsed.map(p => {
              p.widgets = (p.widgets || []).map(normalizeWidget);
              return p;
            });
            state.activePageId = state.pages[0].id;
          } else {
            state.pages = [{
              id: 'page-1',
              name: 'หน้า 1',
              widgets: parsed.map(normalizeWidget)
            }];
            state.activePageId = 'page-1';
          }
        }
      }
    } catch (e) {
      console.warn('Failed to load composer state:', e);
    }
  }

  // Save current layout to localStorage & sync to OBS Server
  let layoutWrites=Promise.resolve();
  function enqueueLayoutSave(payload){
    const body=JSON.stringify(payload);
    const request=layoutWrites.catch(()=>{}).then(()=>fetch('/api/composer/layout',{method:'POST',headers:{'Content-Type':'application/json'},body}));
    layoutWrites=request;return request;
  }
  async function saveState(silent) {
    try {
      const payload = {
        pages: state.pages,
        activePageId: state.activePageId,
        canvasWidth: CANVAS_WIDTH,
        canvasHeight: CANVAS_HEIGHT,
        legacyPlayroomTriggers: state.legacyPlayroomTriggers || [],
        legacyTools: state.legacyTools || {}, legacyChat: state.legacyChat || {},
        updatedAt: Date.now()
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.pages));
      localStorage.setItem(STORAGE_KEY + '_full', JSON.stringify(payload));

      // Push to backend server API for OBS Studio Browser Source
      const savedResponse = await enqueueLayoutSave(payload);
      const savedResult = await savedResponse.json();
      if (!savedResponse.ok || savedResult.saved !== true) throw new Error('Layout save failed');

      window.BP3_BUS?.emit('CANVAS_LAYOUT_SAVED',payload);
      // Broadcast to any open windows
      try {
        if ('BroadcastChannel' in window) {
          const bus = new BroadcastChannel('bp3_system_channel');
          bus.postMessage({ event: 'CANVAS_LAYOUT_SAVED', payload });
        }
      } catch (e) {}

      if (!silent && window.showToast) {
        window.showToast('บันทึกเลย์เอาต์หน้าจอและส่งไปยัง OBS เรียบร้อยแล้ว');
      }
      return true;
    } catch (e) {
      if(window.showToast) window.showToast('บันทึกลงเซิร์ฟเวอร์ไม่สำเร็จ กรุณาตรวจว่าโปรแกรมยังเปิดอยู่');
      console.error('Failed to save composer state:', e);
      return false;
    }
  }

  // Get active page
  function getActivePage() {
    let p = state.pages.find(p => p.id === state.activePageId);
    if (!p && state.pages.length > 0) {
      p = state.pages[0];
      state.activePageId = p.id;
    }
    return p;
  }

  // Get selected widget
  function getSelectedWidget() {
    const page = getActivePage();
    if (!page) return null;
    return page.widgets.find(w => w.id === state.selectedWidgetId) || null;
  }

  // Initialize Composer Studio
  let composerInitialized = false;
  async function initComposerStudio() {
    if(composerInitialized || !document.getElementById('composerCanvasStage'))return;
    composerInitialized=true;
    loadSavedState();
    try {
      const response=await fetch('/api/composer/layout', {cache:'no-store'});
      if(response.ok){
        const layout=await response.json();
        CANVAS_WIDTH=layout.canvasWidth || 1920;CANVAS_HEIGHT=layout.canvasHeight || 1080;
        state.pages=layout.pages.map(page=>({...page,widgets:page.widgets.map(normalizeWidget)}));
        state.activePageId=layout.activePageId || state.pages[0].id;
        state.legacyPlayroomTriggers=layout.legacyPlayroomTriggers || [];
        state.legacyTools=layout.legacyTools || {}; state.legacyChat=layout.legacyChat || {};
        if(window.applyLegacyToolData)window.applyLegacyToolData(layout);
      }
    }catch(_){}

    renderPageTabs();
    setupCanvasEvents();
    setupToolbarEvents();
    renderCanvasWidgets();
    renderLayersList();
    updateTransformInspector();

    // Auto-fit zoom when window is opened
    window.addEventListener('resize', autoFitCanvas);

    // Live clock updater
    if (!clockInterval) {
      clockInterval = setInterval(() => {
        const now = new Date();
        document.querySelectorAll('.composer-widget.type-clock').forEach(el => {
          const wid = el.dataset.id;
          const page = getActivePage();
          const w = page ? page.widgets.find(x => x.id === wid) : null;
          if (!w) return;
          updateClockWidget(el,w,now);
        });
      }, 1000);
    }

    // Keyboard shortcuts
    window.addEventListener('keydown', handleKeyDown);

    // Layers List Expand/Collapse Button Listener
    const btnToggleLayers = document.getElementById('btnToggleLayersExpand');
    const layersList = document.getElementById('composerLayersList');
    if (btnToggleLayers && layersList) {
      btnToggleLayers.addEventListener('click', () => {
        const isExpanded = layersList.classList.toggle('expanded');
        btnToggleLayers.textContent = isExpanded ? '🗗 ย่อขนาด' : '⛶ ขยายดูทั้งหมด';
        btnToggleLayers.style.background = isExpanded ? 'rgba(88, 101, 242, 0.25)' : 'rgba(255,255,255,0.06)';
        btnToggleLayers.style.borderColor = isExpanded ? 'var(--dc-blurple)' : 'rgba(255,255,255,0.15)';
        btnToggleLayers.style.color = isExpanded ? '#ffffff' : '#cbd5e1';
      });
    }

        // Right Sidebar Collapsible Sections (Quick Align & Props)
    document.querySelectorAll('.composer-collapsible-header').forEach(header => {
      header.addEventListener('click', () => {
        const targetId = header.dataset.target;
        if (!targetId) return;
        const targetEl = document.getElementById(targetId);
        const toggleIcon = header.querySelector('.composer-section-toggle');
        if (!targetEl) return;
        const isHidden = targetEl.style.display === 'none';
        targetEl.style.display = isHidden ? '' : 'none';
        if (toggleIcon) toggleIcon.textContent = isHidden ? '▼' : '▶';
      });
    });

    // Left Drawer Expand Button Listener
    const btnExpand = document.getElementById('btnExpandCustPanel');
    if (btnExpand) {
      btnExpand.addEventListener('click', () => {
        state.customizerManuallyCollapsed = false;
        const leftPanel = document.getElementById('composerSidebarLeft');
        if (leftPanel) leftPanel.classList.remove('collapsed');
        btnExpand.classList.remove('visible');
      });
    }

    // Left Drawer Collapse Button Listener
    const btnCollapse = document.getElementById('btnCollapseCustPanel');
    if (btnCollapse) {
      btnCollapse.addEventListener('click', () => {
        state.customizerManuallyCollapsed = true;
        const leftPanel = document.getElementById('composerSidebarLeft');
        if (leftPanel) leftPanel.classList.add('collapsed');
        if (btnExpand) btnExpand.classList.add('visible');
      });
    }
  }

  // Auto-fit canvas into viewport
  function autoFitCanvas() {
    const viewport = document.getElementById('composerViewport');
    const stage = document.getElementById('composerCanvasStage');
    const outer = document.getElementById('composerCanvasOuter');
    if (!viewport || !stage || !outer) return;

    const vpW = viewport.clientWidth - 80;
    const vpH = viewport.clientHeight - 80;
    if (vpW <= 100 || vpH <= 100) return;

    const scaleX = vpW / CANVAS_WIDTH;
    const scaleY = vpH / CANVAS_HEIGHT;
    const fitScale = Math.min(scaleX, scaleY, 0.95);

    setZoom(fitScale);
  }

  // Set zoom level
  function setZoom(factor) {
    state.zoom = Math.max(0.15, Math.min(factor, 1.5));
    const stage = document.getElementById('composerCanvasStage');
    const outer = document.getElementById('composerCanvasOuter');
    const zoomVal = document.getElementById('composerZoomVal');

    if (stage) {
      stage.style.transform = `scale(${state.zoom})`;
      stage.style.setProperty('--composer-guide-width', (1 / state.zoom) + 'px');
    }
    if (outer) {
      outer.style.width = `${CANVAS_WIDTH * state.zoom}px`;
      outer.style.height = `${CANVAS_HEIGHT * state.zoom}px`;
    }
    if (zoomVal) {
      zoomVal.textContent = `${Math.round(state.zoom * 100)}%`;
    }
  }

  // Render Page Tabs & Multi-Page Bar
  function renderPageTabs() {
    const container = document.getElementById('composerPageTabs');
    if (!container) return;
    container.innerHTML = '';

    const pageBar = document.createElement('div');
    pageBar.className = 'composer-page-bar';

    const tabsList = document.createElement('div');
    tabsList.className = 'composer-page-tabs-list';

    state.pages.forEach((page, idx) => {
      const isActive = page.id === state.activePageId;
      const tab = document.createElement('button');
      tab.type = 'button';
      tab.className = `composer-page-tab ${isActive ? 'active' : ''}`;
      tab.title = `สลับไปยัง ${page.name}`;
      const count = page.widgets ? page.widgets.length : 0;
      tab.innerHTML = `<span>📄 ${page.name} <small style="opacity:0.75;">(${count})</small></span>`;
      tab.addEventListener('click', () => switchPage(page.id));
      tabsList.appendChild(tab);
    });

    pageBar.appendChild(tabsList);

    // Action Buttons for current active page
    const actions = document.createElement('div');
    actions.className = 'composer-page-actions';
    actions.innerHTML = `
      <button type="button" class="composer-btn-page-action" id="btnPageNew" title="สร้างหน้าเลย์เอาต์ใหม่">➕ เพิ่มหน้า</button>
      <button type="button" class="composer-btn-page-action" id="btnPageReorder" title="สลับเรียงลำดับหน้าใหม่">🔀 เรียงหน้าใหม่</button>
      <button type="button" class="composer-btn-page-action" id="btnPageDup" title="ทำสำเนาหน้านี้พร้อมวิดเจ็ตทั้งหมด">📋 สำเนา</button>
      <button type="button" class="composer-btn-page-action" id="btnPageRename" title="เปลี่ยนชื่อหน้านี้">✎ เปลี่ยนชื่อ</button>
      ${state.pages.length > 1 ? `<button type="button" class="composer-btn-page-action btn-danger" id="btnPageDel" title="ลบหน้านี้">🗑 ลบ</button>` : ''}
    `;

    const btnNew = actions.querySelector('#btnPageNew');
    if (btnNew) btnNew.addEventListener('click', addNewPage);
    const btnReorder = actions.querySelector('#btnPageReorder');
    if (btnReorder) btnReorder.addEventListener('click', reorderPages);
    const btnDup = actions.querySelector('#btnPageDup');
    if (btnDup) btnDup.addEventListener('click', duplicateCurrentPage);
    const btnRename = actions.querySelector('#btnPageRename');
    if (btnRename) btnRename.addEventListener('click', renameCurrentPage);
    const btnDel = actions.querySelector('#btnPageDel');
    if (btnDel) btnDel.addEventListener('click', () => deletePage(state.activePageId));

    pageBar.appendChild(actions);
    container.appendChild(pageBar);
  }

  function reorderPages() {
    if (state.pages.length <= 1) {
      if (window.showToast) window.showToast('ℹ️ มีหน้าเลย์เอาต์เพียง 1 หน้า กรุณากด "➕ เพิ่มหน้า" ก่อนครับ');
      return;
    }
    const curIdx = state.pages.findIndex(p => p.id === state.activePageId);
    if (curIdx !== -1) {
      const nextIdx = (curIdx + 1) % state.pages.length;
      const [moved] = state.pages.splice(curIdx, 1);
      state.pages.splice(nextIdx, 0, moved);
      renderPageTabs();
      saveState();
      if (window.showToast) window.showToast(`🔀 ย้ายหน้า "${moved.name}" ไปยังลำดับที่ ${nextIdx + 1} แล้ว`);
    }
  }

  // Switch Active Page
  function switchPage(pageId) {
    if (!pageId) return;
    state.activePageId = pageId;
    state.selectedWidgetId = null;
    renderPageTabs();
    renderCanvasWidgets();
    renderLayersList();
    updateTransformInspector();
    renderWidgetCustomizerPanel(null);
    saveState();
  }

  // Add New Page
  function addNewPage() {
    const pageNum = state.pages.length + 1;
    const newPage = {
      id: `page-${Date.now()}`,
      name: `หน้า ${pageNum}`,
      widgets: []
    };
    state.pages.push(newPage);
    switchPage(newPage.id);
    if (window.showToast) {
      window.showToast(`สร้าง ${newPage.name} เรียบร้อยแล้ว`);
    }
  }

  // Duplicate Current Page
  function duplicateCurrentPage() {
    const curPage = getActivePage();
    if (!curPage) return;
    const clonedWidgets = JSON.parse(JSON.stringify(curPage.widgets || [])).map(w => {
      w.id = `w-${w.type}-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`;
      return w;
    });
    const newPage = {
      id: `page-${Date.now()}`,
      name: `${curPage.name} (สำเนา)`,
      widgets: clonedWidgets
    };
    state.pages.push(newPage);
    switchPage(newPage.id);
    if (window.showToast) {
      window.showToast(`ทำสำเนา ${newPage.name} สำเร็จ`);
    }
  }

  // Rename Current Page
  function renameCurrentPage() {
    const curPage = getActivePage();
    if (!curPage) return;
    const newName = prompt('ระบุชื่อหน้าใหม่:', curPage.name);
    if (newName && newName.trim() && newName.trim() !== curPage.name) {
      curPage.name = newName.trim();
      renderPageTabs();
      saveState();
      if (window.showToast) window.showToast(`เปลี่ยนชื่อเป็น "${curPage.name}" สำเร็จ`);
    }
  }

  // Delete Page
  function deletePage(pageId) {
    if (state.pages.length <= 1) {
      if (window.showToast) window.showToast('ต้องมีเลย์เอาต์อย่างน้อย 1 หน้า');
      return;
    }
    const page = state.pages.find(p => p.id === pageId);
    if (!page) return;
    if (confirm(`คุณต้องการลบหน้า "${page.name}" หรือไม่? วิดเจ็ตทั้งหมดในหน้านี้จะหายไปด้วย`)) {
      const idx = state.pages.findIndex(p => p.id === pageId);
      if (idx !== -1) {
        state.pages.splice(idx, 1);
        if (state.activePageId === pageId) {
          state.activePageId = state.pages[0].id;
        }
        switchPage(state.activePageId);
        if (window.showToast) window.showToast('ลบหน้าเรียบร้อยแล้ว');
      }
    }
  }

  // Render Canvas Widgets
  function renderCanvasWidgets() {
    const canvasElement=document.getElementById('composerCanvasStage');
    if(canvasElement){canvasElement.style.width=CANVAS_WIDTH+'px';canvasElement.style.height=CANVAS_HEIGHT+'px';}
    ensureChatThemesStyleSheet();
    const stage = document.getElementById('composerCanvasStage');
    if (!stage) return;

    const previous=new Map([...stage.querySelectorAll(':scope > .composer-widget')].map(el=>[el.dataset.id,el]));

    const page = getActivePage();
    if (!page) return;

    page.widgets.forEach(w => {
      if (w.hidden) return;

      const isFull = isFullscreenWidget(w);
      if (isFull) {
        w.x = 0;
        w.y = 0;
        w.width = CANVAS_WIDTH;
        w.height = CANVAS_HEIGHT;
        w.noDrag = true;
        w.noResize = true;
        w.isFullScreen = true;
      }
      const old=previous.get(String(w.id));previous.delete(String(w.id));
      const signature=JSON.stringify(w);
      if(old && w.type==='chat'){
        Object.assign(old.style,{left:w.x+'px',top:w.y+'px',width:w.width+'px',height:w.height+'px',zIndex:w.z || 1,opacity:w.opacity ?? 1});
        old.classList.toggle('selected',w.id===state.selectedWidgetId);
        if(old._bpSignature!==signature)old.querySelector('iframe')?.contentWindow?.postMessage({type:'bp3-chat-widget',widget:w},location.origin);
        old._bpSignature=signature;return;
      }
      if(old && old._bpSignature===signature){old.classList.toggle('selected',w.id===state.selectedWidgetId);return;}
      const isDanmaku = isFull;
      const el = document.createElement('div');
      const classes = ['composer-widget', 'widget', `type-${w.type}`];
      if (w.id === state.selectedWidgetId) classes.push('selected');
      if (w.locked) classes.push('locked');
      if (isFull) classes.push('widget-fullscreen-fixed', 'widget-danmaku-full');

      if (w.type === 'clock') {
        // Clock decoration belongs to the actual clock content only.
        if (w.clockMode === 'style' && w.clockStyle && w.clockStyle !== 'none') {
          classes.push('clock-style-set', 'clock-style-' + w.clockStyle);
        }
      }
      if (w.type === 'viewer') {
        classes.push('viewer-theme-' + (w.viewerTheme || 'default'));
        classes.push('viewer-align-' + (w.viewerAlign || 'left'));
        classes.push('viewer-direction-' + (w.viewerDirection || 'horizontal'));
      }
      if (w.type === 'webcam') {
        classes.push('webcam-theme-' + (w.webcamTheme || 'simple-white'));
        classes.push('ratio-' + (w.ratio || '16:9').replace(':', '-'));
        el.style.setProperty('--wc-border-width', (w.borderWidth || 4) + 'px');
      }
      if (w.type === 'chat') {
        classes.push('theme-' + (w.chatTheme || 'default'));
      }
      if (w.type === 'text') {
        classes.push('text-' + (w.textMode || 'ticker'));
        el.style.setProperty('--marquee-duration', (w.marqueeSpeed || 15) + 's');
      }

      el.className = classes.join(' ');
      el.id = `widget-${w.id}`;
      el.dataset.id = w.id;
      el.style.left = `${w.x}px`;
      el.style.top = `${w.y}px`;
      el.style.width = `${w.width}px`;
      el.style.height = `${w.height}px`;
      el.style.zIndex = w.z || 1;
      el.style.opacity = w.opacity ?? 1;

      // Badge - Move beneath widget frame if at the very top of canvas
      const isAtTop = (!isFull && w.y < 26);
      if (isAtTop) {
        el.classList.add('badge-at-bottom');
      }
      const badge = document.createElement('div');
      badge.className = `composer-widget-badge${isAtTop ? ' badge-bottom' : ''}`;
      badge.innerHTML = `<span>${getWidgetIcon(w.type)}</span> <span>${w.title}</span> <span style="opacity:0.75; font-size:10px;">${isFull ? 'เต็มจอ 1920×1080' : `${w.width}×${w.height}`}</span> <button type="button" class="btn-widget-gear" title="ตั้งค่าวิดเจ็ต" style="background:transparent; border:none; cursor:pointer; font-size:12px; margin-left:6px; padding:0 2px; color:#ffffff;">⚙️</button>`;
      
      const btnGear = badge.querySelector('.btn-widget-gear');
      if (btnGear) {
        btnGear.addEventListener('mousedown', (e) => e.stopPropagation());
        btnGear.addEventListener('click', (e) => {
          e.stopPropagation();
          openWidgetSettings(w.id);
        });
      }
      el.appendChild(badge);

      // Inner Content
      const inner = document.createElement('div');
      inner.className = 'composer-widget-inner widget-inner';
      if(w.type==='chat' && old?.querySelector('iframe[data-legacy-chat]'))inner.append(old.querySelector('iframe[data-legacy-chat]'));else inner.innerHTML = renderWidgetInnerHtml(w);
      const frame=inner.querySelector('iframe[data-legacy-chat]');
      if(frame){const sync=()=>frame.contentWindow?.postMessage({type:'bp3-chat-widget',widget:w},location.origin);frame.addEventListener('load',sync,{once:true});sync();}
      el.appendChild(inner);

      // 8 Resize Handles - Do NOT add handles if noResize or Danmaku
      if (!w.noResize && !isDanmaku) {
        const handles = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w'];
        handles.forEach(h => {
          const handle = document.createElement('div');
          handle.className = `composer-resize-handle handle-${h}`;
          handle.dataset.handle = h;
          el.appendChild(handle);
        });
      }

      // Selection & Drag listeners
      el.addEventListener('mousedown', (e) => {
        if (e.target.closest('.btn-widget-gear')) return;
        if (e.target.classList.contains('composer-resize-handle')) {
          startResize(e, w, e.target.dataset.handle);
        } else {
          startDrag(e, w);
        }
      });
      el.addEventListener('click', (e) => {
        if (e.target.closest('.btn-widget-gear')) return;
        selectWidget(w.id);
      });

      el._bpSignature=signature;
      if(old)window.BP3PatchWidget(old,el);else stage.appendChild(el);
      if(old)old._bpSignature=signature;

      // Initialize Number Ticker for viewer widget
      if (w.type === 'viewer') {
        updateAllViewerTickers(el, w);
      }
    });
    for(const el of previous.values())el.remove();
    window.BP3LegacyVideos?.mount();
    window.BP3LegacyAvatar?.mount();
    window.BP3LegacyGoals?.mount();
    window.BP3ViewerPreview?.mount();
    window.BP3Music?.mount();
    if(window._liveGwState)window.BP3LegacyGiveaway?.render(window._liveGwState);
  }

  // Get Widget Icon
  function getWidgetIcon(type) {
    const icons = {
      chat: '💬',
      clock: '🕒',
      text: '🔤',
      character: '🎭',
      replie: '💬',
      avatar: '😊',
      webcam: '📹',
      goal: '🎯',
      donate_goal: '🎯',
      viewer: '👥',
      image: '🖼️',
      video: '🎬',
      alert: '🌐',
      browser: '🌐',
      now_playing: '🎵',
      emote_party: '🎉',
      ask: '🗳️',
      giveaway: '🎁',
      playroom: '🎮',
      randomizer: '🎲'
    };
    return icons[type] || '📦';
  }


  // === Takayu & Mooncape Clock Constants & Data ===
  const CC_COLOR_SCHEMES = {
    1: ['#FF5D5D', '#FFC3C3'],  // ดำ/แดง
    2: ['#1363DF', '#DFF6FF'],  // ฟ้า/เหลือง
    3: ['#07D01D', '#E0F3D2'],  // เขียว
    4: ['#F77E21', '#FEF9A7'],  // ส้ม/ชมพู
    5: ['#8D8DAA', '#F7F5F2'],  // ม่วง/ฟ้า
  };
  const CC_DAY_NAMES = ['Sun.', 'Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.', 'Sat.'];

  const FPS_SVGS = {
    2: '<svg viewBox="0 0 300 50" preserveAspectRatio="none"><g class="fps-bg"><path d="M645.64,0H360.36L356,7.45,379.93,50H626.07L650,7.45Z" transform="translate(-353)"/></g><g class="fps-frame"><path d="M360.36,0h-3L353,7.45,376.93,50h3L356,7.45ZM648.64,0h-3L650,7.45,626.07,50h3L653,7.45Z" transform="translate(-353)"/></g></svg>',
    3: '<svg viewBox="0 0 244 50" preserveAspectRatio="none"><g class="fps-bg"><path d="M355.53-102.22h-220l-10-10v-26l10-10h220l10,10v26Z" transform="translate(-123.53 150.22)"/></g><g class="fps-frame"><path d="M128.53-150.22h68l2,2h-63l-10,10v26l-2-2v-31Zm237,12v26l-10,10h-63l2,2h68l5-5v-31Z" transform="translate(-123.53 150.22)"/></g></svg>',
    4: '<svg viewBox="0 0 300 50" preserveAspectRatio="none"><g class="fps-bg"><polygon points="5.44 49 1.18 42.19 26.92 1 294.56 1 298.82 7.81 273.08 49 5.44 49"/></g><g class="fps-frame"><path d="M1914-64.15l3.63,5.82-25.12,40.18H1626L1622.36-24l25.12-40.19H1914m1.11-2H1646.37L1620-24l4.88,7.81h268.75L1920-58.33l-4.88-7.82Z" transform="translate(-1620 66.15)"/></g></svg>',
  };

  const THAI_MONTHS_SHORT = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'];
  const THAI_MONTHS_LONG = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม'];
  const THAI_DAYS_SHORT = ['อา.', 'จ.', 'อ.', 'พ.', 'พฤ.', 'ศ.', 'ส.'];
  const THAI_DAYS_LONG = ['วันอาทิตย์', 'วันจันทร์', 'วันอังคาร', 'วันพุธ', 'วันพฤหัสบดี', 'วันศุกร์', 'วันเสาร์'];
  const EN_MONTHS_SHORT = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const EN_MONTHS_LONG = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const EN_DAYS_SHORT = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const EN_DAYS_LONG = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  function updateClockWidget(el,w,now=new Date()){
    if(!w)return;
          const hasStyle = (w.clockMode || (w.clockStyle && w.clockStyle !== 'none' ? 'style' : 'theme')) === 'style';
          if (hasStyle && w.clockStyle && w.clockStyle !== 'none') {
            const h = String(now.getHours()).padStart(2, '0');
            const m = String(now.getMinutes()).padStart(2, '0');
            const s = String(now.getSeconds()).padStart(2, '0');
            const yr = now.getFullYear();
            const mo = String(now.getMonth() + 1).padStart(2, '0');
            const dy = String(now.getDate()).padStart(2, '0');
            const dotTime = el.querySelector('.dot-time');
            if (dotTime) {
              if (w.clockStyle === 'dot1') dotTime.textContent = `${h}:${m}`;
              else if (w.clockStyle === 'dot2') dotTime.textContent = `${yr}.${mo}.${dy} ${h}:${m}`;
              else dotTime.textContent = `${dy}.${mo}.${yr} ${h}:${m}`;
            }
            const ltTime = el.querySelector('.lt-time');
            if (ltTime) ltTime.innerHTML = `${h}<span class="lt-colon">:</span>${m}`;
            const ltSec = el.querySelector('.lt-sec');
            if (ltSec) ltSec.textContent = s;
            const fpsTime = el.querySelector('.fps-time');
            if (fpsTime) fpsTime.innerHTML = `${h}<span class="fps-colon">:</span>${m}<span class="fps-colon">:</span>${s}`;
            const ccOc = el.querySelector('.cc-oc');
            if (ccOc) {
              const colorNum = parseInt((w.clockStyle || '').replace(/[^0-9]/g, '')) || 1;
              const colors = CC_COLOR_SCHEMES[colorNum] || CC_COLOR_SCHEMES[1];
              const deg = 6 * (now.getSeconds() + now.getMilliseconds() / 1000);
              const phase = Math.floor(now.getMinutes()) % 2;
              const [active, inactive] = phase === 0 ? colors : [colors[1], colors[0]];
              ccOc.style.background = `conic-gradient(${active} 0deg ${deg}deg, ${inactive} ${deg}deg 360deg)`;
            }
            const ccT1 = el.querySelector('.cc-t1');
            if (ccT1) ccT1.textContent = `${h}:${m}`;
            const ccT2 = el.querySelector('.cc-t2');
            if (ccT2 && (w.clockStyle || '').startsWith('ccsec')) ccT2.textContent = s;
          } else {
            const h = String(now.getHours()).padStart(2, '0');
            const m = String(now.getMinutes()).padStart(2, '0');
            const s = String(now.getSeconds()).padStart(2, '0');
            let timeStr = `${h}:${m}`;
            if (w.clockFormat === 'HH:MM:SS') timeStr = `${h}:${m}:${s}`;
            else if (w.clockFormat === '12') {
              let hrs = now.getHours();
              const ampm = hrs >= 12 ? 'PM' : 'AM';
              hrs = hrs % 12 || 12;
              timeStr = w.showSeconds === false ? `${hrs}:${m} ${ampm}` : `${hrs}:${m}:${s} ${ampm}`;
            }
            const timeEl = el.querySelector('.clock-time');
            if (timeEl) timeEl.textContent = timeStr;
            const dateEl = el.querySelector('.clock-date');
            if (dateEl && (w.showDate ?? w.show_date)) {
              dateEl.textContent = formatClockDate(now, w.dateFormat || w.date_format || 'short', w.dateLang || w.date_lang || 'th');
            }
          }

  }
  window.BP3UpdateClock=updateClockWidget;

  function formatClockDate(now, fmt = 'short', lang = 'th') {
    const isEn = lang === 'en';
    const month = now.getMonth();
    const day = now.getDate();
    const year = now.getFullYear();
    const dayName = isEn ? EN_DAYS_SHORT[now.getDay()] : THAI_DAYS_SHORT[now.getDay()];
    const dayNameLong = isEn ? EN_DAYS_LONG[now.getDay()] : THAI_DAYS_LONG[now.getDay()];

    if (fmt === 'long') {
      const mLong = isEn ? EN_MONTHS_LONG[month] : THAI_MONTHS_LONG[month];
      const yr = isEn ? year : year + 543;
      return `${dayNameLong} ${day} ${mLong} ${yr}`;
    } else if (fmt === 'iso') {
      return `${year}-${String(month+1).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
    } else if (fmt === 'weekday') {
      const mShort = isEn ? EN_MONTHS_SHORT[month] : THAI_MONTHS_SHORT[month];
      const yr = isEn ? year : String(year+543).slice(-2);
      return `${dayName} ${day} ${mShort} ${yr}`;
    }
    // short
    const mShort = isEn ? EN_MONTHS_SHORT[month] : THAI_MONTHS_SHORT[month];
    const yr = isEn ? year : String(year+543).slice(-2);
    return `${day} ${mShort} ${yr}`;
  }

  // Ensure scoped stylesheet for all 80 chat themes exists in head
  function ensureChatThemesStyleSheet() {
    let styleTag = document.getElementById('composer-chat-themes-styles');
    if (!styleTag) {
      styleTag = document.createElement('style');
      styleTag.id = 'composer-chat-themes-styles';
      document.head.appendChild(styleTag);
    }
    const allThemes = window.CWC_ALL_THEMES || [];
    if (!allThemes.length || styleTag.dataset.loaded === 'true') return;

    let cssText = `
      /* Base rule for chat messages to seamlessly adopt theme CSS variables */
      :is(.composer-widget, .widget).type-chat :is(.msg, .cwc-msg-item, .chat-line),
      :is(.composer-widget, .widget)[class*="theme-"] :is(.msg, .cwc-msg-item, .chat-line) {
        background: var(--box-bg, rgba(30, 31, 34, 0.85)) !important;
        border: var(--box-border, none) !important;
        border-radius: var(--box-radius, 8px) !important;
        box-shadow: var(--box-shadow, none) !important;
        color: var(--text-color, #ffffff);
        text-shadow: var(--text-shadow, none);
        padding: 8px 14px;
        box-sizing: border-box;
        transition: all 0.2s ease;
      }
    `;

    allThemes.forEach(t => {
      if (!t.css) return;
      const tid = t.id || t.key;
      const scoped = t.css
        .replace(/:root\b/g, `:is(.composer-widget, .widget).theme-${tid}, :is(.composer-widget, .widget)[data-theme="${tid}"]`)
        .replace(/(^|[\s,;{}])\.msg([:\s\.\-_\[{]|$)/g, `$1:is(.composer-widget, .widget).theme-${tid} :is(.msg, .cwc-msg-item, .chat-line)$2`)
        .replace(/(^|[\s,;{}])\.chat-line([:\s\.\-_\[{]|$)/g, `$1:is(.composer-widget, .widget).theme-${tid} :is(.msg, .cwc-msg-item, .chat-line)$2`);
      cssText += '\n' + scoped;
    });

    styleTag.textContent = cssText;
    styleTag.dataset.loaded = 'true';
  }

  function renderClockStyleHtml(w, now) {
    const style = w.clockStyle || w.clock_style || 'none';
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    const s = String(now.getSeconds()).padStart(2, '0');
    const yr = now.getFullYear();
    const mo = String(now.getMonth() + 1).padStart(2, '0');
    const dy = String(now.getDate()).padStart(2, '0');
    const op = w.styleOpacity ?? w.style_opacity ?? 1.0;

    if (style === 'dot1' || style === 'dot2' || style === 'dot3') {
      let timeText = `${h}:${m}`;
      let waitChar = '▼';
      if (style === 'dot2') timeText = `${yr}.${mo}.${dy} ${h}:${m}`;
      else if (style === 'dot3') { timeText = `${dy}.${mo}.${yr} ${h}:${m}`; waitChar = '●'; }
      return `
        <div class="composer-widget-inner widget-type-clock clock-style-set clock-style-${style}" style="opacity:${op}; justify-content:center; align-items:center;">
          <div class="dot-outbox">
            <div class="dot-inbox">
              <span class="dot-time">${timeText}</span>
              <span class="dot-wait">${waitChar}</span>
            </div>
          </div>
        </div>
      `;
    }

    if (style.startsWith('cc')) {
      const colorNum = parseInt(style.replace(/[^0-9]/g, '')) || 1;
      const variant = style.startsWith('ccdate') ? 'date' :
                      style.startsWith('cclive') ? 'live' :
                      style.startsWith('ccsec') ? 'sec' : 'normal';
      const colors = CC_COLOR_SCHEMES[colorNum] || CC_COLOR_SCHEMES[1];
      const ms = now.getMilliseconds();
      const deg = 6 * (now.getSeconds() + ms / 1000);
      const phase = Math.floor(now.getMinutes()) % 2;
      const [active, inactive] = phase === 0 ? colors : [colors[1], colors[0]];

      let extra = '';
      if (variant === 'date') {
        extra = `<div class="cc-t2">${mo}/${dy} ${CC_DAY_NAMES[now.getDay()]}</div>`;
      } else if (variant === 'live') {
        extra = `<div class="cc-live">LIVE</div>`;
      } else if (variant === 'sec') {
        extra = `<div class="cc-t2">${s}</div>`;
      }

      return `
        <div class="composer-widget-inner widget-type-clock clock-style-set clock-style-${style}" style="opacity:${op}; justify-content:center; align-items:center;">
          <div class="cc-main" style="width:140px; height:140px;">
            <div class="cc-oc" style="background:conic-gradient(${active} 0deg ${deg}deg, ${inactive} ${deg}deg 360deg);"></div>
            <div class="cc-ic"></div>
            <div class="cc-t1">${h}:${m}</div>
            ${extra}
          </div>
        </div>
      `;
    }

    if (style.startsWith('lt')) {
      let ltInner = '';
      if (style === 'lt1') {
        ltInner = `<div class="lt-live">LIVE</div><div class="lt-time">${h}<span class="lt-colon">:</span>${m}</div><div class="lt-date">${mo}/${dy} ${CC_DAY_NAMES[now.getDay()]}</div>`;
      } else if (style === 'lt2') {
        ltInner = `<div class="lt-time">${h}<span class="lt-colon">:</span>${m}</div><div class="lt-date">${mo}/${dy} ${CC_DAY_NAMES[now.getDay()]}</div>`;
      } else if (style === 'lt3') {
        ltInner = `<div class="lt-time">${h}<span class="lt-colon">:</span>${m}</div>`;
      } else if (style === 'lt4') {
        ltInner = `<div class="lt-time">${h}<span class="lt-colon">:</span>${m}</div><span class="lt-sec">${s}</span>`;
      } else if (style === 'lt5') {
        ltInner = `<div class="lt-time">${h}<span class="lt-colon">:</span>${m}</div><span class="lt-bolt-svg"><svg viewBox="0 0 20 30" style="width:14px; height:20px; fill:#ff0055;"><polygon points="12.4 0 1 18 9.2 18 7.617 30 19 12 10.8 12 12.4 0"/></svg></span><span class="lt-live-inline" style="font-size:18px; letter-spacing:4px; font-weight:700; color:#ff0055;">LIVE</span>`;
      }
      return `
        <div class="composer-widget-inner widget-type-clock clock-style-set clock-style-${style}" style="opacity:${op}; justify-content:center; align-items:center;">
          <div class="lt-nowtime">${ltInner}</div>
        </div>
      `;
    }

    if (style.startsWith('fps')) {
      const fpsNum = parseInt(style.replace(/[^0-9]/g, '')) || 2;
      return `
        <div class="composer-widget-inner widget-type-clock clock-style-set clock-style-${style}" style="opacity:${op}; justify-content:center; align-items:center;">
          <div class="fps-overlay">
            <div class="fps-svg">${FPS_SVGS[fpsNum] || FPS_SVGS[2]}</div>
            <div class="fps-time">${h}<span class="fps-colon">:</span>${m}<span class="fps-colon">:</span>${s}</div>
          </div>
        </div>
      `;
    }

    return `
      <div class="composer-widget-inner widget-type-clock" style="opacity:${op};">
        <div class="clock-time">${h}:${m}</div>
      </div>
    `;
  }

  // Render Inner HTML according to Widget Type
  function renderWidgetInnerHtml(w) {
    if (w.type === 'chat') {
      return `<iframe data-legacy-chat="true" id="legacyChat_${w.id}" src="/legacy-chat.html?id=${encodeURIComponent(w.id)}&p=${encodeURIComponent(getActivePage()?.id || '')}" style="border:0;width:100%;height:100%;background:transparent;pointer-events:none"></iframe>`;
      const mode = w.chatMode || 'default';
      const theme = w.chatTheme || 'default';

      if (mode === 'danmaku') {
        return `<div class="composer-widget-inner widget-type-chat widget-danmaku-layer" id="widget-danmaku-feed-${w.id}" style="background:transparent;overflow:hidden;position:absolute;inset:0;"></div>`;
      }
      if (mode === 'balloon') {
        return `<div class="composer-widget-inner widget-type-chat" id="widget-balloon-feed-${w.id}" style="background:transparent;display:flex;flex-direction:column;gap:12px;padding:12px;overflow:hidden;"></div>`;
      }
      if (mode === 'character') {
        return `<div class="composer-widget-inner widget-type-chat" id="widget-character-feed-${w.id}" style="background:transparent;position:relative;display:flex;align-items:flex-end;padding:12px;visibility:hidden;"></div>`;
      }

      // Default or Theme with Full Scoped CSS Themes and Live Typography Sync
      const fFam = w.fontFamily || 'Kanit';
      const fSz = w.fontSize || 15;
      const fClr = w.fontColor || '#ffffff';
      const fWeight = w.fontWeight || '600';
      const uClr = w.usernameColor || '#38bdf8';
      const hex = w.bgColor || '#1e1f22';
      const r = parseInt(hex.slice(1, 3), 16) || 30;
      const g = parseInt(hex.slice(3, 5), 16) || 31;
      const b = parseInt(hex.slice(5, 7), 16) || 34;
      const bgOp = w.bgOpacity ?? 0.85;
      const radius = w.boxRadius ?? 8;
      const pad = w.boxPadding ?? 6;
      const isTheme = mode === 'theme';
      const boxEnabled = w.boxEnabled !== false;

      let boxStyle = '';
      if (isTheme && !w.customBoxStyle) {
        boxStyle = ''; // Let theme variables take full effect
      } else if (boxEnabled) {
        boxStyle = `background:rgba(${r}, ${g}, ${b}, ${bgOp}); border-radius:${radius}px; padding:${pad}px 12px;`;
        if (w.boxWidth === 'full') boxStyle += ' width:100%;';
        if (w.boxBorder) boxStyle += ` border:${w.boxBorderWidth || 2}px solid ${w.boxBorderColor || 'rgba(255,255,255,0.2)'};`;
        if (w.boxGlow) boxStyle += ` box-shadow:0 0 12px ${w.boxGlowColor || '#a855f7'};`;
        else if (w.boxShadow) boxStyle += ' box-shadow:0 4px 12px rgba(0,0,0,0.3);';
      } else {
        boxStyle = 'background:transparent; padding:2px 0;';
      }

      const strokeCss = w.textStroke ? `-webkit-text-stroke:${w.textStrokeWidth || 1.5}px ${w.strokeColor || '#000000'}; paint-order:stroke fill;` : '';
      const shadowCss = w.textShadow ? `text-shadow:0 1px ${w.textShadowBlur ?? 3}px ${w.textShadowColor || '#000000'};` : '';
      const alignCss = w.align === 'center' ? 'center' : (w.align === 'right' ? 'flex-end' : 'flex-start');
      const dir = w.direction === 'top' ? 'column' : 'column-reverse';
      const justify = w.direction === 'top' ? 'flex-start' : 'flex-end';
      const spacing = w.msgSpacing ?? 6;

      // Container Background Box: transparent by default unless user enables it
      let containerStyle = 'background:transparent !important; border:none !important; padding:0;';
      if (w.containerBgEnabled) {
        const cHex = w.containerBgColor || '#0a0e1a';
        const cr = parseInt(cHex.slice(1, 3), 16) || 10;
        const cg = parseInt(cHex.slice(3, 5), 16) || 14;
        const cb = parseInt(cHex.slice(5, 7), 16) || 26;
        const cOp = (w.containerBgOpacity !== undefined) ? w.containerBgOpacity : 0.75;
        const cRadius = (w.containerRadius !== undefined) ? w.containerRadius : 8;
        containerStyle = `background:rgba(${cr}, ${cg}, ${cb}, ${cOp}) !important; border-radius:${cRadius}px; padding:8px;`;
        if (w.containerBorder) {
          containerStyle += ` border:${w.containerBorderWidth || 1}px solid ${w.containerBorderColor || 'rgba(255,255,255,0.2)'} !important;`;
        }
      }

      return `
        <div class="composer-widget-inner widget-type-chat theme-${theme}" style="${containerStyle}">
          <div id="widget-chat-feed-${w.id}" style="width:100%; height:100%; overflow-y:auto; overflow-x:hidden; display:flex; flex-direction:${dir}; justify-content:${justify}; gap:${spacing}px; padding:6px;">
          </div>
        </div>
      `;
    }

    if (w.type === 'clock') {
      const now = new Date();
      const hasStyle = (w.clockMode || (w.clockStyle && w.clockStyle !== 'none' ? 'style' : 'theme')) === 'style';
      if (hasStyle && w.clockStyle && w.clockStyle !== 'none') {
        return renderClockStyleHtml(w, now);
      }

      // Theme Mode (Default / 32 Themes)
      const h = String(now.getHours()).padStart(2, '0');
      const m = String(now.getMinutes()).padStart(2, '0');
      const s = String(now.getSeconds()).padStart(2, '0');
      let timeStr = `${h}:${m}`;
      if (w.clockFormat === 'HH:MM:SS') {
        timeStr = `${h}:${m}:${s}`;
      } else if (w.clockFormat === '12') {
        let hrs = now.getHours();
        const ampm = hrs >= 12 ? 'PM' : 'AM';
        hrs = hrs % 12 || 12;
        timeStr = w.showSeconds === false ? `${hrs}:${m} ${ampm}` : `${hrs}:${m}:${s} ${ampm}`;
      }

      const theme = w.clockTheme || w.clock_theme || 'default';
      const fsz = w.fontSize || w.font_size || 28;
      const clr = w.timeColor || w.time_color || w.fontColor || '';
      const op = w.themeOpacity ?? w.theme_opacity ?? 1.0;
      const showDate = w.showDate ?? w.show_date ?? false;
      const dateStr = showDate ? formatClockDate(now, w.dateFormat || w.date_format || 'short', w.dateLang || w.date_lang || 'th') : '';
      const dateFsz = w.dateFontSize || w.date_font_size || 14;
      const dateClr = w.dateColor || w.date_color || '#cccccc';

      return `
        <div class="composer-widget-inner widget-type-clock clock-theme-${theme}" style="opacity:${op}; font-size:${fsz}px; flex-direction:column; gap:2px; justify-content:center; align-items:center;">
          <div class="clock-time" style="${clr ? 'color:' + clr + ';' : ''}">${timeStr}</div>
          ${showDate ? `<div class="clock-date" style="color:${dateClr}; font-size:${dateFsz}px;">${dateStr}</div>` : ''}
        </div>
      `;
    }

    if (w.type === 'text') {
      const isTicker = w.textMode === 'ticker';
      const fsz = w.fontSize || 18;
      const clr = w.fontColor || '#ffffff';
      const bgEnabled = w.bgEnabled !== false;
      const bg = bgEnabled ? (w.bgColor || '#141923') : 'transparent';
      const text = w.text || 'ข้อความประกาศบนหน้าจอไลฟ์สตรีม ยินดีต้อนรับทุกคนครับ!';
      
      const strokeW = w.textStrokeWidth ?? (w.textStroke ? 2 : 0);
      const strokeCss = strokeW > 0 ? `-webkit-text-stroke:${strokeW}px ${w.strokeColor || '#000000'}; paint-order:stroke fill;` : '';
      
      const shadowB = w.textShadowBlur ?? (w.textShadow ? 3 : 0);
      const shadowCss = shadowB > 0 ? `text-shadow:0 1px ${shadowB}px ${w.textShadowColor || '#000000'};` : '';
      
      const fFam = w.fontFamily || 'Kanit';
      const dur = w.marqueeSpeed || 15;
      const vAlign = w.vAlign || 'center';
      const justifyVal = vAlign === 'top' ? 'flex-start' : (vAlign === 'bottom' ? 'flex-end' : 'center');

      if (isTicker) {
        return `
          <div class="composer-widget-inner widget-type-text widget-text-ticker" style="font-family:'${fFam}',sans-serif;font-weight:${w.fontWeight || '600'}; font-size:${fsz}px; color:${clr}; background:${bg}; ${strokeCss} ${shadowCss}; --marquee-duration:${dur}s; --marquee-top:${vAlign==='top'?'0%':vAlign==='bottom'?'100%':'50%'}; --marquee-shift-y:${vAlign==='top'?'0%':vAlign==='bottom'?'-100%':'-50%'}; display:flex; flex-direction:column; justify-content:${justifyVal};">
            <span>${text}</span>
          </div>
        `;
      }

      return `
        <div class="composer-widget-inner widget-type-text" style="font-family:'${fFam}',sans-serif;font-weight:${w.fontWeight || '600'}; font-size:${fsz}px; color:${clr}; background:${bg}; ${strokeCss} ${shadowCss}; display:flex; flex-direction:column; justify-content:${justifyVal}; text-align:center;">
          <span>${text}</span>
        </div>
      `;
    }

    if (w.type === 'replie') {
      return `<div class="composer-widget-inner" style="background:transparent;border:none;"><div data-live-replie="true" id="liveReplie_${w.id}" style="display:none;"></div></div>`;
    }

    if (w.type === 'character') {
      const charImg = w.imageUrl || './assets/dock_offline_character.png';
      const charName = w.characterName || 'Replie';
      return `
        <div class="composer-widget-inner widget-type-character" id="compInnerChar_${w.id}" style="position:relative; display:flex; flex-direction:column; align-items:center; justify-content:center; width:100%; height:100%;">
          <div class="char-bubble-container" id="compCharBubble_${w.id}" style="display:none; position:absolute; bottom:calc(100% - 10px); left:50%; transform:translateX(-50%); background:rgba(15,23,42,0.95); border:1.5px solid #38bdf8; border-radius:12px; padding:6px 14px; font-size:12px; font-weight:600; color:#fff; white-space:nowrap; box-shadow:0 4px 20px rgba(0,0,0,0.5); z-index:30; pointer-events:none; transition:opacity 0.3s ease;">
            <span class="char-bubble-text" id="compCharBubbleText_${w.id}">สวัสดีครับทุกคน!</span>
          </div>
          <img class="widget-character-img" id="compCharImg_${w.id}" src="${charImg}" alt="Character" draggable="false" style="pointer-events:none; -webkit-user-drag:none; transition:transform 0.25s ease;" onerror="this.src='https://api.dicebear.com/7.x/bottts/svg?seed=Replie1'">
          <div class="widget-character-name" id="compCharName_${w.id}">${charName}</div>
        </div>
      `;
    }

    if (w.type === 'webcam') {
      return `
        <div class="composer-widget-inner widget-type-webcam" style="background:transparent !important; border:none !important;">
          <div class="webcam-frame" style="--wc-border-width:${w.borderWidth ?? w.webcam_border_width ?? 4}px;width:100%; height:100%; background:transparent !important;"></div>
        </div>
      `;
    }

    if (w.type === 'ask') {
      const liveAsk = window._liveAskState || {};
      const isAskActive = liveAsk && liveAsk.active === true && (liveAsk.phase === 'voting' || liveAsk.phase === 'ended');
      const q = liveAsk.question || w.askQuestion || '';
      const choices = liveAsk.choices || [];

      const choicesHtml = choices.map(c => `
        <div style="background:rgba(255,255,255,0.05); border-radius:6px; padding:6px 10px; position:relative; overflow:hidden;">
          <div style="position:absolute; inset:0; width:${c.pct}%; background:${c.color || '#38bdf8'}; opacity:0.25; border-radius:6px; transition:width 0.4s ease;"></div>
          <div style="position:relative; z-index:1; display:flex; justify-content:space-between; font-size:12px; font-weight:600; color:#ffffff;">
            <span>${c.label}: ${c.text}</span>
            <span style="color:${c.color || '#38bdf8'}; font-weight:700;">${c.pct}% (${c.votes || 0})</span>
          </div>
        </div>
      `).join('');

      return `
        <div class="composer-widget-inner widget-type-ask" id="compInnerAsk_${w.id}" style="background:transparent !important; border:none !important; width:100%; height:100%; overflow:hidden; display:flex; flex-direction:column; justify-content:center; pointer-events:none;">
          <!-- Standby: hidden. Only displays during active poll -->
          <div class="ask-panel" id="compAskPanel_${w.id}" style="${isAskActive ? 'display:block;' : 'display:none;'} background:rgba(15, 23, 42, 0.92); border:1.5px solid rgba(56, 189, 248, 0.35); border-radius:12px; padding:12px 16px; box-shadow:0 8px 30px rgba(0,0,0,0.5); pointer-events:auto;">
            <div style="font-weight:700; font-size:14px; color:#38bdf8; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
              <span id="compAskQ_${w.id}">📊 ${q}</span>
              <span id="compAskTimer_${w.id}" style="font-size:11px; color:#94a3b8; background:rgba(255,255,255,0.08); padding:2px 8px; border-radius:4px;">⏱</span>
            </div>
            <div id="compAskChoicesList_${w.id}" style="display:flex; flex-direction:column; gap:6px;">
              ${choicesHtml}
            </div>
          </div>
        </div>
      `;
    }

    if (w.type === 'giveaway') {
      return ''; // Legacy presentation mounts in the existing widget-inner.
    }

    if (w.type === 'playroom') {
      return `
        <div class="composer-widget-inner widget-type-playroom" id="compInnerPlayroom_${w.id}" style="background:transparent !important; border:none !important; width:100%; height:100%; overflow:hidden; position:relative; display:flex; align-items:center; justify-content:center;">
          <!-- Active Playroom Media Stage -->
          <div class="playroom-stage" id="compPlayroomStage_${w.id}" style="display:none; width:100%; height:100%; position:absolute; inset:0; z-index:10; flex-direction:column; align-items:center; justify-content:center;">
            <div class="playroom-clip-card" id="compPlayroomCard_${w.id}" style="background:rgba(15,23,42,0.95); border:2px solid #a855f7; border-radius:16px; padding:16px 22px; box-shadow:0 12px 40px rgba(0,0,0,0.8); text-align:center; max-width:92%; transition:transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);">
              <div style="font-size:36px; margin-bottom:4px;">🎮</div>
              <div class="playroom-clip-title" id="compPlayroomTitle_${w.id}" style="font-size:16px; font-weight:800; color:#c084fc; margin-bottom:4px;">เซียมซี: ดวงมหาเฮง</div>
              <div id="compPlayroomTag_${w.id}" style="font-size:11px; color:#cbd5e1; background:rgba(255,255,255,0.08); padding:3px 10px; border-radius:20px; display:inline-block;">คำสั่ง !fortune</div>
              <div style="margin-top:12px; height:4px; background:rgba(255,255,255,0.1); border-radius:2px; overflow:hidden;">
                <div id="compPlayroomBar_${w.id}" style="height:100%; width:100%; background:linear-gradient(90deg, #a855f7, #ec4899); transition:width linear;"></div>
              </div>
            </div>
          </div>
          <!-- Idle Waiting Banner (Hidden on Standby) -->
          <div class="playroom-idle-banner" id="compPlayroomIdle_${w.id}" style="display:none !important;"></div>
        </div>
      `;
    }

    if(w.type==='avatar' || w.type==='donate_goal')return '<div class="composer-widget-inner" style="width:100%;height:100%;position:relative;pointer-events:none"></div>';
    if (w.type === 'goal') {
      const current = w.goalCurrent ?? 0;
      const target = w.goalTarget ?? 1000;
      const pct = Math.min(100, Math.round((current / (target || 1)) * 100));
      const title = w.goalTitle || 'เป้าหมายผู้ติดตาม';
      const unit = w.goalUnit || 'คน';

      return `
        <div class="composer-widget-inner widget-type-goal">
          <div class="widget-goal-header">
            <span>${title}</span>
            <span style="color:#ec4899;">${current} / ${target} ${unit}</span>
          </div>
          <div class="widget-goal-bar-track">
            <div class="widget-goal-bar-fill" style="width:${pct}%;"></div>
          </div>
        </div>
      `;
    }

    if (w.type === 'viewer') {
      const iconSize = w.iconSize ?? w.viewer_icon_size ?? 20;
      const showIcon = (w.showIcon ?? w.viewer_show_icon) !== false;
      const mode = w.viewerMode || 'both';
      const count = window.BP3ViewerPreview?.count(w) ?? 0;
      const fFam = w.fontFamily || 'Kanit';
      const fsz = w.fontSize || 18;
      const clr = w.fontColor || '#ffffff';
      const strokeCss = w.textStroke ? `-webkit-text-stroke:${w.textStrokeWidth ?? 2}px ${w.strokeColor || '#000000'}; paint-order:stroke fill;` : '';
      const shadowCss = w.textShadow ? `text-shadow:0 1px ${w.textShadowBlur ?? 3}px ${w.textShadowColor || '#000000'};` : '';

      const wantTotal = (mode === 'total' || mode === 'both');
      const wantPerPlat = (mode === 'per_platform' || mode === 'both');

      let totalHtml = '';
      if (wantTotal) {
        totalHtml = `<span class="viewer-total">${showIcon ? peopleIconSpan(iconSize) : ''}<span class="viewer-ticker" style="font-family:'${fFam}',sans-serif;font-weight:${w.fontWeight || '600'}; font-size:${fsz}px; color:${clr}; ${strokeCss} ${shadowCss}"></span></span>`;
      }

      let chipsHtml = '';
      if (wantPerPlat) {
        const activePlats = ['youtube','twitch','tiktok','kick','soop','mylive'];
        chipsHtml = activePlats.map(plat => `
          <span class="viewer-chip" data-platform="${plat}" style="display:${(window.BP3ConnectedPlatforms || []).includes(plat)?'inline-flex':'none'};font-family:'${fFam}',sans-serif; font-size:${Math.round(fsz * 0.9)}px; color:${clr}; ${strokeCss} ${shadowCss}">
            ${showIcon ? getPlatformIconHtml(plat, iconSize) : ''}
            <span class="viewer-ticker" data-platform-ticker="${plat}" style="font-family:'${fFam}',sans-serif; font-size:${Math.round(fsz * 0.9)}px; color:${clr}; ${strokeCss} ${shadowCss}"></span>
          </span>
        `).join('');
      }

      return `
        <div class="composer-widget-inner widget-type-viewer viewer-theme-${w.viewerTheme || 'default'} viewer-align-${w.viewerAlign || 'left'} viewer-direction-${w.viewerDirection || 'horizontal'}" style="background:transparent !important; border:none !important;display:flex;width:100%;height:100%;">
          ${totalHtml}
          ${chipsHtml}
        </div>
      `;
    }

    if (w.type === 'randomizer') {
      return `
        <div class="composer-widget-inner widget-type-randomizer" id="compInnerRandomizer_${w.id}" style="background:transparent !important; border:none !important; width:100%; height:100%; overflow:hidden; display:flex; align-items:center; justify-content:center; pointer-events:none;">
          <!-- Standby: completely transparent. Only reveals card during active spin -->
          <div class="randomizer-card-box" id="compRandomizerCard_${w.id}" style="display:none; background:rgba(2, 6, 23, 0.95); border:2px solid #1e293b; border-radius:18px; padding:20px 32px; text-align:center; box-shadow:0 12px 40px rgba(0,0,0,0.8); pointer-events:auto; min-width:320px;">
            <div style="font-size:12px; color:#94a3b8; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">🎲 QUICK RANDOMIZER</div>
            <div id="compRandomizerResult_${w.id}" style="font-size:28px; font-weight:800; color:#38bdf8; text-shadow:0 0 16px rgba(56,189,248,0.5); margin-bottom:8px;"></div>
            <div id="compRandomizerHint_${w.id}" style="font-size:11.5px; color:#cbd5e1; background:rgba(255,255,255,0.06); padding:4px 12px; border-radius:20px; display:inline-block;">สุ่มสำเร็จ 🎉</div>
          </div>
        </div>
      `;
    }

    if (w.type === 'emote_party') {
      return `
        <div class="composer-widget-inner widget-type-emote-party" id="widget-emote-party-${w.id}" style="background:transparent !important; border:none !important; position:relative; overflow:hidden; width:100%; height:100%;"></div>
      `;
    }

    if (w.type === 'image') {
      if (w.imageUrl) {
        return `
          <div class="composer-widget-inner widget-type-image" style="background:transparent !important; border:none !important; width:100%; height:100%;">
            <img src="${w.imageUrl}" draggable="false" style="width:100%; height:100%; object-fit:${w.fitMode || 'cover'}; pointer-events:none; -webkit-user-drag:none; display:block;" onerror="this.style.display='none';">
          </div>
        `;
      }
      return `
        <div class="composer-widget-inner widget-type-image" style="background:transparent !important; border:none !important; width:100%; height:100%;"></div>
      `;
    }

    if (w.type === 'video') {
      if (w.videoUrl) {
        return `
          <div class="composer-widget-inner widget-type-video" style="background:transparent !important; border:none !important; width:100%; height:100%;">
            <video src="${w.videoUrl}" autoplay loop muted playsinline style="width:100%; height:100%; object-fit:${w.fitMode || 'cover'}; pointer-events:none; background:transparent; display:block;"></video>
          </div>
        `;
      }
      return `
        <div class="composer-widget-inner widget-type-video" style="background:transparent !important; border:none !important; width:100%; height:100%;"></div>
      `;
    }

    if (w.type === 'alert') {
      if (w.url) {
        return `
          <div class="composer-widget-inner widget-type-alert" style="background:transparent !important; border:none !important; width:100%; height:100%;">
            <iframe src="${w.url}" allow="autoplay; fullscreen" referrerpolicy="no-referrer" style="width:100%; height:100%; border:none; background:transparent; pointer-events:none;"></iframe>
          </div>
        `;
      }
      return `
        <div class="composer-widget-inner widget-type-alert" style="background:transparent !important; border:none !important; width:100%; height:100%;"></div>
      `;
    }

    if (w.type === 'now_playing') {
      const isTrans = w.npTransparent === true;
      const bgStyle = isTrans ? 'background:transparent !important;' : `background:rgba(${(w.npBgColor || '#1a1a2e').replace('#','').match(/.{2}/g).map(n=>parseInt(n,16)).join(',')},${w.npBgOpacity ?? 0.85});`;
      const artRadius = w.npArtRadius ?? 6;
      const artSize = w.npArtSize ?? 48;
      const radius = w.npRadius ?? 8;
      const accent = w.npAccentColor || '#1db954';
      const textClr = w.npTextColor || '#ffffff';
      const fontSize = w.npFontSize || 14;
      const artistFontSize = w.npArtistFontSize || 12;
      const timeFontSize = w.npTimeFontSize || 10;
      const styleName = w.npStyle || 'flat';
      const showArt = w.npShowArt !== false;
      const showProgress = w.npShowProgress !== false;

      const songTitle = '';
      const artistName = '';

      return `
        <div class="composer-widget-inner widget-type-now-playing" style="visibility:hidden;--np-accent:${accent}; position:relative; ${bgStyle} border-radius:${radius}px; padding:8px 12px; display:flex !important; flex-direction:row !important; align-items:center !important; gap:12px; width:100%; height:100%; box-sizing:border-box; overflow:hidden;">
          <div class="np-style-overlay np-style-${styleName}" style="position:absolute; inset:0; pointer-events:none; border-radius:${radius}px;"></div>
          ${showArt ? `
            <div class="np-art" style="width:${artSize}px; height:${artSize}px; min-width:${artSize}px; max-width:${artSize}px; border-radius:${artRadius}px; background:rgba(255,255,255,0.1); overflow:hidden; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:22px; z-index:1;">
              ${w.thumbnailUrl ? `<img src="${w.thumbnailUrl}" style="width:100%; height:100%; object-fit:cover; display:block;">` : `🎵`}
            </div>
          ` : ''}
          <div class="np-info" style="flex:1; min-width:0; overflow:hidden; display:flex; flex-direction:column; justify-content:center; gap:2px; z-index:1;">
            <div class="np-title-wrap" style="overflow:hidden; white-space:nowrap; position:relative;">
              <span class="np-title-text" style="display:inline-block; font-weight:600; font-size:${fontSize}px; color:${textClr}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:100%;">${songTitle}</span>
            </div>
            <div class="np-artist" style="font-size:${artistFontSize}px; color:rgba(255,255,255,0.7); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${artistName}</div>
            ${showProgress ? `
              <div class="np-progress-row" style="display:flex; align-items:center; gap:6px; margin-top:4px; width:100%;">
                <span style="font-size:${timeFontSize}px; color:rgba(255,255,255,0.5); min-width:28px;" data-np-position>0:00</span>
                <div style="flex:1; height:4px; background:rgba(255,255,255,0.18); border-radius:2px; overflow:hidden;">
                  <div style="width:0%; height:100%; background:${accent}; border-radius:2px;"></div>
                </div>
                <span style="font-size:${timeFontSize}px; color:rgba(255,255,255,0.5); min-width:28px; text-align:right;" data-np-duration>0:00</span>
              </div>
            ` : ''}
          </div>
        </div>
      `;
    }

    return `
      <div class="composer-widget-inner" style="align-items:center; justify-content:center; background:transparent; border:none;">
        <span>${w.title}</span>
      </div>
    `;
  }

  // Select Widget (Does NOT open or close drawer automatically)
  function selectWidget(widgetId) {
    state.selectedWidgetId = widgetId;
    document.querySelectorAll('.composer-widget').forEach(el => {
      el.classList.toggle('selected', el.dataset.id === widgetId);
    });
    renderLayersList();
    updateTransformInspector();

    // If Left Drawer is ALREADY open, smoothly update customizer to the newly selected widget
    const leftPanel = document.getElementById('composerSidebarLeft');
    if (widgetId && leftPanel && !leftPanel.classList.contains('collapsed')) {
      renderWidgetCustomizerPanel(widgetId);
    }
  }

  // Helper to get all active window contexts where Composer UI or cursor may be active
  function getActiveComposerWindows() {
    const list = [window];
    if (typeof window._popoutWindows === 'object' && window._popoutWindows) {
      const pop = window._popoutWindows['composer'];
      if (pop && !pop.closed && !list.includes(pop)) {
        list.push(pop);
      }
    }
    return list;
  }

  // Start Dragging Widget (Multi-window aware)
  function startDrag(e, widget) {
    if (widget.locked || widget.noDrag || isFullscreenWidget(widget)) {
      selectWidget(widget.id);
      return;
    }
    e.stopPropagation();
    if (e.cancelable) e.preventDefault();
    selectWidget(widget.id);

    state.isDragging = true;
    state.dragStartMouseX = e.clientX;
    state.dragStartMouseY = e.clientY;
    state.dragStartWidgetX = widget.x;
    state.dragStartWidgetY = widget.y;

    const targetWin = e.view || (e.target && e.target.ownerDocument && e.target.ownerDocument.defaultView) || window;
    const wins = getActiveComposerWindows();
    if (!wins.includes(targetWin)) wins.push(targetWin);

    state.activeDragWindows = wins;
    wins.forEach(w => {
      try {
        w.addEventListener('mousemove', onMouseMove);
        w.addEventListener('mouseup', onMouseUp);
      } catch (err) {}
    });
  }

  // Start Resizing Widget
  function startResize(e, widget, handle) {
    if (widget.locked || widget.noResize || isFullscreenWidget(widget)) return;
    e.stopPropagation();
    if (e.cancelable) e.preventDefault();
    selectWidget(widget.id);

    state.isResizing = true;
    state.activeResizeHandle = handle;
    state.dragStartMouseX = e.clientX;
    state.dragStartMouseY = e.clientY;
    state.dragStartWidgetX = widget.x;
    state.dragStartWidgetY = widget.y;
    state.dragStartWidgetW = widget.width;
    state.dragStartWidgetH = widget.height;

    const targetWin = e.view || (e.target && e.target.ownerDocument && e.target.ownerDocument.defaultView) || window;
    const wins = getActiveComposerWindows();
    if (!wins.includes(targetWin)) wins.push(targetWin);

    state.activeDragWindows = wins;
    wins.forEach(w => {
      try {
        w.addEventListener('mousemove', onMouseMove);
        w.addEventListener('mouseup', onMouseUp);
      } catch (err) {}
    });
  }

  // Mouse Move for Drag & Resize
  function onMouseMove(e) {
    const widget = getSelectedWidget();
    if (!widget) return;

    const zoom = (state.zoom > 2 ? state.zoom / 100 : (state.zoom || 0.45));
    const deltaX = (e.clientX - state.dragStartMouseX) / zoom;
    const deltaY = (e.clientY - state.dragStartMouseY) / zoom;

    if (state.isDragging) {
      let newX = Math.round(state.dragStartWidgetX + deltaX);
      let newY = Math.round(state.dragStartWidgetY + deltaY);

      if (state.snapGuides) {
        newX = Math.round(newX / 10) * 10;
        newY = Math.round(newY / 10) * 10;
      }

      // Clamp strictly within canvas boundary
      newX = Math.max(0, Math.min(CANVAS_WIDTH - widget.width, newX));
      newY = Math.max(0, Math.min(CANVAS_HEIGHT - widget.height, newY));

      widget.x = newX;
      widget.y = newY;
    } else if (state.isResizing) {
      const handle = state.activeResizeHandle;
      let newX = state.dragStartWidgetX;
      let newY = state.dragStartWidgetY;
      let newW = state.dragStartWidgetW;
      let newH = state.dragStartWidgetH;

      if (handle.includes('e')) {
        const maxW = CANVAS_WIDTH - newX;
        newW = Math.max(50, Math.min(maxW, state.dragStartWidgetW + deltaX));
      }
      if (handle.includes('s')) {
        const maxH = CANVAS_HEIGHT - newY;
        newH = Math.max(30, Math.min(maxH, state.dragStartWidgetH + deltaY));
      }
      if (handle.includes('w')) {
        const rightEdge = state.dragStartWidgetX + state.dragStartWidgetW;
        let potentialX = state.dragStartWidgetX + deltaX;
        potentialX = Math.max(0, potentialX);
        let potentialW = rightEdge - potentialX;
        if (potentialW < 50) {
          potentialW = 50;
          potentialX = rightEdge - 50;
        }
        newW = potentialW;
        newX = potentialX;
      }
      if (handle.includes('n')) {
        const bottomEdge = state.dragStartWidgetY + state.dragStartWidgetH;
        let potentialY = state.dragStartWidgetY + deltaY;
        potentialY = Math.max(0, potentialY);
        let potentialH = bottomEdge - potentialY;
        if (potentialH < 30) {
          potentialH = 30;
          potentialY = bottomEdge - 30;
        }
        newH = potentialH;
        newY = potentialY;
      }

      if (state.snapGuides) {
        newW = Math.round(newW / 10) * 10;
        newH = Math.round(newH / 10) * 10;
        newX = Math.round(newX / 10) * 10;
        newY = Math.round(newY / 10) * 10;
      }

      // Final boundary clamp: widget must NEVER overflow canvas boundaries in any direction
      newX = Math.max(0, Math.min(CANVAS_WIDTH - 50, newX));
      newY = Math.max(0, Math.min(CANVAS_HEIGHT - 30, newY));
      newW = Math.max(50, Math.min(CANVAS_WIDTH - newX, newW));
      newH = Math.max(30, Math.min(CANVAS_HEIGHT - newY, newH));

      widget.x = newX;
      widget.y = newY;
      widget.width = newW;
      widget.height = newH;
    }

    const el = document.getElementById(`widget-${widget.id}`);
    if (el) {
      el.style.left = `${widget.x}px`;
      el.style.top = `${widget.y}px`;
      el.style.width = `${widget.width}px`;
      el.style.height = `${widget.height}px`;

      // Update badge position dynamically (flip beneath widget frame if at the very top of canvas)
      const isDanmakuFull = widget.isDanmaku || widget.chatMode === 'danmaku';
      const isAtTop = (!isDanmakuFull && widget.y < 26);
      el.classList.toggle('badge-at-bottom', isAtTop);
      const badge = el.querySelector('.composer-widget-badge');
      if (badge) {
        badge.classList.toggle('badge-bottom', isAtTop);
        badge.innerHTML = `<span>${getWidgetIcon(widget.type)}</span> <span>${widget.title}</span> <span style="opacity:0.75; font-size:10px;">${widget.width}×${widget.height}</span> <button type="button" class="btn-widget-gear" title="ตั้งค่าวิดเจ็ต" style="background:transparent; border:none; cursor:pointer; font-size:12px; margin-left:6px; padding:0 2px; color:#ffffff;">⚙️</button>`;
        const btnGear = badge.querySelector('.btn-widget-gear');
        if (btnGear) {
          btnGear.addEventListener('mousedown', (ev) => ev.stopPropagation());
          btnGear.addEventListener('click', (ev) => {
            ev.stopPropagation();
            openWidgetSettings(widget.id);
          });
        }
      }
    }

    updateTransformInspector();
  }

  // Mouse Up
  function onMouseUp() {
    if (state.isDragging || state.isResizing) {
      state.isDragging = false;
      state.isResizing = false;
      state.activeResizeHandle = null;
      state.suppressCanvasDeselectUntil = Date.now() + 200;

      const wins = state.activeDragWindows || getActiveComposerWindows();
      wins.forEach(w => {
        try {
          w.removeEventListener('mousemove', onMouseMove);
          w.removeEventListener('mouseup', onMouseUp);
        } catch (err) {}
      });
      state.activeDragWindows = null;
      saveState();
    }
  }

  // Move Layer by one step: dir = -1 (ขึ้นบน / bring forward), dir = +1 (ลงล่าง / send backward)
  function moveLayerByOne(id, dir) {
    const page = getActivePage();
    if (!page || !page.widgets || page.widgets.length <= 1) return;

    // Sort descending by z (index 0 is topmost with highest z)
    const sorted = [...page.widgets].sort((a, b) => (b.z || 0) - (a.z || 0));
    const idx = sorted.findIndex(w => w.id === id);
    if (idx < 0) return;

    const targetIdx = idx + dir;
    if (targetIdx < 0 || targetIdx >= sorted.length) {
      if (window.showToast) {
        window.showToast(dir < 0 ? 'เลเยอร์อยู่บนสุดแล้ว' : 'เลเยอร์อยู่ล่างสุดแล้ว');
      }
      return;
    }

    // Swap positions
    const temp = sorted[idx];
    sorted[idx] = sorted[targetIdx];
    sorted[targetIdx] = temp;

    // Reassign z values: index 0 gets highest z
    const total = sorted.length;
    sorted.forEach((w, i) => {
      w.z = total - i;
    });

    renderCanvasWidgets();
    renderLayersList();
    saveState();

    if (window.showToast) {
      window.showToast(dir < 0 ? 'สลับ Layer ขึ้นบน ⬆️ (Ctrl+[)' : 'สลับ Layer ลงล่าง ⬇️ (Ctrl+])');
    }
  }

  // Keyboard Shortcuts
  function handleKeyDown(e) {
    if (!state.selectedWidgetId) return;
    if (e.target?.closest?.('input,textarea,select,[contenteditable="true"],[role="combobox"]')) return;

    const widget = getSelectedWidget();
    if (!widget) return;

    const isCtrl = e.ctrlKey || e.metaKey;

    if (e.key === 'Delete' || e.key === 'Backspace') {
      e.preventDefault();
      deleteSelectedWidget();
    } else if (e.key === 'd' && isCtrl) {
      e.preventDefault();
      duplicateWidget(widget.id);
    } else if (isCtrl && (e.key === '[' || e.code === 'BracketLeft')) {
      e.preventDefault();
      moveLayerByOne(widget.id, -1); // สลับ layer ขึ้นบน
    } else if (isCtrl && (e.key === ']' || e.code === 'BracketRight')) {
      e.preventDefault();
      moveLayerByOne(widget.id, +1); // สลับ layer ลงล่าง
    } else if (e.key.startsWith('Arrow') && !widget.locked && !widget.noDrag && !widget.isDanmaku) {
      e.preventDefault();
      const step = e.shiftKey ? 10 : 1;
      if (e.key === 'ArrowLeft') widget.x -= step;
      if (e.key === 'ArrowRight') widget.x += step;
      if (e.key === 'ArrowUp') widget.y -= step;
      if (e.key === 'ArrowDown') widget.y += step;
      widget.x = Math.max(0, Math.min(CANVAS_WIDTH - widget.width, widget.x));
      widget.y = Math.max(0, Math.min(CANVAS_HEIGHT - widget.height, widget.y));
      renderCanvasWidgets();
      updateTransformInspector();
      saveState();
    }
  }

  // Show Duplicate Confirmation Modal (Zero GPU Lockup)
  function showComposerConfirmModal({ title, message, confirmText, cancelText, onConfirm }) {
    const modal = document.getElementById('composerConfirmModal');
    if (!modal) {
      if (confirm(message)) onConfirm();
      return;
    }
    const titleEl = document.getElementById('composerConfirmTitle');
    const msgEl = document.getElementById('composerConfirmMsg');
    const okBtn = document.getElementById('btnComposerConfirmOk');
    const cancelBtn = document.getElementById('btnComposerConfirmCancel');

    if (titleEl) titleEl.textContent = title || 'วิดเจ็ตนี้มีอยู่ในหน้าจอแล้ว';
    if (msgEl) msgEl.textContent = message || 'หน้าจอนี้มีวิดเจ็ตนี้อยู่แล้ว คุณต้องการเพิ่มซ้ำอีกอันหรือไม่?';
    if (okBtn) okBtn.textContent = confirmText || '➕ ยืนยันเพิ่มซ้ำ';
    if (cancelBtn) cancelBtn.textContent = cancelText || 'ยกเลิก';

    modal.style.display = 'flex';

    const cleanup = () => {
      modal.style.display = 'none';
      okBtn.removeEventListener('click', handleOk);
      cancelBtn.removeEventListener('click', handleCancel);
    };

    const handleOk = () => {
      cleanup();
      if (typeof onConfirm === 'function') onConfirm();
    };

    const handleCancel = () => {
      cleanup();
    };

    okBtn.addEventListener('click', handleOk, { once: true });
    cancelBtn.addEventListener('click', handleCancel, { once: true });
  }

  // Check if widget exists before adding, warn if duplicate
  function checkAndAddWidget(type, chatMode = null) {
    const page = getActivePage();
    if (!page) return;

    let exists = false;
    let widgetName = '';
    if (type === 'chat') {
      const mode = chatMode || 'default';
      const names = {
        default: 'กล่องแชทมาตรฐาน',
        danmaku: 'แชทลอยหน้าจอ ดันมากุ',
        balloon: 'บอลลูนแชท',
        character: 'แชทตัวละคร'
      };
      widgetName = names[mode] || 'กล่องแชท';
      exists = page.widgets.some(w => w.type === 'chat' && (w.chatMode || 'default') === mode);
    } else {
      const names = {
        clock: 'นาฬิกาสตรีม',
        text: 'แถบข้อความประกาศ',
        character: 'ตัวละครพูด Replie',
        webcam: 'กรอบกล้องเว็บแคม',
        goal: 'เป้าหมายผู้ติดตาม',
        viewer: 'ตัวนับยอดผู้ชมสด',
        image: 'กรอบรูปภาพ',
        video: 'วิดีโอลูป',
        alert: 'เบราว์เซอร์ URL',
        now_playing: 'เพลงที่กำลังเล่น',
        emote_party: 'ปาร์ตี้อีโมทลอย'
      };
      widgetName = names[type] || 'วิดเจ็ตนี้';
      exists = page.widgets.some(w => w.type === type);
    }

    if (exists) {
      showComposerConfirmModal({
        title: 'วิดเจ็ตนี้มีอยู่ในหน้าจอแล้ว',
        message: `หน้าจอนี้มี "${widgetName}" อยู่แล้ว คุณต้องการเพิ่มซ้ำอีกอันหรือไม่?`,
        confirmText: '➕ ยืนยันเพิ่มซ้ำ',
        cancelText: 'ยกเลิก',
        onConfirm: () => {
          addWidget(type, chatMode);
        }
      });
    } else {
      addWidget(type, chatMode);
    }
  }

  // Add a new Widget to canvas
  function addWidget(type, chatMode = null) {
    if(type==='character')type='replie';
    const page = getActivePage();
    if (!page) return;

    const presets = {
      chat: {
        title: 'กล่องแชทมาตรฐาน',
        width: 440,
        height: 600,
        chatMode: chatMode || 'default',
        chatTheme: 'default',
        fontSize: 15,
        fontColor: '#ffffff',
        bgColor: '#1e1f22',
        bgOpacity: 0.85,
        boxRadius: 8,
        containerBgEnabled: false,
        containerBgColor: '#0a0e1a',
        containerBgOpacity: 0.75,
        containerRadius: 8,
        animation: 'slide',
        exitAnimation: 'auto',
        autoHide: false,
        hideAfter: 8
      },
      clock: { title: 'นาฬิกาสตรีม', width: 280, height: 80, clockTheme: 'cyberpunk', clockFormat: '24', showSeconds: true, fontSize: 26, fontColor: '#38bdf8' },
      text: { title: 'แถบข้อความประกาศ', width: 800, height: 50, text: 'ข้อความสตรีมสดใหม่ ยินดีต้อนรับทุกคนครับ!', textMode: 'ticker', fontSize: 18, fontColor: '#ffffff' },
      character: { title: 'ตัวละครพูด Replie', width: 340, height: 420, characterName: 'Replie', imageUrl: './assets/dock_offline_character.png' },
      webcam: { title: 'กรอบกล้องเว็บแคม', width: 480, height: 270, ratio: '16:9', borderColor: '#5865f2', borderWidth: 4, borderRadius: 8, glow: true, showStreamerName: true, streamerName: 'Streamer LIVE' },
      avatar: {title:'PNG Avatar',width:320,height:400,avatar_preset:'man',avatar_mode:'tts'},
      donate_goal: {title:'เป้าหมายโดเนต',width:420,height:120,dg_goal_amount:1000,dg_goal_title:'เป้าหมายโดเนต',dg_theme:'neon'},
      goal: { title: 'เป้าหมายผู้ติดตาม', width: 420, height: 80, goalTitle: 'เป้าหมายผู้ติดตาม', goalCurrent: 0, goalTarget: 1000, goalUnit: 'คน' },
      viewer: { title: 'ตัวนับยอดผู้ชมสด', width: 240, height: 55, viewerTheme: 'pill', mockViewerCount: 0 },
      image: { title: 'กรอบรูปภาพแบนเนอร์', width: 340, height: 200, fitMode: 'contain' },
      video: { title: 'วิดีโอลูป', width: 480, height: 270, loop: true },
      alert: { title: 'เบราว์เซอร์ URL', width: 400, height: 300, alertUrl: 'https://overlay.example.com' },
      now_playing: { title: 'เพลงที่กำลังเล่น', width: 340, height: 75, songTitle: '', artist: '', npSource: 'auto', np_source: 'auto' },
      emote_party: { title: 'ปาร์ตี้อีโมทลอย (Emote Party)', width: CANVAS_WIDTH, height: CANVAS_HEIGHT, isFullScreen: true, noDrag: true, noResize: true },
      ask: { title: 'โพลสำรวจความคิดเห็น (ASK)', width: CANVAS_WIDTH, height: CANVAS_HEIGHT, isFullScreen: true, noDrag: true, noResize: true, askQuestion: 'สตรีมวันนี้ เล่นเกมอะไรต่อดีครับ?', askChoices: ['Valorant', 'ROV / Garena'] },
      giveaway: { title: 'สุ่มแจกรางวัล (Giveaway)', width: CANVAS_WIDTH, height: CANVAS_HEIGHT, isFullScreen: true, noDrag: true, noResize: true, code: '#join' },
      replie: { title: 'Replie ข้อความ / ภาพ / Combo', width: CANVAS_WIDTH, height: CANVAS_HEIGHT, isFullScreen: true, noDrag: true, noResize: true, characterName: 'Replie', imageUrl: './assets/dock_offline_character.png' },
      randomizer: { title: 'สุ่มด่วน (Quick Randomizer)', width: CANVAS_WIDTH, height: CANVAS_HEIGHT, isFullScreen: true, noDrag: true, noResize: true },
      playroom: { title: 'Playroom Studio มินิเกม', width: 480, height: 320 }
    };

    const preset = presets[type] || { title: 'วิดเจ็ตใหม่', width: 300, height: 200 };

    if (type === 'chat') {
      const mode = chatMode || 'default';
      preset.chatMode = mode;
      if (mode === 'danmaku') {
        preset.title = 'แชทลอยหน้าจอ ดันมากุ';
        preset.width = CANVAS_WIDTH;
        preset.height = CANVAS_HEIGHT;
        preset.isDanmaku = true;
        preset.noResize = true;
        preset.noDrag = true;
        preset.fontSize = 24;
        preset.fontColor = '#ffffff';
        preset.textStroke = false;
        preset.textStrokeWidth = 2;
        preset.strokeColor = '#000000';
        preset.textShadow = true;
        preset.textShadowBlur = 3;
        preset.textShadowColor = 'rgba(0,0,0,0.6)';
        preset.speed = 6;
        preset.slider_zone = 'middle';
      } else if (mode === 'balloon') {
        preset.title = 'บอลลูนแชท';
        preset.width = 460;
        preset.height = 480;
        preset.balloonBg = '#ffffff';
        preset.balloonTextColor = '#0f172a';
        preset.balloonRadius = 14;
        preset.balloonOpacity = 0.95;
        preset.fontSize = 15;
      } else if (mode === 'character') {
        preset.title = 'แชทตัวละคร';
        preset.width = 480;
        preset.height = 480;
        preset.characterName = 'Replie';
        preset.imageUrl = './assets/dock_offline_character.png';
        preset.charBubbleBg = 'rgba(255,255,255,0.96)';
        preset.charTextColor = '#0f172a';
        preset.charFontSize = 15;
      } else {
        preset.title = 'กล่องแชทมาตรฐาน';
      }
    }

    const isFull = isFullscreenWidget(preset) || (type === 'chat' && chatMode === 'danmaku');
    const newWidget = {
      id: `w-${type}-${Date.now()}`,
      type: type,
      title: preset.title,
      x: isFull ? 0 : Math.round(CANVAS_WIDTH / 2 - preset.width / 2),
      y: isFull ? 0 : Math.round(CANVAS_HEIGHT / 2 - preset.height / 2),
      width: isFull ? CANVAS_WIDTH : preset.width,
      height: isFull ? CANVAS_HEIGHT : preset.height,
      z: page.widgets.length + 1,
      opacity: 1,
      locked: false,
      hidden: false,
      noDrag: isFull,
      noResize: isFull,
      isFullScreen: isFull,
      text: preset.text || '',
      ...preset
    };
    if (isFull) {
      newWidget.x = 0;
      newWidget.y = 0;
      newWidget.width = CANVAS_WIDTH;
      newWidget.height = CANVAS_HEIGHT;
      newWidget.noDrag = true;
      newWidget.noResize = true;
      newWidget.isFullScreen = true;
    }

    page.widgets.push(newWidget);
    renderCanvasWidgets();
    selectWidget(newWidget.id);
    saveState();

    // Visual Flash & Temporary Indicator
    setTimeout(() => {
      const el = document.getElementById(`widget-${newWidget.id}`);
      if (el) {
        el.classList.add('composer-widget-flash-highlight');
        const ind = document.createElement('div');
        ind.className = 'composer-widget-new-indicator';
        ind.textContent = `✨ เพิ่ม${preset.title}แล้ว`;
        el.appendChild(ind);
        setTimeout(() => {
          el.classList.remove('composer-widget-flash-highlight');
          ind.remove();
        }, 2200);

        // Center within outer scroll if not danmaku
        const outer = document.getElementById('composerCanvasOuter');
        if (outer && !preset.isDanmaku) {
          const zoom = (state.zoom || 45) / 100;
          const targetX = newWidget.x * zoom;
          const targetY = newWidget.y * zoom;
          outer.scrollTo({
            left: Math.max(0, targetX - outer.clientWidth / 2 + (newWidget.width * zoom) / 2),
            top: Math.max(0, targetY - outer.clientHeight / 2 + (newWidget.height * zoom) / 2),
            behavior: 'smooth'
          });
        }
      }
    }, 50);

    if (window.showToast) {
      window.showToast(`เพิ่ม${preset.title}บนหน้าจอแล้ว`);
    }
  }

  // Duplicate Widget
  function duplicateWidget(id) {
    const page = getActivePage();
    if (!page) return;
    const orig = page.widgets.find(w => w.id === id);
    if (!orig) return;

    const newWidget = JSON.parse(JSON.stringify(orig));
    newWidget.id = `w-${orig.type}-${Date.now()}`;
    newWidget.title = `${orig.title} คัดลอก`;
    if (!newWidget.isDanmaku && newWidget.chatMode !== 'danmaku') {
      newWidget.x += 30;
      newWidget.y += 30;
      newWidget.x = Math.max(0, Math.min(CANVAS_WIDTH - newWidget.width, newWidget.x));
      newWidget.y = Math.max(0, Math.min(CANVAS_HEIGHT - newWidget.height, newWidget.y));
    }
    newWidget.z = page.widgets.length + 1;

    page.widgets.push(newWidget);
    renderCanvasWidgets();
    selectWidget(newWidget.id);
    saveState();
  }

  // Delete a widget by id
  function deleteWidget(id) {
    const page = getActivePage();
    if (!page || !id) return;

    const idx = page.widgets.findIndex(w => w.id === id);
    if (idx !== -1) {
      const removed = page.widgets.splice(idx, 1)[0];
      if (state.selectedWidgetId === id) {
        state.selectedWidgetId = null;
        renderWidgetCustomizerPanel(null);
      }
      renderCanvasWidgets();
      renderLayersList();
      updateTransformInspector();
      saveState();

      if (window.showToast) {
        window.showToast(`ลบ${removed.title}เรียบร้อยแล้ว`);
      }
    }
  }

  // Delete selected widget
  function deleteSelectedWidget() {
    deleteWidget(state.selectedWidgetId);
  }

  // Render Layers List
  function renderLayersList() {
    const list = document.getElementById('composerLayersList');
    if (!list) return;

    const page = getActivePage();
    if (!page) {
      list.innerHTML = '<div style="font-size:11.5px; color:var(--dc-text-muted); padding:10px;">ไม่มีวิดเจ็ต</div>';
      return;
    }

    const previousScroll=list.scrollTop;
    list.innerHTML = '';
    const sorted = [...page.widgets].sort((a, b) => (b.z || 0) - (a.z || 0));
    const countEl = document.getElementById('composerLayerCount');
    if (countEl) countEl.textContent = `${sorted.length} เลเยอร์`;

    // SVG Icons
    const svgSettings = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>`;
    const svgEye = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;
    const svgEyeOff = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#f43f5e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>`;
    const svgLock = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>`;
    const svgUnlock = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 9.9-1"></path></svg>`;
    const svgTrash = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`;

    sorted.forEach((w,index) => {
      const item = document.createElement('div');
      item.className = `composer-layer-item ${w.id === state.selectedWidgetId ? 'active' : ''}`;
      item.dataset.id = w.id;
      item.draggable = true;

      item.innerHTML = `
        <div class="composer-layer-main"><div class="composer-layer-handle" title="คลิกค้างเพื่อลากสลับลำดับเลเยอร์">⠿</div>
        <span class="composer-layer-icon">${getWidgetIcon(w.type)}</span>
        <span class="composer-layer-name"></span>
        </div>
        <div class="composer-layer-actions">
          <div class="composer-layer-order-controls">
            <button type="button" class="composer-btn-layer-action" data-action="move-up" title="เลื่อน Layer ขึ้น" aria-label="เลื่อน Layer ขึ้น" ${index===0?'disabled':''}>▲</button>
            <button type="button" class="composer-btn-layer-action" data-action="move-down" title="เลื่อน Layer ลง" aria-label="เลื่อน Layer ลง" ${index===sorted.length-1?'disabled':''}>▼</button>
          </div>
          <button type="button" class="composer-btn-layer-action" data-action="toggle-hide" title="${w.hidden ? 'แสดง' : 'ซ่อน'}">
            ${w.hidden ? svgEyeOff : svgEye}
          </button>
          <button type="button" class="composer-btn-layer-action btn-layer-setting" data-action="setting" data-layer-id="${w.id}" title="ตั้งค่าวิดเจ็ต">
            ${svgSettings}
          </button>
          <button type="button" class="composer-btn-layer-action" data-action="toggle-lock" title="${w.locked ? 'ปลดล็อค' : 'ล็อค'}">
            ${w.locked ? svgLock : svgUnlock}
          </button>
          <button type="button" class="composer-btn-layer-action close-red" data-action="delete" title="ลบวิดเจ็ต">
            ${svgTrash}
          </button>
        </div>
      `;

      const title=item.querySelector('.composer-layer-name');title.textContent=w.title || w.type;title.title=w.title || w.type;
      // Drag & Drop Reordering
      item.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', w.id);
        item.classList.add('dragging');
      });

      item.addEventListener('dragover', (e) => {
        e.preventDefault();
        const rect = item.getBoundingClientRect();
        const midY = rect.top + rect.height / 2;
        if (e.clientY < midY) {
          item.classList.add('drag-over-top');
          item.classList.remove('drag-over-bottom');
        } else {
          item.classList.add('drag-over-bottom');
          item.classList.remove('drag-over-top');
        }
      });

      item.addEventListener('dragleave', () => {
        item.classList.remove('drag-over-top', 'drag-over-bottom');
      });

      item.addEventListener('drop', (e) => {
        e.preventDefault();
        item.classList.remove('drag-over-top', 'drag-over-bottom');
        const srcId = e.dataTransfer.getData('text/plain');
        const targetId = w.id;
        if (!srcId || srcId === targetId) return;

        const ordered=[...page.widgets].sort((a,b)=>(b.z || 0)-(a.z || 0));
        const srcIdx=ordered.findIndex(x=>x.id===srcId);if(srcIdx<0)return;
        const [moved]=ordered.splice(srcIdx,1);
        const targetIdx=ordered.findIndex(x=>x.id===targetId);if(targetIdx<0)return;
        const rect=item.getBoundingClientRect(),insertAfter=e.clientY>=rect.top+rect.height/2;
        ordered.splice(targetIdx+(insertAfter?1:0),0,moved);
        ordered.forEach((widget,index)=>{widget.z=ordered.length-index;});
        page.widgets=ordered.reverse();

        renderCanvasWidgets();
        renderLayersList();
        saveState();
        if (window.showToast) window.showToast(`✨ สลับลำดับเลเยอร์ ${moved.title} เรียบร้อยแล้ว`);
      });

      item.addEventListener('dragend', () => {
        document.querySelectorAll('.composer-layer-item').forEach(el => {
          el.classList.remove('dragging', 'drag-over-top', 'drag-over-bottom');
        });
      });

      item.addEventListener('click', (e) => {
        const actionBtn = e.target.closest('.composer-btn-layer-action');
        if (actionBtn) {
          e.stopPropagation();
          if(actionBtn.disabled)return;
          const act = actionBtn.dataset.action;
          if(act==='move-up' || act==='move-down'){moveLayerByOne(w.id,act==='move-up'?-1:1);return;}
          if (act === 'toggle-hide') {
            w.hidden = !w.hidden;
            renderCanvasWidgets();
            renderLayersList();
            saveState();
          } else if (act === 'toggle-lock') {
            w.locked = !w.locked;
            renderCanvasWidgets();
            renderLayersList();
            saveState();
          } else if (act === 'setting') {
            selectWidget(w.id);
            openWidgetSettings(w.id);
          } else if (act === 'delete') {
            deleteWidget(w.id);
          }
        } else {
          selectWidget(w.id);
        }
      });

      list.appendChild(item);
    });
    list.scrollTop=previousScroll;
  }

  // Align Widget
  function alignWidget(direction) {
    const widget = getSelectedWidget();
    if (!widget || widget.locked || isFullscreenWidget(widget)) return;

    if (direction === 'left') widget.x = 0;
    if (direction === 'center') widget.x = Math.round(CANVAS_WIDTH / 2 - widget.width / 2);
    if (direction === 'right') widget.x = CANVAS_WIDTH - widget.width;
    if (direction === 'top') widget.y = 0;
    if (direction === 'middle') widget.y = Math.round(CANVAS_HEIGHT / 2 - widget.height / 2);
    if (direction === 'bottom') widget.y = CANVAS_HEIGHT - widget.height;

    widget.x = Math.max(0, Math.min(CANVAS_WIDTH - widget.width, widget.x));
    widget.y = Math.max(0, Math.min(CANVAS_HEIGHT - widget.height, widget.y));

    renderCanvasWidgets();
    updateTransformInspector();
    saveState();
  }

  // Update Transform Inspector
  function updateTransformInspector() {
    const widget = getSelectedWidget();
    const inpX = document.getElementById('compPropX');
    const inpY = document.getElementById('compPropY');
    const inpW = document.getElementById('compPropW');
    const inpH = document.getElementById('compPropH');
    const inpOp = document.getElementById('compPropOp');

    if (!widget) {
      if (inpX) { inpX.value = '-'; inpX.disabled = false; }
      if (inpY) { inpY.value = '-'; inpY.disabled = false; }
      if (inpW) { inpW.value = '-'; inpW.disabled = false; }
      if (inpH) { inpH.value = '-'; inpH.disabled = false; }
      if (inpOp) inpOp.value = '100%';
      return;
    }

    const isFull = isFullscreenWidget(widget);
    if (inpX) { inpX.value = isFull ? 0 : widget.x; inpX.disabled = isFull; }
    if (inpY) { inpY.value = isFull ? 0 : widget.y; inpY.disabled = isFull; }
    if (inpW) { inpW.value = isFull ? CANVAS_WIDTH : widget.width; inpW.disabled = isFull; }
    if (inpH) { inpH.value = isFull ? CANVAS_HEIGHT : widget.height; inpH.disabled = isFull; }
    if (inpOp) inpOp.value = isFull ? `${Math.round((widget.opacity ?? 1) * 100)}% - ล็อคเต็มจอ (1920×1080)` : `${Math.round((widget.opacity ?? 1) * 100)}%`;
  }

  // Open Left Widget Customizer Drawer
  function openWidgetSettings(widgetId) {
    if (!widgetId) return;
    state.selectedWidgetId = widgetId;
    state.customizerManuallyCollapsed = false;
    renderCanvasWidgets();
    renderLayersList();
    updateTransformInspector();
    renderWidgetCustomizerPanel(widgetId);

    const leftPanel = document.getElementById('composerSidebarLeft');
    const expandBtn = document.getElementById('btnExpandCustPanel');
    if (leftPanel) leftPanel.classList.remove('collapsed');
    if (expandBtn) expandBtn.classList.remove('visible');
  }

  const openWidgetCustomizer = openWidgetSettings;

  // Setup Canvas Events with flicker-free deselect, Ctrl+Wheel Zoom, and Overlapping Context Menu
  function setupCanvasEvents() {
    const viewport = document.getElementById('composerViewport');
    const stage = document.getElementById('composerCanvasStage');
    if (!viewport || !stage) return;

    // Suppress deselect when clicking a widget
    viewport.addEventListener('click', (e) => {
      if (Date.now() < (state.suppressCanvasDeselectUntil || 0)) return;
      if (e.target.id === 'composerViewport' || e.target.id === 'composerCanvasStage' || e.target.id === 'composerCanvasOuter') {
        selectWidget(null);
      }
    });

    // Spacebar Canvas Panning & Double-Spacebar Reset (Photoshop / Figma style)
    let isSpacebarDown = false;
    let isPanningCanvas = false;
    let panStartX = 0;
    let panStartY = 0;
    let panStartScrollLeft = 0;
    let panStartScrollTop = 0;
    let lastSpacebarPressTime = 0;

    function bindSpacebarPanning(winTarget) {
      if (!winTarget || winTarget.__bpSpacebarPanningBound) return;
      winTarget.__bpSpacebarPanningBound = true;

      winTarget.addEventListener('keydown', (e) => {
        const activeTag = winTarget.document?.activeElement ? winTarget.document.activeElement.tagName.toLowerCase() : '';
        if (activeTag === 'input' || activeTag === 'textarea' || activeTag === 'select' || winTarget.document?.activeElement?.isContentEditable) return;

        if (e.code === 'Space' && !e.repeat) {
          const now = Date.now();
          if (now - lastSpacebarPressTime < 350) {
            e.preventDefault();
            autoFitCanvas();
            const vp = document.getElementById('composerViewport');
            if (vp) {
              vp.scrollLeft = (vp.scrollWidth - vp.clientWidth) / 2;
              vp.scrollTop = (vp.scrollHeight - vp.clientHeight) / 2;
            }
            if (window.showToast) window.showToast('🎯 พอดีจอ & จัดกึ่งกลางผ้าใบ (Double Spacebar)');
            lastSpacebarPressTime = 0;
            return;
          }
          lastSpacebarPressTime = now;
          isSpacebarDown = true;
          const vp = document.getElementById('composerViewport');
          if (vp) vp.style.cursor = 'grab';
        }
      });

      winTarget.addEventListener('keyup', (e) => {
        if (e.code === 'Space') {
          isSpacebarDown = false;
          isPanningCanvas = false;
          const vp = document.getElementById('composerViewport');
          if (vp) vp.style.cursor = '';
        }
      });

      winTarget.addEventListener('mousemove', (e) => {
        if (isPanningCanvas && isSpacebarDown) {
          const vp = document.getElementById('composerViewport');
          if (vp) {
            const dx = e.clientX - panStartX;
            const dy = e.clientY - panStartY;
            vp.scrollLeft = panStartScrollLeft - dx;
            vp.scrollTop = panStartScrollTop - dy;
            e.preventDefault();
          }
        }
      });

      winTarget.addEventListener('mouseup', () => {
        if (isPanningCanvas) {
          isPanningCanvas = false;
          const vp = document.getElementById('composerViewport');
          if (vp) vp.style.cursor = isSpacebarDown ? 'grab' : '';
        }
      });
    }

    bindSpacebarPanning(window);

    viewport.addEventListener('mousedown', (e) => {
      if (isSpacebarDown) {
        isPanningCanvas = true;
        panStartX = e.clientX;
        panStartY = e.clientY;
        panStartScrollLeft = viewport.scrollLeft;
        panStartScrollTop = viewport.scrollTop;
        viewport.style.cursor = 'grabbing';
        e.preventDefault();
        e.stopPropagation();
      }
    });

    // Ctrl + Mouse Wheel Canvas Zoom
    viewport.addEventListener('wheel', (e) => {
      if (e.ctrlKey) {
        e.preventDefault();
        const delta = e.deltaY < 0 ? 0.05 : -0.05;
        const currentZoom = state.zoom || 0.45;
        const newZoom = Math.min(1.5, Math.max(0.2, currentZoom + delta));
        setZoom(newZoom);
      }
    }, { passive: false });

    // Right-Click Context Menu on Canvas Stage
    const hideContextMenu = () => {
      const existing = document.getElementById('composerContextMenu');
      if (existing) existing.remove();
    };

    document.addEventListener('click', (e) => {
      if (!e.target.closest('#composerContextMenu')) {
        hideContextMenu();
      }
    });

    stage.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      e.stopPropagation();
      hideContextMenu();

      const page = getActivePage();
      if (!page || !page.widgets || page.widgets.length === 0) return;

      const rect = stage.getBoundingClientRect();
      const scale = state.zoom > 2 ? state.zoom / 100 : (state.zoom || 0.45);
      const canvasX = (e.clientX - rect.left) / scale;
      const canvasY = (e.clientY - rect.top) / scale;

      // Find all widgets at this coordinate (Fullscreen widgets cover [0, 0, CANVAS_WIDTH, CANVAS_HEIGHT])
      const widgetsAtPoint = page.widgets.filter(w => {
        if (isFullscreenWidget(w)) {
          return canvasX >= 0 && canvasX <= CANVAS_WIDTH && canvasY >= 0 && canvasY <= CANVAS_HEIGHT;
        }
        return canvasX >= w.x && canvasX <= (w.x + w.width) &&
               canvasY >= w.y && canvasY <= (w.y + w.height);
      }).sort((a, b) => (b.z || 0) - (a.z || 0));

      if (widgetsAtPoint.length === 0) return;

      const menu = document.createElement('div');
      menu.id = 'composerContextMenu';
      menu.className = 'composer-context-menu';
      menu.style.left = `${e.clientX + 4}px`;
      menu.style.top = `${e.clientY + 4}px`;

      let menuHtml = `
        <div class="composer-ctx-header">
          <span>📦 วิดเจ็ตที่จุดนี้</span>
          <span style="color:#38bdf8; font-weight:700;">${widgetsAtPoint.length} เลเยอร์</span>
        </div>
        <div class="composer-ctx-list">
      `;

      widgetsAtPoint.forEach(targetW => {
        menuHtml += `
          <div class="composer-ctx-widget-row" data-widget-id="${targetW.id}">
            <div class="composer-ctx-widget-info">
              <span class="composer-ctx-widget-icon">${getWidgetIcon(targetW.type)}</span>
              <span class="composer-ctx-widget-title">${targetW.title}</span>
            </div>
            <span class="composer-ctx-arrow">▶</span>
            <div class="composer-ctx-flyout-menu">
              <div class="composer-ctx-action" data-action="setting">⚙️ ตั้งค่าวิดเจ็ต</div>
              <div class="composer-ctx-action" data-action="duplicate">📋 ทำซ้ำ</div>
              <div class="composer-ctx-action" data-action="toggle-hide">${targetW.hidden ? '👁️‍🗨️ แสดงวิดเจ็ต' : '👁️ ซ่อนวิดเจ็ต'}</div>
              <div class="composer-ctx-action" data-action="toggle-lock">${targetW.locked ? '🔓 ปลดล็อควิดเจ็ต' : '🔒 ล็อควิดเจ็ต'}</div>
              <div class="composer-ctx-divider"></div>
              <div class="composer-ctx-action danger" data-action="delete">🗑️ ลบวิดเจ็ต</div>
            </div>
          </div>
        `;
      });

      menuHtml += `</div>`;
      menu.innerHTML = menuHtml;
      document.body.appendChild(menu);

      // Bind flyout actions
      menu.querySelectorAll('.composer-ctx-widget-row').forEach(row => {
        const wid = row.dataset.widgetId;
        const targetW = page.widgets.find(w => w.id === wid);
        if (!targetW) return;

        row.querySelectorAll('.composer-ctx-action').forEach(actBtn => {
          actBtn.addEventListener('click', (ev) => {
            ev.stopPropagation();
            hideContextMenu();
            const action = actBtn.dataset.action;
            if (action === 'setting') {
              selectWidget(targetW.id);
              openWidgetSettings(targetW.id);
            } else if (action === 'duplicate') {
              duplicateWidget(targetW.id);
            } else if (action === 'toggle-hide') {
              targetW.hidden = !targetW.hidden;
              renderCanvasWidgets();
              renderLayersList();
              saveState();
            } else if (action === 'toggle-lock') {
              targetW.locked = !targetW.locked;
              renderCanvasWidgets();
              renderLayersList();
              saveState();
            } else if (action === 'delete') {
              deleteWidget(targetW.id);
            }
          });
        });
      });
    });
  }

  // Render Left Customizer Panel with all settings for the selected widget
  function renderWidgetCustomizerPanel(id) {
    const studioRoot=window.document.getElementById('win-composer');
    if(!studioRoot)return;
    const document=new Proxy(studioRoot.ownerDocument,{get(target,key){
      if(key==='getElementById')return id=>studioRoot.querySelector('#'+CSS.escape(id));
      if(key==='querySelector')return selector=>studioRoot.querySelector(selector);
      if(key==='querySelectorAll')return selector=>studioRoot.querySelectorAll(selector);
      const value=Reflect.get(target,key,target);return typeof value==='function'?value.bind(target):value;
    }});

    let demoHtml = '';
    let specificHtml = '';
    const page = getActivePage();
    if (!page) return;
    const w = page.widgets.find(x => x.id === id);
    if (!w) return;

    const iconEl = document.getElementById('compCustIcon');
    const titleEl = document.getElementById('compCustTitle');
    const typeEl = document.getElementById('compCustType');
    const bodyEl = document.getElementById('composerCustomizerBody');
    if (!bodyEl) return;
    const settingsChanged=bodyEl.dataset.widgetId!==String(id);bodyEl.dataset.widgetId=String(id);

    let dispTitle = w.title;
    let dispType = 'การปรับแต่งวิดเจ็ต';
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      if (mode === 'danmaku') {
        dispTitle = 'แชทลอยหน้าจอ ดันมากุ';
        dispType = 'วิดเจ็ตแชทลอยหน้าจอแบบ Danmaku';
      } else if (mode === 'balloon') {
        dispTitle = 'บอลลูนแชท';
        dispType = 'วิดเจ็ตแชทสไตล์บอลลูนคำพูด';
      } else if (mode === 'character') {
        dispTitle = 'แชทตัวละคร';
        dispType = 'วิดเจ็ตแชทพร้อมตัวละครสนทนา';
      } else {
        dispTitle = 'กล่องแชทมาตรฐาน';
        dispType = 'วิดเจ็ตกล่องแชทสด';
      }
    } else {
      const typeNames = {
        clock: 'วิดเจ็ตนาฬิกาสตรีม',
        text: 'วิดเจ็ตแถบข้อความประกาศ',
        webcam: 'วิดเจ็ตกรอบเว็บแคม',
        goal: 'วิดเจ็ตเป้าหมายยอดผู้ติดตาม',
        viewer: 'วิดเจ็ตตัวนับยอดผู้ชมสด',
        character: 'วิดเจ็ตตัวละครพูด Replie',
        image: 'วิดเจ็ตกรอบรูปภาพแบนเนอร์',
        video: 'วิดเจ็ตวิดีโอลูป',
        alert: 'วิดเจ็ตเบราว์เซอร์ URL ภายนอก',
        now_playing: 'วิดเจ็ตเพลงที่กำลังเล่น',
        emote_party: 'วิดเจ็ตปาร์ตี้อีโมทลอย'
      };
      dispType = typeNames[w.type] || 'การปรับแต่งวิดเจ็ต';
    }

    if (iconEl) iconEl.textContent = getWidgetIcon(w.type);
    if (titleEl) titleEl.textContent = dispTitle;
    if (typeEl) typeEl.textContent = dispType;

    // Helper binder for inputs
    const bindField = (elId, key, type = 'text', suffix = '') => {
      const el = document.getElementById(elId);
      if (!el) return;
      const handler = () => {
        if (type === 'checkbox') {
          w[key] = el.checked;
        } else if (type === 'number') {
          w[key] = parseFloat(el.value);
          const lbl = document.getElementById(elId + 'Val');
          if (lbl) lbl.textContent = el.value + suffix;
        } else if (type === 'opacity') {
          w[key] = parseFloat(el.value) / 100;
          const lbl = document.getElementById(elId + 'Val');
          if (lbl) lbl.textContent = el.value + '%';
        } else {
          w[key] = el.value;
        }
        renderCanvasWidgets();
        renderLayersList();
        updateTransformInspector();
        saveState();
      };
      el.addEventListener('input', handler);
      el.addEventListener('change', handler);
    };

    // Build Demo Action Bar HTML with interactive custom input and live test
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      if (mode === 'danmaku') {
        demoHtml = `
          <div class="comp-demo-section" style="background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.25); border-radius:8px; padding:10px; margin-bottom:12px;">
            <div class="comp-demo-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span class="comp-demo-title" style="font-size:12.5px; font-weight:700; color:#38bdf8;">⚡ ทดสอบกระสุนดันมากุบนจอ</span>
              <span style="font-size:11px; color:#94a3b8;">วิ่งบนจอตามโซน</span>
            </div>
            <div style="display:flex; gap:6px; margin-bottom:8px;">
              <input type="text" class="cwc-input-text" id="compChatDemoInput" placeholder="พิมพ์ข้อความกระสุนที่นี่..." style="flex:1; padding:6px 10px; font-size:12px; background:#111215; border:1px solid rgba(255,255,255,0.12); border-radius:6px; color:#ffffff;">
              <button type="button" class="btn-comp-demo-action" id="btnCompChatDemoSend" style="padding:6px 14px; font-weight:700; background:#3b82f6; color:#ffffff;">ส่ง</button>
            </div>
            <div class="comp-demo-actions" style="display:flex; gap:6px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoDanmakuLoop" style="flex:1;">▶ เล่นกระสุนดันมากุสด</button>
              <button type="button" class="btn-comp-demo-action" id="btnDemoDanmakuSingle" style="flex:1;">⚡ ปล่อย 1 ข้อความ</button>
              <button type="button" class="btn-comp-demo-action" id="btnDemoChatClear" style="padding:6px 10px;" title="ล้างข้อความทั้งหมด">🧹</button>
            </div>
          </div>
        `;
      } else if (mode === 'balloon') {
        demoHtml = `
          <div class="comp-demo-section" style="background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.25); border-radius:8px; padding:10px; margin-bottom:12px;">
            <div class="comp-demo-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span class="comp-demo-title" style="font-size:12.5px; font-weight:700; color:#38bdf8;">💬 ทดสอบบอลลูนคำพูด</span>
              <span style="font-size:11px; color:#94a3b8;">บอลลูนเด้งสด</span>
            </div>
            <div style="display:flex; gap:6px; margin-bottom:8px;">
              <input type="text" class="cwc-input-text" id="compChatDemoInput" placeholder="พิมพ์ข้อความบอลลูน..." style="flex:1; padding:6px 10px; font-size:12px; background:#111215; border:1px solid rgba(255,255,255,0.12); border-radius:6px; color:#ffffff;">
              <button type="button" class="btn-comp-demo-action" id="btnCompChatDemoSend" style="padding:6px 14px; font-weight:700; background:#3b82f6; color:#ffffff;">ส่ง</button>
            </div>
            <div class="comp-demo-actions" style="display:flex; gap:6px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoBalloonSingle" style="flex:1;">💬 ส่งบอลลูน 1 ข้อความ</button>
              <button type="button" class="btn-comp-demo-action" id="btnDemoChatClear" style="padding:6px 10px;" title="ล้างข้อความทั้งหมด">🧹</button>
            </div>
          </div>
        `;
      } else if (mode === 'character') {
        demoHtml = `
          <div class="comp-demo-section" style="background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.25); border-radius:8px; padding:10px; margin-bottom:12px;">
            <div class="comp-demo-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span class="comp-demo-title" style="font-size:12.5px; font-weight:700; color:#38bdf8;">🎭 ทดสอบบทพูดตัวละคร</span>
              <span style="font-size:11px; color:#94a3b8;">ตัวละครขยับพร้อมคำพูด</span>
            </div>
            <div style="display:flex; gap:6px; margin-bottom:8px;">
              <input type="text" class="cwc-input-text" id="compChatDemoInput" placeholder="พิมพ์ให้ตัวละครพูด..." style="flex:1; padding:6px 10px; font-size:12px; background:#111215; border:1px solid rgba(255,255,255,0.12); border-radius:6px; color:#ffffff;">
              <button type="button" class="btn-comp-demo-action" id="btnCompChatDemoSend" style="padding:6px 14px; font-weight:700; background:#3b82f6; color:#ffffff;">ส่ง</button>
            </div>
            <div class="comp-demo-actions">
              <button type="button" class="btn-comp-demo-action" id="btnDemoCharTalk" style="width:100%;">▶ สุ่มบทพูดตัวละครสด</button>
            </div>
          </div>
        `;
      } else {
        demoHtml = `
          <div class="comp-demo-section" style="background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.25); border-radius:8px; padding:10px; margin-bottom:12px;">
            <div class="comp-demo-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span class="comp-demo-title" style="font-size:12.5px; font-weight:700; color:#38bdf8;">🎮 ทดสอบจำลองส่งข้อความแชท</span>
              <span style="font-size:11px; color:#94a3b8;">พิมพ์ส่งข้อความขึ้นจอสด</span>
            </div>
            <div style="display:flex; gap:6px; margin-bottom:8px;">
              <input type="text" class="cwc-input-text" id="compChatDemoInput" placeholder="พิมพ์ข้อความทดสอบที่นี่..." style="flex:1; padding:6px 10px; font-size:12px; background:#111215; border:1px solid rgba(255,255,255,0.12); border-radius:6px; color:#ffffff;">
              <button type="button" class="btn-comp-demo-action" id="btnCompChatDemoSend" style="padding:6px 14px; font-weight:700; background:#3b82f6; color:#ffffff;">ส่ง</button>
            </div>
            <div class="comp-demo-actions" style="display:flex; gap:6px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoChatLoop" style="flex:1;">▶ เล่นแชทต่อเนื่อง</button>
              <button type="button" class="btn-comp-demo-action" id="btnDemoChatSingle" style="flex:1;">➕ สุ่ม 1 ข้อความ</button>
              <button type="button" class="btn-comp-demo-action" id="btnDemoChatClear" style="padding:6px 10px;" title="ล้างข้อความทั้งหมด">🧹</button>
            </div>
          </div>
        `;
      }
    } else if (w.type === 'clock') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🕒 ทดสอบสลับรูปแบบเวลา</span>
            <span style="font-size:11px; color:#94a3b8;">นาฬิกาเดินสด</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoClockToggle">🕒 สลับ 12 / 24 ชม.</button>
            <button type="button" class="btn-comp-demo-action" id="btnDemoClockSecs">⏱️ สลับแสดงวินาที</button>
          </div>
        </div>
      `;
    } else if (w.type === 'text') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🔤 ทดสอบตัววิ่ง Marquee</span>
            <span style="font-size:11px; color:#94a3b8;">ข้อความเลื่อนวิ่งสด</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoTextTicker">▶ สลับโหมดตัววิ่ง</button>
          </div>
        </div>
      `;
    } else if (w.type === 'webcam') {
      demoHtml = '';
    } else if (w.type === 'goal') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🎯 ทดสอบยอดเป้าหมาย</span>
            <span style="font-size:11px; color:#94a3b8;">หลอดเพิ่มแบบอนิเมชัน</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoGoalPlus">🎉 จำลองผู้ติดตามใหม่ (+50)</button>
            <button type="button" class="btn-comp-demo-action" id="btnDemoGoalReset">🔄 รีเซ็ตยอด</button>
          </div>
        </div>
      `;
    } else if (w.type === 'viewer') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">👥 ทดสอบตัวนับยอดผู้ชมสด</span>
            <span style="font-size:11px; color:#94a3b8;">อนิเมชันตัวเลขหมุนนุ่มนวล</span>
          </div>
          <div class="comp-demo-actions" style="display:flex; gap:6px;">
            <button type="button" class="btn-comp-demo-action" id="btnDemoViewerRandom" style="flex:1;">🎲 สุ่มยอดคนดู</button>
            <button type="button" class="btn-comp-demo-action" id="btnDemoViewerAdd" style="flex:1;">📈 เพิ่ม +50 คน</button>
            <button type="button" class="btn-comp-demo-action" id="btnDemoViewerSub" style="flex:1;">📉 ลด -30 คน</button>
            <button type="button" class="btn-comp-demo-action" id="btnViewerUseLive">↩ กลับไปใช้ยอดจริง</button>
          </div>
        </div>
      `;
    } else if (w.type === 'ask') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">📊 การตั้งค่าโพลสำรวจ (ASK)</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">หัวข้อคำถาม</span>
              <input type="text" class="cwc-input" id="compAskQuestion" value="${w.askQuestion || 'โหวตเลือกอะไรดีในสตรีมนี้?'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">รูปแบบ Layout</span>
              <select class="cwc-select" id="compAskLayout">
                <option value="vright" ${(w.askLayout || 'vright') === 'vright' ? 'selected' : ''}>แถวเดี่ยวแนวตั้ง (Right / Tower)</option>
                <option value="hband" ${(w.askLayout || 'vright') === 'hband' ? 'selected' : ''}>แถบแนวนอนยาว (Horizontal Band)</option>
                <option value="minimal" ${(w.askLayout || 'vright') === 'minimal' ? 'selected' : ''}>การ์ดมินิมอล (Card Minimal)</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">การนับถอยหลัง</span>
              <select class="cwc-select" id="compAskCountdownStyle">
                <option value="text" ${(w.askCountdownStyle || 'text') === 'text' ? 'selected' : ''}>แสดงเวลาตัวเลข</option>
                <option value="bar" ${(w.askCountdownStyle || 'text') === 'bar' ? 'selected' : ''}>แถบหลอดเวลาวิ่ง</option>
              </select>
            </div>
            <div style="margin-top:10px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoAskVote" style="width:100%; padding:8px; font-weight:700;">📊 จำลองคะแนนโหวตสด</button>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'giveaway') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎁 การตั้งค่าสุ่มแจกรางวัล (Giveaway)</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">เวลานับถอยหลัง (วินาที)</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compGiveawayDuration" min="10" max="120" value="${w.giveawayDuration || 30}">
                <span class="cwc-slider-val" id="compGiveawayDurationVal">${w.giveawayDuration || 30}s</span>
              </div>
            </div>
            <div style="margin-top:10px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoGiveawayDraw" style="width:100%; padding:8px; font-weight:700;">🎁 ทดสอบเริ่มสุ่มแจกรางวัล</button>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'playroom') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎮 การตั้งค่า Playroom Interactive</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">URL ของ Playroom</span>
              <input type="text" class="cwc-input" id="compPlayroomUrl" value="${w.playroomUrl || 'http://127.0.0.1:8080/playroom-widget'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">เปิดใช้งาน Chroma Key</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compPlayroomCkEnabled" ${w.ckEnabled ? 'checked' : ''}>
                <span class="cwc-switch-slider"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีฉากเขียวที่ตัดออก (Chroma)</span>
              <div class="cwc-color-wrap">
                <input type="color" class="cwc-color-pick" id="compPlayroomCkColor" value="${w.ckColor || '#00ff00'}">
              </div>
            </div>
          </div>
        </div>
      `;

    } else if (w.type === 'emote_party') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🎉 ทดสอบปาร์ตี้อีโมทสด</span>
            <span style="font-size:11px; color:#94a3b8;">พุ่งลอยบนจอสด</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoEmoteParty">🎉 ปล่อยอีโมททดสอบ</button>
          </div>
        </div>
      `;
    } else if (w.type === 'now_playing') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🎵 ทดสอบเพลงที่กำลังเล่น</span>
            <span style="font-size:11px; color:#94a3b8;">เปลี่ยนเพลงสด</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoNowPlayingNext">🎵 จำลองเพลงถัดไป</button>
          </div>
        </div>
      `;
    }

    // ==========================================
    // 1. CHAT WIDGET CUSTOMIZER (INTEGRATED FULL CHAT WIDGET CUSTOMIZER ACCORDIONS)
    // ==========================================
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';

      // Helper function for full categorized accordion sections
      function renderFullChatAccordionSections(w) {
        const fonts = [
          'Kanit',
          'Noto Sans Thai Looped',
          'Sarabun',
          'Prompt',
          'Mitr',
          'Chonburi',
          'Mali',
          'Bai Jamjuree',
          'Krub',
          'Taviraj',
          'Pattaya',
          'Itim',
          'Pridi',
          'Athiti',
          'Chakra Petch',
          'Kavivanar',
          'Charmonman',
          'Sriracha',
          'KoHo',
          'Fahkwang',
          'Roboto',
          'Inter',
          'Outfit',
          'Fredoka',
          'Bebas Neue',
          'Montserrat',
          'Poppins',
          'Open Sans',
          'Press Start 2P'
        ];

        let fontOpts = fonts.map(f => `<option value="${f}" ${(w.fontFamily || 'Kanit') === f ? 'selected' : ''}>${f}</option>`).join('');

        return `
          <!-- SECTION 1: LAYOUT & STRUCTURE -->
          <div class="cwc-section">
            <div class="cwc-section-header">
              <span class="cwc-section-title">📐 การจัดวาง & สไตล์โครงสร้าง</span>
              <span class="cwc-section-toggle">▼</span>
            </div>
            <div class="cwc-section-body">
              <div class="cwc-row">
                <span class="cwc-label">รูปแบบการจัดวาง:</span>
                <select class="cwc-select" id="cwcLayout">
                  <option value="compact" ${(w.layout || 'compact') === 'compact' ? 'selected' : ''}>ข้อความกระชับติดกัน</option>
                  <option value="bubble" ${w.layout === 'bubble' ? 'selected' : ''}>บอลลูนแยกกล่องชัดเจน</option>
                  <option value="stacked" ${w.layout==='stacked'?'selected':''}>ชื่ออยู่เหนือข้อความ</option>
                  <option value="inline_no_logo" ${w.layout==='inline_no_logo'?'selected':''}>บรรทัดเดียว ไม่แสดงโลโก้</option>
                  <option value="stacked_no_logo" ${w.layout==='stacked_no_logo'?'selected':''}>สองบรรทัด ไม่แสดงโลโก้</option>
                  <option value="message_only" ${w.layout==='message_only'?'selected':''}>แสดงเฉพาะข้อความ</option>
                  <option value="inline" ${w.layout === 'inline' ? 'selected' : ''}>ชื่อและข้อความบรรทัดเดียว</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ทิศทางข้อความ:</span>
                <select class="cwc-select" id="cwcDirection">
                  <option value="bottom-up" ${(w.direction || 'bottom-up') === 'bottom-up' ? 'selected' : ''}>ข้อความใหม่ดันจากล่างขึ้นบน</option>
                  <option value="top-down" ${w.direction === 'top-down' ? 'selected' : ''}>ข้อความใหม่ไหลจากบนลงล่าง</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">จัดตำแหน่งชิด:</span>
                <select class="cwc-select" id="cwcAlign">
                  <option value="left" ${(w.align || 'left') === 'left' ? 'selected' : ''}>ชิดซ้าย</option>
                  <option value="center" ${w.align === 'center' ? 'selected' : ''}>กึ่งกลาง</option>
                  <option value="right" ${w.align === 'right' ? 'selected' : ''}>ชิดขวา</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ระยะห่างระหว่างข้อความ:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcMsgSpacing" min="2" max="24" step="1" value="${w.msgSpacing ?? 6}">
                  <span class="cwc-slider-val" id="cwcMsgSpacingVal">${w.msgSpacing ?? 6}px</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">จำนวนข้อความสูงสุด:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcMaxMessages" min="5" max="50" step="1" value="${w.maxMessages || 15}">
                  <span class="cwc-slider-val" id="cwcMaxMessagesVal">${w.maxMessages || 15}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- SECTION 2: TYPOGRAPHY & FONT -->
          <div class="cwc-section">
            <div class="cwc-section-header">
              <span class="cwc-section-title">✍️ ฟอนต์ & ขนาดตัวอักษร</span>
              <span class="cwc-section-toggle">▼</span>
            </div>
            <div class="cwc-section-body">
              <div class="cwc-row">
                <span class="cwc-label">ตระกูลฟอนต์:</span>
                <select class="cwc-select" id="cwcFontFamily">
                  ${fontOpts}
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ขนาดตัวอักษร:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcFontSize" min="11" max="36" step="1" value="${w.fontSize || 15}">
                  <span class="cwc-slider-val" id="cwcFontSizeVal">${w.fontSize || 15}px</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ความหนาตัวอักษร:</span>
                <select class="cwc-select" id="cwcFontWeight">
                  <option value="300" ${w.fontWeight === '300' ? 'selected' : ''}>300 บางเบา</option>
                  <option value="400" ${(w.fontWeight || '500') === '400' ? 'selected' : ''}>400 ปกติ</option>
                  <option value="500" ${(w.fontWeight || '500') === '500' ? 'selected' : ''}>500 ปานกลาง</option>
                  <option value="600" ${w.fontWeight === '600' ? 'selected' : ''}>600 หนาแน่น</option>
                  <option value="700" ${w.fontWeight === '700' ? 'selected' : ''}>700 หนาพิเศษ</option>
                  <option value="900" ${w.fontWeight === '900' ? 'selected' : ''}>900 หนาที่สุด</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">สีชื่อผู้ส่ง:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcUsernameColor" value="${w.usernameColor || '#38bdf8'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">สีข้อความแชท:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcMessageColor" value="${w.fontColor || '#ffffff'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">เส้นขอบตัวอักษร:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcTextStroke" ${w.textStroke ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row" id="cwcTextStrokeWidthRow" style="display:${w.textStroke ? 'flex' : 'none'};">
                <span class="cwc-label">ความหนาขอบตัวอักษร:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcTextStrokeWidth" min="1" max="5" step="0.5" value="${w.textStrokeWidth || 1.5}">
                  <span class="cwc-slider-val" id="cwcTextStrokeWidthVal">${w.textStrokeWidth || 1.5}px</span>
                </div>
              </div>
              <div class="cwc-row" id="cwcTextStrokeColorRow" style="display:${w.textStroke ? 'flex' : 'none'};">
                <span class="cwc-label">สีขอบตัวอักษร:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcTextStrokeColor" value="${w.strokeColor || '#000000'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">เงาตัวอักษร:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcTextShadow" ${w.textShadow !== false ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row" id="cwcTextShadowBlurRow" style="display:${w.textShadow !== false ? 'flex' : 'none'};">
                <span class="cwc-label">ระยะเบลอเงา:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcTextShadowBlur" min="0" max="12" step="1" value="${w.textShadowBlur ?? 3}">
                  <span class="cwc-slider-val" id="cwcTextShadowBlurVal">${w.textShadowBlur ?? 3}px</span>
                </div>
              </div>
              <div class="cwc-row" id="cwcTextShadowColorRow" style="display:${w.textShadow !== false ? 'flex' : 'none'};">
                <span class="cwc-label">สีเงาตัวอักษร:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcTextShadowColor" value="${w.textShadowColor || '#000000'}">
                </div>
              </div>
            </div>
          </div>

          <!-- SECTION 3: MESSAGE BOX & BUBBLE (กล่องข้อความแต่ละอัน) -->
          <div class="cwc-section">
            <div class="cwc-section-header">
              <span class="cwc-section-title">💬 กล่องข้อความ & บับเบิล</span>
              <span class="cwc-section-toggle">▼</span>
            </div>
            <div class="cwc-section-body">
              <div class="cwc-row">
                <span class="cwc-label">เปิดใช้งานกล่องข้อความ:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcBoxEnabled" ${w.boxEnabled !== false ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ความกว้างกล่อง:</span>
                <select class="cwc-select" id="cwcBoxWidth">
                  <option value="fit" ${(w.boxWidth || 'fit') === 'fit' ? 'selected' : ''}>พอดีเนื้อหาข้อความ</option>
                  <option value="full" ${w.boxWidth === 'full' ? 'selected' : ''}>เต็มความกว้างแถว</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">สีพื้นหลังกล่องข้อความ:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcBgColor" value="${w.bgColor || '#1e1f22'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ความโปร่งใสกล่องข้อความ:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcBgOpacity" min="0" max="100" step="5" value="${Math.round((w.bgOpacity ?? 0.85) * 100)}">
                  <span class="cwc-slider-val" id="cwcBgOpacityVal">${Math.round((w.bgOpacity ?? 0.85) * 100)}%</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ความโค้งมนมุมกล่อง:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcBoxRadius" min="0" max="28" step="1" value="${w.boxRadius ?? 8}">
                  <span class="cwc-slider-val" id="cwcBoxRadiusVal">${w.boxRadius ?? 8}px</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ระยะขอบภายใน:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcBoxPadding" min="4" max="24" step="1" value="${w.boxPadding || 10}">
                  <span class="cwc-slider-val" id="cwcBoxPaddingVal">${w.boxPadding || 10}px</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">เส้นขอบกล่องข้อความ:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcBoxBorder" ${w.boxBorder ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row" id="cwcBoxBorderWidthRow" style="display:${w.boxBorder ? 'flex' : 'none'};">
                <span class="cwc-label">ความหนาเส้นขอบ:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcBoxBorderWidth" min="1" max="6" step="1" value="${w.boxBorderWidth || 1}">
                  <span class="cwc-slider-val" id="cwcBoxBorderWidthVal">${w.boxBorderWidth || 1}px</span>
                </div>
              </div>
              <div class="cwc-row" id="cwcBoxBorderColorRow" style="display:${w.boxBorder ? 'flex' : 'none'};">
                <span class="cwc-label">สีเส้นขอบ:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcBoxBorderColor" value="${w.boxBorderColor || '#38bdf8'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">เงากล่องข้อความ:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcBoxShadow" ${w.boxShadow !== false ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">เรืองแสงนีออนรอบกล่อง:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcBoxGlow" ${w.boxGlow ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row" id="cwcBoxGlowColorRow" style="display:${w.boxGlow ? 'flex' : 'none'};">
                <span class="cwc-label">สีเรืองแสง:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcBoxGlowColor" value="${w.boxGlowColor || '#38bdf8'}">
                </div>
              </div>
            </div>
          </div>

          <!-- SECTION: CHAT CONTAINER BOX (กล่องพื้นหลังรวมของแชท) -->
          <div class="cwc-section">
            <div class="cwc-section-header">
              <span class="cwc-section-title">🖼 กล่องพื้นหลังแชท (Container Box)</span>
              <span class="cwc-section-toggle">▼</span>
            </div>
            <div class="cwc-section-body">
              <div class="cwc-row">
                <span class="cwc-label">เปิดใช้งานกล่องพื้นหลัง:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="compChatContainerBgEnabled" ${w.containerBgEnabled ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div id="compChatContainerSettingsWrap" style="display:${w.containerBgEnabled ? 'block' : 'none'};">
                <div class="cwc-row">
                  <span class="cwc-label">สีพื้นหลังกล่อง:</span>
                  <div class="cwc-color-wrap">
                    <input type="color" class="cwc-color-pick" id="compChatContainerBgColor" value="${w.containerBgColor || '#0a0e1a'}">
                  </div>
                </div>
                <div class="cwc-row">
                  <span class="cwc-label">ความโปร่งใสกล่อง:</span>
                  <div class="cwc-slider-wrap">
                    <input type="range" class="cwc-slider" id="compChatContainerBgOpacity" min="0" max="100" step="5" value="${Math.round(((w.containerBgOpacity !== undefined) ? w.containerBgOpacity : 0.75) * 100)}">
                    <span class="cwc-slider-val" id="compChatContainerBgOpacityVal">${Math.round(((w.containerBgOpacity !== undefined) ? w.containerBgOpacity : 0.75) * 100)}%</span>
                  </div>
                </div>
                <div class="cwc-row">
                  <span class="cwc-label">ความโค้งมนของกล่อง:</span>
                  <div class="cwc-slider-wrap">
                    <input type="range" class="cwc-slider" id="compChatContainerRadius" min="0" max="32" step="1" value="${(w.containerRadius !== undefined) ? w.containerRadius : 8}">
                    <span class="cwc-slider-val" id="compChatContainerRadiusVal">${(w.containerRadius !== undefined) ? w.containerRadius : 8}px</span>
                  </div>
                </div>
                <div class="cwc-row">
                  <span class="cwc-label">เส้นขอบกล่อง:</span>
                  <label class="cwc-switch">
                    <input type="checkbox" id="compChatContainerBorder" ${w.containerBorder ? 'checked' : ''}>
                    <span class="cwc-switch-slider"></span>
                  </label>
                </div>
                <div class="cwc-row" id="compChatContainerBorderWidthRow" style="display:${w.containerBorder ? 'flex' : 'none'};">
                  <span class="cwc-label">ความหนาขอบกล่อง:</span>
                  <div class="cwc-slider-wrap">
                    <input type="range" class="cwc-slider" id="compChatContainerBorderWidth" min="1" max="6" step="1" value="${w.containerBorderWidth || 1}">
                    <span class="cwc-slider-val" id="compChatContainerBorderWidthVal">${w.containerBorderWidth || 1}px</span>
                  </div>
                </div>
                <div class="cwc-row" id="compChatContainerBorderColorRow" style="display:${w.containerBorder ? 'flex' : 'none'};">
                  <span class="cwc-label">สีเส้นขอบกล่อง:</span>
                  <div class="cwc-color-wrap">
                    <input type="color" class="cwc-color-pick" id="compChatContainerBorderColor" value="${w.containerBorderColor || '#38bdf8'}">
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- SECTION 4: ANIMATIONS & AUTO-HIDE -->
          <div class="cwc-section">
            <div class="cwc-section-header">
              <span class="cwc-section-title">✨ แอนิเมชัน & ซ่อนข้อความ</span>
              <span class="cwc-section-toggle">▼</span>
            </div>
            <div class="cwc-section-body">
              <div class="cwc-row">
                <span class="cwc-label">แอนิเมชันขาเข้า (Anim In):</span>
                <select class="cwc-select" id="compChatAnimIn">
                  <option value="slide" ${(w.animation || w.animIn || 'slide') === 'slide' ? 'selected' : ''}>เลื่อนเข้า (Slide)</option>
                  <option value="fade" ${(w.animation || w.animIn) === 'fade' ? 'selected' : ''}>ค่อยๆ ปรากฏ (Fade)</option>
                  <option value="pop" ${(w.animation || w.animIn) === 'pop' ? 'selected' : ''}>เด้งขยาย (Pop)</option>
                  <option value="bounce" ${(w.animation || w.animIn) === 'bounce' ? 'selected' : ''}>กระเด้ง (Bounce)</option>
                  <option value="none" ${(w.animation || w.animIn) === 'none' ? 'selected' : ''}>ไม่มีแอนิเมชัน (None)</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">แอนิเมชันขาออก (Anim Out):</span>
                <select class="cwc-select" id="compChatAnimOut">
                  <option value="auto" ${(w.exitAnimation || w.animOut || 'auto') === 'auto' ? 'selected' : ''}>ตามขาเข้า (Auto)</option>
                  <option value="fade" ${(w.exitAnimation || w.animOut) === 'fade' ? 'selected' : ''}>ค่อยๆ จางหาย (Fade)</option>
                  <option value="slide-left" ${(w.exitAnimation || w.animOut) === 'slide-left' ? 'selected' : ''}>เลื่อนออกซ้าย (Slide Left)</option>
                  <option value="slide-right" ${(w.exitAnimation || w.animOut) === 'slide-right' ? 'selected' : ''}>เลื่อนออกขวา (Slide Right)</option>
                  <option value="slide-up" ${(w.exitAnimation || w.animOut) === 'slide-up' ? 'selected' : ''}>เลื่อนขึ้นบน (Slide Up)</option>
                  <option value="slide-down" ${(w.exitAnimation || w.animOut) === 'slide-down' ? 'selected' : ''}>เลื่อนลงล่าง (Slide Down)</option>
                  <option value="none" ${(w.exitAnimation || w.animOut) === 'none' ? 'selected' : ''}>หายทันที (None)</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ซ่อนข้อความอัตโนมัติ:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="compChatAutoHide" ${w.autoHide ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row" id="compChatHideAfterRow" style="display:${w.autoHide ? 'flex' : 'none'};">
                <span class="cwc-label">ระยะเวลาก่อนซ่อนข้อความ:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compChatHideAfter" min="2" max="60" step="1" value="${w.hideAfter || 8}">
                  <span class="cwc-slider-val" id="compChatHideAfterVal">${w.hideAfter || 8} วินาที</span>
                </div>
              </div>
            </div>
          </div>
        `;
      }

      if (mode === 'danmaku') {
        specificHtml = `
          <!-- DANMAKU CONTROLS -->
          <div class="cwc-section">
            <div class="cwc-section-header">
              <span class="cwc-section-title">⚡ ตั้งค่ากระสุนดันมากุ</span>
              <span class="cwc-section-toggle">▼</span>
            </div>
            <div class="cwc-section-body">
              <div class="cwc-row">
                <span class="cwc-label">ความเร็วการวิ่ง:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcSliderDuration" min="3" max="15" step="0.5" value="${w.speed || 6}">
                  <span class="cwc-slider-val" id="cwcSliderDurationVal">${w.speed || 6}s</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ความสูงแต่ละเลน:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcSliderLaneHeight" min="25" max="70" step="1" value="${w.laneHeight || 40}">
                  <span class="cwc-slider-val" id="cwcSliderLaneHeightVal">${w.laneHeight || 40}px</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ตำแหน่งการแสดงผล:</span>
                <select class="cwc-select" id="cwcSliderZone">
                  <option value="all" ${(w.slider_zone || 'middle') === 'all' ? 'selected' : ''}>เต็มหน้าจอ</option>
                  <option value="top" ${w.slider_zone === 'top' ? 'selected' : ''}>ครึ่งบน</option>
                  <option value="middle" ${(w.slider_zone || 'middle') === 'middle' ? 'selected' : ''}>ตรงกลาง</option>
                  <option value="bottom" ${w.slider_zone === 'bottom' ? 'selected' : ''}>ครึ่งล่าง</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ขนาดฟอนต์ดันมากุ:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcSliderFontSize" min="16" max="48" step="1" value="${w.fontSize || 24}">
                  <span class="cwc-slider-val" id="cwcSliderFontSizeVal">${w.fontSize || 24}px</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">สีตัวอักษรดันมากุ:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcSliderTextColor" value="${w.fontColor || '#ffffff'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">เส้นขอบตัวอักษรดันมากุ:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcSliderTextStroke" ${w.textStroke ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row" id="cwcSliderStrokeWidthRow" style="display:${w.textStroke ? 'flex' : 'none'};">
                <span class="cwc-label">ความหนาเส้นขอบ:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcSliderStrokeWidth" min="1" max="6" step="1" value="${w.textStrokeWidth || 2}">
                  <span class="cwc-slider-val" id="cwcSliderStrokeWidthVal">${w.textStrokeWidth ?? 2}px</span>
                </div>
              </div>
              <div class="cwc-row" id="cwcSliderStrokeColorRow" style="display:${w.textStroke ? 'flex' : 'none'};">
                <span class="cwc-label">สีเส้นขอบ:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcSliderStrokeColor" value="${w.strokeColor || '#000000'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">เงาตัวอักษรดันมากุ:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcSliderTextShadow" ${w.textShadow !== false ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">แสดงโลโก้ข้างข้อความ:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcSliderShowLogo" ${w.showLogo !== false ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
            </div>
          </div>
        `;
      } else if (mode === 'balloon') {
        specificHtml = `
          <!-- BALLOON CONTROLS -->
          <div class="cwc-section">
            <div class="cwc-section-header">
              <span class="cwc-section-title">💬 ตั้งค่าบอลลูนคำพูด</span>
              <span class="cwc-section-toggle">▼</span>
            </div>
            <div class="cwc-section-body">
              <div class="cwc-row">
                <span class="cwc-label">ความโปร่งใสบอลลูน:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcBalloonOpacity" min="10" max="100" step="5" value="${Math.round((w.balloonOpacity ?? 0.95) * 100)}">
                  <span class="cwc-slider-val" id="cwcBalloonOpacityVal">${Math.round((w.balloonOpacity ?? 0.95) * 100)}%</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ขนาดฟอนต์บอลลูน:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcBalloonFontSize" min="14" max="36" step="1" value="${w.fontSize || 15}">
                  <span class="cwc-slider-val" id="cwcBalloonFontSizeVal">${w.fontSize || 15}px</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">สีตัวอักษรบอลลูน:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcBalloonTextColor" value="${w.balloonTextColor || '#0f172a'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">สีพื้นหลังบอลลูน:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcBalloonBg" value="${w.balloonBg || '#ffffff'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ความโค้งมนมุมบอลลูน:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcBalloonRadius" min="6" max="32" step="1" value="${w.balloonRadius ?? 14}">
                  <span class="cwc-slider-val" id="cwcBalloonRadiusVal">${w.balloonRadius ?? 14}px</span>
                </div>
              </div>
            </div>
          </div>
        `;
      } else if (mode === 'character') {
        specificHtml = `
          <!-- CHARACTER TALK CONTROLS -->
          <div class="cwc-section">
            <div class="cwc-section-header">
              <span class="cwc-section-title">🎭 ตั้งค่าตัวละครพูด</span>
              <span class="cwc-section-toggle">▼</span>
            </div>
            <div class="cwc-section-body">
              <div class="cwc-row">
                <span class="cwc-label">ชื่อตัวละคร:</span>
                <input type="text" class="cwc-input-text" id="cwcCharName" value="${w.characterName || 'Replie'}" style="flex:1; padding:6px 10px; font-size:12px; background:#111215; border:1px solid rgba(255,255,255,0.12); border-radius:6px; color:#ffffff;">
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ตำแหน่งตัวละคร:</span>
                <select class="cwc-select" id="cwcCharAlign">
                  <option value="left" ${(w.charAlign || 'left') === 'left' ? 'selected' : ''}>ตัวละครอยู่ฝั่งซ้าย</option>
                  <option value="right" ${(w.charAlign || 'left') === 'right' ? 'selected' : ''}>ตัวละครอยู่ฝั่งขวา</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">รูปภาพตัวละคร:</span>
                <select class="cwc-select" id="cwcCharAvatar">
                  <option value="./assets/dock_offline_character.png" ${(w.imageUrl || '').includes('dock_offline_character') ? 'selected' : ''}>Replie คลาสสิก</option>
                  <option value="./assets/character_cheer.png" ${(w.imageUrl || '').includes('character_cheer') ? 'selected' : ''}>Replie เชียร์สดใส</option>
                  <option value="./assets/character_game.png" ${(w.imageUrl || '').includes('character_game') ? 'selected' : ''}>Replie เล่นเกม</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">สีพื้นหลังกล่องพูด:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcCharBubbleBg" value="${w.charBubbleBg || '#ffffff'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">สีตัวอักษร:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcCharTextColor" value="${w.charTextColor || '#0f172a'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ขนาดตัวอักษร:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcCharFontSize" min="12" max="28" step="1" value="${w.charFontSize || 15}">
                  <span class="cwc-slider-val" id="cwcCharFontSizeVal">${w.charFontSize || 15}px</span>
                </div>
              </div>
            </div>
          </div>
        `;
      } else {
        // Mode: Default (Standard & Theme modes)
        const currentSubTab = w.chatMode === 'theme' ? 'theme' : 'standard';
        specificHtml = `
          <div class="cwc-mode-segmented-bar">
            <button type="button" class="cwc-mode-tab-btn ${currentSubTab === 'standard' ? 'active' : ''}" id="tabSubStandard">⚙️ Default</button>
            <button type="button" class="cwc-mode-tab-btn ${currentSubTab === 'theme' ? 'active' : ''}" id="tabSubTheme">🎨 Theme</button>
          </div>
        `;

        if (currentSubTab === 'standard') {
          specificHtml += renderFullChatAccordionSections(w);
        } else {
          // 80 Themes Grid with Pagination
          const allThemes = window.CWC_ALL_THEMES || [];
          const pageNum = state.chatThemePage || 1;
          const pageSize = 8;
          const totalPages = Math.ceil(allThemes.length / pageSize) || 10;
          const startIdx = (pageNum - 1) * pageSize;
          const currentThemes = allThemes.slice(startIdx, startIdx + pageSize);

          let themeCardsHtml = '';
          currentThemes.forEach(t => {
            const themeId = t.id || t.key;
            const isSel = (w.chatTheme || 'default') === themeId;
            themeCardsHtml += `
              <div class="cwc-preset-card ${isSel ? 'active' : ''}" data-chat-theme="${themeId}" style="border:1.5px solid ${isSel ? '#38bdf8' : 'rgba(255,255,255,0.1)'}; border-radius:8px; padding:8px 10px; cursor:pointer; background:${isSel ? 'rgba(56,189,248,0.12)' : 'rgba(255,255,255,0.03)'}; transition:all 0.15s ease;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                  <span style="font-weight:700; font-size:12px; color:${isSel ? '#38bdf8' : '#ffffff'};">${t.name.replace(/\s*\([^)]*[ก-๙][^)]*\)/g,'')}</span>
                  <span style="font-size:10px; background:rgba(255,255,255,0.08); padding:1px 6px; border-radius:4px; color:#94a3b8;">${t.badge || ''}</span>
                </div>
                <div style="font-size:11px; color:#cbd5e1; line-height:1.3; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;"></div>
              </div>
            `;
          });

          specificHtml += `
            <div class="cwc-section">
              <div class="cwc-section-header">
                <span class="cwc-section-title">🎨 รูปแบบธีมสำเร็จรูป (80 ธีม)</span>
                <span class="cwc-section-toggle">▼</span>
              </div>
              <div class="cwc-section-body">
                <div class="cwc-presets-grid" id="cwcPresetsGrid" style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:10px;">
                  ${themeCardsHtml}
                </div>
                <div class="cwc-pagination" style="display:flex; justify-content:space-between; align-items:center; padding:8px 10px; background:rgba(0,0,0,0.3); border-radius:6px; margin-top:8px;">
                  <button type="button" class="cwc-page-btn" id="compBtnThemePrev" style="padding:5px 12px; font-size:12px; font-weight:600; background:#22252a; border:1px solid rgba(255,255,255,0.15); border-radius:4px; color:#ffffff; cursor:pointer;" ${pageNum <= 1 ? 'disabled style="opacity:0.4; cursor:not-allowed;"' : ''}>◀ ก่อนหน้า</button>
                  <span class="cwc-page-indicator" id="compThemePageIndicator" style="font-size:12px; font-weight:700; color:#38bdf8;">หน้า ${pageNum} / ${totalPages}</span>
                  <button type="button" class="cwc-page-btn" id="compBtnThemeNext" style="padding:5px 12px; font-size:12px; font-weight:600; background:#22252a; border:1px solid rgba(255,255,255,0.15); border-radius:4px; color:#ffffff; cursor:pointer;" ${pageNum >= totalPages ? 'disabled style="opacity:0.4; cursor:not-allowed;"' : ''}>ถัดไป ▶</button>
                </div>
              </div>
            </div>
          `;

          // Also include the full 4 accordion sections below theme grid so user can fine-tune!
          specificHtml += renderFullChatAccordionSections(w);
        }
      }
    }
    else if (w.type === 'clock') {
      const clockMode = w.clockMode || (w.clockStyle && w.clockStyle !== 'none' ? 'style' : 'theme');
      const curTheme = w.clockTheme || w.clock_theme || 'default';
      const curStyle = w.clockStyle || w.clock_style || 'dot1';
      const curFormat = w.clockFormat || w.clock_format || 'HH:MM';
      const themeOp = Math.round((w.themeOpacity ?? w.theme_opacity ?? 1.0) * 100);
      const styleOp = Math.round((w.styleOpacity ?? w.style_opacity ?? 1.0) * 100);

      const clockThemesList = [
        { id: 'default', name: 'Default (ขาวมาตรฐาน)' },
        { id: 'neon', name: 'Neon (นีออนฟ้า-น้ำเงิน)' },
        { id: 'cyberpunk', name: 'Cyberpunk (ชมพู-เขียว)' },
        { id: 'digital', name: 'Digital (เขียวเทอมินอล)' },
        { id: 'digital-red', name: 'Digital Red (แดงดิจิทัล)' },
        { id: 'digital-amber', name: 'Digital Amber (เหลืองดิจิทัล)' },
        { id: 'glass', name: 'Glass (กระจกฝ้า)' },
        { id: 'sakura', name: 'Sakura (ชมพูซากุระ)' },
        { id: 'gold', name: 'Gold (ทองหรูหรา)' },
        { id: 'retro', name: 'Retro (เรโทรคลาสสิก)' },
        { id: 'pipboy', name: 'Pip-Boy (เขียว Fallout)' },
        { id: 'minimal', name: 'Minimal (เรียบหรู)' },
        { id: 'outline', name: 'Outline (โปร่งใสขอบขาว)' },
        { id: 'shadow', name: 'Shadow (เงาดำเข้ม)' },
        { id: 'matrix', name: 'Matrix (เขียวเมทริกซ์)' },
        { id: 'vaporwave', name: 'Vaporwave (ชมพู-ฟ้า)' },
        { id: 'fire', name: 'Fire (ส้ม-แดงไฟ)' },
        { id: 'ice', name: 'Ice (ฟ้าเยือกแข็ง)' },
        { id: 'royal', name: 'Royal (ทอง-น้ำเงินเข้ม)' },
        { id: 'sunset', name: 'Sunset (ส้ม-ชมพู)' },
        { id: 'hologram', name: 'Hologram (ฟ้า-ชมพูโฮโลแกรม)' },
        { id: 'led', name: 'LED (แดง)' },
        { id: 'led-green', name: 'LED Green (เขียว)' },
        { id: 'led-blue', name: 'LED Blue (ฟ้า)' },
        { id: 'aqua', name: 'Aqua (ฟ้าน้ำทะเล)' },
        { id: 'coral', name: 'Coral (ส้มปะการัง)' },
        { id: 'mint', name: 'Mint (เขียวมิ้นต์)' },
        { id: 'lavender', name: 'Lavender (ม่วงลาเวนเดอร์)' },
        { id: 'bronze', name: 'Bronze (บรอนซ์)' },
        { id: 'platinum', name: 'Platinum (แพลตตินัม)' },
        { id: 'neon-purple', name: 'Neon Purple (ม่วงนีออน)' },
        { id: 'pixel-rpg', name: 'Pixel RPG (พิกเซลย้อนยุค)' }
      ];

      specificHtml = `
        <div class="cwc-mode-segmented-bar" style="margin-bottom:12px;">
          <button type="button" class="cwc-mode-tab-btn ${clockMode === 'theme' ? 'active' : ''}" id="tabClockTheme">🎨 Theme (32 ธีม)</button>
          <button type="button" class="cwc-mode-tab-btn ${clockMode === 'style' ? 'active' : ''}" id="tabClockStyle">⚙ Style (สไตล์พิเศษ)</button>
        </div>

        <!-- THEME SECTION -->
        <div id="compClockThemeSection" style="${clockMode === 'theme' ? 'display:block;' : 'display:none;'}">
          <div class="comp-card-section">
            <div class="comp-card-header"><span class="comp-card-title">🎨 รูปแบบธีมสำเร็จรูป (32 ธีม)</span></div>
            <div class="comp-card-body">
              <div class="comp-field-row">
                <span class="comp-field-label">เลือกธีม</span>
                <select class="cwc-select" id="compClockTheme">
                  ${clockThemesList.map(t => `<option value="${t.id}" ${curTheme === t.id ? 'selected' : ''}>${t.name}</option>`).join('')}
                </select>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">รูปแบบเวลา</span>
                <select class="cwc-select" id="compClockFormat">
                  <option value="HH:MM" ${curFormat === 'HH:MM' ? 'selected' : ''}>HH:MM (เช่น 19:30)</option>
                  <option value="HH:MM:SS" ${curFormat === 'HH:MM:SS' ? 'selected' : ''}>HH:MM:SS (เช่น 19:30:45)</option>
                </select>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ขนาด Font เวลา</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compClockFontSize" min="14" max="96" value="${w.fontSize || 28}">
                  <span class="cwc-slider-val" id="compClockFontSizeVal">${w.fontSize || 28}px</span>
                </div>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">สีตัวเลขอักษรเวลา</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="compClockTimeColor" value="${w.timeColor || '#ffffff'}">
                </div>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ความโปร่งใส Opacity</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compClockThemeOpacity" min="10" max="100" value="${themeOp}">
                  <span class="cwc-slider-val" id="compClockThemeOpacityVal">${themeOp}%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- DATE SETTINGS -->
          <div class="comp-card-section" style="margin-top:10px;">
            <div class="comp-card-header"><span class="comp-card-title">📅 การตั้งค่าวันที่</span></div>
            <div class="comp-card-body">
              <div class="comp-field-row">
                <span class="comp-field-label">เปิดแสดงวันที่</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="compClockShowDate" ${w.showDate ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ภาษาแสดงวันที่</span>
                <select class="cwc-select" id="compClockDateLang">
                  <option value="th" ${(w.dateLang || 'th') === 'th' ? 'selected' : ''}>ภาษาไทย (3 ส.ค. 69)</option>
                  <option value="en" ${(w.dateLang || 'th') === 'en' ? 'selected' : ''}>English (3 Aug 2026)</option>
                </select>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">รูปแบบวันที่</span>
                <select class="cwc-select" id="compClockDateFormat">
                  <option value="short" ${(w.dateFormat || 'short') === 'short' ? 'selected' : ''}>แบบสั้น (3 ส.ค. 69 / 3 Aug 26)</option>
                  <option value="long" ${(w.dateFormat || 'short') === 'long' ? 'selected' : ''}>แบบยาว (วันจันทร์ 3 สิงหาคม 2569)</option>
                  <option value="iso" ${(w.dateFormat || 'short') === 'iso' ? 'selected' : ''}>ISO (2026-08-03)</option>
                  <option value="weekday" ${(w.dateFormat || 'short') === 'weekday' ? 'selected' : ''}>วัน + วันที่ (จ. 3 ส.ค. 69)</option>
                </select>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ขนาด Font วันที่</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compClockDateFontSize" min="10" max="48" value="${w.dateFontSize || 14}">
                  <span class="cwc-slider-val" id="compClockDateFontSizeVal">${w.dateFontSize || 14}px</span>
                </div>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">สีตัวอักษรวันที่</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="compClockDateColor" value="${w.dateColor || '#cccccc'}">
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- STYLE SECTION -->
        <div id="compClockStyleSection" style="${clockMode === 'style' ? 'display:block;' : 'display:none;'}">
          <div class="comp-card-section">
            <div class="comp-card-header"><span class="comp-card-title">⚙ สไตล์พิเศษจาก Version 2</span></div>
            <div class="comp-card-body">
              <div class="comp-field-row">
                <span class="comp-field-label">เลือก Style</span>
                <select class="cwc-select" id="compClockStyle">
                  <optgroup label="⏱ Dot Clock (ตัวเลข + จุดนับวินาที)">
                    <option value="dot1" ${curStyle === 'dot1' ? 'selected' : ''}>Dot 1 — HH:MM + ◯</option>
                    <option value="dot2" ${curStyle === 'dot2' ? 'selected' : ''}>Dot 2 — YYYY.MM.DD HH:MM + ◯</option>
                    <option value="dot3" ${curStyle === 'dot3' ? 'selected' : ''}>Dot 3 — DD.MM.YYYY HH:MM + ◎</option>
                  </optgroup>
                  <optgroup label="⭕ Circle Clock (วงแหวนเรืองแสงหมุนตามวินาที)">
                    <option value="cc1" ${curStyle === 'cc1' ? 'selected' : ''}>Circle Normal — ดำ/แดง</option>
                    <option value="cc2" ${curStyle === 'cc2' ? 'selected' : ''}>Circle Normal — ฟ้า/เหลือง</option>
                    <option value="cc3" ${curStyle === 'cc3' ? 'selected' : ''}>Circle Normal — เขียว</option>
                    <option value="cc4" ${curStyle === 'cc4' ? 'selected' : ''}>Circle Normal — ส้ม/ชมพู</option>
                    <option value="cc5" ${curStyle === 'cc5' ? 'selected' : ''}>Circle Normal — ม่วง/ฟ้า</option>
                    <option value="ccdate1" ${curStyle === 'ccdate1' ? 'selected' : ''}>Circle + Date — ดำ/แดง</option>
                    <option value="ccdate2" ${curStyle === 'ccdate2' ? 'selected' : ''}>Circle + Date — ฟ้า/เหลือง</option>
                    <option value="ccdate3" ${curStyle === 'ccdate3' ? 'selected' : ''}>Circle + Date — เขียว</option>
                    <option value="ccdate4" ${curStyle === 'ccdate4' ? 'selected' : ''}>Circle + Date — ส้ม/ชมพู</option>
                    <option value="ccdate5" ${curStyle === 'ccdate5' ? 'selected' : ''}>Circle + Date — ม่วง/ฟ้า</option>
                    <option value="cclive1" ${curStyle === 'cclive1' ? 'selected' : ''}>Circle + LIVE — ดำ/แดง</option>
                    <option value="cclive2" ${curStyle === 'cclive2' ? 'selected' : ''}>Circle + LIVE — ฟ้า/เหลือง</option>
                    <option value="cclive3" ${curStyle === 'cclive3' ? 'selected' : ''}>Circle + LIVE — เขียว</option>
                    <option value="cclive4" ${curStyle === 'cclive4' ? 'selected' : ''}>Circle + LIVE — ส้ม/ชมพู</option>
                    <option value="cclive5" ${curStyle === 'cclive5' ? 'selected' : ''}>Circle + LIVE — ม่วง/ฟ้า</option>
                    <option value="ccsec1" ${curStyle === 'ccsec1' ? 'selected' : ''}>Circle + Seconds — ดำ/แดง</option>
                    <option value="ccsec2" ${curStyle === 'ccsec2' ? 'selected' : ''}>Circle + Seconds — ฟ้า/เหลือง</option>
                    <option value="ccsec3" ${curStyle === 'ccsec3' ? 'selected' : ''}>Circle + Seconds — เขียว</option>
                    <option value="ccsec4" ${curStyle === 'ccsec4' ? 'selected' : ''}>Circle + Seconds — ส้ม/ชมพู</option>
                    <option value="ccsec5" ${curStyle === 'ccsec5' ? 'selected' : ''}>Circle + Seconds — ม่วง/ฟ้า</option>
                  </optgroup>
                  <optgroup label="⚡ Clock with Live Text">
                    <option value="lt1" ${curStyle === 'lt1' ? 'selected' : ''}>Live Text 1 — LIVE + เวลา + วันที่</option>
                    <option value="lt2" ${curStyle === 'lt2' ? 'selected' : ''}>Live Text 2 — เวลา + วันที่</option>
                    <option value="lt3" ${curStyle === 'lt3' ? 'selected' : ''}>Live Text 3 — เวลา (ตรงกลาง)</option>
                    <option value="lt4" ${curStyle === 'lt4' ? 'selected' : ''}>Live Text 4 — เวลา + วินาที</option>
                    <option value="lt5" ${curStyle === 'lt5' ? 'selected' : ''}>Live Text 5 — เวลา + LIVE สายฟ้า</option>
                  </optgroup>
                  <optgroup label="🎮 FPS Clock (กรอบเรขาคณิตเกมมิ่ง)">
                    <option value="fps2" ${curStyle === 'fps2' ? 'selected' : ''}>FPS 2 — หกเหลี่ยม Hexagon</option>
                    <option value="fps3" ${curStyle === 'fps3' ? 'selected' : ''}>FPS 3 — สี่เหลี่ยมตัดมุม</option>
                    <option value="fps4" ${curStyle === 'fps4' ? 'selected' : ''}>FPS 4 — แปดเหลี่ยม Octagon</option>
                  </optgroup>
                </select>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ความโปร่งใส Opacity</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compClockStyleOpacity" min="10" max="100" value="${styleOp}">
                  <span class="cwc-slider-val" id="compClockStyleOpacityVal">${styleOp}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'text') {
      const isTicker = (w.textMode || 'ticker') === 'ticker';
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🔤 ข้อความและรูปแบบ</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">ข้อความประกาศ</span>
              <textarea class="cwc-input" id="compTextInput" rows="2" style="width:100%; resize:vertical;">${w.text || ''}</textarea>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">โหมดแสดงผล</span>
              <select class="cwc-select" id="compTextMode">
                <option value="ticker" ${w.textMode === 'ticker' ? 'selected' : ''}>ตัววิ่ง Marquee สด</option>
                <option value="static" ${w.textMode !== 'ticker' ? 'selected' : ''}>ข้อความนิ่ง</option>
              </select>
            </div>
            <div class="comp-field-row" id="compTextSpeedRow" style="display:${w.textMode === 'ticker' ? 'flex' : 'none'};">
              <span class="cwc-label">ความเร็วตัววิ่ง (วินาทีต่อรอบ):</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextSpeed" min="5" max="60" value="${w.marqueeSpeed || 15}">
                <span class="cwc-slider-val" id="compTextSpeedVal">${w.marqueeSpeed || 15} วิ</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดฟอนต์</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextFontSize" min="12" max="64" value="${w.fontSize || 18}">
                <span class="cwc-slider-val" id="compTextFontSizeVal">${w.fontSize || 18}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ตำแหน่งแนวตั้ง</span>
              <div style="display:flex; gap:6px;">
                <button type="button" class="composer-btn-sub ${w.vAlign === 'top' ? 'active' : ''}" id="btnTextVAlignTop">⬆️ บน</button>
                <button type="button" class="composer-btn-sub ${(!w.vAlign || w.vAlign === 'center') ? 'active' : ''}" id="btnTextVAlignMid">↕️ กลาง</button>
                <button type="button" class="composer-btn-sub ${w.vAlign === 'bottom' ? 'active' : ''}" id="btnTextVAlignBot">⬇️ ล่าง</button>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีตัวอักษร</span>
              <input type="color" class="cwc-color-pick" id="compTextFontColor" value="${w.fontColor || '#ffffff'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีพื้นหลัง</span>
              <div style="display:flex; align-items:center; gap:8px;">
                <input type="color" class="cwc-color-pick" id="compTextBgColor" value="${w.bgColor || '#141923'}" ${w.bgEnabled === false ? 'disabled style="opacity:0.4;"' : ''}>
                <button type="button" class="composer-btn-sub ${w.bgEnabled === false ? 'active' : ''}" id="btnTextToggleBg">
                  ${w.bgEnabled === false ? '🚫 ไม่ใช้พื้นหลัง (ใส)' : '🎨 เปิดใช้พื้นหลัง'}
                </button>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ความหนาเส้นขอบ (Stroke)</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextStrokeWidth" min="0" max="10" value="${w.textStrokeWidth ?? 0}">
                <span class="cwc-slider-val" id="compTextStrokeWidthVal">${w.textStrokeWidth ?? 0}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีเส้นขอบ</span>
              <input type="color" class="cwc-color-pick" id="compTextStrokeColor" value="${w.strokeColor || '#000000'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดเงา (Shadow Blur)</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextShadowBlur" min="0" max="20" value="${w.textShadowBlur ?? 0}">
                <span class="cwc-slider-val" id="compTextShadowBlurVal">${w.textShadowBlur ?? 0}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีเงา</span>
              <input type="color" class="cwc-color-pick" id="compTextShadowColor" value="${w.textShadowColor || '#000000'}">
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'now_playing') {
      specificHtml = `<div class="comp-card-section"><div class="comp-card-header"><span class="comp-card-title">🎵 แหล่งเพลงและรูปแบบ</span></div><div class="comp-card-body"><div class="comp-field-row"><label class="comp-field-label" for="compNpSource">จับเพลงจาก</label><select class="cwc-select" id="compNpSource"><option value="auto" ${(w.npSource || 'auto') === 'auto' ? 'selected' : ''}>ทุกแหล่งที่กำลังเล่น</option><option value="spotify" ${(w.npSource || 'auto') === 'spotify' ? 'selected' : ''}>Spotify เท่านั้น</option><option value="ytmusic" ${(w.npSource || 'auto') === 'ytmusic' ? 'selected' : ''}>YouTube Music เท่านั้น</option><option value="desktop_player" ${(w.npSource || 'auto') === 'desktop_player' ? 'selected' : ''}>เครื่องเล่นมีเดียในคอมพิวเตอร์</option></select></div><div class="comp-field-row"><label class="comp-field-label" for="compNpTheme">ธีม</label><select class="cwc-select" id="compNpTheme"><option value="custom" ${(w.npTheme || 'custom') === 'custom' ? 'selected' : ''}>กำหนดเอง</option><option value="spotify" ${(w.npTheme || 'custom') === 'spotify' ? 'selected' : ''}>Spotify (เขียวเข้ม)</option><option value="applemusic" ${(w.npTheme || 'custom') === 'applemusic' ? 'selected' : ''}>Apple Music (แดงชมพู)</option><option value="ytmusic" ${(w.npTheme || 'custom') === 'ytmusic' ? 'selected' : ''}>YouTube Music (ดำ/แดง)</option><option value="neon" ${(w.npTheme || 'custom') === 'neon' ? 'selected' : ''}>Neon (นีออนม่วง)</option><option value="glass" ${(w.npTheme || 'custom') === 'glass' ? 'selected' : ''}>Glass (กระจกโปร่ง)</option><option value="dark" ${(w.npTheme || 'custom') === 'dark' ? 'selected' : ''}>Dark (ดำล้วน)</option><option value="light" ${(w.npTheme || 'custom') === 'light' ? 'selected' : ''}>Light (ขาวสะอาด)</option><option value="retro" ${(w.npTheme || 'custom') === 'retro' ? 'selected' : ''}>Retro (ส้มย้อนยุค)</option><option value="ocean" ${(w.npTheme || 'custom') === 'ocean' ? 'selected' : ''}>Ocean (ฟ้าทะเล)</option><option value="sunset" ${(w.npTheme || 'custom') === 'sunset' ? 'selected' : ''}>Sunset (ส้มชมพวก)</option><option value="cyberpunk" ${(w.npTheme || 'custom') === 'cyberpunk' ? 'selected' : ''}>Cyberpunk (ฟ้า/ม่วงนีออน)</option><option value="aurora" ${(w.npTheme || 'custom') === 'aurora' ? 'selected' : ''}>Aurora (เขียวออโรร่า)</option><option value="lava" ${(w.npTheme || 'custom') === 'lava' ? 'selected' : ''}>Lava (แดงภูเขาไฟ)</option><option value="mint" ${(w.npTheme || 'custom') === 'mint' ? 'selected' : ''}>Mint (เขียวมิ้นต์)</option><option value="lavender" ${(w.npTheme || 'custom') === 'lavender' ? 'selected' : ''}>Lavender (ม่วงลาเวนเดอร์)</option><option value="crimson" ${(w.npTheme || 'custom') === 'crimson' ? 'selected' : ''}>Crimson (แดงเข้ม)</option><option value="gold" ${(w.npTheme || 'custom') === 'gold' ? 'selected' : ''}>Gold (ทอง)</option><option value="deepocean" ${(w.npTheme || 'custom') === 'deepocean' ? 'selected' : ''}>Deep Ocean (น้ำเงินลึก)</option><option value="forest" ${(w.npTheme || 'custom') === 'forest' ? 'selected' : ''}>Forest (เขียวป่า)</option><option value="bubblegum" ${(w.npTheme || 'custom') === 'bubblegum' ? 'selected' : ''}>Bubblegum (ชมพูหวาน)</option></select></div><div class="comp-field-row"><label class="comp-field-label" for="compNpStyle">ลวดลาย</label><select class="cwc-select" id="compNpStyle"><option value="flat" ${(w.npStyle || 'flat') === 'flat' ? 'selected' : ''}>Flat (เรียบ)</option><option value="metal" ${(w.npStyle || 'flat') === 'metal' ? 'selected' : ''}>Metal (เหล็กด้าน)</option><option value="neon" ${(w.npStyle || 'flat') === 'neon' ? 'selected' : ''}>Neon Glow (เรืองแสง)</option><option value="crt" ${(w.npStyle || 'flat') === 'crt' ? 'selected' : ''}>CRT (สแกนไลน์)</option><option value="pixel" ${(w.npStyle || 'flat') === 'pixel' ? 'selected' : ''}>Pixel (พิกเซลเกม)</option><option value="glass" ${(w.npStyle || 'flat') === 'glass' ? 'selected' : ''}>Glass (กระจกเบลอ)</option><option value="vinyl" ${(w.npStyle || 'flat') === 'vinyl' ? 'selected' : ''}>Vinyl (แผ่นเสียง)</option><option value="carbon" ${(w.npStyle || 'flat') === 'carbon' ? 'selected' : ''}>Carbon (เส้นทแยง)</option><option value="holo" ${(w.npStyle || 'flat') === 'holo' ? 'selected' : ''}>Holographic (สายรุ้ง)</option><option value="wood" ${(w.npStyle || 'flat') === 'wood' ? 'selected' : ''}>Wood (ไม้ลาย)</option><option value="cassette" ${(w.npStyle || 'flat') === 'cassette' ? 'selected' : ''}>Cassette (เทปคาสเซ็ท)</option><option value="circuit" ${(w.npStyle || 'flat') === 'circuit' ? 'selected' : ''}>Circuit Board (วงจรอิเล็กทรอนิกส์)</option><option value="camo" ${(w.npStyle || 'flat') === 'camo' ? 'selected' : ''}>Camouflage (ลายพราง)</option><option value="diamond" ${(w.npStyle || 'flat') === 'diamond' ? 'selected' : ''}>Diamond Plate (เหล็กเพชร)</option><option value="marble" ${(w.npStyle || 'flat') === 'marble' ? 'selected' : ''}>Marble (หินอ่อน)</option><option value="stripes" ${(w.npStyle || 'flat') === 'stripes' ? 'selected' : ''}>Stripes (ลายทาง)</option><option value="dots" ${(w.npStyle || 'flat') === 'dots' ? 'selected' : ''}>Dots (จุด)</option><option value="mesh" ${(w.npStyle || 'flat') === 'mesh' ? 'selected' : ''}>Gradient Mesh (ไล่เฉด)</option><option value="fire" ${(w.npStyle || 'flat') === 'fire' ? 'selected' : ''}>Fire (เปลวเพลิง)</option><option value="ice" ${(w.npStyle || 'flat') === 'ice' ? 'selected' : ''}>Ice (น้ำแข็ง)</option><option value="rainbow" ${(w.npStyle || 'flat') === 'rainbow' ? 'selected' : ''}>Rainbow (สายรุ้งเคลื่อนไหว)</option></select></div></div></div>        <!-- การ์ด 3: ฟอนต์และสี -->
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🔤 ฟอนต์และสี</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดฟอนต์ชื่อเพลง</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compNpFontSize" min="8" max="40" value="${w.npFontSize || 14}">
                <span class="cwc-slider-val" id="compNpFontSizeVal">${w.npFontSize || 14}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดฟอนต์ชื่อศิลปิน</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compNpArtistFontSize" min="8" max="32" value="${w.npArtistFontSize || 12}">
                <span class="cwc-slider-val" id="compNpArtistFontSizeVal">${w.npArtistFontSize || 12}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดฟอนต์เวลา</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compNpTimeFontSize" min="6" max="24" value="${w.npTimeFontSize || 10}">
                <span class="cwc-slider-val" id="compNpTimeFontSizeVal">${w.npTimeFontSize || 10}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีข้อความ</span>
              <input type="color" class="cwc-color-pick" id="compNpTextColor" value="${w.npTextColor || '#ffffff'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีแถบเวลา Progress</span>
              <input type="color" class="cwc-color-pick" id="compNpAccentColor" value="${w.npAccentColor || '#1db954'}">
            </div>
          </div>
        </div>

        <!-- การ์ด 4: ตัวเลือกการแสดงผล -->
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">⚙️ ตัวเลือกการแสดงผล</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">แสดงภาพปกอัลบั้ม</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compNpShowArt" ${w.npShowArt !== false ? 'checked' : ''}>
                <span class="cwc-switch-slider"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">แสดงแถบความคืบหน้า</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compNpShowProgress" ${w.npShowProgress !== false ? 'checked' : ''}>
                <span class="cwc-switch-slider"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">เลื่อนชื่อเพลงยาว</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compNpScrollTitle" ${w.npScrollTitle !== false ? 'checked' : ''}>
                <span class="cwc-switch-slider"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">โหมด Sync เวลา</span>
              <select class="cwc-select" id="compNpSyncMode">
                <option value="browser" ${(w.npSyncMode || 'browser') === 'browser' ? 'selected' : ''}>ประหยัดทรัพยากร</option>
                <option value="precise" ${w.npSyncMode === 'precise' ? 'selected' : ''}>แม่นยำสูง</option>
              </select>
            </div>
          </div>
        </div>

        <!-- การ์ด 5: กรอบและพื้นหลัง -->
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">📦 กรอบและพื้นหลัง</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">พื้นหลังโปร่งใส</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compNpTransparent" ${w.npTransparent ? 'checked' : ''}>
                <span class="cwc-switch-slider"></span>
              </label>
            </div>
            <div class="comp-field-row" id="compNpBgColorRow" style="display:${w.npTransparent ? 'none' : 'flex'};">
              <span class="comp-field-label">สีพื้นหลัง</span>
              <input type="color" class="cwc-color-pick" id="compNpBgColor" value="${w.npBgColor || '#1a1a2e'}">
            </div>
            <div class="comp-field-row" id="compNpBgOpacityRow" style="display:${w.npTransparent ? 'none' : 'flex'};">
              <span class="comp-field-label">ความโปร่งใสพื้นหลัง</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compNpBgOpacity" min="0" max="100" step="5" value="${Math.round((w.npBgOpacity ?? 0.85) * 100)}">
                <span class="cwc-slider-val" id="compNpBgOpacityVal">${Math.round((w.npBgOpacity ?? 0.85) * 100)}%</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ความโค้งมุมกรอบ</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compNpRadius" min="0" max="24" step="1" value="${w.npRadius ?? 8}">
                <span class="cwc-slider-val" id="compNpRadiusVal">${w.npRadius ?? 8}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ความโค้งมุมปก</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compNpArtRadius" min="0" max="24" step="1" value="${w.npArtRadius ?? 6}">
                <span class="cwc-slider-val" id="compNpArtRadiusVal">${w.npArtRadius ?? 6}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดภาพปก</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compNpArtSize" min="24" max="120" step="4" value="${w.npArtSize ?? 48}">
                <span class="cwc-slider-val" id="compNpArtSizeVal">${w.npArtSize ?? 48}px</span>
              </div>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'ask') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">📊 การตั้งค่าโพลสำรวจ (ASK)</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">หัวข้อคำถาม</span>
              <input type="text" class="cwc-input" id="compAskQuestion" value="${w.askQuestion || 'โหวตเลือกอะไรดีในสตรีมนี้?'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">รูปแบบ Layout</span>
              <select class="cwc-select" id="compAskLayout">
                <option value="vright" ${(w.askLayout || 'vright') === 'vright' ? 'selected' : ''}>แถวเดี่ยวแนวตั้ง (Right / Tower)</option>
                <option value="hband" ${(w.askLayout || 'vright') === 'hband' ? 'selected' : ''}>แถบแนวนอนยาว (Horizontal Band)</option>
                <option value="minimal" ${(w.askLayout || 'vright') === 'minimal' ? 'selected' : ''}>การ์ดมินิมอล (Card Minimal)</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">การนับถอยหลัง</span>
              <select class="cwc-select" id="compAskCountdownStyle">
                <option value="text" ${(w.askCountdownStyle || 'text') === 'text' ? 'selected' : ''}>แสดงเวลาตัวเลข</option>
                <option value="bar" ${(w.askCountdownStyle || 'text') === 'bar' ? 'selected' : ''}>แถบหลอดเวลาวิ่ง</option>
              </select>
            </div>
            <div style="margin-top:10px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoAskVote" style="width:100%; padding:8px; font-weight:700;">📊 จำลองคะแนนโหวตสด</button>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'giveaway') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎁 การตั้งค่าสุ่มแจกรางวัล (Giveaway)</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">เวลานับถอยหลัง (วินาที)</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compGiveawayDuration" min="10" max="120" value="${w.giveawayDuration || 30}">
                <span class="cwc-slider-val" id="compGiveawayDurationVal">${w.giveawayDuration || 30}s</span>
              </div>
            </div>
            <div style="margin-top:10px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoGiveawayDraw" style="width:100%; padding:8px; font-weight:700;">🎁 ทดสอบเริ่มสุ่มแจกรางวัล</button>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'playroom') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎮 การตั้งค่า Playroom Interactive</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">URL ของ Playroom</span>
              <input type="text" class="cwc-input" id="compPlayroomUrl" value="${w.playroomUrl || 'http://127.0.0.1:8080/playroom-widget'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">เปิดใช้งาน Chroma Key</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compPlayroomCkEnabled" ${w.ckEnabled ? 'checked' : ''}>
                <span class="cwc-switch-slider"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีฉากเขียวที่ตัดออก (Chroma)</span>
              <div class="cwc-color-wrap">
                <input type="color" class="cwc-color-pick" id="compPlayroomCkColor" value="${w.ckColor || '#00ff00'}">
              </div>
            </div>
          </div>
        </div>
      `;

    } else if (w.type === 'emote_party') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎉 ตั้งค่าปาร์ตี้อีโมทลอย</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">รูปแบบอนิเมชัน</span>
              <select class="cwc-select" id="compEpAnimation">
                <option value="float" ${(w.epAnimation || 'float') === 'float' ? 'selected' : ''}>ลอยขึ้นนุ่มนวล</option>
                <option value="shake" ${w.epAnimation === 'shake' ? 'selected' : ''}>สั่นและหมุน</option>
                <option value="dvd" ${w.epAnimation === 'dvd' ? 'selected' : ''}>เด้งชนผนัง</option>
                <option value="drop" ${w.epAnimation === 'drop' ? 'selected' : ''}>ตกกระทบพื้น</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ระยะเวลาแสดงผล</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compEpDuration" min="1" max="10" value="${w.epDuration || 4}">
                <span class="cwc-slider-val" id="compEpDurationVal">${w.epDuration || 4} วิ</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">จำนวนสูงสุดบนจอ</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compEpMaxEmotes" min="5" max="50" value="${w.epMaxEmotes || 15}">
                <span class="cwc-slider-val" id="compEpMaxEmotesVal">${w.epMaxEmotes || 15} ตัว</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดอีโมท</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compEpEmoteSize" min="24" max="96" value="${w.epEmoteSize || 48}">
                <span class="cwc-slider-val" id="compEpEmoteSizeVal">${w.epEmoteSize || 48}px</span>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    if(w.type==='replie'){specificHtml='<section class="comp-card-section"><div class="comp-card-header">Replie — Bot Commands</div><div class="comp-card-body"><p>แสดงข้อความ รูปภาพ หรือ Combo ตามคำสั่งบอต ใช้พื้นที่เต็ม Canvas และย่อขนาด Widget ไม่ได้</p><button type="button" class="btn-comp-demo-action" id="btnReplieCommands">เปิดคำสั่งและการตั้งค่า Replie</button></div></section>';demoHtml='';}
    bodyEl.innerHTML = demoHtml + specificHtml;
    bodyEl.querySelector('#btnReplieCommands')?.addEventListener('click',()=>window.openToolWindow?.('replie'));
    window.BP3LegacyControls?.mount(bodyEl,w,()=>{renderCanvasWidgets();saveState();});
    window.BP3ChatControls?.mount(bodyEl,w,()=>{renderCanvasWidgets();saveState(true);});
    if(w.type==='chat')bodyEl.addEventListener('input',event=>{if(/^cwc(Box|Bg)/.test(event.target.id))w.customBoxStyle=true;if(/^cwcTextShadow/.test(event.target.id))w.customTextShadow=true;},true);
    if(w.type==='webcam'){
      const d=bodyEl.ownerDocument,panel=d.createElement('div');panel.className='comp-card-section';const title=d.createElement('div');title.className='comp-card-header';title.textContent='กรอบกล้องเว็บแคม';panel.append(title);
      const themes=['simple-white','simple-black','rounded','glass','neon-blue','neon-pink','gold','cyberpunk','pixel','none','glow-pulse','rainbow-border','neon-flow','pulse-ring','electric','gradient-shift','bounce-border','fire-border','sparkle','game-shield','game-loading','rpg-aura','tron-line'];
      for(const [id,label,values,current] of [['compWebcamTheme','รูปแบบกรอบ',themes,w.webcamTheme || w.webcam_theme || 'simple-white'],['compWebcamRatio','สัดส่วน',['16:9','4:3','1:1','9:16'],w.ratio || w.webcamRatio || w.webcam_ratio || '16:9']]){const row=d.createElement('label');row.style.cssText='display:flex;gap:8px;align-items:center;margin:8px';row.append(label);const select=d.createElement('select');select.id=id;select.className='cwc-input';for(const value of values){const option=d.createElement('option');option.value=value;option.textContent=value;select.append(option);}select.value=current;row.append(select);panel.append(row);}
      const row=d.createElement('label');row.style.cssText='display:flex;gap:8px;align-items:center;margin:8px';row.append('ความหนาขอบ');const width=d.createElement('input');width.id='compWebcamBorderWidth';width.type='number';width.min=0;width.max=40;width.className='cwc-input';width.value=w.borderWidth ?? w.webcam_border_width ?? 4;row.append(width);panel.append(row);bodyEl.append(panel);
    }

    if(['image','video','alert'].includes(w.type)){
      const mediaDoc=bodyEl.ownerDocument,panel=mediaDoc.createElement('div');panel.className='comp-card-section';
      const title=mediaDoc.createElement('div');title.className='comp-card-header';title.textContent=w.type==='alert'?'URL เบราว์เซอร์ Overlay':'ไฟล์'+(w.type==='video'?'วิดีโอ':'รูปภาพ');panel.append(title);
      const fieldKey=w.type==='alert'?'url':w.type==='video'?'videoUrl':'imageUrl';const prefix=w.type==='alert'?'compAlert':w.type==='video'?'compVideo':'compImage';
      const url=mediaDoc.createElement('input');url.type='text';url.id=prefix+'Url';url.className='cwc-input';url.value=w[fieldKey] || w[fieldKey.replace('Url','_url')] || '';url.placeholder='URL';url.style.width='100%';panel.append(url);
      url.onchange=()=>{const value=url.value.trim();if(value){try{const parsed=new URL(value,location.href);if(!['http:','https:','data:'].includes(parsed.protocol) || (w.type==='alert' && parsed.protocol==='data:'))throw Error();}catch{window.showToast?.('URL ไม่ถูกต้อง');return;}}w[fieldKey]=value;if(w.type!=='alert')w[fieldKey.replace('Url','_url')]=value;if(w.type==='image')w.images=[];renderCanvasWidgets();saveState();};
      if(w.type!=='alert'){
        const button=mediaDoc.createElement('button');button.id='btnCompImportMedia';button.className='btn-comp-demo-action';button.textContent='เลือกไฟล์จากเครื่อง';panel.append(button);
        button.onclick=()=>{const picker=mediaDoc.createElement('input');picker.type='file';picker.accept=w.type==='video'?'video/*':'image/*';picker.hidden=true;mediaDoc.body.append(picker);picker.onchange=async()=>{try{const file=picker.files[0];if(!file)return;const expected=w.type==='video'?'video/':'image/';if(!file.type.startsWith(expected))throw Error('ชนิดไฟล์ไม่ตรงกับ Widget');const response=await fetch('/api/playroom/import',{method:'POST',headers:{'Content-Type':'application/octet-stream','X-Filename':encodeURIComponent(file.name)},body:file});const result=await response.json();if(!response.ok)throw Error(result.error);w[fieldKey]=result.url;w[fieldKey.replace('Url','_url')]=result.url;if(w.type==='image')w.images=[];url.value=result.url;renderCanvasWidgets();saveState();}catch(error){window.showToast?.(error.message);}finally{picker.remove();}};picker.click();};
        const fit=mediaDoc.createElement('select');fit.id=prefix+'Fit';fit.className='cwc-input';for(const [value,label] of [['cover','เต็มกรอบ'],['contain','แสดงครบภาพ'],['fill','ยืดตามกรอบ']]){const option=mediaDoc.createElement('option');option.value=value;option.textContent=label;fit.append(option);}fit.value=w.fitMode || 'cover';panel.append(fit);
      }
      if(w.type==='video'){
        for(const [id,key,raw,type,label,fallback] of [['compVideoCkEnabled','ckEnabled','ck_enabled','checkbox','ตัดพื้นหลังด้วยสี',false],['compVideoCkColor','ckColor','ck_color','color','สีพื้นหลัง','#00ff00'],['compVideoCkSimilarity','ckSimilarity','ck_similarity','number','ความใกล้เคียงของสี',50],['compVideoCkSmoothness','ckSmoothness','ck_smoothness','number','ความนุ่มของขอบ',30]]){
          const row=mediaDoc.createElement('label');row.style.cssText='display:flex;gap:8px;align-items:center;margin:8px';row.append(label);const input=mediaDoc.createElement('input');input.id=id;input.type=type;if(type==='checkbox')input.checked=w[key] ?? w[raw] ?? fallback;else input.value=w[key] ?? w[raw] ?? fallback;if(type==='number'){input.min=0;input.max=100;}input.onchange=()=>{w[key]=w[raw]=type==='checkbox'?input.checked:type==='number'?Math.min(100,Math.max(0,Number(input.value))):input.value;renderCanvasWidgets();saveState();};row.append(input);panel.append(row);
        }
      }
      bodyEl.append(panel);
    }


    window.BP3LegacyControls?.polish(bodyEl,w.type);
    if(settingsChanged)bodyEl.scrollTop=0;

    document.getElementById('btnViewerUseLive')?.addEventListener('click',()=>window.BP3ViewerPreview?.reset(w));

    document.getElementById('btnDemoChatClear')?.addEventListener('click',()=>window.clearChat?.());
    // Bind Demo Action Buttons
    const btnDemoChatLoop = document.getElementById('btnDemoChatLoop');
    const btnDemoChatSingle = document.getElementById('btnDemoChatSingle');
    if (btnDemoChatLoop) btnDemoChatLoop.addEventListener('click', () => ComposerDemoManager.toggleChatLoop(w, btnDemoChatLoop));
    if (btnDemoChatSingle) btnDemoChatSingle.addEventListener('click', () => ComposerDemoManager.sendChatMsg(w));

    const btnDemoDanmakuLoop = document.getElementById('btnDemoDanmakuLoop');
    const btnDemoDanmakuSingle = document.getElementById('btnDemoDanmakuSingle');
    if (btnDemoDanmakuLoop) btnDemoDanmakuLoop.addEventListener('click', () => ComposerDemoManager.toggleDanmakuLoop(w, btnDemoDanmakuLoop));
    if (btnDemoDanmakuSingle) btnDemoDanmakuSingle.addEventListener('click', () => ComposerDemoManager.sendDanmakuMsg(w));

    const btnCompChatDemoSend = document.getElementById('btnCompChatDemoSend');
    const compChatDemoInput = document.getElementById('compChatDemoInput');
    if (btnCompChatDemoSend && compChatDemoInput) {
      const sendCustom = () => {
        const val = compChatDemoInput.value.trim();
        if (!val) return;
        if (w.chatMode === 'danmaku') {
          ComposerDemoManager.sendDanmakuMsg(w, val);
        } else {
          ComposerDemoManager.sendChatMsg(w, val);
        }
        compChatDemoInput.value = '';
      };
      btnCompChatDemoSend.addEventListener('click', sendCustom);
      compChatDemoInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') sendCustom();
      });
    }

    const btnDemoBalloonSingle = document.getElementById('btnDemoBalloonSingle');
    if (btnDemoBalloonSingle) btnDemoBalloonSingle.addEventListener('click', () => ComposerDemoManager.sendBalloonMsg(w));

    const btnDemoCharTalk = document.getElementById('btnDemoCharTalk');
    if (btnDemoCharTalk) btnDemoCharTalk.addEventListener('click', () => ComposerDemoManager.triggerCharacterTalk(w));

    const btnDemoClockToggle = document.getElementById('btnDemoClockToggle');
    if (btnDemoClockToggle) {
      btnDemoClockToggle.addEventListener('click', () => {
        w.clockFormat = w.clockFormat === '12' ? '24' : '12';
        renderCanvasWidgets();
        renderWidgetCustomizerPanel(w.id);
        saveState();
      });
    }

    const btnDemoClockSecs = document.getElementById('btnDemoClockSecs');
    if (btnDemoClockSecs) {
      btnDemoClockSecs.addEventListener('click', () => {
        w.showSeconds = w.showSeconds === false ? true : false;
        renderCanvasWidgets();
        renderWidgetCustomizerPanel(w.id);
        saveState();
      });
    }

    const btnDemoTextTicker = document.getElementById('btnDemoTextTicker');
    if (btnDemoTextTicker) {
      btnDemoTextTicker.addEventListener('click', () => {
        w.textMode = w.textMode === 'ticker' ? 'static' : 'ticker';
        renderCanvasWidgets();
        renderWidgetCustomizerPanel(w.id);
        saveState();
      });
    }

    const btnDemoWebcamRec = document.getElementById('btnDemoWebcamRec');
    if (btnDemoWebcamRec) {
      btnDemoWebcamRec.addEventListener('click', () => {
        const dot = document.querySelector(`#widget-${w.id} .webcam-rec-dot`);
        if (dot) dot.style.display = dot.style.display === 'none' ? 'block' : 'none';
      });
    }

    const btnDemoWebcamAudio = document.getElementById('btnDemoWebcamAudio');
    if (btnDemoWebcamAudio) {
      btnDemoWebcamAudio.addEventListener('click', () => {
        const bars = document.querySelectorAll(`#widget-${w.id} .webcam-vu-bar`);
        bars.forEach(b => {
          b.style.height = (4 + Math.random() * 12) + 'px';
        });
      });
    }

    const btnDemoGoalPlus = document.getElementById('btnDemoGoalPlus');
    const btnDemoGoalReset = document.getElementById('btnDemoGoalReset');
    if (btnDemoGoalPlus) btnDemoGoalPlus.addEventListener('click', () => ComposerDemoManager.triggerGoalPlus(w));
    if (btnDemoGoalReset) btnDemoGoalReset.addEventListener('click', () => ComposerDemoManager.triggerGoalReset(w));

    const btnDemoViewerRandom = document.getElementById('btnDemoViewerRandom');
    const btnDemoViewerAdd = document.getElementById('btnDemoViewerAdd');
    const btnDemoViewerSub = document.getElementById('btnDemoViewerSub');
    if (btnDemoViewerRandom) btnDemoViewerRandom.addEventListener('click', () => ComposerDemoManager.triggerViewerRandom(w));
    if (btnDemoViewerAdd) btnDemoViewerAdd.addEventListener('click', () => ComposerDemoManager.triggerViewerAdd(w, 50));
    if (btnDemoViewerSub) btnDemoViewerSub.addEventListener('click', () => ComposerDemoManager.triggerViewerSub(w, 30));

    const btnDemoAskVote = document.getElementById('btnDemoAskVote');
    if (btnDemoAskVote) btnDemoAskVote.addEventListener('click', () => ComposerDemoManager.triggerAskVote(w));
    const btnDemoGiveawayDraw = document.getElementById('btnDemoGiveawayDraw');
    if (btnDemoGiveawayDraw) btnDemoGiveawayDraw.addEventListener('click', () => ComposerDemoManager.triggerGiveawayDraw(w));

    const btnDemoEmoteParty = document.getElementById('btnDemoEmoteParty');
    if (btnDemoEmoteParty) btnDemoEmoteParty.addEventListener('click', () => ComposerDemoManager.triggerEmoteParty(w));

    const btnDemoNowPlayingNext = document.getElementById('btnDemoNowPlayingNext');
    if (btnDemoNowPlayingNext) btnDemoNowPlayingNext.addEventListener('click', () => ComposerDemoManager.triggerNowPlayingNext(w));

    // Binders for specific widgets
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      if (mode === 'danmaku') {
        bindField('cwcSliderTextColor', 'fontColor');
        bindField('cwcSliderFontSize', 'fontSize', 'number', 'px');
        bindField('cwcSliderDuration', 'speed', 'number', ' วิ');
        bindField('cwcSliderLaneHeight','slider_lane_height','number','px');
        bindField('cwcSliderTextShadow','textShadow','checkbox');
        bindField('cwcSliderShowLogo','showLogo','checkbox');
        bindField('cwcDanmakuOpacity', 'opacity', 'opacity');
        bindField('cwcSliderZone', 'slider_zone');
        bindField('cwcSliderStrokeColor', 'strokeColor');
        bindField('cwcSliderStrokeWidth', 'textStrokeWidth', 'number', 'px');
        bindField('cwcDanmakuShadowColor', 'textShadowColor');
        const chkDanmakuStroke = document.getElementById('cwcSliderTextStroke');
        if (chkDanmakuStroke) {
          chkDanmakuStroke.addEventListener('change', () => {
            w.textStroke = chkDanmakuStroke.checked;
            renderCanvasWidgets();
            saveState();
          });
        }
      } else if (mode === 'balloon') {
        bindField('cwcBalloonBg', 'balloonBg');
        bindField('cwcBalloonTextColor', 'balloonTextColor');
        bindField('cwcBalloonRadius', 'balloonRadius', 'number', 'px');
        bindField('cwcBalloonFontSize', 'fontSize', 'number', 'px');
        bindField('cwcBalloonOpacity', 'balloonOpacity', 'opacity');
      } else if (mode === 'character') {
        bindField('cwcCharName', 'characterName');
        bindField('cwcCharAlign', 'charAlign');
        bindField('cwcCharBubbleBg', 'charBubbleBg');
        bindField('cwcCharTextColor', 'charTextColor');
        bindField('cwcCharFontSize', 'charFontSize', 'number', 'px');
      } else {
        // Mode: Default / Theme
        const tabStd = document.getElementById('tabSubStandard');
        const tabThm = document.getElementById('tabSubTheme');
        if (tabStd) tabStd.addEventListener('click', () => { w.chatMode = w.chat_mode = 'default'; w.chatSubTab = w.chat_sub_tab = state.chatSubTab = 'standard'; renderCanvasWidgets(); renderWidgetCustomizerPanel(w.id); saveState(); });
        if (tabThm) tabThm.addEventListener('click', () => { w.chatMode = w.chat_mode = 'theme'; w.chatSubTab = w.chat_sub_tab = state.chatSubTab = 'theme'; renderCanvasWidgets(); renderWidgetCustomizerPanel(w.id); saveState(); });

        const allThemes=window.CWC_ALL_THEMES || [],pageSize=8,totalPages=Math.max(1,Math.ceil(allThemes.length/pageSize));
        const grid=document.getElementById('cwcPresetsGrid'),btnPrev=document.getElementById('compBtnThemePrev'),btnNext=document.getElementById('compBtnThemeNext');
        function updateThemePage(){
          if(!grid)return;
          const page=Math.max(1,Math.min(totalPages,state.chatThemePage || 1));state.chatThemePage=page;
          while(grid.children.length<pageSize){const card=grid.ownerDocument.createElement('div');card.className='cwc-preset-card';card.innerHTML='<div style="display:flex;align-items:center"><span></span><span></span></div>';grid.append(card);}
          [...grid.children].forEach((card,index)=>{
            const theme=allThemes[(page-1)*pageSize+index];card.style.visibility=theme?'':'hidden';if(!theme){delete card.dataset.chatTheme;return;}
            const tid=theme.id || theme.key,selected=(w.chatTheme || 'default')===tid;
            card.dataset.chatTheme=tid;card.title=theme.name;card.classList.toggle('active',selected);
            card.style.borderColor=selected?'#38bdf8':'rgba(255,255,255,0.1)';card.style.background=selected?'rgba(56,189,248,0.12)':'rgba(255,255,255,0.03)';
            const labels=card.firstElementChild.children;labels[0].textContent=theme.name.replace(/\s*\([^)]*[ก-๙][^)]*\)/g,'');labels[0].style.color=selected?'#38bdf8':'#ffffff';labels[1].textContent=theme.badge || '';
          });
          document.getElementById('compThemePageIndicator').textContent=`หน้า ${page} / ${totalPages}`;
          if(btnPrev)btnPrev.disabled=page===1;if(btnNext)btnNext.disabled=page===totalPages;
        }
        grid?.addEventListener('click',event=>{
          const card=event.target.closest('[data-chat-theme]');if(!card || !grid.contains(card))return;event.stopPropagation();
          const tid=card.dataset.chatTheme;w.chatTheme=w.chat_theme=tid;w.chatMode=tid==='default'?'default':'theme';w.customBoxStyle=false;w.chatSubTab=w.chat_sub_tab=state.chatSubTab='theme';
          updateThemePage();renderCanvasWidgets();saveState();
        });
        if(btnPrev)btnPrev.addEventListener('click',event=>{event.stopPropagation();state.chatThemePage=Math.max(1,(state.chatThemePage || 1)-1);updateThemePage();});
        if(btnNext)btnNext.addEventListener('click',event=>{event.stopPropagation();state.chatThemePage=Math.min(totalPages,(state.chatThemePage || 1)+1);updateThemePage();});
        updateThemePage();

        // Section 1: Layout & Structure
        bindField('cwcLayout', 'layout');
        bindField('cwcDirection', 'direction');
        bindField('cwcAlign', 'align');
        bindField('cwcMsgSpacing', 'msgSpacing', 'number', 'px');
        bindField('cwcMaxMessages', 'maxMessages', 'number');

        // Section 2: Typography & Font
        bindField('cwcFontFamily', 'fontFamily');
        bindField('cwcFontSize', 'fontSize', 'number', 'px');
        bindField('cwcFontWeight', 'fontWeight');
        bindField('cwcUsernameColor', 'usernameColor');
        bindField('cwcMessageColor', 'fontColor');
        bindField('cwcTextStrokeWidth', 'textStrokeWidth', 'number', 'px');
        bindField('cwcTextStrokeColor', 'strokeColor');
        bindField('cwcTextShadowBlur', 'textShadowBlur', 'number', 'px');
        bindField('cwcTextShadowColor', 'textShadowColor');

        const chkStroke = document.getElementById('cwcTextStroke');
        const strokeWRow = document.getElementById('cwcStrokeWidthRow');
        const strokeCRow = document.getElementById('cwcStrokeColorRow');
        if (chkStroke) {
          chkStroke.addEventListener('change', () => {
            w.textStroke = chkStroke.checked;
            if (strokeWRow) strokeWRow.style.display = chkStroke.checked ? 'flex' : 'none';
            if (strokeCRow) strokeCRow.style.display = chkStroke.checked ? 'flex' : 'none';
            renderCanvasWidgets();
            saveState();
          });
        }

        const chkShadow = document.getElementById('cwcTextShadow');
        const shadowBRow = document.getElementById('cwcShadowBlurRow');
        const shadowCRow = document.getElementById('cwcShadowColorRow');
        if (chkShadow) {
          chkShadow.addEventListener('change', () => {
            w.textShadow = chkShadow.checked;
            if (shadowBRow) shadowBRow.style.display = chkShadow.checked ? 'flex' : 'none';
            if (shadowCRow) shadowCRow.style.display = chkShadow.checked ? 'flex' : 'none';
            renderCanvasWidgets();
            saveState();
          });
        }

        // Section 3: Message Box & Bubble
        bindField('cwcBoxWidth', 'boxWidth');
        bindField('cwcBgColor', 'bgColor');
        bindField('cwcBgOpacity', 'bgOpacity', 'opacity');
        bindField('cwcBoxRadius', 'boxRadius', 'number', 'px');
        bindField('cwcBoxPadding', 'boxPadding', 'number', 'px');
        bindField('cwcBoxBorderWidth', 'boxBorderWidth', 'number', 'px');
        bindField('cwcBoxBorderColor', 'boxBorderColor');
        bindField('cwcBoxGlowColor', 'boxGlowColor');

        const chkBoxEnabled = document.getElementById('cwcBoxEnabled');
        if (chkBoxEnabled) chkBoxEnabled.addEventListener('change', () => { w.boxEnabled = chkBoxEnabled.checked; renderCanvasWidgets(); saveState(); });

        const chkBoxBorder = document.getElementById('cwcBoxBorder');
        const boxBorderWRow = document.getElementById('cwcBoxBorderWidthRow');
        const boxBorderCRow = document.getElementById('cwcBoxBorderColorRow');
        if (chkBoxBorder) {
          chkBoxBorder.addEventListener('change', () => {
            w.boxBorder = chkBoxBorder.checked;
            if (boxBorderWRow) boxBorderWRow.style.display = chkBoxBorder.checked ? 'flex' : 'none';
            if (boxBorderCRow) boxBorderCRow.style.display = chkBoxBorder.checked ? 'flex' : 'none';
            renderCanvasWidgets();
            saveState();
          });
        }

        const chkBoxShadow = document.getElementById('cwcBoxShadow');
        if (chkBoxShadow) chkBoxShadow.addEventListener('change', () => { w.boxShadow = chkBoxShadow.checked; renderCanvasWidgets(); saveState(); });

        const chkBoxGlow = document.getElementById('cwcBoxGlow');
        const boxGlowCRow = document.getElementById('cwcBoxGlowColorRow');
        if (chkBoxGlow) {
          chkBoxGlow.addEventListener('change', () => {
            w.boxGlow = chkBoxGlow.checked;
            if (boxGlowCRow) boxGlowCRow.style.display = chkBoxGlow.checked ? 'flex' : 'none';
            renderCanvasWidgets();
            saveState();
          });
        }

        // Section: Chat Container Background Box
        const chkContainerBg = document.getElementById('compChatContainerBgEnabled');
        const wrapContainerSettings = document.getElementById('compChatContainerSettingsWrap');
        if (chkContainerBg) {
          chkContainerBg.addEventListener('change', () => {
            w.containerBgEnabled = chkContainerBg.checked;
            w.container_bg_enabled = chkContainerBg.checked;
            if (wrapContainerSettings) wrapContainerSettings.style.display = chkContainerBg.checked ? 'block' : 'none';
            renderCanvasWidgets();
            saveState();
          });
        }
        bindField('compChatContainerBgColor', 'containerBgColor');
        bindField('compChatContainerBgOpacity', 'containerBgOpacity', 'opacity');
        bindField('compChatContainerRadius', 'containerRadius', 'number', 'px');

        const chkContainerBorder = document.getElementById('compChatContainerBorder');
        const containerBorderWRow = document.getElementById('compChatContainerBorderWidthRow');
        const containerBorderCRow = document.getElementById('compChatContainerBorderColorRow');
        if (chkContainerBorder) {
          chkContainerBorder.addEventListener('change', () => {
            w.containerBorder = chkContainerBorder.checked;
            w.container_border = chkContainerBorder.checked;
            if (containerBorderWRow) containerBorderWRow.style.display = chkContainerBorder.checked ? 'flex' : 'none';
            if (containerBorderCRow) containerBorderCRow.style.display = chkContainerBorder.checked ? 'flex' : 'none';
            renderCanvasWidgets();
            saveState();
          });
        }
        bindField('compChatContainerBorderWidth', 'containerBorderWidth', 'number', 'px');
        bindField('compChatContainerBorderColor', 'containerBorderColor');

        // Section 4: Animations & Auto-Hide
        const selAnimIn = document.getElementById('compChatAnimIn');
        if (selAnimIn) {
          selAnimIn.addEventListener('change', () => {
            w.animation = selAnimIn.value;
            w.animIn = selAnimIn.value;
            w.anim_in = selAnimIn.value;
            renderCanvasWidgets();saveState();
          });
        }

        const selAnimOut = document.getElementById('compChatAnimOut');
        if (selAnimOut) {
          selAnimOut.addEventListener('change', () => {
            w.exitAnimation = selAnimOut.value;
            w.animOut = selAnimOut.value;
            w.exit_animation = selAnimOut.value;
            w.anim_out = selAnimOut.value;
            renderCanvasWidgets();saveState();
          });
        }

        const chkAutoHide = document.getElementById('compChatAutoHide');
        const hideAfterRow = document.getElementById('compChatHideAfterRow');
        if (chkAutoHide) {
          chkAutoHide.addEventListener('change', () => {
            w.autoHide = chkAutoHide.checked;
            w.auto_hide = chkAutoHide.checked;
            renderCanvasWidgets();
            if (hideAfterRow) hideAfterRow.style.display = chkAutoHide.checked ? 'flex' : 'none';
            saveState();
          });
        }
        bindField('compChatHideAfter', 'hideAfter', 'number', ' วินาที');
      }
    }
    else if (w.type === 'clock') {
      const tabClkTheme = document.getElementById('tabClockTheme');
      const tabClkStyle = document.getElementById('tabClockStyle');
      if (tabClkTheme) {
        tabClkTheme.addEventListener('click', () => {
          w.clockMode = 'theme';
          w.clock_mode = 'theme';
          renderCanvasWidgets();
          renderWidgetCustomizerPanel(w.id);
          saveState();
        });
      }
      if (tabClkStyle) {
        tabClkStyle.addEventListener('click', () => {
          w.clockMode = 'style';
          w.clock_mode = 'style';
          if (!w.clockStyle || w.clockStyle === 'none') {
            w.clockStyle = 'dot1';
            w.clock_style = 'dot1';
          }
          renderCanvasWidgets();
          renderWidgetCustomizerPanel(w.id);
          saveState();
        });
      }

      bindField('compClockTheme', 'clockTheme');
      bindField('compClockFormat', 'clockFormat');
      bindField('compClockFontSize', 'fontSize', 'number', 'px');
      bindField('compClockTimeColor', 'timeColor');
      bindField('compClockThemeOpacity', 'themeOpacity', 'opacity');

      const chkShowDate = document.getElementById('compClockShowDate');
      if (chkShowDate) {
        chkShowDate.addEventListener('change', () => {
          w.showDate = chkShowDate.checked;
          w.show_date = chkShowDate.checked;
          renderCanvasWidgets();
          saveState();
        });
      }
      bindField('compClockDateLang', 'dateLang');
      bindField('compClockDateFormat', 'dateFormat');
      bindField('compClockDateFontSize', 'dateFontSize', 'number', 'px');
      bindField('compClockDateColor', 'dateColor');

      bindField('compClockStyle', 'clockStyle');
      bindField('compClockStyleOpacity', 'styleOpacity', 'opacity');
    } else if (w.type === 'text') {
      bindField('compTextInput', 'text');
      const textModeEl = document.getElementById('compTextMode');
      const speedRow = document.getElementById('compTextSpeedRow');
      if (textModeEl) {
        textModeEl.addEventListener('change', () => {
          w.textMode = textModeEl.value;
          if (speedRow) speedRow.style.display = w.textMode === 'ticker' ? 'flex' : 'none';
          renderCanvasWidgets();
          saveState();
        });
      }
      bindField('compTextSpeed', 'marqueeSpeed', 'number', ' วิ');
      bindField('compTextFontSize', 'fontSize', 'number', 'px');
      bindField('compTextFontColor', 'fontColor');
      bindField('compTextBgColor', 'bgColor');

      // Vertical alignment buttons
      const btnVTop = document.getElementById('btnTextVAlignTop');
      const btnVMid = document.getElementById('btnTextVAlignMid');
      const btnVBot = document.getElementById('btnTextVAlignBot');
      if (btnVTop && btnVMid && btnVBot) {
        const updateVAlign = (val) => {
          w.vAlign = val;
          btnVTop.classList.toggle('active', val === 'top');
          btnVMid.classList.toggle('active', val === 'center');
          btnVBot.classList.toggle('active', val === 'bottom');
          renderCanvasWidgets();
          saveState();
        };
        btnVTop.addEventListener('click', () => updateVAlign('top'));
        btnVMid.addEventListener('click', () => updateVAlign('center'));
        btnVBot.addEventListener('click', () => updateVAlign('bottom'));
      }

      // Background toggle
      const btnBgToggle = document.getElementById('btnTextToggleBg');
      const inpBgColor = document.getElementById('compTextBgColor');
      if (btnBgToggle) {
        btnBgToggle.addEventListener('click', () => {
          w.bgEnabled = (w.bgEnabled === false) ? true : false;
          btnBgToggle.textContent = w.bgEnabled ? '🎨 เปิดใช้พื้นหลัง' : '🚫 ไม่ใช้พื้นหลัง (ใส)';
          btnBgToggle.classList.toggle('active', !w.bgEnabled);
          if (inpBgColor) {
            inpBgColor.disabled = !w.bgEnabled;
            inpBgColor.style.opacity = w.bgEnabled ? '1' : '0.4';
          }
          renderCanvasWidgets();
          saveState();
        });
      }

      // Stroke controls (default 0)
      bindField('compTextStrokeWidth', 'textStrokeWidth', 'number', 'px');
      bindField('compTextStrokeColor', 'strokeColor');

      // Shadow controls (default 0)
      bindField('compTextShadowBlur', 'textShadowBlur', 'number', 'px');
      bindField('compTextShadowColor', 'textShadowColor');
    } else if (w.type === 'webcam') {
      const ratioEl = document.getElementById('compWebcamRatio');
      if (ratioEl) {
        ratioEl.addEventListener('change', () => {
          const ratio = ratioEl.value;
          w.ratio = ratio;w.webcamRatio=ratio;w.webcam_ratio=ratio;
          let newH = w.height;
          if (ratio === '16:9') newH = Math.round(w.width * 9 / 16);
          else if (ratio === '4:3') newH = Math.round(w.width * 3 / 4);
          else if (ratio === '1:1') newH = Math.round(w.width);
          else if (ratio === '9:16') newH = Math.round(w.width * 16 / 9);
          w.height = newH;
          updateTransformInspector();
          renderCanvasWidgets();
          saveState();
        });
      }
      bindField('compWebcamTheme', 'webcamTheme');
      bindField('compWebcamBorderWidth', 'borderWidth', 'number', 'px');
      bindField('compWebcamBorderColor', 'borderColor');
    } else if (w.type === 'goal') {
      bindField('compGoalTitle', 'goalTitle');
      bindField('compGoalCurrent', 'goalCurrent', 'number');
      bindField('compGoalTarget', 'goalTarget', 'number');
      bindField('compGoalUnit', 'goalUnit');
    } else if (w.type === 'viewer') {
      // Bound by BP3LegacyControls with legacy-compatible keys.
    } else if (w.type === 'replie') {
      bindField('compCharWidgetName', 'characterName');
    } else if (w.type === 'image') {

      bindField('compImageFit', 'fitMode');
    } else if (w.type === 'video') {

      bindField('compVideoFit', 'fitMode');
    } else if (w.type === 'alert') {

      const btnRefresh = document.getElementById('btnRefreshAlert');
      if (btnRefresh) {
        btnRefresh.addEventListener('click', () => {
          renderCanvasWidgets();
          if (window.showToast) window.showToast('รีเฟรชหน้าเว็บเบราว์เซอร์สำเร็จ');
        });
      }
    } else if (w.type === 'now_playing') {
      // 1. Source
      const selNpSource = document.getElementById('compNpSource');
      if (selNpSource) {
        selNpSource.addEventListener('change', () => {
          w.npSource = selNpSource.value;
          w.np_source = selNpSource.value;
          renderCanvasWidgets();
          saveState();
        });
      }

      // 2. Theme Presets
      const selNpTheme = document.getElementById('compNpTheme');
      if (selNpTheme) {
        selNpTheme.addEventListener('change', () => {
          const theme = selNpTheme.value;
          w.npTheme = theme;
          w.np_theme = theme;
          const npPresets = {
            spotify:    { bg:'#1ed760', accent:'#000000', text:'#0a0a0a', opacity:95, radius:12, artRadius:6 },
            applemusic: { bg:'#fc2c55', accent:'#ffffff', text:'#ffffff', opacity:90, radius:16, artRadius:8 },
            ytmusic:    { bg:'#0f0f0f', accent:'#ff0000', text:'#ffffff', opacity:90, radius:4, artRadius:2 },
            neon:       { bg:'#1a0a2e', accent:'#bf00ff', text:'#e0b3ff', opacity:85, radius:8, artRadius:6 },
            glass:      { bg:'#2a2a3e', accent:'#64c8ff', text:'#ffffff', opacity:50, radius:16, artRadius:12 },
            dark:       { bg:'#000000', accent:'#333333', text:'#cccccc', opacity:90, radius:6, artRadius:4 },
            light:      { bg:'#ffffff', accent:'#0066cc', text:'#1a1a1a', opacity:95, radius:12, artRadius:8 },
            retro:      { bg:'#2a1a00', accent:'#ff8800', text:'#ffcc66', opacity:85, radius:4, artRadius:2 },
            ocean:      { bg:'#001a33', accent:'#00bfff', text:'#cce8ff', opacity:85, radius:12, artRadius:8 },
            sunset:     { bg:'#2a0a1a', accent:'#ff6b9d', text:'#ffd6e8', opacity:85, radius:12, artRadius:8 },
            cyberpunk:  { bg:'#0a0014', accent:'#00ffff', text:'#ff00ff', opacity:90, radius:2, artRadius:2 },
            aurora:     { bg:'#001a1a', accent:'#00ffaa', text:'#aaffee', opacity:80, radius:16, artRadius:12 },
            lava:       { bg:'#1a0500', accent:'#ff4400', text:'#ffaa88', opacity:90, radius:4, artRadius:2 },
            mint:       { bg:'#00220a', accent:'#00ff88', text:'#aaffcc', opacity:85, radius:12, artRadius:8 },
            lavender:   { bg:'#1a0a2a', accent:'#aa88ff', text:'#ddccff', opacity:85, radius:16, artRadius:12 },
            crimson:    { bg:'#1a0000', accent:'#ff0044', text:'#ff88aa', opacity:90, radius:6, artRadius:4 },
            gold:       { bg:'#1a1400', accent:'#ffcc00', text:'#ffeeaa', opacity:85, radius:8, artRadius:6 },
            deepocean:  { bg:'#000a1a', accent:'#0088ff', text:'#88ccff', opacity:85, radius:12, artRadius:8 },
            forest:     { bg:'#0a1a00', accent:'#44aa00', text:'#aacc88', opacity:85, radius:8, artRadius:6 },
            bubblegum:  { bg:'#2a0a1a', accent:'#ff44aa', text:'#ffaadd', opacity:85, radius:20, artRadius:16 },
          };
          if (theme !== 'custom' && npPresets[theme]) {
            const p = npPresets[theme];
            w.npBgColor = p.bg; w.np_bg_color = p.bg;
            w.npAccentColor = p.accent; w.np_accent_color = p.accent;
            w.npTextColor = p.text; w.np_text_color = p.text;
            w.npBgOpacity = p.opacity / 100; w.np_bg_opacity = p.opacity / 100;
            w.npRadius = p.radius; w.np_radius = p.radius;
            w.npArtRadius = p.artRadius; w.np_art_radius = p.artRadius;
            w.npTransparent = false;

            // Update UI elements in drawer
            const elBg = document.getElementById('compNpBgColor'); if (elBg) elBg.value = p.bg;
            const elAcc = document.getElementById('compNpAccentColor'); if (elAcc) elAcc.value = p.accent;
            const elTxt = document.getElementById('compNpTextColor'); if (elTxt) elTxt.value = p.text;
            const elOp = document.getElementById('compNpBgOpacity'); if (elOp) elOp.value = p.opacity;
            const elOpVal = document.getElementById('compNpBgOpacityVal'); if (elOpVal) elOpVal.textContent = p.opacity + '%';
            const elRad = document.getElementById('compNpRadius'); if (elRad) elRad.value = p.radius;
            const elRadVal = document.getElementById('compNpRadiusVal'); if (elRadVal) elRadVal.textContent = p.radius + 'px';
            const elArtRad = document.getElementById('compNpArtRadius'); if (elArtRad) elArtRad.value = p.artRadius;
            const elArtRadVal = document.getElementById('compNpArtRadiusVal'); if (elArtRadVal) elArtRadVal.textContent = p.artRadius + 'px';
            const chkTr = document.getElementById('compNpTransparent'); if (chkTr) chkTr.checked = false;
            const rowBg = document.getElementById('compNpBgColorRow'); if (rowBg) rowBg.style.display = 'flex';
            const rowOp = document.getElementById('compNpBgOpacityRow'); if (rowOp) rowOp.style.display = 'flex';
          }
          renderCanvasWidgets();
          saveState();
        });
      }

      // 3. Style Pattern
      const selNpStyle = document.getElementById('compNpStyle');
      if (selNpStyle) {
        selNpStyle.addEventListener('change', () => {
          w.npStyle = selNpStyle.value;
          w.np_style = selNpStyle.value;
          renderCanvasWidgets();
          saveState();
        });
      }

      // 4. Fonts and Colors
      bindField('compNpFontSize', 'npFontSize', 'number', 'px');
      bindField('compNpArtistFontSize', 'npArtistFontSize', 'number', 'px');
      bindField('compNpTimeFontSize', 'npTimeFontSize', 'number', 'px');
      bindField('compNpTextColor', 'npTextColor');
      bindField('compNpAccentColor', 'npAccentColor');

      // 5. Display Toggles
      bindField('compNpShowArt', 'npShowArt', 'checkbox');
      bindField('compNpShowProgress', 'npShowProgress', 'checkbox');
      bindField('compNpScrollTitle', 'npScrollTitle', 'checkbox');
      bindField('compNpSyncMode', 'npSyncMode');

      // 6. Box & Background
      const chkTrans = document.getElementById('compNpTransparent');
      const bgClrRow = document.getElementById('compNpBgColorRow');
      const bgOpRow = document.getElementById('compNpBgOpacityRow');
      if (chkTrans) {
        chkTrans.addEventListener('change', () => {
          w.npTransparent = chkTrans.checked;
          if (bgClrRow) bgClrRow.style.display = chkTrans.checked ? 'none' : 'flex';
          if (bgOpRow) bgOpRow.style.display = chkTrans.checked ? 'none' : 'flex';
          renderCanvasWidgets();
          saveState();
        });
      }
      bindField('compNpBgColor', 'npBgColor');
      bindField('compNpBgOpacity', 'npBgOpacity', 'opacity');
      bindField('compNpRadius', 'npRadius', 'number', 'px');
      bindField('compNpArtRadius', 'npArtRadius', 'number', 'px');
      bindField('compNpArtSize', 'npArtSize', 'number', 'px');
    } else if (w.type === 'ask') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">📊 การตั้งค่าโพลสำรวจ (ASK)</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">หัวข้อคำถาม</span>
              <input type="text" class="cwc-input" id="compAskQuestion" value="${w.askQuestion || 'โหวตเลือกอะไรดีในสตรีมนี้?'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">รูปแบบ Layout</span>
              <select class="cwc-select" id="compAskLayout">
                <option value="vright" ${(w.askLayout || 'vright') === 'vright' ? 'selected' : ''}>แถวเดี่ยวแนวตั้ง (Right / Tower)</option>
                <option value="hband" ${(w.askLayout || 'vright') === 'hband' ? 'selected' : ''}>แถบแนวนอนยาว (Horizontal Band)</option>
                <option value="minimal" ${(w.askLayout || 'vright') === 'minimal' ? 'selected' : ''}>การ์ดมินิมอล (Card Minimal)</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">การนับถอยหลัง</span>
              <select class="cwc-select" id="compAskCountdownStyle">
                <option value="text" ${(w.askCountdownStyle || 'text') === 'text' ? 'selected' : ''}>แสดงเวลาตัวเลข</option>
                <option value="bar" ${(w.askCountdownStyle || 'text') === 'bar' ? 'selected' : ''}>แถบหลอดเวลาวิ่ง</option>
              </select>
            </div>
            <div style="margin-top:10px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoAskVote" style="width:100%; padding:8px; font-weight:700;">📊 จำลองคะแนนโหวตสด</button>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'giveaway') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎁 การตั้งค่าสุ่มแจกรางวัล (Giveaway)</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">เวลานับถอยหลัง (วินาที)</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compGiveawayDuration" min="10" max="120" value="${w.giveawayDuration || 30}">
                <span class="cwc-slider-val" id="compGiveawayDurationVal">${w.giveawayDuration || 30}s</span>
              </div>
            </div>
            <div style="margin-top:10px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoGiveawayDraw" style="width:100%; padding:8px; font-weight:700;">🎁 ทดสอบเริ่มสุ่มแจกรางวัล</button>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'playroom') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎮 การตั้งค่า Playroom Interactive</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">URL ของ Playroom</span>
              <input type="text" class="cwc-input" id="compPlayroomUrl" value="${w.playroomUrl || 'http://127.0.0.1:8080/playroom-widget'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">เปิดใช้งาน Chroma Key</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compPlayroomCkEnabled" ${w.ckEnabled ? 'checked' : ''}>
                <span class="cwc-switch-slider"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีฉากเขียวที่ตัดออก (Chroma)</span>
              <div class="cwc-color-wrap">
                <input type="color" class="cwc-color-pick" id="compPlayroomCkColor" value="${w.ckColor || '#00ff00'}">
              </div>
            </div>
          </div>
        </div>
      `;

    } else if (w.type === 'emote_party') {
      bindField('compEpAnimation', 'epAnimation');
      bindField('compEpDuration', 'epDuration', 'number', ' วิ');
      bindField('compEpMaxEmotes', 'epMaxEmotes', 'number', ' ตัว');
      bindField('compEpEmoteSize', 'epEmoteSize', 'number', 'px');
    }
  }


  // Export Profile (JSON download)
  function exportProfile() {
    try {
      const data = {
        version: '3.0.0',
        exportedAt: new Date().toISOString(),
        pages: state.pages,
        activePageId: state.activePageId,
        canvasWidth: CANVAS_WIDTH, canvasHeight: CANVAS_HEIGHT,
        legacyPlayroomTriggers: state.legacyPlayroomTriggers || [], legacyTools: state.legacyTools || {}, legacyChat: state.legacyChat || {}
      };
      const jsonStr = JSON.stringify(data, null, 2);
      const blob = new Blob([jsonStr], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `broadcast_playroom_profile_${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      if (window.showToast) window.showToast('ส่งออกไฟล์ Profile สำเร็จ');
    } catch (e) {
      alert('ส่งออกไม่สำเร็จ: ' + e);
    }
  }

  // Import Profile (Parse JSON & Auto-Migrate)
  async function importProfile(jsonStr) {
    try {
      const source = typeof jsonStr === 'string' ? JSON.parse(jsonStr) : jsonStr;
      const response = await fetch('/api/composer/normalize', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(source)});
      if(!response.ok) throw new Error('ไฟล์นี้ไม่ใช่ Profile ของ Composer');
      const parsed = await response.json();
      CANVAS_WIDTH = parsed.canvasWidth || 1920;CANVAS_HEIGHT = parsed.canvasHeight || 1080;
      state.pages=parsed.pages.map(page=>({...page,widgets:page.widgets.map(normalizeWidget)}));
      state.activePageId=parsed.activePageId;
      state.legacyPlayroomTriggers=parsed.legacyPlayroomTriggers || [];
      state.legacyTools=parsed.legacyTools || {}; state.legacyChat=parsed.legacyChat || {};
      if(window.applyLegacyToolData)window.applyLegacyToolData(parsed);
      renderPageTabs();renderCanvasWidgets();renderLayersList();
      if(!await saveState(true))return false;
      if(window.showToast)window.showToast('นำเข้า Profile เดิมและบันทึกแล้ว');
      return true;
    } catch(error) {
      alert('นำเข้าไฟล์ไม่สำเร็จ: '+error.message);
      return false;
    }
  }

  // Toggle Clean Preview Mode
  function togglePreviewMode() {
    const modal = document.getElementById('win-composer') || document.getElementById('composerStudioModal') || document.querySelector('.composer-window');
    if (!modal) return;
    const isPreview = modal.classList.toggle('preview-clean-mode');
    const btn = document.getElementById('btnCompPreview');
    if (btn) {
      btn.innerHTML = isPreview ? '✏️ แก้ไข' : '👁️ พรีวิว';
      btn.classList.toggle('active', isPreview);
    }
    if (window.showToast) {
      window.showToast(isPreview ? 'เข้าสู่โหมดพรีวิว (ซ่อนเครื่องมือทั้งหมด)' : 'กลับสู่โหมดแก้ไข');
    }
  }

  // Setup Toolbar Events
  function setupToolbarEvents() {
    // Zoom buttons
    document.getElementById('btnCompZoomIn')?.addEventListener('click', () => setZoom(state.zoom + 0.1));
    document.getElementById('btnCompZoomOut')?.addEventListener('click', () => setZoom(state.zoom - 0.1));
    document.getElementById('btnCompZoomFit')?.addEventListener('click', autoFitCanvas);

    // Snap toggle
    const btnSnap = document.getElementById('btnCompSnap');
    if (btnSnap) {
      btnSnap.addEventListener('click', () => {
        state.snapGuides = !state.snapGuides;
        btnSnap.classList.toggle('active', state.snapGuides);
        if (window.showToast) {
          window.showToast(state.snapGuides ? 'เปิดระบบแม่เหล็กจัดแนวแล้ว' : 'ปิดระบบแม่เหล็กจัดแนวแล้ว');
        }
      });
    }

    // Background toggle
    document.querySelectorAll('.composer-bg-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.composer-bg-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const mode = btn.dataset.bg;
        const stage = document.getElementById('composerCanvasStage');
        if (stage) {
          stage.className = `composer-canvas-stage bg-${mode}`;
        }
      });
    });

    // Chat appearance chooser stays attached to Composer but renders above clipping.
    const btnChatMenu = document.getElementById('btnCompAddChatMenu');
    const menuChat = document.getElementById('compChatDropdownMenu');
    if (btnChatMenu && menuChat) {
      menuChat.setAttribute('popover','auto');menuChat.setAttribute('role','menu');
      btnChatMenu.setAttribute('aria-haspopup','menu');btnChatMenu.setAttribute('aria-expanded','false');
      const items=[...menuChat.querySelectorAll('.comp-chat-menu-item')];
      items.forEach(item=>{item.tabIndex=0;item.setAttribute('role','menuitem');});
      const close=()=>{if(menuChat.matches(':popover-open'))menuChat.hidePopover();menuChat.style.display='none';btnChatMenu.setAttribute('aria-expanded','false');};
      const open=()=>{const rect=btnChatMenu.getBoundingClientRect(),view=menuChat.ownerDocument.defaultView;menuChat.style.cssText='position:fixed;inset:auto;margin:0;display:block;left:'+Math.max(8,Math.min(rect.left,view.innerWidth-336))+'px;top:'+Math.min(rect.bottom+6,Math.max(8,view.innerHeight-340))+'px;max-height:calc(100vh - 24px);overflow-y:auto';menuChat.showPopover();btnChatMenu.setAttribute('aria-expanded','true');};
      let wasOpen=false;btnChatMenu.addEventListener('pointerdown',()=>{wasOpen=menuChat.matches(':popover-open');});
      btnChatMenu.addEventListener('click',e=>{e.stopPropagation();if(wasOpen || menuChat.matches(':popover-open'))close();else open();wasOpen=false;});
      menuChat.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();close();btnChatMenu.focus();}});
      btnChatMenu.addEventListener('keydown',e=>{if(e.key==='ArrowDown'){e.preventDefault();e.stopPropagation();open();items[0]?.focus();}});
      items.forEach((item,index)=>{item.addEventListener('click',e=>{e.stopPropagation();close();checkAndAddWidget('chat',item.dataset.chatMode || 'default');});item.addEventListener('keydown',e=>{if(['ArrowDown','ArrowUp'].includes(e.key)){e.preventDefault();e.stopPropagation();items[(index+(e.key==='ArrowDown'?1:items.length-1))%items.length].focus();}else if(['Enter',' '].includes(e.key)){e.preventDefault();item.click();}});});
      menuChat.addEventListener('toggle',()=>{btnChatMenu.setAttribute('aria-expanded',String(menuChat.matches(':popover-open')));});
    }

    // Add Widget Buttons (Excluding the chat dropdown trigger)
    document.querySelectorAll('.btn-add-widget').forEach(btn => {
      if (btn.id === 'btnCompAddChatMenu') return;
      btn.addEventListener('click', () => {
        checkAndAddWidget(btn.dataset.widgetType);
      });
    });

    // Align Buttons
    document.querySelectorAll('.composer-btn-align').forEach(btn => {
      btn.addEventListener('click', () => {
        alignWidget(btn.dataset.align);
      });
    });

    // Transform Inspector inputs (clamped to canvas bounds)
    const bindProp = (id, key, minVal) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener('change', () => {
        const widget = getSelectedWidget();
        if (!widget || widget.locked) return;
        const val = parseInt(el.value, 10);
        if (!isNaN(val)) {
          if (key === 'x') {
            widget.x = Math.max(0, Math.min(CANVAS_WIDTH - widget.width, val));
          } else if (key === 'y') {
            widget.y = Math.max(0, Math.min(CANVAS_HEIGHT - widget.height, val));
          } else if (key === 'width') {
            widget.width = Math.max(50, Math.min(CANVAS_WIDTH - widget.x, val));
          } else if (key === 'height') {
            widget.height = Math.max(30, Math.min(CANVAS_HEIGHT - widget.y, val));
          } else {
            widget[key] = Math.max(minVal, val);
          }
          renderCanvasWidgets();
          updateTransformInspector();
          saveState();
        }
      });
    };

    bindProp('compPropX', 'x', 0);
    bindProp('compPropY', 'y', 0);
    bindProp('compPropW', 'width', 50);
    bindProp('compPropH', 'height', 30);

    // Preview Mode Button
    document.getElementById('btnCompPreview')?.addEventListener('click', togglePreviewMode);

    // Export Profile Button
    document.getElementById('btnCompExport')?.addEventListener('click', exportProfile);

    // Import Profile Button & File Input
    const btnImport = document.getElementById('btnCompImport');
    const fileInput = document.getElementById('fileCompImportProfile');
    if (btnImport && fileInput) {
      btnImport.addEventListener('click', () => fileInput.click());
      fileInput.addEventListener('change', (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (evt) => {
          importProfile(evt.target.result);
          fileInput.value = '';
        };
        reader.readAsText(file);
      });
    }

    // Save Button
    document.getElementById('btnCompSave')?.addEventListener('click', saveState);

    // Copy OBS URL Button
    document.getElementById('btnCompCopyObs')?.addEventListener('click', copyComposerObsUrl);

    // Test in Browser Button
    document.getElementById('btnCompTestBrowser')?.addEventListener('click', openComposerTestInBrowser);
  }

  // Copy OBS URL
  function copyComposerObsUrl() {
    const host = (window.location.origin && window.location.origin.startsWith('http')) ? window.location.origin : 'http://localhost:8801';
    const activePage = getActivePage();
    const pageIndex = state.pages.findIndex(p => p.id === state.activePageId) + 1;
    const url = `${host}/?p=${pageIndex}`;
    saveState(true);

    if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(() => {
        if (window.showToast) window.showToast(`📋 คัดลอกลิงก์ OBS สำหรับหน้า ${pageIndex} สำเร็จ (${url})`);
      }).catch(() => {
        prompt('คัดลอกลิงก์ OBS ของคุณ:', url);
      });
    } else {
      prompt('คัดลอกลิงก์ OBS ของคุณ:', url);
    }
  }

  // Open live test preview in browser
  function openComposerTestInBrowser() {
    const host = (window.location.origin && window.location.origin.startsWith('http')) ? window.location.origin : 'http://localhost:8801';
    const pageIndex = state.pages.findIndex(p => p.id === state.activePageId) + 1;
    const url = `${host}/?p=${pageIndex}&test=1`;
    saveState(true);
    window.open(url, '_blank');
    if (window.showToast) {
      window.showToast(`🧪 เปิดหน้าต่างทดสอบ Overlay (หน้า ${pageIndex}) ในเบราว์เซอร์แล้ว`);
    }
  }

  // Expose Global Helper
  window.initComposerStudio = initComposerStudio;
  window.autoFitCanvas = autoFitCanvas;
  window.renderWidgetInnerHtml = renderWidgetInnerHtml;
  window.isFullscreenWidget = isFullscreenWidget;
  window.openComposerTestInBrowser = openComposerTestInBrowser;
  window.copyComposerObsUrl = copyComposerObsUrl;
  function bindComposerPopoutWindow(popWindow) {
    if (!popWindow || popWindow.closed) return;
    try {
      popWindow.addEventListener('resize', autoFitCanvas);
      popWindow.addEventListener('keydown', handleKeyDown);
      bindSpacebarPanning(popWindow);
      setTimeout(autoFitCanvas, 80);
    } catch (e) {
      console.warn('Could not bind composer popout window:', e);
    }
  }

  window.ComposerStudio = {
    init: initComposerStudio,
    autoFitCanvas: autoFitCanvas,
    bindWindow: bindComposerPopoutWindow,
    selectWidget: selectWidget,
    openWidgetSettings: openWidgetSettings,
    openWidgetCustomizer: openWidgetCustomizer,
    getState: () => state,
    getActivePage: getActivePage,
    state: state,
    addWidget: addWidget,
    checkAndAddWidget: checkAndAddWidget,
    deleteWidget: deleteWidget,
    duplicateWidget: duplicateWidget,
    renderCanvasWidgets: renderCanvasWidgets,
    renderLayersList: renderLayersList,
    updateTransformInspector: updateTransformInspector,
    alignWidget: alignWidget,
    demoManager: ComposerDemoManager,
    moveLayerByOne: moveLayerByOne,
    addNewPage: addNewPage,
    duplicateCurrentPage: duplicateCurrentPage,
    renameCurrentPage: renameCurrentPage,
    deletePage: deletePage,
    switchPage: switchPage,
    exportProfile: exportProfile,
    importProfile: importProfile,
    togglePreviewMode: togglePreviewMode,
    normalizeWidget: normalizeWidget,
    saveState: saveState,
    renderWidgetInnerHtml: renderWidgetInnerHtml,
    isFullscreenWidget: isFullscreenWidget,
    openTestInBrowser: openComposerTestInBrowser,
    copyObsUrl: copyComposerObsUrl
  };
  window.composerStudio = window.ComposerStudio;

  // Auto-init
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initComposerStudio);
  } else {
    initComposerStudio();
  }

})();


// ----------------------------------------------------
// ATTACH REAL-TIME BP3_BUS LISTENERS TO CANVAS STUDIO
// ----------------------------------------------------
function initStudioBusListener() {
  if (document.getElementById('obsCanvasStage') || window._studioBusReady) return;
  if (typeof window === 'undefined') return;
  const bus = window.BP3_BUS;
  if (!bus) {
    setTimeout(initStudioBusListener, 200);
    return;
  }

  
  window._studioBusReady = true;
  bus.on('REPLIE_DISMISS',()=>window.BP3LegacyReplie?.dismiss());
  let _csRandomizerTimer = null;
  bus.on('RANDOMIZER_SPIN', (data) => {
    if (!data) return;
    const curPage = window.ComposerStudio?.getActivePage?.() || window.ComposerStudio?.state?.pages?.[0];
    if (curPage) {
      curPage.widgets.forEach(w => {
        if (w.type === 'randomizer') {
          const card = document.getElementById(`compRandomizerCard_${w.id}`);
          const res = document.getElementById(`compRandomizerResult_${w.id}`);
          const hint = document.getElementById(`compRandomizerHint_${w.id}`);
          if (card && res) {
            card.style.display = 'block';
            card.style.animation = 'none';
            void card.offsetHeight;
            card.style.animation = 'randCardPopIn 0.35s cubic-bezier(0.16, 1, 0.3, 1)';

            const items = (data.items && data.items.length) ? data.items : ['1', '2'];
            let ticks = 0;
            const timer = setInterval(() => {
              ticks++;
              res.textContent = items[Math.floor(Math.random() * items.length)];
              res.style.color = '#fbbf24';
              if (ticks > 16) {
                clearInterval(timer);
                res.textContent = data.winner || items[0];
                res.style.color = '#38bdf8';
                if (hint) hint.textContent = 'สุ่มสำเร็จ 🎉';
                setTimeout(() => {
                  card.style.display = 'none';
                }, (data.duration || 5) * 1000);
              }
            }, Math.max(2, Math.min(7, Number(data.settings?.spin_duration) || 4)) * 1000 / 17);
          }
        }
      });
    }

    // On-Demand Dynamic Modal Overlay inside Composer Canvas only.
    // NEVER attach to document.body in main app window (which would cover Live Chat)!
    const canvas = document.getElementById('composer-canvas');
    if (!canvas) return;
    const compWin = document.getElementById('win-composer');
    if (compWin && !compWin.classList.contains('active')) return;
    const existing = document.getElementById('on-demand-randomizer-overlay-cs');
    if (existing) existing.remove();
    if (_csRandomizerTimer) {
      clearTimeout(_csRandomizerTimer);
      _csRandomizerTimer = null;
    }

    const items = (data.items && data.items.length) ? data.items : ['ตัวเลือก 1', 'ตัวเลือก 2'];
    const winner = data.winner || items[0];
    const title = data.title || '🎰 สุ่มกิจกรรม';
    const st = data.settings || {};
    const scale = (st.scale || 100) / 100;
    const ox = parseInt(st.offset_x, 10) || 0;
    const oy = parseInt(st.offset_y, 10) || 0;
    const holdDuration = (st.duration !== undefined ? parseFloat(st.duration) : (data.duration || 5)) * 1000;
    const anchors = {
      'top-left':['top:40px;left:40px;','translate(0,0)','top left'],
      'top-center':['top:40px;left:50%;','translate(-50%,0)','top center'],
      'top-right':['top:40px;right:40px;','translate(0,0)','top right'],
      'middle-left':['top:50%;left:40px;','translate(0,-50%)','left center'],
      'middle-right':['top:50%;right:40px;','translate(0,-50%)','right center'],
      'bottom-left':['bottom:40px;left:40px;','translate(0,0)','bottom left'],
      'bottom-center':['bottom:40px;left:50%;','translate(-50%,0)','bottom center'],
      'bottom-right':['bottom:40px;right:40px;','translate(0,0)','bottom right'],
      'center':['top:50%;left:50%;','translate(-50%,-50%)','center center']
    };
    const [anchorStyle, baseTransform, transformOrigin] = anchors[st.anchor] || anchors.center;

    const overlay = document.createElement('div');
    overlay.id = 'on-demand-randomizer-overlay-cs';
    overlay.style.cssText = `
      position: absolute;
      ${anchorStyle}
      z-index: 9999999;
      pointer-events: none;
      transform: ${baseTransform} translate(${ox}px, ${oy}px) scale(${scale});
      transform-origin: ${transformOrigin};
      transition: opacity 0.4s ease-out, transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
      opacity: 0;
      contain: layout style paint;
      isolation: isolate;
    `;
    overlay.innerHTML = `
      <div style="
        width: 460px;
        background: rgba(11, 17, 32, 0.96);
        border: 2px solid #3b82f6;
        border-radius: 18px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.85), 0 0 25px rgba(59, 130, 246, 0.25);
        padding: 24px 26px 20px 26px;
        font-family: -apple-system, BlinkMacSystemFont, 'Prompt', 'Kanit', sans-serif;
        box-sizing: border-box;
        color: #ffffff;
        text-align: center;
        contain: layout style paint;
      ">
        <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 14px;">
          <span style="font-size: 20px;">🎰</span>
          <span style="font-size: 15px; font-weight: 800; color: #38bdf8; letter-spacing: 0.5px; text-transform: uppercase;">
            <span id="cs-randomizer-title"></span>
          </span>
        </div>
        <div id="cs-roller-box" style="
          background: rgba(2, 6, 23, 0.95);
          border: 2px solid #1e293b;
          border-radius: 12px;
          height: 76px;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0 16px;
          box-sizing: border-box;
          overflow: hidden;
          transition: border-color 0.3s, background-color 0.3s;
        ">
          <span id="cs-roller-text" style="
            font-size: 24px;
            font-weight: 800;
            color: #f1f5f9;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 100%;
          ">...</span>
        </div>
        <div id="cs-footer-pill" style="
          margin-top: 14px;
          font-size: 12.5px;
          font-weight: 600;
          color: #94a3b8;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
        ">
          <span>⚡ กำลังสุ่ม...</span>
        </div>
      </div>
    `;
    const palette = {pastel:['#c4b5fd','#f9a8d4'], neon:['#d946ef','#22d3ee'], gold:['#f59e0b','#fbbf24'], mint:['#10b981','#6ee7b7']}[st.color_theme] || ['#c4b5fd','#f9a8d4'];
    overlay.firstElementChild.style.borderColor = palette[0];
    overlay.querySelector('#cs-randomizer-title').textContent = title;
    overlay.querySelector('#cs-randomizer-title').parentElement.style.color = palette[1];
    canvas.appendChild(overlay);
    requestAnimationFrame(() => { overlay.style.opacity = '1'; });

    const rollerText = overlay.querySelector('#cs-roller-text');
    const rollerBox = overlay.querySelector('#cs-roller-box');
    const footerPill = overlay.querySelector('#cs-footer-pill');
    const randomVisual = window.BP3RandomizerVisual?.mount(overlay.firstElementChild, data, Math.max(2, Math.min(7, Number(st.spin_duration) || 4)));

    let ticks = 0;
    const maxTicks = 26;
    const delay = Math.max(2, Math.min(7, Number(st.spin_duration) || 4)) * 1000 / maxTicks;

    function runCsTick() {
      if (!overlay.isConnected) return;
      ticks++;
      const cand = items[Math.floor(Math.random() * items.length)];
      if (rollerText) rollerText.textContent = cand;
      if (ticks < maxTicks) {
        setTimeout(runCsTick, delay);
      } else {
        if (rollerText) rollerText.textContent = winner;
        randomVisual?.finish();
        if (rollerBox) {
          rollerBox.style.borderColor = '#f59e0b';
          rollerBox.style.backgroundColor = 'rgba(245, 158, 11, 0.12)';
          rollerText.style.color = '#fbbf24';
        }
        if (footerPill) {
          footerPill.innerHTML = '<span style="color: #fbbf24; font-weight: 700;">🎉 ผลการสุ่มเรียบร้อยแล้ว</span>';
        }
        _csRandomizerTimer = setTimeout(() => {
          overlay.style.opacity = '0';
          overlay.style.transform = `${baseTransform} translate(${ox}px, ${oy - 20}px) scale(${scale * 0.95})`;
          setTimeout(() => { overlay.remove(); }, 400);
        }, holdDuration);
      }
    }
    runCsTick();
  });

  bus.on('ASK_UPDATE', (data) => {
    if(data?.demo && window._liveAskState?.active)return;
    if(!data?.demo)window._liveAskState = data;
    const curPage = window.ComposerStudio?.getActivePage?.() || window.ComposerStudio?.state?.pages?.[0];
    if (curPage) {
      curPage.widgets.forEach(w => {
        if (w.type === 'ask') {
          const panel = document.getElementById(`compAskPanel_${w.id}`);
          const isAskActive = data && data.active === true && (data.phase === 'voting' || data.phase === 'paused' || data.phase === 'ended');
          if (panel) {
            panel.style.display = isAskActive ? 'block' : 'none';
          }
          const qEl = document.getElementById(`compAskQ_${w.id}`);
          if (qEl) qEl.textContent = data.phase === 'ended' ? `🏆 สรุปผล: ${data.question}` : `📊 ${data.question}`;
          const timerEl = document.getElementById(`compAskTimer_${w.id}`);
          if (timerEl) {
            if (data.phase === 'ended') {
              timerEl.textContent = '🏆 สรุปผล';
              timerEl.style.color = '#fbbf24';
            } else if (data.phase === 'paused') {
              timerEl.textContent = '⏸ พักโหวต';
              timerEl.style.color = '#f59e0b';
            } else if (data.remainingSec != null) {
              timerEl.textContent = `⏱ ${data.remainingSec}s`;
              timerEl.style.color = data.remainingSec <= 10 ? '#f43f5e' : '#94a3b8';
            } else {
              timerEl.textContent = '🗳️ โหวตสด';
              timerEl.style.color = '#34d399';
            }
          }
          const listEl = document.getElementById(`compAskChoicesList_${w.id}`);
          if (listEl && data.choices) {
            const isEnded = (data.phase === 'ended');
            const choices = isEnded ? [...data.choices].sort((a,b) => (b.votes || 0) - (a.votes || 0)) : data.choices;
            listEl.innerHTML = choices.map((c, idx) => {
              const isWinner = isEnded && idx === 0 && (c.votes || 0) > 0;
              return `
              <div style="background:${isWinner ? 'rgba(251,191,36,0.15)' : 'rgba(255,255,255,0.05)'}; border:${isWinner ? '1.5px solid #fbbf24' : '1px solid rgba(255,255,255,0.06)'}; border-radius:6px; padding:6px 10px; position:relative; overflow:hidden;">
                <div style="position:absolute; inset:0; width:${c.pct}%; background:${isWinner ? '#f59e0b' : (c.color || '#38bdf8')}; opacity:${isWinner ? '0.35' : '0.25'}; border-radius:6px; transition:width 0.4s ease;"></div>
                <div style="position:relative; z-index:1; display:flex; justify-content:space-between; font-size:12px; font-weight:600; color:#ffffff;">
                  <span>${isWinner ? '👑 ' : ''}${c.label}: ${c.text}</span>
                  <span style="color:${isWinner ? '#fbbf24' : (c.color || '#38bdf8')}; font-weight:700;">${c.pct}% (${c.votes || 0})</span>
                </div>
              </div>
            `;
            }).join('');
          }
        }
      });
    }
  });

  bus.on('GIVEAWAY_UPDATE', (data) => {
    if(data?.demo && window._liveGwState?.active)return;
    if(!data?.demo)window._liveGwState = data;
    window.BP3LegacyGiveaway?.render(data);
  });

  bus.on('REPLIE_ACTION', (data) => {
    if(window.BP3LegacyReplie){window.BP3LegacyReplie.render(data);return;}
    const curPage = window.ComposerStudio?.getActivePage?.() || window.ComposerStudio?.state?.pages?.[window.ComposerStudio?.state?.activePageIndex];
    if (curPage) {
      curPage.widgets.forEach(w => {
        if (w.type === 'character' || w.type === 'avatar' || w.type === 'replie') {
          const bubble = document.getElementById(`compCharBubble_${w.id}`);
          const bubbleText = document.getElementById(`compCharBubbleText_${w.id}`);
          const img = document.getElementById(`compCharImg_${w.id}`);
          if (bubble && bubbleText) {
            bubbleText.textContent = data.text || 'สวัสดีครับ!';
            bubble.style.display = 'block';
            bubble.style.opacity = '1';
            if (img) {
              img.style.transform = 'scale(1.15) translateY(-8px)';
              setTimeout(() => { img.style.transform = 'scale(1)'; }, 350);
            }
            setTimeout(() => {
              bubble.style.opacity = '0';
              setTimeout(() => { bubble.style.display = 'none'; }, 300);
            }, 5000);
          }
        }
      });
    }
  });

  bus.on('PLAYROOM_PLAY_CLIP', (data) => {
    const curPage = window.ComposerStudio?.getActivePage?.() || window.ComposerStudio?.state?.pages?.[window.ComposerStudio?.state?.activePageIndex];
    if (curPage) {
      curPage.widgets.forEach(w => {
        if (w.type === 'playroom') {
          const stage = document.getElementById(`compPlayroomStage_${w.id}`);
          const idle = document.getElementById(`compPlayroomIdle_${w.id}`);
          const title = document.getElementById(`compPlayroomTitle_${w.id}`);
          const tag = document.getElementById(`compPlayroomTag_${w.id}`);
          const bar = document.getElementById(`compPlayroomBar_${w.id}`);
          if (stage && idle && title && tag && bar) {
            title.textContent = data.name;
            tag.textContent = `คำสั่ง ${data.trigger}`;
            idle.style.display = 'none';
            stage.style.display = 'flex';
            bar.style.transition = 'none';
            bar.style.width = '100%';
            setTimeout(() => {
              bar.style.transition = `width ${data.duration || 5}s linear`;
              bar.style.width = '0%';
            }, 50);

            try {
              const audio = new Audio(data.url);
              audio.volume = (data.vol || 80) / 100;
              audio.play().catch(() => {});
            } catch (e) {}

            setTimeout(() => {
              stage.style.display = 'none';
              idle.style.display = 'flex';
            }, (data.duration || 5) * 1000);
          }
        }
      });
    }
  });
}

if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', initStudioBusListener);
  setTimeout(initStudioBusListener, 500);
}
