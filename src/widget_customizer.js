/* ========================================================
   BROADCAST PLAYROOM 3 - CHAT WIDGET CUSTOMIZER LOGIC
   OneComme-style visual editor with real-time live preview
   Integrated 80 Presets from Version 2 with 8-per-page Pagination
   Zero-lag Real-time Danmaku & Crisp Speech Balloon Rendering
   ======================================================== */

(function () {
  'use strict';

  // Default configuration covering all 5 chat modes
  const DEFAULT_CONFIG = {
    mode: 'default', // 'default' | 'theme' | 'danmaku' | 'balloon' | 'character'
    theme: 'glass',  // 80 themes available in window.CWC_ALL_THEMES
    direction: 'bottom',
    layout: 'inline',
    chat_align: 'left',
    show_logo: true,
    show_timestamp: false,
    max_messages: 20,
    msg_spacing: 6,
    chat_padding: 12,

    // Typography
    font_family: 'Kanit',
    font_size: 15,
    font_weight: '600',
    font_color: '#ffffff',
    text_stroke: false,
    text_stroke_width: 2,
    text_stroke_color: '#000000',
    text_shadow: true,
    text_shadow_blur: 3,
    text_shadow_color: '#000000',

    // Box & Bubble
    box_enabled: true,
    box_width: 'fit',
    bg_color: '#1e1f22',
    bg_opacity: 0.85,
    box_radius: 8,
    box_padding: 8,
    box_border: false,
    box_border_width: 1,
    box_border_color: '#5865f2',
    box_shadow: true,
    box_glow: false,
    box_glow_color: '#a855f7',

    // Animations
    animation: 'slide_up',
    exit_animation: 'fade_out',
    auto_hide: false,
    hide_after: 8,

    // Danmaku Slider
    slider_duration: 6,
    slider_lane_height: 40,
    slider_zone: 'middle',
    slider_font_size: 24,
    slider_font_family: 'Kanit',
    slider_font_weight: '700',
    slider_text_color: '#ffffff',
    slider_text_stroke: true,
    slider_text_stroke_width: 2,
    slider_text_stroke_color: '#000000',
    slider_text_shadow: true,
    slider_text_shadow_blur: 3,
    slider_text_shadow_color: '#000000',
    slider_show_logo: true,
    slider_emote_size: 28,

    // Balloon
    balloon_bg_opacity: 0.95,
    balloon_hide_after: 5,
    balloon_font_size: 18,
    balloon_font_family: 'Kanit',
    balloon_font_weight: '600',
    balloon_text_color: '#1a1a2e',
    balloon_emote_size: 28,

    // Character Talk
    character_size: 110,
    character_bubble_width: 380,
    character_hide_after: 6,
    character_max_on_screen: 5,
    character_random_pos: true,
    character_font_family: 'Kanit',
    character_font_color: '#1a1a2e',
    character_name_size: 12,
    character_name_color: '#ffffff',
    character_show_name: true,
    character_show_logo: true,

    // Author Colors
    author_color_mode: 'auto',
    author_color_map: {
      twitch: '#9146ff',
      youtube: '#ff0000',
      kick: '#53fc18',
      tiktok: '#ff0050',
      soop: '#2e7bf6',
      mylive: '#ff9900'
    },

    // Custom CSS
    custom_css_enabled: false,
    custom_css: ''
  };

  // Mock messages pool
  const MOCK_MESSAGES = [
    { user: 'สตรีมเมอร์เกมเมอร์', text: 'สวัสดีทุกคนในไลฟ์สตรีม ภาพและเสียงชัดเจนดีไหมครับ! 🎮', platform: 'youtube', color: '#ef4444' },
    { user: 'Zack_Twitch', text: 'สตรีมภาพสวยคมชัด 60fps ลื่นไหลมากเลยครับ 🔥', platform: 'twitch', color: '#a855f7' },
    { user: 'Kik_Master', text: 'ยินดีต้อนรับเพื่อนๆ ทุกคนที่แวะเข้ามาพูดคุยกันนะครับ!', platform: 'kick', color: '#22c55e' },
    { user: 'Mali_Cute', text: 'กดติดตามและกดแชร์เป็นกำลังใจให้สตรีมเมอร์ด้วยน้า 💖', platform: 'tiktok', color: '#ec4899' },
    { user: 'Captain_Soop', text: 'เล่นเกมเพลินมาก ดนตรีแบ็คกราวด์ฟังสบายสุดๆ ครับ ⭐', platform: 'soop', color: '#3b82f6' }
  ];

  let currentConfig = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
  let mockList = [...MOCK_MESSAGES];
  let previewBgMode = 'checkered';

  // Theme Presets Pagination State
  let themeCurrentPage = 0;
  const THEMES_PER_PAGE = 8;

  // Load from localStorage if present
  function loadSavedConfig() {
    try {
      const saved = localStorage.getItem('bp3_chat_widget_config');
      if (saved) {
        const parsed = JSON.parse(saved);
        currentConfig = Object.assign({}, DEFAULT_CONFIG, parsed);
        // Normalize mode if migrating from old theme2
        if (currentConfig.mode === 'theme2') {
          currentConfig.mode = 'theme';
        }
      }
    } catch (e) {
      console.warn('Failed to parse saved widget config:', e);
    }
  }

  // Initialize UI controls and event listeners
  function init() {
    loadSavedConfig();
    renderThemePresetsPage(themeCurrentPage);
    syncControlsFromConfig();
    setupEventListeners();
    applyThemeCssForCurrentConfig();
    applyLivePreview();
  }

  // Switch between 5 main modes
  function switchWidgetMode(mode) {
    currentConfig.mode = mode;
    document.querySelectorAll('.cwc-tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.mode === mode);
    });

    // Show/hide mode-specific accordion cards
    const cardDanmaku = document.getElementById('cwcSecDanmaku');
    const cardBalloon = document.getElementById('cwcSecBalloon');
    const cardCharacter = document.getElementById('cwcSecCharacter');
    const cardThemePresets = document.getElementById('cwcSecThemePresets');
    const cardDefaultBox = document.getElementById('cwcSecBox');
    const cardLayout = document.getElementById('cwcSecLayout');

    if (cardDanmaku) cardDanmaku.style.display = (mode === 'danmaku') ? 'block' : 'none';
    if (cardBalloon) cardBalloon.style.display = (mode === 'balloon') ? 'block' : 'none';
    if (cardCharacter) cardCharacter.style.display = (mode === 'character') ? 'block' : 'none';
    if (cardThemePresets) cardThemePresets.style.display = (mode === 'theme') ? 'block' : 'none';

    // Box styling applies to default and themes
    if (cardDefaultBox) cardDefaultBox.style.display = (mode === 'danmaku' || mode === 'balloon' || mode === 'character') ? 'none' : 'block';
    if (cardLayout) cardLayout.style.display = (mode === 'danmaku') ? 'none' : 'block';

    applyThemeCssForCurrentConfig();
    applyLivePreview();

    if (window.showToast) {
      const modeNames = {
        default: 'ค่ามาตรฐาน',
        theme: 'ธีมสำเร็จรูป',
        danmaku: 'ดันมากุ',
        balloon: 'บอลลูนคำพูด',
        character: 'ตัวละครพูด'
      };
      window.showToast(`เปลี่ยนโหมด: ${modeNames[mode] || mode}`);
    }
  }

  // Render Theme Presets Grid with 8 items per page
  function renderThemePresetsPage(pageIndex) {
    const grid = document.getElementById('cwcPresetsGrid');
    const indicator = document.getElementById('themePageIndicator');
    const btnPrev = document.getElementById('btnThemePrev');
    const btnNext = document.getElementById('btnThemeNext');
    if (!grid) return;

    const allThemes = window.CWC_ALL_THEMES || [];
    const totalPages = Math.max(1, Math.ceil(allThemes.length / THEMES_PER_PAGE));
    themeCurrentPage = Math.max(0, Math.min(pageIndex, totalPages - 1));

    const start = themeCurrentPage * THEMES_PER_PAGE;
    const pageThemes = allThemes.slice(start, start + THEMES_PER_PAGE);

    grid.innerHTML = '';
    pageThemes.forEach(t => {
      const card = document.createElement('div');
      card.className = `cwc-preset-card ${currentConfig.theme === t.id ? 'active' : ''}`;
      card.dataset.theme = t.id;
      card.title = t.name;

      card.innerHTML = `
        <div class="cwc-preset-badge">${t.badge || '🎨'}</div>
        <div class="cwc-preset-info">
          <div class="cwc-preset-name">${t.name}</div>
          <div class="cwc-preset-desc">${t.desc || ''}</div>
        </div>
      `;

      card.addEventListener('click', () => {
        selectTheme(t.id);
      });

      grid.appendChild(card);
    });

    if (indicator) {
      indicator.textContent = `หน้า ${themeCurrentPage + 1} / ${totalPages}`;
    }
    if (btnPrev) {
      btnPrev.disabled = (themeCurrentPage === 0);
    }
    if (btnNext) {
      btnNext.disabled = (themeCurrentPage >= totalPages - 1);
    }
  }

  // Select a theme
  function selectTheme(themeId) {
    currentConfig.theme = themeId;
    document.querySelectorAll('.cwc-preset-card').forEach(c => {
      c.classList.toggle('active', c.dataset.theme === themeId);
    });

    applyThemeCssForCurrentConfig();
    applyLivePreview();

    if (window.showToast) {
      const allThemes = window.CWC_ALL_THEMES || [];
      const found = allThemes.find(t => t.id === themeId);
      window.showToast(`เลือกธีม: ${found ? found.name : themeId}`);
    }
  }

  // Apply theme CSS scoped to live preview
  function applyThemeCssForCurrentConfig() {
    let tag = document.getElementById('cwcThemeCustomStyle');
    if (!tag) {
      tag = document.createElement('style');
      tag.id = 'cwcThemeCustomStyle';
      document.head.appendChild(tag);
    }

    if (currentConfig.mode !== 'theme') {
      tag.textContent = '';
      return;
    }

    const allThemes = window.CWC_ALL_THEMES || [];
    const t = allThemes.find(item => item.id === currentConfig.theme);
    if (!t || !t.css) {
      tag.textContent = '';
      return;
    }

    // Correctly scope CSS rules to #cwcPreviewStage without breaking .msg-bg or pseudo-elements
    let scoped = t.css
      .replace(/:root\b/g, '#cwcPreviewStage')
      .replace(/(^|[\s,;{}])\.msg([:\s\.\-_\[{]|$)/g, '$1#cwcPreviewStage .msg$2')
      .replace(/(^|[\s,;{}])\.chat-line([:\s\.\-_\[{]|$)/g, '$1#cwcPreviewStage .chat-line$2');

    tag.textContent = scoped;
  }

  // Sync controls UI with currentConfig
  function syncControlsFromConfig() {
    // Top Tabs
    document.querySelectorAll('.cwc-tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.mode === currentConfig.mode);
    });

    // Inputs helper
    const setVal = (id, val) => {
      const el = document.getElementById(id);
      if (!el) return;
      if (el.type === 'checkbox') {
        el.checked = !!val;
      } else {
        el.value = val;
      }
    };

    const setSlider = (id, val, suffix = '') => {
      const el = document.getElementById(id);
      const lbl = document.getElementById(id + 'Val');
      if (el) el.value = val;
      if (lbl) lbl.textContent = val + suffix;
    };

    // Layout
    setVal('cwcDirection', currentConfig.direction);
    setVal('cwcLayout', currentConfig.layout);
    setVal('cwcChatAlign', currentConfig.chat_align);
    setVal('cwcShowLogo', currentConfig.show_logo);
    setVal('cwcShowTimestamp', currentConfig.show_timestamp);
    setSlider('cwcMaxMessages', currentConfig.max_messages, ' ข้อความ');
    setSlider('cwcMsgSpacing', currentConfig.msg_spacing, 'px');
    setSlider('cwcChatPadding', currentConfig.chat_padding, 'px');

    // Typography
    setVal('cwcFontFamily', currentConfig.font_family);
    setSlider('cwcFontSize', currentConfig.font_size, 'px');
    setVal('cwcFontWeight', currentConfig.font_weight);
    setVal('cwcFontColor', currentConfig.font_color);
    setVal('cwcFontColorHex', currentConfig.font_color);
    setVal('cwcTextStroke', currentConfig.text_stroke);
    setSlider('cwcTextStrokeWidth', currentConfig.text_stroke_width, 'px');
    setVal('cwcTextStrokeColor', currentConfig.text_stroke_color);
    setVal('cwcTextStrokeColorHex', currentConfig.text_stroke_color);
    setVal('cwcTextShadow', currentConfig.text_shadow);
    setSlider('cwcTextShadowBlur', currentConfig.text_shadow_blur, 'px');
    setVal('cwcTextShadowColor', currentConfig.text_shadow_color);
    setVal('cwcTextShadowColorHex', currentConfig.text_shadow_color);

    // Box
    setVal('cwcBoxEnabled', currentConfig.box_enabled);
    setVal('cwcBoxWidth', currentConfig.box_width);
    setVal('cwcBgColor', currentConfig.bg_color);
    setVal('cwcBgColorHex', currentConfig.bg_color);
    setSlider('cwcBgOpacity', Math.round(currentConfig.bg_opacity * 100), '%');
    setSlider('cwcBoxRadius', currentConfig.box_radius, 'px');
    setSlider('cwcBoxPadding', currentConfig.box_padding, 'px');
    setVal('cwcBoxBorder', currentConfig.box_border);
    setSlider('cwcBoxBorderWidth', currentConfig.box_border_width, 'px');
    setVal('cwcBoxBorderColor', currentConfig.box_border_color);
    setVal('cwcBoxBorderColorHex', currentConfig.box_border_color);
    setVal('cwcBoxShadow', currentConfig.box_shadow);
    setVal('cwcBoxGlow', currentConfig.box_glow);
    setVal('cwcBoxGlowColor', currentConfig.box_glow_color);
    setVal('cwcBoxGlowColorHex', currentConfig.box_glow_color);

    // Animations
    setVal('cwcAnimation', currentConfig.animation);
    setVal('cwcExitAnimation', currentConfig.exit_animation);
    setVal('cwcAutoHide', currentConfig.auto_hide);
    setSlider('cwcHideAfter', currentConfig.hide_after, ' วินาที');

    // Danmaku
    setSlider('cwcSliderDuration', currentConfig.slider_duration, 's');
    setSlider('cwcSliderLaneHeight', currentConfig.slider_lane_height, 'px');
    setVal('cwcSliderZone', currentConfig.slider_zone);
    setSlider('cwcSliderFontSize', currentConfig.slider_font_size, 'px');
    setVal('cwcSliderTextColor', currentConfig.slider_text_color);
    setVal('cwcSliderTextColorHex', currentConfig.slider_text_color);
    setVal('cwcSliderTextStroke', currentConfig.slider_text_stroke);
    setSlider('cwcSliderStrokeWidth', currentConfig.slider_text_stroke_width, 'px');
    setVal('cwcSliderStrokeColor', currentConfig.slider_text_stroke_color);
    setVal('cwcSliderTextShadow', currentConfig.slider_text_shadow);
    setVal('cwcSliderShowLogo', currentConfig.slider_show_logo);

    // Balloon
    setSlider('cwcBalloonOpacity', Math.round(currentConfig.balloon_bg_opacity * 100), '%');
    setSlider('cwcBalloonHideAfter', currentConfig.balloon_hide_after, 's');
    setSlider('cwcBalloonFontSize', currentConfig.balloon_font_size, 'px');
    setVal('cwcBalloonTextColor', currentConfig.balloon_text_color);

    // Character
    setSlider('cwcCharSize', currentConfig.character_size, 'px');
    setSlider('cwcCharBubbleWidth', currentConfig.character_bubble_width, 'px');
    setSlider('cwcCharHideAfter', currentConfig.character_hide_after, 's');
    setVal('cwcCharRandomPos', currentConfig.character_random_pos);
    setVal('cwcCharShowName', currentConfig.character_show_name);

    // Custom CSS
    setVal('cwcCustomCssEnabled', currentConfig.custom_css_enabled);
    setVal('cwcCustomCss', currentConfig.custom_css || '');

    switchWidgetMode(currentConfig.mode);
  }

  // Setup UI event listeners
  function setupEventListeners() {
    // Mode Switcher Tabs
    document.querySelectorAll('.cwc-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        switchWidgetMode(btn.dataset.mode);
      });
    });

    // Accordion headers toggle
    document.querySelectorAll('.cwc-section-header').forEach(hdr => {
      hdr.addEventListener('click', () => {
        const parent = hdr.closest('.cwc-section');
        if (parent) parent.classList.toggle('collapsed');
      });
    });

    // Theme Pagination Buttons
    const btnPrev = document.getElementById('btnThemePrev');
    const btnNext = document.getElementById('btnThemeNext');
    if (btnPrev) {
      btnPrev.addEventListener('click', () => {
        renderThemePresetsPage(themeCurrentPage - 1);
      });
    }
    if (btnNext) {
      btnNext.addEventListener('click', () => {
        renderThemePresetsPage(themeCurrentPage + 1);
      });
    }

    // Helper binder for inputs
    const bindInput = (id, key, type = 'text', suffix = '') => {
      const el = document.getElementById(id);
      if (!el) return;
      const handler = () => {
        if (type === 'checkbox') {
          currentConfig[key] = el.checked;
        } else if (type === 'number') {
          currentConfig[key] = parseFloat(el.value);
          const lbl = document.getElementById(id + 'Val');
          if (lbl) lbl.textContent = el.value + suffix;
        } else if (type === 'opacity') {
          currentConfig[key] = parseFloat(el.value) / 100;
          const lbl = document.getElementById(id + 'Val');
          if (lbl) lbl.textContent = el.value + '%';
        } else {
          currentConfig[key] = el.value;
        }
        applyLivePreview();
      };
      el.addEventListener('input', handler);
      el.addEventListener('change', handler);
    };

    // Helper for color pickers paired with hex inputs
    const bindColor = (pickerId, hexId, key) => {
      const pick = document.getElementById(pickerId);
      const hex = document.getElementById(hexId);
      if (pick) {
        pick.addEventListener('input', () => {
          if (hex) hex.value = pick.value.toUpperCase();
          currentConfig[key] = pick.value;
          applyLivePreview();
        });
      }
      if (hex) {
        hex.addEventListener('input', () => {
          let val = hex.value;
          if (!val.startsWith('#')) val = '#' + val;
          if (/^#[0-9A-Fa-f]{6}$/.test(val)) {
            if (pick) pick.value = val;
            currentConfig[key] = val;
            applyLivePreview();
          }
        });
      }
    };

    // Bind layout controls
    bindInput('cwcDirection', 'direction');
    bindInput('cwcLayout', 'layout');
    bindInput('cwcChatAlign', 'chat_align');
    bindInput('cwcShowLogo', 'show_logo', 'checkbox');
    bindInput('cwcShowTimestamp', 'show_timestamp', 'checkbox');
    bindInput('cwcMaxMessages', 'max_messages', 'number', ' ข้อความ');
    bindInput('cwcMsgSpacing', 'msg_spacing', 'number', 'px');
    bindInput('cwcChatPadding', 'chat_padding', 'number', 'px');

    // Bind typography
    bindInput('cwcFontFamily', 'font_family');
    bindInput('cwcFontSize', 'font_size', 'number', 'px');
    bindInput('cwcFontWeight', 'font_weight');
    bindColor('cwcFontColor', 'cwcFontColorHex', 'font_color');
    bindInput('cwcTextStroke', 'text_stroke', 'checkbox');
    bindInput('cwcTextStrokeWidth', 'text_stroke_width', 'number', 'px');
    bindColor('cwcTextStrokeColor', 'cwcTextStrokeColorHex', 'text_stroke_color');
    bindInput('cwcTextShadow', 'text_shadow', 'checkbox');
    bindInput('cwcTextShadowBlur', 'text_shadow_blur', 'number', 'px');
    bindColor('cwcTextShadowColor', 'cwcTextShadowColorHex', 'text_shadow_color');

    // Bind box
    bindInput('cwcBoxEnabled', 'box_enabled', 'checkbox');
    bindInput('cwcBoxWidth', 'box_width');
    bindColor('cwcBgColor', 'cwcBgColorHex', 'bg_color');
    bindInput('cwcBgOpacity', 'bg_opacity', 'opacity');
    bindInput('cwcBoxRadius', 'box_radius', 'number', 'px');
    bindInput('cwcBoxPadding', 'box_padding', 'number', 'px');
    bindInput('cwcBoxBorder', 'box_border', 'checkbox');
    bindInput('cwcBoxBorderWidth', 'box_border_width', 'number', 'px');
    bindColor('cwcBoxBorderColor', 'cwcBoxBorderColorHex', 'box_border_color');
    bindInput('cwcBoxShadow', 'box_shadow', 'checkbox');
    bindInput('cwcBoxGlow', 'box_glow', 'checkbox');
    bindColor('cwcBoxGlowColor', 'cwcBoxGlowColorHex', 'box_glow_color');

    // Bind animations
    bindInput('cwcAnimation', 'animation');
    bindInput('cwcExitAnimation', 'exit_animation');
    bindInput('cwcAutoHide', 'auto_hide', 'checkbox');
    bindInput('cwcHideAfter', 'hide_after', 'number', ' วินาที');

    // Bind Danmaku
    bindInput('cwcSliderDuration', 'slider_duration', 'number', 's');
    bindInput('cwcSliderLaneHeight', 'slider_lane_height', 'number', 'px');
    bindInput('cwcSliderZone', 'slider_zone');
    bindInput('cwcSliderFontSize', 'slider_font_size', 'number', 'px');
    bindColor('cwcSliderTextColor', 'cwcSliderTextColorHex', 'slider_text_color');
    bindInput('cwcSliderTextStroke', 'slider_text_stroke', 'checkbox');
    bindInput('cwcSliderStrokeWidth', 'slider_text_stroke_width', 'number', 'px');
    bindColor('cwcSliderStrokeColor', 'cwcSliderStrokeColorHex', 'slider_text_stroke_color');
    bindInput('cwcSliderTextShadow', 'slider_text_shadow', 'checkbox');
    bindInput('cwcSliderShowLogo', 'slider_show_logo', 'checkbox');

    // Bind Balloon
    bindInput('cwcBalloonOpacity', 'balloon_bg_opacity', 'opacity');
    bindInput('cwcBalloonHideAfter', 'balloon_hide_after', 'number', 's');
    bindInput('cwcBalloonFontSize', 'balloon_font_size', 'number', 'px');
    bindColor('cwcBalloonTextColor', 'cwcBalloonTextColor', 'balloon_text_color');

    // Bind Character
    bindInput('cwcCharSize', 'character_size', 'number', 'px');
    bindInput('cwcCharBubbleWidth', 'character_bubble_width', 'number', 'px');
    bindInput('cwcCharHideAfter', 'character_hide_after', 'number', 's');
    bindInput('cwcCharRandomPos', 'character_random_pos', 'checkbox');
    bindInput('cwcCharShowName', 'character_show_name', 'checkbox');

    // Bind Custom CSS
    bindInput('cwcCustomCssEnabled', 'custom_css_enabled', 'checkbox');
    bindInput('cwcCustomCss', 'custom_css');

    // Background toggle buttons
    document.querySelectorAll('.cwc-bg-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.cwc-bg-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        previewBgMode = btn.dataset.bg;
        setPreviewStageBg(previewBgMode);
      });
    });

    // Preview Action Buttons
    const btnAddMsg = document.getElementById('cwcBtnAddMsg');
    const btnClearStage = document.getElementById('cwcBtnClearStage');
    const btnResetDefaults = document.getElementById('cwcBtnResetDefaults');
    const btnSavePreset = document.getElementById('cwcBtnSavePreset');
    const btnCopyObs = document.getElementById('cwcBtnCopyObs');

    if (btnAddMsg) btnAddMsg.addEventListener('click', addMockMessage);
    if (btnClearStage) btnClearStage.addEventListener('click', clearPreviewStage);
    if (btnResetDefaults) btnResetDefaults.addEventListener('click', resetToDefaults);
    if (btnSavePreset) btnSavePreset.addEventListener('click', saveConfiguration);
    if (btnCopyObs) btnCopyObs.addEventListener('click', copyObsUrl);
  }

  // Set background of preview stage
  function setPreviewStageBg(mode) {
    const stage = document.getElementById('cwcPreviewStage');
    if (!stage) return;
    stage.className = `cwc-stage bg-${mode}`;
  }

  // Primary rendering function that updates the Live Preview in real time
  function applyLivePreview() {
    const stage = document.getElementById('cwcPreviewStage');
    if (!stage) return;

    const mode = currentConfig.mode;

    if (mode === 'danmaku') {
      updateOrRenderDanmakuPreview(stage);
    } else if (mode === 'balloon') {
      renderBalloonPreview(stage);
    } else if (mode === 'character') {
      renderCharacterPreview(stage);
    } else {
      // Default or Theme
      renderDefaultOrThemePreview(stage);
    }

    // Apply custom CSS if enabled
    applyCustomCssToPreview();
  }

  // 1. Render Default / Theme Mode
  function renderDefaultOrThemePreview(stage) {
    stage.innerHTML = '';
    const feed = document.createElement('div');
    feed.className = 'cwc-chat-feed';
    feed.style.flexDirection = currentConfig.direction === 'top' ? 'column' : 'column-reverse';
    feed.style.justifyContent = currentConfig.direction === 'top' ? 'flex-start' : 'flex-end';
    feed.style.padding = `${currentConfig.chat_padding}px`;
    feed.style.gap = `${currentConfig.msg_spacing}px`;

    mockList.slice(0, currentConfig.max_messages).forEach((msg, idx) => {
      const item = document.createElement('div');
      item.className = `cwc-msg-item msg chat-line theme-${currentConfig.theme || 'default'}`;
      item.style.alignSelf = currentConfig.chat_align === 'center' ? 'center' : (currentConfig.chat_align === 'right' ? 'flex-end' : 'flex-start');
      item.style.animation = `cwc-${currentConfig.animation || 'fade'} 0.3s ease-out`;

      // Theme background carrier element
      const msgBg = document.createElement('div');
      msgBg.className = 'msg-bg';
      item.appendChild(msgBg);

      // Box styling (Default Mode)
      if (currentConfig.mode === 'default' && currentConfig.box_enabled) {
        const hex = currentConfig.bg_color || '#1e1f22';
        const r = parseInt(hex.slice(1, 3), 16) || 30;
        const g = parseInt(hex.slice(3, 5), 16) || 31;
        const b = parseInt(hex.slice(5, 7), 16) || 34;
        const opacity = currentConfig.bg_opacity ?? 0.85;

        item.style.backgroundColor = `rgba(${r}, ${g}, ${b}, ${opacity})`;
        item.style.borderRadius = `${currentConfig.box_radius}px`;
        item.style.padding = `${currentConfig.box_padding}px 12px`;
        item.style.width = currentConfig.box_width === 'full' ? '100%' : 'fit-content';

        if (currentConfig.box_border) {
          item.style.border = `${currentConfig.box_border_width}px solid ${currentConfig.box_border_color}`;
        }
        if (currentConfig.box_shadow) {
          item.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
        }
        if (currentConfig.box_glow) {
          item.style.boxShadow = `0 0 12px ${currentConfig.box_glow_color || '#a855f7'}`;
        }
      } else if (currentConfig.mode === 'default') {
        item.style.background = 'transparent';
        item.style.padding = '3px 0';
      }

      // Avatar
      let avatarHtml = '';
      if (currentConfig.layout !== 'message_only') {
        const seed = encodeURIComponent(msg.user);
        avatarHtml = `<img class="cwc-msg-avatar" src="https://api.dicebear.com/7.x/bottts/svg?seed=${seed}" alt="avatar" onerror="this.style.display='none'">`;
      }

      // Logo
      let logoHtml = '';
      if (currentConfig.show_logo && currentConfig.layout !== 'message_only') {
        const platK = (msg.platform || 'youtube').toLowerCase();
        const pSrc = (typeof PLATFORM_LOGOS !== 'undefined' && PLATFORM_LOGOS[platK]) ? PLATFORM_LOGOS[platK] : `./assets/platforms/${platK}.png`;
        logoHtml = `<img class="cwc-msg-logo logo" src="${pSrc}" alt="${platK}" style="width:16px;height:16px;object-fit:contain;vertical-align:middle;display:inline-block;flex-shrink:0;margin-right:6px;" onerror="this.src='./assets/platforms/${platK}.png'; this.onerror=function(){this.style.display='none';};">`;
      }

      // Timestamp
      let timeHtml = '';
      if (currentConfig.show_timestamp) {
        timeHtml = `<span class="cwc-msg-time">18:3${idx}</span>`;
      }

      // Author color
      let authorColor = msg.color || '#5865f2';
      if (currentConfig.author_color_mode === 'custom' && currentConfig.author_color_map[msg.platform]) {
        authorColor = currentConfig.author_color_map[msg.platform];
      }

      // Stroke & Shadow on Text with paint-order: stroke fill
      let strokeStyle = currentConfig.text_stroke ? `-webkit-text-stroke: ${currentConfig.text_stroke_width}px ${currentConfig.text_stroke_color}; paint-order: stroke fill;` : '';
      let shadowStyle = currentConfig.text_shadow ? `text-shadow: 0 1px ${currentConfig.text_shadow_blur}px ${currentConfig.text_shadow_color};` : '';

      // Typography
      const fontFam = `'${currentConfig.font_family || 'Kanit'}', sans-serif`;
      const fontSz = `${currentConfig.font_size || 15}px`;
      const fontWt = currentConfig.font_weight || '600';
      const fontClr = currentConfig.font_color || '#ffffff';

      // Assemble content wrapper
      const content = document.createElement('div');
      content.className = 'cwc-msg-content';
      content.style.fontFamily = fontFam;
      content.style.fontSize = fontSz;
      content.style.fontWeight = fontWt;
      content.style.color = fontClr;
      content.style.cssText += `${strokeStyle} ${shadowStyle}`;

      if (currentConfig.layout === 'stacked') {
        content.innerHTML = `
          <div class="cwc-msg-header" style="display:flex; align-items:center; gap:6px; margin-bottom:2px;">
            ${avatarHtml}
            ${logoHtml}
            <span class="cwc-msg-author author" style="color: ${authorColor}; font-weight:700;">${msg.user}</span>
            ${timeHtml}
          </div>
          <div class="cwc-msg-text text" style="color:${fontClr};">${msg.text}</div>
        `;
      } else if (currentConfig.layout === 'message_only') {
        content.innerHTML = `
          <div class="cwc-msg-text text" style="color:${fontClr};">${msg.text}</div>
        `;
      } else {
        // inline layout
        content.innerHTML = `
          <div style="display:inline-flex; align-items:center; gap:6px; flex-wrap:wrap;">
            ${avatarHtml}
            ${logoHtml}
            <span class="cwc-msg-author author" style="color: ${authorColor}; font-weight:700;">${msg.user}:</span>
            <span class="cwc-msg-text text" style="color:${fontClr};">${msg.text}</span>
            ${timeHtml}
          </div>
        `;
      }

      item.appendChild(content);
      feed.appendChild(item);
    });

    stage.appendChild(feed);
  }

  // 2. Render Danmaku Mode with Continuous In-Flight Streaming & Zone Clamping
  function updateOrRenderDanmakuPreview(stage) {
    let container = stage.querySelector('.cwc-danmaku-container');
    const isNew = !container;

    if (isNew) {
      stage.innerHTML = '';
      container = document.createElement('div');
      container.className = 'cwc-danmaku-container';
      stage.appendChild(container);

      // Zone indicator visual box
      const zoneBox = document.createElement('div');
      zoneBox.className = 'cwc-danmaku-zone-box';
      zoneBox.id = 'cwcDanmakuZoneBox';
      container.appendChild(zoneBox);

      // Guides container
      const guidesWrap = document.createElement('div');
      guidesWrap.id = 'cwcDanmakuGuides';
      container.appendChild(guidesWrap);

      // Bullets container
      const bulletsWrap = document.createElement('div');
      bulletsWrap.id = 'cwcDanmakuBullets';
      container.appendChild(bulletsWrap);
    }

    const zoneBox = container.querySelector('#cwcDanmakuZoneBox');
    const guidesWrap = container.querySelector('#cwcDanmakuGuides');
    const bulletsWrap = container.querySelector('#cwcDanmakuBullets');

    // Calculate zone bounds based on currentConfig.slider_zone and stage height
    const H = stage.clientHeight || 360;
    const zone = currentConfig.slider_zone || 'middle';
    let bandTop = 0, bandHeight = H;

    if (zone === 'top') {
      bandTop = 10;
      bandHeight = Math.floor(H * 0.30) - 10;
    } else if (zone === 'top50') {
      bandTop = 10;
      bandHeight = Math.floor(H * 0.50) - 10;
    } else if (zone === 'middle') {
      bandTop = Math.floor(H * 0.30);
      bandHeight = Math.floor(H * 0.40);
    } else if (zone === 'bottom50') {
      bandTop = Math.floor(H * 0.50);
      bandHeight = Math.floor(H * 0.50) - 10;
    } else if (zone === 'bottom') {
      bandTop = Math.floor(H * 0.70);
      bandHeight = Math.floor(H * 0.30) - 10;
    } else { // full 100%
      bandTop = 10;
      bandHeight = H - 20;
    }

    if (bandHeight < 40) bandHeight = 40;

    // Update zone visual boundary box
    if (zoneBox) {
      zoneBox.style.top = `${bandTop}px`;
      zoneBox.style.height = `${bandHeight}px`;
      zoneBox.style.background = 'rgba(88, 101, 242, 0.04)';
      zoneBox.style.borderTop = '1px dashed rgba(88, 101, 242, 0.3)';
      zoneBox.style.borderBottom = '1px dashed rgba(88, 101, 242, 0.3)';
    }

    // Lane height & count
    const laneH = Math.max(25, Number(currentConfig.slider_lane_height) || 40);
    const numLanes = Math.max(1, Math.floor(bandHeight / laneH));

    // Render lane guides
    if (guidesWrap) {
      guidesWrap.innerHTML = '';
      for (let i = 0; i < numLanes; i++) {
        const guide = document.createElement('div');
        guide.className = 'cwc-danmaku-lane-guide';
        guide.style.top = `${bandTop + i * laneH}px`;
        guide.style.height = `${laneH}px`;
        guidesWrap.appendChild(guide);
      }
    }

    // Update CSS variables on container: in-flight bullets immediately update font size, speed, color, stroke without restarting animation!
    const dur = currentConfig.slider_duration || 6;
    container.style.setProperty('--cwc-danmaku-dur', `${dur}s`);
    container.style.setProperty('--cwc-danmaku-font-size', `${currentConfig.slider_font_size || 24}px`);
    container.style.setProperty('--cwc-danmaku-color', currentConfig.slider_text_color || '#ffffff');
    container.style.setProperty('--cwc-danmaku-font-family', `'${currentConfig.slider_font_family || 'Kanit'}', sans-serif`);
    container.style.setProperty('--cwc-danmaku-font-weight', currentConfig.slider_font_weight || '700');
    container.style.setProperty(
      '--cwc-danmaku-stroke',
      currentConfig.slider_text_stroke
        ? `${currentConfig.slider_text_stroke_width || 2}px ${currentConfig.slider_text_stroke_color || '#000000'}`
        : '0 transparent'
    );
    container.style.setProperty(
      '--cwc-danmaku-shadow',
      currentConfig.slider_text_shadow
        ? `0 1px ${currentConfig.slider_text_shadow_blur || 3}px ${currentConfig.slider_text_shadow_color || '#000000'}`
        : 'none'
    );

    // If new container, spawn mock bullets with staggered negative delays so bullets are ALREADY FLOWING immediately!
    if (isNew && bulletsWrap) {
      bulletsWrap.innerHTML = '';
      const sampleBullets = [
        { text: '✨ ตัวอย่างข้อความดันมากุสตรีมสด!', lane: 0, delay: -4.5, platform: 'youtube' },
        { text: 'สตรีมภาพสวยมาก 1080p60fps คมชัดสุดๆ 🔥', lane: 1, delay: -2.8, platform: 'twitch' },
        { text: 'ยินดีต้อนรับทุกคนเข้าสู่ไลฟ์สตรีมครับ! 👋', lane: 2, delay: -1.2, platform: 'kick' },
        { text: 'กดติดตามและกดแชร์เป็นกำลังใจให้ด้วยน้า 💖', lane: 0, delay: -0.2, platform: 'tiktok' },
        { text: 'เล่นเกมเก่งจัด จังหวะนี้สุดยอดเลย 🎮', lane: 1, delay: 1.5, platform: 'soop' },
        { text: 'เสียงไมค์ชัด ดนตรีคลอเบาๆ กำลังดีมากครับ ✨', lane: 2, delay: 3.0, platform: 'youtube' }
      ];

      sampleBullets.forEach((b, idx) => {
        const el = document.createElement('div');
        el.className = 'cwc-danmaku-bullet animating';
        el.dataset.lane = b.lane;
        el.dataset.bulletIdx = idx;

        // Position in lane
        const laneIdx = b.lane % numLanes;
        el.style.top = `${bandTop + laneIdx * laneH + 4}px`;

        // Animation timing with negative delay for instant mid-screen appearance
        el.style.animationDuration = `var(--cwc-danmaku-dur, 6s)`;
        el.style.animationDelay = `${b.delay}s`;

        // Logo
        let logoHtml = '';
        if (currentConfig.slider_show_logo) {
          logoHtml = `<img class="cwc-msg-logo" src="./assets/${b.platform}.png" alt="${b.platform}" style="height:0.9em; width:auto; vertical-align:-0.1em; margin-right:4px;">`;
        }

        el.innerHTML = `${logoHtml}<span>${b.text}</span>`;
        bulletsWrap.appendChild(el);
      });
    } else if (bulletsWrap) {
      // Reposition existing bullets to new lane vertical positions if zone or lane height changed
      const bullets = bulletsWrap.querySelectorAll('.cwc-danmaku-bullet');
      bullets.forEach((el, idx) => {
        const assignedLane = parseInt(el.dataset.lane || 0, 10);
        const laneIdx = assignedLane % numLanes;
        el.style.top = `${bandTop + laneIdx * laneH + 4}px`;

        // Update logo visibility
        const existingLogo = el.querySelector('.cwc-msg-logo');
        if (currentConfig.slider_show_logo && !existingLogo) {
          const plat = ['youtube', 'twitch', 'kick', 'tiktok', 'soop'][idx % 5];
          const img = document.createElement('img');
          img.className = 'cwc-msg-logo';
          img.src = `./assets/${plat}.png`;
          img.style.cssText = 'height:0.9em; width:auto; vertical-align:-0.1em; margin-right:4px;';
          el.prepend(img);
        } else if (!currentConfig.slider_show_logo && existingLogo) {
          existingLogo.remove();
        }
      });
    }
  }

  // 3. Render Balloon Preview with Clean Downward Tail
  function renderBalloonPreview(stage) {
    stage.innerHTML = '';
    const container = document.createElement('div');
    container.className = 'cwc-balloon-container';

    const balloonSamples = [
      { text: 'สวัสดีทุกคนในไลฟ์สตรีมครับ! ยินดีต้อนรับจ้า ✨', top: 30, left: 30, bg: '#ffffff', color: currentConfig.balloon_text_color || '#1a1a2e' },
      { text: 'วันนี้เล่นเกมอะไรกันดีครับ มีโหวตไหมเอ่ย! 🎮', top: 120, left: 140, bg: '#fef08a', color: '#713f12' },
      { text: 'ขอบคุณสำหรับการโดเนทและกดติดตามนะครับผม 💖', top: 210, left: 60, bg: '#bbf7d0', color: '#14532d' }
    ];

    balloonSamples.forEach(b => {
      const bubble = document.createElement('div');
      bubble.className = 'cwc-balloon-bubble';
      bubble.style.top = `${b.top}px`;
      bubble.style.left = `${b.left}px`;
      bubble.style.backgroundColor = b.bg;
      bubble.style.setProperty('--balloon-bg', b.bg);
      bubble.style.opacity = currentConfig.balloon_bg_opacity ?? 0.95;
      bubble.style.color = currentConfig.balloon_text_color || b.color;
      bubble.style.fontSize = `${currentConfig.balloon_font_size || 18}px`;
      bubble.style.fontFamily = `'${currentConfig.balloon_font_family || 'Kanit'}', sans-serif`;
      bubble.style.fontWeight = currentConfig.balloon_font_weight || '600';
      bubble.textContent = b.text;
      container.appendChild(bubble);
    });

    stage.appendChild(container);
  }

  // 4. Render Character Talk Preview
  function renderCharacterPreview(stage) {
    stage.innerHTML = '';
    const container = document.createElement('div');
    container.className = 'cwc-character-container';

    const chars = [
      { name: 'สตรีมเมอร์ 1', text: 'ยินดีต้อนรับทุกคนครับ!', avatar: '1' },
      { name: 'สตรีมเมอร์ 2', text: 'วันนี้เกมมันส์แน่นอน ลุยกันเลย!', avatar: '2' },
      { name: 'แขกรับเชิญ', text: 'พร้อมลุยไปด้วยกันแล้วจ้า ⭐', avatar: '3' }
    ];

    chars.forEach((c, idx) => {
      const item = document.createElement('div');
      item.className = 'cwc-character-item';

      const bubble = document.createElement('div');
      bubble.className = 'cwc-character-bubble';
      bubble.textContent = c.text;
      bubble.style.maxWidth = `${Math.min(currentConfig.character_bubble_width || 380, 240)}px`;

      const avatar = document.createElement('img');
      avatar.className = 'cwc-character-avatar';
      avatar.src = `https://api.dicebear.com/7.x/bottts/svg?seed=Char_${idx}`;
      avatar.style.width = `${currentConfig.character_size || 110}px`;
      avatar.style.height = `${currentConfig.character_size || 110}px`;

      let nameEl = '';
      if (currentConfig.character_show_name) {
        nameEl = `<div class="cwc-character-name">${c.name}</div>`;
      }

      item.appendChild(bubble);
      item.appendChild(avatar);
      if (nameEl) {
        const wrap = document.createElement('div');
        wrap.innerHTML = nameEl;
        item.appendChild(wrap.firstElementChild);
      }

      container.appendChild(item);
    });

    stage.appendChild(container);
  }

  // Apply custom CSS
  function applyCustomCssToPreview() {
    let styleTag = document.getElementById('cwcCustomCssStyle');
    if (!styleTag) {
      styleTag = document.createElement('style');
      styleTag.id = 'cwcCustomCssStyle';
      document.head.appendChild(styleTag);
    }
    if (currentConfig.custom_css_enabled && currentConfig.custom_css) {
      styleTag.textContent = currentConfig.custom_css;
    } else {
      styleTag.textContent = '';
    }
  }

  // Add random mock message
  function addMockMessage() {
    const platforms = ['youtube', 'twitch', 'kick', 'tiktok', 'soop'];
    const users = ['PlayerOne', 'Kittisak_Pro', 'NongMali', 'SpeedRunner_TH', 'NightOwl', 'GamerGirl'];
    const texts = [
      'ช็อตเมื่อกี้นี้ไวมาก!',
      'เพลงนี้เพราะจังเลยครับ',
      'สู้ๆ นะครับ ใกล้จบด่านแล้ว!',
      'ขออนุญาตแชร์ไลฟ์ต่อนะครับ',
      'วันนี้สตรีมถึงกี่โมงครับผม'
    ];

    const rnd = arr => arr[Math.floor(Math.random() * arr.length)];
    const newMsg = {
      user: rnd(users),
      text: rnd(texts),
      platform: rnd(platforms),
      color: '#38bdf8'
    };

    mockList.unshift(newMsg);
    if (mockList.length > 50) mockList.pop();

    applyLivePreview();
    if (window.showToast) window.showToast('เพิ่มข้อความทดสอบแล้ว');
  }

  // Clear preview stage
  function clearPreviewStage() {
    mockList = [];
    applyLivePreview();
    if (window.showToast) window.showToast('ล้างข้อความในหน้าทดสอบเรียบร้อย');
  }

  // Reset to defaults
  function resetToDefaults() {
    currentConfig = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
    syncControlsFromConfig();
    applyThemeCssForCurrentConfig();
    applyLivePreview();
    if (window.showToast) window.showToast('คืนค่ามาตรฐานเรียบร้อยแล้ว');
  }

  // Save configuration
  function saveConfiguration() {
    try {
      localStorage.setItem('bp3_chat_widget_config', JSON.stringify(currentConfig));
      if (window.showToast) window.showToast('บันทึกการตั้งค่า Chat Widget เรียบร้อยแล้ว');
    } catch (e) {
      console.error('Failed to save chat widget config:', e);
      if (window.showToast) window.showToast('เกิดข้อผิดพลาดในการบันทึกการตั้งค่า');
    }
  }

  // Copy OBS URL
  function copyObsUrl() {
    const host = window.location.origin || 'http://localhost:8000';
    const mode = currentConfig.mode;
    const theme = currentConfig.theme;
    const url = `${host}/overlay.html?mode=${encodeURIComponent(mode)}&theme=${encodeURIComponent(theme)}`;

    navigator.clipboard.writeText(url).then(() => {
      if (window.showToast) window.showToast(`คัดลอกลิงก์ OBS สำเร็จ: ${url}`);
    }).catch(err => {
      console.error('Copy failed:', err);
      prompt('คัดลอกลิงก์ OBS ของคุณ:', url);
    });
  }

  // Auto-init on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
