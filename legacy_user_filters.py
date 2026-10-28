"""Read only the legacy filter settings needed for migration."""
import json, os, sys
from pathlib import Path

KEYS=('blocked_users','tts_bot_blacklist','overlay_hide_bots','twitch_bot_name','banned_words','dns_enabled','dns_service','dns_custom','ask_post_result', *(f'auto_connect_{platform}' for platform in ('twitch','youtube','kick','tiktok','mylive','soop')), 'twitch_channel','youtube_url','kick_channel','tiktok_username','mylive_url','soop_bid')
def candidates():
    base=Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parent
    result=[base/'data'/'settings.json']
    if not getattr(sys,'frozen',False):result.append(base.parent/'broadcast playroom dev'/'data'/'settings.json')
    result.append(Path.home()/'.tts-for-livestream'/'settings.json')
    return result

def load(paths=None):
    merged={}
    for path in paths if paths is not None else candidates():
        try:
            path=Path(path)
            if not path.is_file() or path.stat().st_size>4*1024*1024:continue
            with path.open('r',encoding='utf8') as source:data=json.load(source)
            if not isinstance(data,dict):continue
            result={}
            for key in KEYS:
                value=data.get(key)
                if key=='blocked_users' and isinstance(value,list):
                    result[key]=[item[:200] if isinstance(item,str) else {'name':str(item.get('name',''))[:200], 'hide_overlay':bool(item.get('hide_overlay',True))} for item in value[:2000] if isinstance(item,(str,dict))]
                elif key in ('tts_bot_blacklist','banned_words') and isinstance(value,list):result[key]=[item[:200] for item in value[:2000] if isinstance(item,str)]
                elif key=='overlay_hide_bots' and isinstance(value,bool):result[key]=value
                elif key=='twitch_bot_name' and isinstance(value,str):result[key]=value[:200]
                elif (key in ('dns_enabled','ask_post_result') or key.startswith('auto_connect_')) and isinstance(value,bool):result[key]=value
                elif key in ('twitch_channel','youtube_url','kick_channel','tiktok_username','mylive_url','soop_bid') and isinstance(value,str):result[key]=value[:500]
                elif key in ('dns_service','dns_custom') and isinstance(value,str):result[key]=value[:500]
            for key,value in result.items():merged.setdefault(key,value)
        except (OSError,ValueError,TypeError):continue
    return merged
