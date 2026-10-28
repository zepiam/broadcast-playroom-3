"""Saved local OBS connection and retrying status monitor."""
import json, os, tempfile, threading, time
from urllib.parse import urlsplit, parse_qs
from pathlib import Path

class ObsConnection:
    def __init__(self, path, clip_markers, protect=None, unprotect=None, interval=5, source_ports=None):
        self.path=Path(path); self.clip_markers=clip_markers; self.interval=interval; self.source_ports=source_ports or (lambda: {8801}); self.last_refresh={}
        self.lock=threading.RLock(); self.wake=threading.Event(); self.stopped=threading.Event(); self.thread=None
        self.config={'enabled':False,'host':'127.0.0.1','port':4455,'password':''}; self.state='disabled'; self.generation=0
        self.scene={'connected':False,'scene_name':'','has_overlay':False,'sources':[]}; self.stream={'active':False,'timecode':'','duration_ms':0}; self.event_client=None
        if protect is None or unprotect is None:
            import win32crypt
            protect=lambda data:win32crypt.CryptProtectData(data,'Broadcast Playroom OBS',None,None,None,0)
            unprotect=lambda data:win32crypt.CryptUnprotectData(data,None,None,None,0)[1]
        self.protect=protect; self.unprotect=unprotect
        try:
            if self.path.exists():
                value=json.loads(self.unprotect(self.path.read_bytes()).decode('utf-8'))
                if isinstance(value,dict): self.config.update(value)
                if self.config['enabled']:
                    self.state='waiting'; self.clip_markers.configure(self.config['host'],self.config['port'],self.config['password'])
        except Exception: self.state='error'

    def public(self):
        with self.lock:
            return {'enabled':bool(self.config['enabled']),'host':self.config['host'],'port':self.config['port'], 'has_password':bool(self.config['password']),'state':self.state,'scene':dict(self.scene),'stream':dict(self.stream)}

    def password_for(self, host, port):
        with self.lock:
            return self.config['password'] if self.config['host']==host and self.config['port']==port else ''

    def save(self, data):
        host=data.get('host','').strip(); port=int(data.get('port',0)); password=data.get('password','')
        if not host or len(host)>253 or any(c in host for c in '/\\@?#') or not 1<=port<=65535 or not isinstance(password,str) or len(password)>1024: raise ValueError('invalid')
        with self.lock:
            if not password and not data.get('clear_password'): password=self.config['password']
            new={'enabled':bool(data.get('enabled')),'host':host,'port':port,'password':password}
            blob=self.protect(json.dumps(new,ensure_ascii=False).encode('utf8'))
            self.path.parent.mkdir(parents=True,exist_ok=True); temp=None
            try:
                with tempfile.NamedTemporaryFile(dir=self.path.parent,delete=False) as file: temp=file.name;file.write(blob)
                os.replace(temp,self.path);temp=None
            finally:
                if temp and os.path.exists(temp):os.unlink(temp)
            changed=new != self.config
            self.config=new
            if changed:self.generation+=1;self.state='waiting' if new['enabled'] else 'disabled'
            self.clip_markers.configure(host,port,password) if new['enabled'] else self.clip_markers.configure(None,None,None)
        if changed:self._stop_events()
        self.wake.set();self.start();return self.public()

    def start(self):
        with self.lock:
            if self.thread and self.thread.is_alive():return
            self.thread=threading.Thread(target=self._run,name='OBS-monitor',daemon=True);self.thread.start()

    def stop(self):
        self.stopped.set();self.wake.set()
        self._stop_events()
        if self.thread:self.thread.join(timeout=4)

    def _stop_events(self):
        with self.lock: client=self.event_client;self.event_client=None
        if client:
            try:client.unsubscribe()
            except Exception:pass

    def _start_events(self, obs, config, generation):
        if not hasattr(obs, 'EventClient'):return
        client=None
        try:
            client=obs.EventClient(host=config['host'],port=config['port'],password=config['password'],timeout=3)
            def on_current_program_scene_changed(data):self.wake.set()
            def on_scene_item_enable_state_changed(data):self.wake.set()
            def on_scene_item_created(data):self.wake.set()
            def on_scene_item_removed(data):self.wake.set()
            def on_scene_item_list_reindexed(data):self.wake.set()
            def on_input_settings_changed(data):self.wake.set()
            def on_input_name_changed(data):self.wake.set()
            def on_stream_state_changed(data):self.wake.set()
            client.callback.register((on_current_program_scene_changed,on_scene_item_enable_state_changed,on_scene_item_created,on_scene_item_removed,on_scene_item_list_reindexed,on_input_settings_changed,on_input_name_changed,on_stream_state_changed))
            with self.lock:
                if generation==self.generation and not self.stopped.is_set():self.event_client=client;client=None
        except Exception:pass  # polling remains available when event subscription is unavailable
        finally:
            if client:
                try:client.unsubscribe()
                except Exception:pass

    def _inspect_scene(self, client):
        current=client.get_current_program_scene()
        name=getattr(current,'current_program_scene_name',getattr(current,'scene_name','')) or ''
        sources=[]
        allowed_ports=set(self.source_ports())
        def visit(scene_name, group=False, path=()):
            # Nested scene references can be cyclic. Only inspect visible ancestors.
            if not scene_name or scene_name in path or len(path)>=16:return
            try:
                response=client.get_group_scene_item_list(scene_name) if group else client.get_scene_item_list(scene_name)
                items=response.scene_items or []
            except Exception:return
            for item in items:
                if not item.get('sceneItemEnabled',True):continue
                source=item.get('sourceName','')
                if not source:continue
                if item.get('isGroup') or item.get('inputKind')=='group':
                    visit(source,True,path+(scene_name,));continue
                if item.get('sourceType')=='OBS_SOURCE_TYPE_SCENE' or item.get('inputKind')=='scene':
                    visit(source,False,path+(scene_name,));continue
                if item.get('inputKind')!='browser_source':continue
                try:
                    url=urlsplit(str((client.get_input_settings(source).input_settings or {}).get('url','')))
                    if url.scheme!='http' or url.hostname not in ('localhost','127.0.0.1') or url.port not in allowed_ports or url.path not in ('/','/composer','/composer.html'):continue
                    query=parse_qs(url.query);pinned=(query.get('p') or query.get('page') or [None])[0]
                    sources.append({'source_name':source,'is_pinned':bool(pinned),'pinned_page':pinned})
                except Exception:continue
        visit(name)
        return {'connected':True,'scene_name':name,'has_overlay':bool(sources),'sources':sources}

    def _inspect_stream(self, client):
        status=client.get_stream_status()
        return {'active':bool(getattr(status,'output_active',False)),'timecode':str(getattr(status,'output_timecode','') or ''),'duration_ms':int(getattr(status,'output_duration',0) or 0)}

    def _refresh_sources(self, client):
        allowed_paths={'/','/composer','/composer.html','/overlay.html','/chat-widget','/giveaway','/giveaway_overlay.html','/playroom-widget','/playroom.html','/viewer_overlay.html'}
        try: inputs=client.get_input_list().inputs or []
        except Exception:return
        for source in inputs:
            try:
                if source.get('inputKind')!='browser_source':continue
                name=source.get('inputName','')
                if not name:continue
                settings=client.get_input_settings(name).input_settings or {}
                url=urlsplit(str(settings.get('url','')))
                if url.scheme!='http' or url.hostname not in ('localhost','127.0.0.1') or url.port not in set(self.source_ports()) or url.path not in allowed_paths:continue
                now=time.monotonic()
                if now-self.last_refresh.get(name,0)<30:continue
                client.press_input_properties_button(name,'refreshnocache');self.last_refresh[name]=now
            except Exception:continue

    def _run(self):
        while not self.stopped.is_set():
            with self.lock: config=dict(self.config); generation=self.generation
            if config['enabled']:
                client=None
                try:
                    import obsws_python as obs
                    client=obs.ReqClient(host=config['host'],port=config['port'],password=config['password'],timeout=3)
                    client.get_version(); state='connected'
                    with self.lock: fresh=generation==self.generation and self.state!='connected'
                    if fresh:
                        self._refresh_sources(client);self._start_events(obs,config,generation)
                    try:scene=self._inspect_scene(client)
                    except Exception:scene={'connected':True,'scene_name':'','has_overlay':False,'sources':[]}
                    try:
                        stream=self._inspect_stream(client)
                        if generation==self.generation:self.clip_markers.update_stream(stream['active'])
                    except Exception:stream={'active':False,'timecode':'','duration_ms':0}
                except Exception:
                    state='waiting';scene={'connected':False,'scene_name':'','has_overlay':False,'sources':[]};stream={'active':False,'timecode':'','duration_ms':0};self._stop_events()
                finally:
                    if client:
                        try:client.base_client.ws.close()
                        except Exception:pass
                with self.lock:
                    if generation==self.generation:self.state=state;self.scene=scene;self.stream=stream
            else:
                with self.lock:self.scene={'connected':False,'scene_name':'','has_overlay':False,'sources':[]};self.stream={'active':False,'timecode':'','duration_ms':0}
            self.wake.wait(min(self.interval,1.5));self.wake.clear()
