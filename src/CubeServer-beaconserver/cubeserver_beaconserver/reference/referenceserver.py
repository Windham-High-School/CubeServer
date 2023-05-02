"""A server for sending stuff to the reference cubes' connections

This is a modified version of the BeaconServer class from the beaconserver.py file.

The protocol is as follows (R is reference, S is server):
    R->S    Establish persistent encrypted socket connection
    ...
    S->R    Send command in the form of a byte array (see ReferenceCommand)
    R->S    Upon receipt of the command, one byte (ACK or NAK)
            At this point, the reference station will grab the specified data
    R->S    Upon completion of the collection, a response (see ReferenceCommand)
    ...
"""

import logging
from threading import Lock, Event

import struct
from errno import EAGAIN
import time
from ssl import SSLEOFError
import socket

from cubeserver_common.models.team import Team, TeamLevel
from cubeserver_common.reference_api import protocol

from ..generic.sslsocketserver import *

socket.setdefaulttimeout(10.0)

class ReferenceServer:
    """A server for dealing with the server-beacon communications"""
    def __init__(self, reference_team: Team, timeout=10, repeat_attempts=10, **kwargs):
        if reference_team.weight_class != TeamLevel.REFERENCE:
            raise ValueError("The provided team is not a reference team")
        self.team = reference_team
        tcp_port = reference_team.reference_port
        self.socketserver = SSLSocketServer(port=tcp_port, **kwargs)
        self.repeat_attempts = repeat_attempts
        self.sock = None
        self.timeout = timeout
        self.keepalivetime = time.time() + timeout
        self.lock = Lock()
        self.running = False
        self.connection_present = Event()

        @self.socketserver.on_connect
        def connect_hook(client_ssl_socket):
            """Runs on connect from station"""
            self.connection_present.set()

            self.keepalivetime = time.time()

            self.sock = client_ssl_socket
            self.sock.settimeout(self.timeout)

            try:
                # Wait/blockuntil connection ends before accepting another:
                while True:
                    if not self.connection_present.is_set():
                        break
                    with self.lock: # Lock to prevent multiple threads from sending at once
                        logging.debug("Sending keepalive...")
                        self.sock.setblocking(True)
                        self.sock.send(b'Keep-Alive\x00\x00\x00')
                        if self.rx_bytes(1) != protocol.ReferenceSignal.ACK.value:
                            self.connection_present.clear()
                            return
                        self.keepalivetime = time.time()
                        # Connection is still alive!
                    time.sleep(2.5)  # Send keepalive every 5 seconds
            except SSLEOFError:
                pass
            finally:
                self.sock = None
                self.connection_present.clear()

            self.keepalivetime = time.time()

            # Socket is closed upon this method's return
            return

    @property
    def is_stale(self) -> bool:  # Don't worry about stale connection if there never was one-
        """Returns True if the connection is stale"""
        return self.connection_present.is_set() and time.time() - self.keepalivetime > self.timeout

    # def send_cmd(self, message: BeaconCommand) -> bool:
    #     """Sends a command to the beacon.
    #     Returns True on success
    #     """
    #     logging.debug("\n\n")
    #     logging.info(f"send_cmd {message}")
    #     self.connection_present.wait()
    #     with self.lock:  # Lock to prevent multiple threads from sending at once
    #         success = False
    #         # Send message over:
    #         self.tx_bytes(message.serialize())

    #         # Check for ACK:
    #         response = self.rx_bytes(1)
    #         if response[0:1] != BeaconStatus.ACK.value:
    #             logging.debug("No ACK; aborting")
    #             return False
    #         logging.debug("Got beacon ACK")

    #         # Wait for transmission to finish:
    #         buf = self.rx_bytes(1)
    #         while buf == BeaconStatus.TXG.value:
    #             buf = self.rx_bytes(1)
    #             logging.debug("Got TXG")
    #         if buf != BeaconStatus.ACK.value:
    #             return False
    #         del buf

    #         # Wait for end of transmission:
    #         check = self.rx_bytes(2)
    #         logging.debug("Rx'd okay bytes")
    #         logging.debug(check[0])
    #         logging.debug(len(message.message) % 255)
    #         if check[0] != (len(message.message) % 255):
    #             logging.debug("Bad checksum")
    #             return False
    #         logging.debug("Good length checksum")
    #         return True

    def run(self):
        """A blocking method that never returns
        Runs the server"""
        self.running = True
        self.socketserver.run_server()

    def tx_bytes(self, stuff: bytes) -> int:
        """Sends some stuff to the reference station and returns an int return code"""
        if self.sock is None:
            return ConnectionError("Connection from the station not established")
        self.keepalivetime = time.time()
        self.sock.sendall(stuff)
        logging.debug(f"Sent stuff: \"{stuff}\"")

    def rx_bytes(self, size: int, chunkby: int = 256) -> bytes:
        """Receives a given number of bytes from the reference station and returns them"""
        if self.sock is None:
            return ConnectionError("Connection from the station not established")
        self.keepalivetime = time.time()
        self.sock.setblocking(True)
        response = b""
        while True:
            buf = bytearray(min(size-len(response), chunkby))
            try:
                recvd = self.sock.recv_into(buf, min(size-len(response), chunkby))
                if buf.rfind(bytearray(protocol.ReferenceSignal.EOT.value)) >= 0:
                    recvd -= 1
                    break
            except OSError as e:
                if e.errno == EAGAIN:
                    recvd = -1
                else:
                    raise
            response += buf
            del buf
            if recvd == 0:
                del recvd
                break
        logging.debug(f"Received stuff: \"{response}\"")
        return response
