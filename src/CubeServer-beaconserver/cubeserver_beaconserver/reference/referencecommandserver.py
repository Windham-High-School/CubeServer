"""A server to redirect request to reference stations via ReferenceServer instances"""

import time

from cubeserver_common.models.team import Team, TeamLevel

from ..generic.plainsocketserver import *
from .referencereq import ReferenceStatus, MeasurementType, ReferenceCommand
from .referenceserver import ReferenceServer

class ReferenceServer:
    """A server for dealing with the server-beacon communications"""
    def __init__(self, routing_id_map: map[int,int], listen_port: int, timeout: int, **kwargs):
        self.socketserver = PlainSocketServer(port=listen_port, **kwargs)
        self.timeout = timeout

        @self.socketserver.on_connect
        def connect_hook(client_socket):
            """Runs on connect from internal api"""
            self.sock = client_socket
            self.sock.settimeout(self.timeout)

            try:
                # Wait/blockuntil connection ends before accepting another:
                while True:
                    if self.busy:  # TODO: Implement this busy-wait with asyncio or something
                        time.sleep(1)
                        continue
                    logging.debug("Sending keepalive...")
                    self.sock.setblocking(False)
                    self.sock.send(b'Keep-Alive\x00\x00\x00')
                    self.sock.setblocking(True)
                    if self.socketserver.rx_bytes(1) != ReferenceStatus.ACK.value:
                        return
                    # Connection is still alive!
                    time.sleep(5)
            except EOFError:
                pass

            # Socket is closed upon this method's return
            return

    def run(self):
        """A blocking method that never returns
        Runs the server"""
        self.socketserver.run_server()

