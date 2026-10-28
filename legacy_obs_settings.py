"""Import only OBS connection settings from an old local installation."""
import json,os
from pathlib import Path
from legacy_user_filters import candidates

def migrate(service, paths=None, obs_config_path=None):
    if service.path.exists():return False
    for path in paths if paths is not None else candidates():
        try:
            path=Path(path)
            if not path.is_file() or path.stat().st_size>4*1024*1024:continue
            with path.open(encoding='utf-8') as stream:data=json.load(stream)
            if not isinstance(data,dict) or not isinstance(data.get('obs_ws_enabled'),bool):continue
            enabled=data['obs_ws_enabled'];host=data.get('obs_ws_host','localhost');port=data.get('obs_ws_port',4455);password=data.get('obs_ws_password','')
            if enabled and not password:
                config=Path(obs_config_path) if obs_config_path else Path(os.environ.get('APPDATA') or '')/'obs-studio'/'plugin_config'/'obs-websocket'/'config.json'
                try:
                    if config.is_file() and config.stat().st_size<=1024*1024:
                        with config.open(encoding='utf-8') as stream:password=json.load(stream).get('server_password','') or ''
                except (OSError,ValueError,AttributeError):pass
            if service.path.exists():return False
            service.save({'enabled':enabled,'host':host,'port':port,'password':password})
            return True
        except (OSError,ValueError,TypeError,AttributeError):continue
    return False
