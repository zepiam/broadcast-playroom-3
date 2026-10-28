"""Read-only conversion of legacy Composer exports/settings to the v3 layout schema."""
import copy


def normalize_layout(source):
    if isinstance(source, list):
        source = {'pages': source} if source and isinstance(source[0], dict) and 'widgets' in source[0] else {'widgets': source}
    if not isinstance(source, dict):
        raise ValueError('Layout must be an object or list')
    source = copy.deepcopy(source)
    if source.get('type') == 'full_settings' and isinstance(source.get('settings'),dict):
        source = source['settings']
    pages = source.get('pages', source.get('composer_pages'))
    if not pages:
        widgets = source.get('widgets', source.get('composer_widgets'))
        if not isinstance(widgets, list):
            raise ValueError('No Composer widgets/pages in this file')
        pages = [{'id': 'p1', 'name': 'หน้า 1', 'widgets': widgets}]
    if not isinstance(pages, list) or not pages:
        raise ValueError('Layout must contain at least one page')
    size = source.get('canvas_size', source.get('composer_canvas_size', '1080p'))
    width = int(source.get('canvasWidth', source.get('canvas_w', 1280 if size == '720p' else 1920)))
    height = int(source.get('canvasHeight', source.get('canvas_h', 720 if size == '720p' else 1080)))
    if not 1 <= width <= 8192 or not 1 <= height <= 8192:
        raise ValueError('Invalid canvas size')
    active_source = str(source.get('activePageId', source.get('composer_active_page', source.get('active', ''))))
    if source.get('composer_pages') and isinstance(source.get('composer_widgets'), list):
        for page in pages:
            if str(page.get('id')) == active_source:
                page['widgets'] = source['composer_widgets']
    result = []
    ids = set()
    for i, page in enumerate(pages):
        if not isinstance(page, dict) or not isinstance(page.get('widgets'), list):
            raise ValueError('Invalid page')
        page['id'] = str(page.get('id') or f'p{i+1}')
        if page['id'] in ids:
            raise ValueError('Duplicate page ID')
        ids.add(page['id'])
        page.setdefault('name', f'หน้า {i+1}')
        for j, widget in enumerate(page['widgets']):
            if not isinstance(widget, dict) or not widget.get('type'):
                raise ValueError('Invalid widget')
            if widget.get('type')=='character':
                widget.update(type='replie',title='Replie',x=0,y=0,width=width,height=height,isFullScreen=True,noDrag=True,noResize=True)
            widget['id'] = str(widget.get('id') or f'w-{i+1}-{j+1}')
            if widget.get('type')=='chat' and 'appearance_mode' in widget:
                appearance=widget['appearance_mode']
                widget.setdefault('chatMode',{'slider':'danmaku','theme2':'theme'}.get(appearance,appearance))
                widget.setdefault('chatTheme',widget.get('theme','default'))
            for key, value in list(widget.items()):
                if '_' in key:
                    parts = key.split('_')
                    widget.setdefault(parts[0] + ''.join(part[:1].upper()+part[1:] for part in parts[1:]), value)
            widget['width'] = widget.get('width', widget.get('w', 300))
            widget['height'] = widget.get('height', widget.get('h', 180))
            widget['opacity'] = widget.get('opacity', widget.get('alpha', 1))
            widget['hidden'] = widget.get('hidden', widget.get('enabled') is False)
            for old, new in [('image_url','imageUrl'),('video_url','videoUrl'),('chat_theme','chatTheme'),('chat_mode','chatMode'),('clock_theme','clockTheme'),('clock_style','clockStyle'),('clock_format','clockFormat'),('text_mode','textMode'),('font_size','fontSize'),('font_color','fontColor')]:
                if new not in widget and old in widget:
                    widget[new] = widget[old]
        result.append(page)
    active = str(source.get('activePageId', source.get('composer_active_page', source.get('active', result[0]['id']))))
    tools = copy.deepcopy(source.get('legacyTools') or {})
    for key in ('giveaway','replie_commands','replie_default_duration_sec','replie_cooldown_sec','ask_presets','voice_id','rvc_f0method','rvc_pitch','blocked_users','tts_bot_blacklist','overlay_hide_bots','twitch_bot_name','banned_words'):
        if key in source: tools[key] = copy.deepcopy(source[key])
    public_keys = ('twitch_channel','youtube_url','mylive_url','tiktok_username','kick_channel','soop_bid')
    public_keys += tuple(f'{prefix}_{platform}' for prefix in ('read_tts','tts_volume') for platform in ('twitch','youtube','mylive','tiktok','kick','soop'))
    for key in ('more_overlays',)+tuple(key for key in source if key.startswith(('game_overlay_','more_overlay_','viewer_overlay_')))+public_keys:
        if key in source: tools[key] = copy.deepcopy(source[key])
    legacy_chat=copy.deepcopy(source.get('legacyChat') or {key:value for key,value in source.items() if key.startswith('overlay_') or key.startswith('character_')})
    return {'legacyChat':legacy_chat,'legacyTools': tools, 'legacyPlayroomTriggers': copy.deepcopy(source.get('legacyPlayroomTriggers', source.get('playroom_triggers', []))), 'pages': result, 'activePageId': active if active in ids else result[0]['id'],
            'canvasWidth': width, 'canvasHeight': height, 'updatedAt': source.get('updatedAt', 0)}
