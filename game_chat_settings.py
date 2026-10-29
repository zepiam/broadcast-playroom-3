"""Validated settings for the legacy-style desktop game chat overlay."""
import copy, math, re
from game_overlay_themes import get_theme_list
from legacy_chat_config import build_game_chat_config

MODES = ['default', 'theme', 'special', 'character']
FONTS = ['Kanit','Prompt','Sarabun','Mitr','Bai Jamjuree','Noto Sans Thai','IBM Plex Sans Thai','Plus Jakarta Sans']
ANIM_IN = ['minimal','fade','slide_left','slide_up','zoom','bounce','pop','flip','glow','typewriter','slide_pop','card_flip','liquid','neon_pulse','glassy','elastic']
ANIM_OUT = ['fade_out','slide_right','slide_down','shrink','blur_out','dissolve']
LAYOUTS = ['stacked','inline','message_only','stacked_no_logo','inline_no_logo']

# type, default, bounds/choices; keys match build_game_chat_config and the old app.
FIELDS = {
 'theme':('theme','default'), 'show_logo':('bool',True), 'show_timestamp':('bool',False),
 'layout':('enum','inline',LAYOUTS), 'font_size':('number',14,10,64), 'emote_size':('number',24,12,64),
 'max_rows':('number',15,1,100), 'msg_spacing':('number',4,0,30),
 'font_family':('enum','Kanit',FONTS), 'font_weight':('enum','500',['300','400','500','600','700']),
 'text_color':('color','#ffffff'), 'text_stroke':('bool',False), 'text_stroke_color':('color','#000000'),
 'text_stroke_width':('number',2,0,6), 'text_shadow':('bool',True), 'text_shadow_color':('color','#000000'),
 'text_shadow_blur':('number',3,0,10), 'anim_in':('enum','fade',ANIM_IN), 'anim_out':('enum','fade_out',ANIM_OUT),
 'auto_hide':('bool',True), 'hide_after':('number',10,3,60), 'box_enabled':('bool',False),
 'box_bg_color':('color','#0a0e1a'), 'box_bg_opacity':('number',0.55,0,1), 'box_radius':('number',8,0,30),
 'box_border':('bool',False), 'box_border_color':('color','#7c3aed'), 'box_border_width':('number',1,0,6),
 'box_shadow':('bool',False), 'box_glow':('bool',False), 'box_glow_color':('color','#7c3aed'),
 'balloon_hide_after':('number',5,2,30), 'balloon_bg_opacity':('number',0.95,0.1,1),
 'character_hide_after':('number',6,2,60), 'character_size':('number',120,40,400),
 'character_max_on_screen':('number',8,1,30), 'character_bubble_width':('number',500,200,800),
 'character_name_size':('number',11,8,24), 'character_name_stroke':('bool',True),
 'character_name_stroke_color':('color','#000000'), 'character_name_stroke_width':('number',1,1,4),
 'character_name_shadow':('bool',True), 'character_name_shadow_color':('color','#000000'),
 'character_name_shadow_blur':('number',2,0,8), 'character_random_pos':('bool',True),
 'max_msg_length':('number',0,0,500), 'demo_interval':('number',5,1,60), 'animated_emotes':('bool',False), 'custom_css':('text',''), 'default_image_url':('image',''),
 'hotkey':('hotkey','ctrl+shift+g'), 'hotkey_edit':('hotkey','ctrl+shift+h'),
}
GLOBAL = {key for key in FIELDS if key.startswith('character_')} | {'max_msg_length','demo_interval','animated_emotes','custom_css','default_image_url','hotkey','hotkey_edit'}

def snapshot(settings):
    settings = settings or {}
    mode = settings.get('game_overlay_appearance_mode', 'default')
    if mode not in MODES: mode = 'default'
    mc = (settings.get('game_overlay_mode_configs') or {}).get(mode, {})
    if not isinstance(mc, dict): mc = {}
    values = {}
    for key, spec in FIELDS.items():
        flat = key if key.startswith('character_') else 'game_overlay_' + key
        values[key] = (settings.get(flat, spec[1]) if key in GLOBAL else mc.get(key, settings.get(flat, spec[1])))
    return {'mode':mode, 'values':values, 'themes':get_theme_list(), 'config':build_game_chat_config(settings)}

def update(settings, mode, key, value):
    if mode not in MODES: raise ValueError('Invalid appearance mode')
    if key == 'mode':
        result = copy.deepcopy(settings)
        previous = snapshot(settings)
        configs = result.get('game_overlay_mode_configs')
        if not isinstance(configs,dict): configs = {}
        current = configs.get(previous['mode'])
        if not isinstance(current,dict): current = {}
        for name in FIELDS:
            if name not in GLOBAL: current.setdefault(name, previous['values'][name])
        configs[previous['mode']] = current
        result['game_overlay_mode_configs'] = configs
        result['game_overlay_appearance_mode'] = mode
        return result
    if key not in FIELDS: raise ValueError('Unknown game chat setting')
    spec = FIELDS[key]; kind = spec[0]
    if kind == 'bool':
        if type(value) is not bool: raise ValueError('Invalid checkbox value')
    elif kind == 'number':
        if type(value) not in (int,float) or not math.isfinite(value) or not spec[2] <= value <= spec[3]: raise ValueError('Invalid number')
    elif kind == 'color':
        if not isinstance(value,str) or not re.fullmatch(r'#[0-9a-fA-F]{6}',value): raise ValueError('Invalid color')
    elif kind == 'theme':
        if value not in dict(get_theme_list()): raise ValueError('Invalid theme')
    elif kind == 'enum':
        if value not in spec[2]: raise ValueError('Invalid choice')
    elif kind == 'text':
        if not isinstance(value,str) or len(value)>20000: raise ValueError('Invalid text')
    elif kind == 'image':
        if not isinstance(value,str) or (value and not re.fullmatch(r'/playroom-media/[0-9a-f]{64}\.(?:png|jpg|jpeg|webp|gif|bmp)',value)):
            raise ValueError('Invalid image')
    elif kind == 'hotkey':
        if not isinstance(value,str) or not re.fullmatch(r'(?:(?:ctrl|shift|alt|win)\+){1,4}(?:[a-z0-9]|f(?:[1-9]|1[0-9]|2[0-4]))',value):
            raise ValueError('คีย์ลัดต้องมี Ctrl, Shift, Alt หรือ Win และตัวอักษร ตัวเลข หรือ F1–F24')
        if len(set(value.split('+')[:-1])) != len(value.split('+')[:-1]): raise ValueError('คีย์ลัดมีปุ่มซ้ำ')
    result = copy.deepcopy(settings)
    if key in GLOBAL:
        flat = key if key.startswith('character_') else 'game_overlay_' + key
        result[flat] = value
    else:
        configs = result.get('game_overlay_mode_configs')
        if not isinstance(configs,dict): configs = {}
        mc = configs.get(mode)
        if not isinstance(mc,dict): mc = {}
        mc[key] = value; configs[mode] = mc; result['game_overlay_mode_configs'] = configs
        result['game_overlay_' + key] = value
    return result
