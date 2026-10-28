import sys,socket,threading
from pathlib import Path
from http.server import BaseHTTPRequestHandler
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from loopback_server import LoopbackServer
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):self.send_response(200);self.send_header('Content-Length','2');self.end_headers();self.wfile.write(b'ok')
 def log_message(self,*args):pass
server=LoopbackServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
try:
 for address in ['127.0.0.1']+(['::1'] if server.ipv6_server else []):
  with socket.create_connection((address,server.server_port),timeout=3) as client:
   client.sendall(b'GET / HTTP/1.0\r\nHost: localhost\r\n\r\n');assert b'200 OK' in client.recv(4096)
 assert server.server_address[0]=='127.0.0.1'
 if server.ipv6_server:assert server.ipv6_server.server_address[0]=='::1'
 print('PASS IPv4/IPv6 loopback only same port')
finally:server.shutdown();thread.join(timeout=5);server.server_close()
assert not thread.is_alive()
