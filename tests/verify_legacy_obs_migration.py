import sys,tempfile,json,base64,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from obs_connection import ObsConnection
from clip_markers import ClipMarkers
from legacy_obs_settings import migrate
enc=lambda b:base64.b64encode(b);dec=lambda b:base64.b64decode(b)
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);old=root/'old.json';old.write_text(json.dumps({'obs_ws_enabled':True,'obs_ws_host':'localhost','obs_ws_port':4455,'obs_ws_password':'','secret':'do-not-copy'}));h=hashlib.sha256(old.read_bytes()).digest()
 cfg=root/'obs.json';cfg.write_text(json.dumps({'server_password':'private-password'}));service=ObsConnection(root/'new.dat',ClipMarkers(root/'markers'),enc,dec);service.start=lambda:None
 assert migrate(service,[old],cfg);assert service.public()['enabled'] and service.public()['has_password'];assert 'private-password' not in str(service.public()) and b'private-password' not in service.path.read_bytes();assert service.clip_markers._connection[2]=='private-password'
 service.save({'enabled':False,'host':'localhost','port':4455,'password':'','clear_password':True});assert not migrate(service,[old],cfg);assert not service.public()['enabled'];assert hashlib.sha256(old.read_bytes()).digest()==h
 print('PASS legacy OBS import with encrypted password, existing settings preserved and source unchanged')
