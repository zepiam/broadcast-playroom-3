"""HTTP server on IPv4 and IPv6 loopback only; retain the same advertised port."""
import errno, socket, threading
from http.server import ThreadingHTTPServer

class _IPv6LoopbackServer(ThreadingHTTPServer):
    address_family=socket.AF_INET6
    def server_bind(self):
        self.socket.setsockopt(socket.IPPROTO_IPV6,socket.IPV6_V6ONLY,1)
        super().server_bind()

class LoopbackServer(ThreadingHTTPServer):
    def __init__(self,address,handler):
        super().__init__(address,handler)
        self.ipv6_server=None
        try:self.ipv6_server=_IPv6LoopbackServer(('::1',self.server_port),handler)
        except OSError as error:
            if error.errno==errno.EADDRINUSE or getattr(error,'winerror',None)==10048:
                super().server_close()
                raise OSError(f'Loopback port {self.server_port} is busy on IPv6') from error
            # IPv6 may be disabled; retain the IPv4 listener.
            self.ipv6_server=None
        self.ipv6_thread=None
    def serve_forever(self,poll_interval=0.5):
        if self.ipv6_server:
            self.ipv6_thread=threading.Thread(target=self.ipv6_server.serve_forever,kwargs={'poll_interval':poll_interval},daemon=True)
            self.ipv6_thread.start()
        try:super().serve_forever(poll_interval=poll_interval)
        finally:
            if self.ipv6_server and self.ipv6_thread:
                self.ipv6_server.shutdown();self.ipv6_thread.join(timeout=2)
    def server_close(self):
        super().server_close()
        if self.ipv6_server:self.ipv6_server.server_close()
