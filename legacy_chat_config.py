from types import SimpleNamespace
from game_overlay_themes import get_theme_css

def build_chat_config(w: dict, settings=None) -> dict:

        """build config สำหรับ overlay.html ที่อยู่ใน chat widget iframe



        แปลง widget settings → config format ที่ overlay.html เข้าใจ (overlay_* fields)

        + inject theme_css (จาก game_overlay_themes)

        """

        w = dict(w)
        aliases={'chatMode':'appearance_mode','chatTheme':'theme','fontSize':'font_size','fontFamily':'font_family','fontWeight':'font_weight','fontColor':'font_color','textStroke':'text_stroke','textStrokeWidth':'text_stroke_width','strokeColor':'text_stroke_color','textShadow':'text_shadow','textShadowBlur':'text_shadow_blur','textShadowColor':'text_shadow_color','align':'chat_align','showAvatar':'show_avatar','showBadges':'show_badges','showLogo':'show_logo','showTimestamp':'show_timestamp','maxMessages':'max_messages','autoHide':'auto_hide','hideAfter':'hide_after','hideTimeout':'hide_after','boxEnabled':'box_enabled','bgColor':'bg_color','bgOpacity':'bg_opacity','boxRadius':'box_radius','boxPadding':'box_padding','boxWidth':'box_width','boxBorder':'box_border','boxBorderWidth':'box_border_width','boxBorderColor':'box_border_color','boxShadow':'box_shadow','boxGlow':'box_glow','boxGlowColor':'box_glow_color','msgSpacing':'msg_spacing','animIn':'animation','animOut':'exit_animation'}
        for camel,raw in aliases.items():
            if camel in w:w[raw]=w[camel]
        if w.get('appearance_mode')=='danmaku':w['appearance_mode']='slider'
        w['layout']={'compact':'inline','bubble':'stacked'}.get(w.get('layout'),w.get('layout','inline'))
        w['direction']={'bottom-up':'bottom','top-down':'top'}.get(w.get('direction'),w.get('direction','bottom'))
        if w.get('box_width')=='full':w['box_width']='wide'
        animations={'slide':'slide-up','auto':'fade_out','fade':'fade'}
        w['animation']=animations.get(w.get('animation'),w.get('animation','fade'))
        w['exit_animation']=animations.get(w.get('exit_animation'),w.get('exit_animation','fade_out'))
        if 'appearance_mode' not in w and w.get('theme','default') != 'default': w['appearance_mode'] = 'theme'
        mode=w.get('appearance_mode','default')
        if mode=='slider':
            for camel,raw in {'fontSize':'slider_font_size','fontFamily':'slider_font_family','fontWeight':'slider_font_weight','fontColor':'slider_text_color','textStroke':'slider_text_stroke','strokeColor':'slider_text_stroke_color','textStrokeWidth':'slider_text_stroke_width','textShadow':'slider_text_shadow','textShadowColor':'slider_text_shadow_color','textShadowBlur':'slider_text_shadow_blur','speed':'slider_duration','showLogo':'slider_show_logo'}.items():
                if camel in w:w[raw]=w[camel]
        if mode=='balloon':
            for camel,raw in {'fontSize':'balloon_font_size','fontFamily':'balloon_font_family','fontWeight':'balloon_font_weight','balloonTextColor':'balloon_text_color','balloonOpacity':'balloon_bg_opacity'}.items():
                if camel in w:w[raw]=w[camel]
        if mode=='character':
            for camel,raw in {'charFontSize':'character_font_size','fontFamily':'character_font_family','fontWeight':'character_font_weight','charTextColor':'character_font_color'}.items():
                if camel in w:w[raw]=w[camel]


        s = SimpleNamespace(**(settings or {}))

        appearance = w.get("appearance_mode", "default")

        theme = w.get("theme", "default")

        custom_css = w.get("custom_css", "")

        # compute theme_css (raw CSS string)

        # ★ theme ใช้ได้ในทุก mode (ไม่ใช่แค่ mode=theme)

        # ★ theme2 = "Theme Part 2" (ชุดธีมใหม่ 2026-09, appearance_mode แยกจาก theme แต่ใช้ pipeline เดียวกัน)

        try:

            theme_css = ""

            if appearance in ("theme", "theme2") and theme and theme != "default":

                theme_css = get_theme_css(theme, "")

            elif appearance == "default" and w.get("custom_css_enabled") and custom_css:

                # ★ Custom CSS ย้ายมาโหมด Default (เปิดผ่าน checkbox)

                theme_css = custom_css

        except Exception:

            theme_css = ""



        # mode flags ตาม appearance

        balloon_mode = (appearance == "balloon")

        character_mode = (appearance == "character")

        slider_mode = (appearance == "slider")



        config = {

            # mode

            "appearance_mode": appearance,

            "theme": theme if appearance in ("theme", "theme2") else "default",

            "theme_css": theme_css,

            "custom_css": custom_css if theme == "custom" else "",

            "balloon_mode": balloon_mode,

            "character_mode": character_mode,

            "slider_mode": slider_mode,

            # chat layout/animation (จาก widget)

            "layout": w.get("layout", "inline"),

            "direction": w.get("direction", "bottom"),

            "animation": w.get("animation", "fade"),

            "exit_animation": w.get("exit_animation", "fade_out"),

            "chat_align": w.get("chat_align", "left"),

            "show_logo": w.get("show_logo", True),

            "show_timestamp": w.get("show_timestamp", False),

            "max_messages": w.get("max_messages", 30),

            # auto-hide

            "auto_hide": w.get("auto_hide", False),

            "hide_after": w.get("hide_after", 8),

            # font (อ่านจาก widget ก่อน ไม่ใช้ shared overlay settings)

            "font_size": w.get("font_size", 18),

            "font_family": w.get("font_family", getattr(s, "overlay_font_family", "Kanit")),

            "font_weight": w.get("font_weight", "600"),

            "text_color": w.get("font_color", "#ffffff"),

            # stroke/shadow (จาก widget — แยก stroke/shadow ชัดเจน)

            "text_stroke": w.get("text_stroke", True),

            "text_stroke_color": w.get("text_stroke_color", "#000000"),

            "text_stroke_width": w.get("text_stroke_width", 2),

            "text_shadow": w.get("text_shadow", True),

            "text_shadow_color": w.get("text_shadow_color", "#000000"),

            "text_shadow_blur": w.get("text_shadow_blur", 3),

            # ★ สีชื่อผู้พูดตามแพลตฟอร์ม (2026-09-25) — auto = สีจริงจากแพลตฟอร์ม (msg.color/platformColor เดิม)

            #   custom = เขียนทับด้วย author_color_map ต่อแพลตฟอร์ม (ดู overlay.html resolveAuthorColor())

            "author_color_mode": w.get("author_color_mode", "auto"),

            "author_color_map": w.get("author_color_map") or {},

            # box (จาก widget — ครบทุก field)

            "box_enabled": w.get("box_enabled", True),

            "box_bg_color": w.get("bg_color", "#0a0e1a"),

            "box_bg_opacity": w.get("bg_opacity", 1.0),

            "box_radius": w.get("box_radius", 8),

            "box_padding": w.get("box_padding", 8),

            "chat_padding": w.get("chat_padding", 12),

            "box_border": w.get("box_border", False),

            "box_border_width": w.get("box_border_width", 1),

            "box_border_color": w.get("box_border_color", "#ffffff"),

            "box_shadow": w.get("box_shadow", True),

            "box_blur": 0,

            "box_glow": w.get("box_glow", False),

            "box_glow_color": w.get("box_glow_color", "#a855f7"),

            "box_width": w.get("box_width", "fit"),

            "msg_spacing": w.get("msg_spacing", 4),

            # balloon (per-widget — แยกจาก default/theme สนิท)

            "balloon_hide_after": w.get("balloon_hide_after", 5),

            "balloon_bg_opacity": w.get("balloon_bg_opacity", 0.95),

            "balloon_font_family": w.get("balloon_font_family", "Kanit"),

            "balloon_font_weight": w.get("balloon_font_weight", 600),

            "balloon_font_size": w.get("balloon_font_size", 18),

            "balloon_text_color": w.get("balloon_text_color", "#1a1a2e"),

            "balloon_emote_size": w.get("balloon_emote_size", 28),

            # ★ text slider (Niconico style — ข้อความเลื่อนขวา→ซ้าย แล้วหายไปเอง)

            "slider_font_size": w.get("slider_font_size", 24),

            "slider_font_family": w.get("slider_font_family", "Kanit"),

            "slider_font_weight": w.get("slider_font_weight", 700),

            "slider_text_color": w.get("slider_text_color", "#ffffff"),

            "slider_text_stroke": w.get("slider_text_stroke", False),

            "slider_text_stroke_color": w.get("slider_text_stroke_color", "#000000"),

            "slider_text_stroke_width": w.get("slider_text_stroke_width", 2),

            "slider_text_shadow": w.get("slider_text_shadow", True),

            "slider_text_shadow_color": w.get("slider_text_shadow_color", "#000000"),

            "slider_text_shadow_blur": w.get("slider_text_shadow_blur", 3),

            "slider_duration": w.get("slider_duration", 5.0),

            "slider_emote_size": w.get("slider_emote_size", 28),

            "slider_show_logo": w.get("slider_show_logo", True),

            "slider_lane_height": w.get("slider_lane_height", 40),

            "slider_zone": w.get("slider_zone", "middle"),

            # event colors (จาก settings ทั่วไป)

            "color_sub": getattr(s, "overlay_color_sub", "#f47fff"),

            "color_bits": getattr(s, "overlay_color_bits", "#ffaa00"),

            "color_donate": getattr(s, "overlay_color_donate", "#00ff7f"),

            "color_system": getattr(s, "overlay_color_system", "#aaaaaa"),

            # translator/channel points

            "show_original": getattr(s, "overlay_show_original", True),

            "show_redeem": getattr(s, "overlay_show_redeem", True),

            # emote/animate

            "emote_size": w.get("emote_size", getattr(s, "overlay_emote_size", 28)),

            "animated_emotes": getattr(s, "overlay_animated_emotes", True),

            # ★ per-mode configs (สำหรับ overlay.html per-mode CSS vars)

            "mode_configs": getattr(s, "overlay_mode_configs", {}),

        }

        # ★ character mode → เพิ่ม character settings

        if character_mode:

            config.update({

                "character_mode": True,

                "character_font_family": w.get("character_font_family", "Kanit"),

                "character_font_weight": w.get("character_font_weight", 600),

                "character_font_color": w.get("character_font_color", "#1a1a2e"),

                "character_stroke": w.get("character_stroke", False),

                "character_stroke_width": w.get("character_stroke_width", 2),

                "character_stroke_color": w.get("character_stroke_color", "#000000"),

                "character_shadow": w.get("character_shadow", False),

                "character_shadow_blur": w.get("character_shadow_blur", 3),

                "character_shadow_color": w.get("character_shadow_color", "#000000"),

                "character_emote_size": w.get("character_emote_size", 28),

                "character_name_font_family": w.get("character_name_font_family", "Kanit"),

                "character_name_font_weight": w.get("character_name_font_weight", 600),

                "character_name_color": w.get("character_name_color", "#ffffff"),

                "character_size": w.get("character_size", 120),

                "character_hide_after": w.get("character_hide_after", 6),

                "character_max_on_screen": w.get("character_max_on_screen", 8),

                "character_random_pos": w.get("character_random_pos", True),

                "character_name_size": w.get("character_name_size", 11),

                "character_name_stroke": w.get("character_name_stroke", True),

                "character_name_stroke_color": w.get("character_name_stroke_color", "#000000"),

                "character_name_stroke_width": w.get("character_name_stroke_width", 1),

                "character_name_shadow": w.get("character_name_shadow", True),

                "character_name_shadow_color": w.get("character_name_shadow_color", "#000000"),

                "character_name_shadow_blur": w.get("character_name_shadow_blur", 2),

                "character_show_name": w.get("character_show_name", True),

                "character_show_logo": w.get("character_show_logo", True),

                "character_bubble_width": w.get("character_bubble_width", 500),

            })

        if 'usernameColor' in w:
            config['author_color_mode']='custom';config['author_color_map']={name:w['usernameColor'] for name in ['youtube','twitch','tiktok','kick','soop','mylive','facebook']}
        config['show_avatar']=w.get('show_avatar',False)
        config['show_badges']=w.get('show_badges',True)
        config['custom_text_shadow']=w.get('customTextShadow',False)
        config['custom_box_style']=w.get('customBoxStyle',False)
        config['character_font_size']=w.get('character_font_size',18)
        for key in ('containerBgEnabled','containerBgColor','containerBgOpacity','containerRadius','containerBorder','containerBorderColor','containerBorderWidth','balloonBg','balloonRadius','charBubbleBg'):
            if key in w:config[key]=w[key]
        return config


def build_global_chat_config(settings=None) -> dict:
    """config สำหรับ overlay (client ใช้ render + apply CSS variables แบบสด)"""
    s = SimpleNamespace(**(settings or {}))
    # theme CSS (mirror game_overlay_themes.py — ใช้ source เดียวกัน)
    try:
        from game_overlay_themes import get_theme_css
        theme = getattr(s, "overlay_theme", "default")
        custom_css = getattr(s, "overlay_custom_css", "")
        theme_css = get_theme_css(theme, custom_css)
    except Exception:
        theme = getattr(s, "overlay_theme", "default")
        theme_css = ""
        custom_css = getattr(s, "overlay_custom_css", "")
    # ★ merge per-mode config — อ่านค่าของ mode ปัจจุบัน (override flat settings)
    active_mode = getattr(s, "overlay_appearance_mode", "default")
    mode_cfgs = getattr(s, "overlay_mode_configs", {})
    mc = mode_cfgs.get(active_mode, {}) if isinstance(mode_cfgs, dict) else {}
    # helper: อ่านจาก mode config ก่อน ไม่มี → fallback flat settings
    def mcv(key, fallback):
        return mc.get(key, getattr(s, f"overlay_{key}", fallback))

    return {
        # พื้นฐาน (ใช้ค่าของ mode ปัจจุบัน)
        "font_size": mcv("font_size", 18),
        "emote_size": mcv("emote_size", 28),
        "animation": getattr(s, "overlay_animation", "fade"),
        "exit_animation": getattr(s, "overlay_exit_animation", "fade_out"),
        "max_messages": getattr(s, "overlay_max_messages", 20),
        "direction": getattr(s, "overlay_direction", "bottom"),
        # เนื้อหา
        "show_logo": getattr(s, "overlay_show_logo", True),
        "show_timestamp": getattr(s, "overlay_show_timestamp", False),
        # auto-hide
        "auto_hide": getattr(s, "overlay_auto_hide", False),
        "hide_after": getattr(s, "overlay_hide_after", 10.0),
        # ฟอนต์ + text styling (ใช้ค่าของ mode ปัจจุบัน)
        "font_family": mcv("font_family", "Kanit"),
        "font_weight": mcv("font_weight", "500"),
        "text_color": mcv("text_color", "#ffffff"),
        "text_stroke": mcv("text_stroke", False),
        "text_stroke_color": mcv("text_stroke_color", "#000000"),
        "text_stroke_width": mcv("text_stroke_width", 2),
        "text_shadow": mcv("text_shadow", True),
        "text_shadow_color": mcv("text_shadow_color", "#000000"),
        "text_shadow_blur": mcv("text_shadow_blur", 3),
        # ★ ส่งค่าทั้ง 4 modes แยกกัน (สำหรับ CSS vars ของแต่ละ mode)
        "mode_configs": {
            "default": mode_cfgs.get("default", {}),
            "theme": mode_cfgs.get("theme", {}),
            "special": mode_cfgs.get("special", {}),
            "character": mode_cfgs.get("character", {}),
        },
        # layout: inline (บรรทัดเดียว) | stacked (สองบรรทัด)
        "layout": getattr(s, "overlay_layout", "inline"),
        # กล่องข้อความ
        "box_enabled": getattr(s, "overlay_box_enabled", False),
        "box_bg_color": getattr(s, "overlay_bg_color", "#0a0e1a"),
        "box_bg_opacity": getattr(s, "overlay_box_bg_opacity", 0.55),
        "box_radius": getattr(s, "overlay_box_radius", 8),
        "box_border": getattr(s, "overlay_box_border", False),
        "box_border_color": getattr(s, "overlay_box_border_color", "#7c3aed"),
        "box_border_width": getattr(s, "overlay_box_border_width", 1),
        "box_shadow": getattr(s, "overlay_box_shadow", False),
        "box_blur": float(getattr(s, "overlay_box_blur", 0) or 0),
        # balloon mode → ปิด glow animation เสมอ (กันบัค)
        "box_glow": False if getattr(s, "overlay_balloon_mode", False) else getattr(s, "overlay_box_glow", False),
        "box_glow_color": getattr(s, "overlay_box_glow_color", "#7c3aed"),
        "box_width": getattr(s, "overlay_box_width", "fit"),
        "msg_spacing": getattr(s, "overlay_msg_spacing", 4.0),
        "msg_only": getattr(s, "overlay_msg_only", False),
        "balloon_mode": getattr(s, "overlay_balloon_mode", False),
        "balloon_hide_after": getattr(s, "overlay_balloon_hide_after", 5.0),
        "balloon_bg_opacity": getattr(s, "overlay_balloon_bg_opacity", 0.95),
        # Character Talk
        "character_mode": getattr(s, "overlay_character_mode", False),
        "character_hide_after": getattr(s, "character_hide_after", 6.0),
        "character_size": getattr(s, "character_size", 120),
        "character_max_on_screen": getattr(s, "character_max_on_screen", 8),
        "character_name_size": getattr(s, "character_name_size", 11),
        "character_name_stroke": getattr(s, "character_name_stroke", True),
        "character_name_stroke_color": getattr(s, "character_name_stroke_color", "#000000"),
        "character_name_stroke_width": getattr(s, "character_name_stroke_width", 1),
        "character_name_shadow": getattr(s, "character_name_shadow", True),
        "character_name_shadow_color": getattr(s, "character_name_shadow_color", "#000000"),
        "character_name_shadow_blur": getattr(s, "character_name_shadow_blur", 2),
        "character_random_pos": getattr(s, "character_random_pos", True),
        "character_bubble_width": getattr(s, "character_bubble_width", 500),
        "character_jobs": [cj.get("name", "") for cj in getattr(s, "character_jobs", [])],
        # theme + custom CSS (3-mode restructure)
        "theme": theme,
        "theme_css": theme_css,
        "custom_css": custom_css,
        # event colors
        "color_sub": getattr(s, "overlay_color_sub", "#22c55e"),
        "color_bits": getattr(s, "overlay_color_bits", "#f59e0b"),
        "color_donate": getattr(s, "overlay_color_donate", "#22c55e"),
        "color_system": getattr(s, "overlay_color_system", "#9ca3af"),
        # Translator — แสดงต้นฉบับ [xxx] ในวงเล็บ
        "show_original": getattr(s, "overlay_show_original", True),
        # Channel Points redemption — แสดง reward redemption
        "show_redeem": getattr(s, "overlay_show_redeem", True),
    }


def build_game_chat_config(settings=None) -> dict:
    s = SimpleNamespace(**(settings or {}))
    # ★ อ่าน appearance mode + mode-specific config (เหมือน v1)
    #    mode_configs[mode] มีค่า styling เฉพาะของ mode นั้น → override flat settings
    appearance_mode = getattr(s, "game_overlay_appearance_mode", "default")
    mode_configs = getattr(s, "game_overlay_mode_configs", {}) or {}
    mc = dict(mode_configs.get(appearance_mode, {}))  # mode-specific overrides

    # helper: อ่านจาก mode config ก่อน → fallback flat settings
    def mc_get(key, flat_key, default):
        if key in mc:
            return mc[key]
        return getattr(s, flat_key, default)

    # theme + CSS — อ่านจาก mode config ของ theme mode (ถ้าเป็น theme mode)
    if appearance_mode == "theme":
        theme = mc.get("theme", getattr(s, "game_overlay_theme", "default"))
    else:
        theme = "default"  # default/special/character → ไม่มี theme CSS
    theme_css = get_theme_css(theme, getattr(s, "game_overlay_custom_css", "")) if theme != "default" else ""
    custom_css = getattr(s, "game_overlay_custom_css", "")

    # balloon/character mode flags (จาก appearance mode)
    balloon_mode = (appearance_mode == "special")
    character_mode = (appearance_mode == "character")

    return {
        "theme": theme,
        "theme_css": theme_css,
        "custom_css": custom_css,
        # ★ styling อ่านจาก mode config ก่อน → fallback flat
        "font_size": mc_get("font_size", "game_overlay_font_size", 14),
        "emote_size": mc_get("emote_size", "game_overlay_emote_size", 24),
        "animation": mc_get("anim_in", "game_overlay_anim_in", "fade"),
        "exit_animation": mc_get("anim_out", "game_overlay_anim_out", "fade_out"),
        "max_messages": mc_get("max_rows", "game_overlay_max_rows", 15),
        "direction": getattr(s, "game_overlay_direction", "bottom"),
        "show_logo": mc_get("show_logo", "game_overlay_show_logo", True),
        "show_timestamp": mc_get("show_timestamp", "game_overlay_show_timestamp", False),
        "auto_hide": mc_get("auto_hide", "game_overlay_auto_hide", True),
        "hide_after": mc_get("hide_after", "game_overlay_hide_after", 10.0),
        "font_family": mc_get("font_family", "game_overlay_font_family", "Kanit"),
        "font_weight": mc_get("font_weight", "game_overlay_font_weight", "500"),
        "text_color": mc_get("text_color", "game_overlay_text_color", "#ffffff"),
        "color_sub": getattr(s, "game_overlay_color_sub", "#22c55e"),
        "color_bits": getattr(s, "game_overlay_color_bits", "#f59e0b"),
        "color_donate": getattr(s, "game_overlay_color_donate", "#22c55e"),
        "color_system": getattr(s, "game_overlay_color_system", "#9ca3af"),
        "show_original": getattr(s, "game_overlay_show_original", True),
        "show_redeem": getattr(s, "game_overlay_show_redeem", True),
        "text_stroke": mc_get("text_stroke", "game_overlay_text_stroke", False),
        "text_stroke_color": mc_get("text_stroke_color", "game_overlay_text_stroke_color", "#000000"),
        "text_stroke_width": mc_get("text_stroke_width", "game_overlay_text_stroke_width", 2),
        "text_shadow": mc_get("text_shadow", "game_overlay_text_shadow", True),
        "text_shadow_color": mc_get("text_shadow_color", "game_overlay_text_shadow_color", "#000000"),
        "text_shadow_blur": mc_get("text_shadow_blur", "game_overlay_text_shadow_blur", 3),
        "layout": mc_get("layout", "game_overlay_layout", "inline"),
        # box settings — อ่านจาก mode config ก่อน
        "box_enabled": mc_get("box_enabled", "game_overlay_box_enabled", False),
        "box_bg_color": mc_get("box_bg_color", "game_overlay_box_bg_color", "#0a0e1a"),
        "box_bg_opacity": mc_get("box_bg_opacity", "game_overlay_box_bg_opacity", 0.55),
        "box_radius": mc_get("box_radius", "game_overlay_box_radius", 8),
        "box_border": mc_get("box_border", "game_overlay_box_border", False),
        "box_border_color": mc_get("box_border_color", "game_overlay_box_border_color", "#7c3aed"),
        "box_border_width": mc_get("box_border_width", "game_overlay_box_border_width", 1),
        "box_shadow": mc_get("box_shadow", "game_overlay_box_shadow", False),
        "box_blur": float(mc_get("box_blur", "game_overlay_box_blur", 0) or 0),
        "box_glow": (
            False if balloon_mode
            else mc_get("box_glow", "game_overlay_box_glow", False)
        ),
        "box_glow_color": mc_get("box_glow_color", "game_overlay_box_glow_color", "#7c3aed"),
        "box_width": getattr(s, "game_overlay_box_width", "fit"),
        "msg_spacing": mc_get("msg_spacing", "game_overlay_msg_spacing", 4.0),
        "msg_only": mc_get("layout", "game_overlay_layout", "inline") == "message_only",
        "balloon_mode": balloon_mode,
        "balloon_hide_after": mc_get("balloon_hide_after", "game_overlay_balloon_hide_after", 5.0),
        "balloon_bg_opacity": mc_get("balloon_bg_opacity", "game_overlay_balloon_bg_opacity", 0.95),
        # Character Talk
        "character_mode": character_mode,
        "character_hide_after": getattr(s, "character_hide_after", 6.0),
        "character_size": getattr(s, "character_size", 120),
        "character_max_on_screen": getattr(s, "character_max_on_screen", 8),
        "character_name_size": getattr(s, "character_name_size", 11),
        "character_name_stroke": getattr(s, "character_name_stroke", True),
        "character_name_stroke_color": getattr(s, "character_name_stroke_color", "#000000"),
        "character_name_stroke_width": getattr(s, "character_name_stroke_width", 1),
        "character_name_shadow": getattr(s, "character_name_shadow", True),
        "character_name_shadow_color": getattr(s, "character_name_shadow_color", "#000000"),
        "character_name_shadow_blur": getattr(s, "character_name_shadow_blur", 2),
        "character_random_pos": getattr(s, "character_random_pos", True),
        "character_bubble_width": getattr(s, "character_bubble_width", 500),
        "character_jobs": [cj.get("name", "") for cj in getattr(s, "character_jobs", [])],
        "scrollbar": getattr(s, "game_overlay_scrollbar", "none"),
        "max_msg_length": getattr(s, "game_overlay_max_msg_length", 0),
    }
