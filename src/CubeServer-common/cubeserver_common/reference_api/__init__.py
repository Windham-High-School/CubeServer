"""Describes the API used to send requests the the reference command server

See CubeServer-beaconserver.reference
"""

import logging
import socket

from cubeserver_common.config import REFERENCE_COMMAND_PORT
from . import protocol

class DispatcherClient:
    """A class for sending requests to the reference server"""

    def __init__(self, timeout: int=10, host='127.0.0.1', port=REFERENCE_COMMAND_PORT):
        """Connects to the reference dispatcher server via a tcpip socket"""
        self.timeout = timeout
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(timeout)
        self.sock.connect((host, port))
    
    def request(self, req: protocol.ReferenceRequest) -> protocol.ReferenceResponse:
        """Sends a request to the reference server and returns the response"""
        self.sock.setblocking(True)
        self.sock.send(req.dump())
        return protocol.ReferenceResponse.from_socket(self.sock)

    def close(self):
        """Closes the socket"""
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
