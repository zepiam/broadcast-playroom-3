"""Legacy standalone viewer settings and live connected-provider counts."""
DEFAULTS={'mode':'total','align':'center','icon_size':24,'font_size':18,'font_color':'#ffffff','text_stroke':True,'text_stroke_color':'#000000','text_stroke_width':2,'text_shadow':True,'text_shadow_color':'#000000','text_shadow_blur':3}
def snapshot(layout,statuses):
 settings=(layout or {}).get('legacyTools') or {}
 config={key:settings.get('viewer_overlay_'+key,value) for key,value in DEFAULTS.items()}
 config['font_family']=settings.get('game_overlay_font_family','Kanit');config['font_weight']=settings.get('game_overlay_font_weight','700')
 counts={name:max(0,int(status.get('viewers') or 0)) if status.get('connected') else 0 for name,status in statuses.items()}
 return {'config':config,'counts':{'total':sum(counts.values()),'platforms':counts}}
def configure(settings,values):
 import re
 for key,value in values.items():
  if key in ('mode','align'):
   if value not in ({'off','total','per_platform'} if key=='mode' else {'left','center','right','flex-start','flex-end'}):raise ValueError('Invalid viewer option')
  elif key in ('text_stroke','text_shadow'):value=bool(value)
  elif key.endswith('color'):
   if not re.fullmatch(r'#[0-9a-fA-F]{6}',str(value)):raise ValueError('Invalid viewer color')
  elif key in ('width','height','icon_size','font_size','text_stroke_width','text_shadow_blur','alpha'):
   low,high=(0,1) if key=='alpha' else (80,3840) if key=='width' else (40,2160) if key=='height' else (0,120)
   value=max(low,min(high,float(value)));value=value if key=='alpha' else int(value)
  else:continue
  settings['viewer_overlay_'+key]=value
