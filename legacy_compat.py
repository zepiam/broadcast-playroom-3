"""Fixed legacy listener ports. A busy port is reported, never silently renumbered."""
import json
import threading
import socket
from pathlib import Path
from loopback_server import LoopbackServer

DEFAULT_PORTS = {'composer_compat': 8080, 'chat': 8765, 'playroom': 8766, 'viewer': 8790}


def make_server(handler_class, view, port):
    if int(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            if probe.connect_ex(('127.0.0.1', int(port))) == 0:
                raise OSError(f'Port {port} is already in use')
    class LegacyHandler(handler_class):
        legacy_view = 'composer' if view == 'composer_compat' else view
    return LoopbackServer(('127.0.0.1', int(port)), LegacyHandler)


def start_servers(handler_class, main_port, config_path=None):
    ports = dict(DEFAULT_PORTS)
    if config_path and Path(config_path).is_file():
        raw = json.loads(Path(config_path).read_text(encoding='utf-8'))
        for view in ports:
            if view in raw:
                value = int(raw[view])
                if not 1 <= value <= 65535:
                    raise ValueError(f'Invalid legacy port for {view}')
                ports[view] = value
    servers, statuses = [], []
    for view, port in ports.items():
        if port == main_port:
            continue
        try:
            server = make_server(handler_class, view, port)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            servers.append(server)
            statuses.append({'view': view, 'port': port, 'status': 'online'})
            print(f'[LEGACY] {view}: http://localhost:{port}/', flush=True)
        except OSError as error:
            statuses.append({'view': view, 'port': port, 'status': 'unavailable'})
            print(f'[LEGACY] Port {port} unavailable for {view}; close the previous app or check legacy_compat.json. {error}', flush=True)
    return servers, statuses
