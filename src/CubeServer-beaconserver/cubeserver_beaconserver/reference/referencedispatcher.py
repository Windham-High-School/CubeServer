"""A server to redirect request to reference stations via ReferenceServer instances"""

from ssl import SSLEOFError
import time

from cubeserver_common.reference_api import protocol
from cubeserver_common.models.team import Team, TeamLevel

from ..generic.plainsocketserver import *
from .referenceserver import ReferenceServer

class ReferenceDispatcherServer:
    """A server for dealing with the server-beacon communications"""
    def __init__(self, routing_id_map: map[int,ReferenceServer], listen_port: int, timeout: int, **kwargs):
        self.socketserver = PlainSocketServer(port=listen_port, **kwargs)
        self.timeout = timeout

        @self.socketserver.on_connect
        def connect_hook(client_socket):
            """Runs on connect from internal api"""
            self.sock = client_socket
            self.sock.settimeout(self.timeout)

            try:
                with self.lock: # Lock to prevent multiple threads from sending at once
                    self.sock.setblocking(True)
                    # Figure out how to route the request
                    req = protocol.ReferenceRequest.from_bytes(self.rx_bytes(6))
                    if req.routing_id not in routing_id_map:
                        self.sock.send(protocol.ReferenceSignal.NACK.value)
                        return
                    self.sock.send(protocol.ReferenceSignal.ACK.value)
                    # Send the request to the appropriate reference server
                    routing_id_map[req.routing_id].tx_bytes(req.dump())

                    # Wait for response from reference server
                    # <version><signal><length><struct_type><response><EOT>
                    version = self.rx_bytes(1)
                    if version != protocol.REFERENCECOM_VERSION:
                        self.sock.send(protocol.ReferenceSignal.NACK.value)
                        return
                    signal = self.rx_bytes(1)
                    if signal != protocol.ReferenceSignal.ACK.value:
                        self.sock.send(protocol.ReferenceSignal.NACK.value)
                        return
                    length = int.from_bytes(self.rx_bytes(1), 'big')
                    struct_type = self.rx_bytes(1)
                    response = self.rx_bytes(length)
                    eot = self.rx_bytes(1)
                    if eot != protocol.ReferenceSignal.EOT.value:
                        self.sock.send(protocol.ReferenceSignal.NACK.value)
                        return
                    
                    # Package response
                    response = protocol.ReferenceResponse(
                        signal=signal,
                        length=length,
                        struct_type=struct_type,
                        response=response
                    )

                    # Send response to internal api
                    self.sock.send(response.dump())

            except SSLEOFError | OSError | EOFError | protocol.ProtocolError as e:
                logging.warn("Error while receiving request from internal api: %s", e)
            finally:
                self.sock = None
                self.connection_present.clear()
            # Socket is closed upon this method's return
            return

    def run(self):
        """A blocking method that never returns
        Runs the server"""
        self.socketserver.run_server()

