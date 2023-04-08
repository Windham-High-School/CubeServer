"""A server for sending stuff to the reference cubes' connections
"""

import logging
import struct
from errno import EAGAIN
import time
from ssl import SSLEOFError

from cubeserver_common.models.team import Team, TeamLevel

from ..generic.sslsocketserver import *
from .referencereq import ReferenceStatus, ReferenceCommand

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
        self.busy = False

        @self.socketserver.on_connect
        def connect_hook(client_ssl_socket):
            """Runs on connect from station"""
            self.sock = client_ssl_socket
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
                    if self.rx_bytes(1) != ReferenceStatus.ACK.value:
                        return
                    # Connection is still alive!
                    time.sleep(5)
            except SSLEOFError:
                pass

            # Socket is closed upon this method's return
            return

    def send_cmd(self, cmd: ReferenceCommand) -> any:
        """Sends a command to a reference; returns the response
        """
        logging.debug("\n\n")
        logging.debug(f"send_cmd {cmd}")
        self.busy = True
        success = False
        for _ in range(self.repeat_attempts):
            logging.debug("\tANOTHER ATTEMPT TO SEND CMD")
            # Send message over:
            self.tx_bytes(cmd.serialize())
            # Check for ACK:
            response = self.rx_bytes(1)
            if response[0:1] != ReferenceStatus.ACK.value:
                logging.debug("No ACK; Resending message")
                continue
            logging.debug("Got reference ACK")
            # Get and unpack response- <n bytes><struct type><byte 1><byte 2>...<byte n>
            # Example response:  b'\x04fy\xe9\xf6B' => 4-byte float: 123.456
            response_length = int(self.rx_bytes(1)[0])
            response_type = str(self.rx_bytes(1))
            bin_val = self.rx_bytes(response_length)
            actual_val = struct.unpack(response_type, bin_val)
            logging.debug("Rx'd response:")
            logging.debug(actual_val)            
            return actual_val
        self.busy = False
        return None

    def run(self):
        """A blocking method that never returns
        Runs the server"""
        self.socketserver.run_server()


# TODO: Avoid repeated code from beaconserver.py
    def tx_bytes(self, stuff: bytes) -> int:
        """Sends some stuff to the beacon and returns an int return code"""
        logging.debug(f"Sending stuff:\n{stuff}")
        if self.sock is None:
            return ConnectionError("Connection from the beacon not established")
        logging.debug(f"Writing {stuff}")
        #while sent < len(stuff):
        #    sent += self.sock.send(stuff[sent:])
        #    if self.v:
        #        print(f"Sent {sent}/{len(stuff)} bytes")
        # #self.sock.flush()
        self.sock.sendall(stuff)

    def rx_bytes(self, size: int, chunkby: int = 256) -> bytes:
        """Receives a given number of bytes from the station"""
        logging.debug(f"Blocking read for {size} bytes...")
        if self.sock is None:
            return ConnectionError("Connection from the station not established")
        self.sock.setblocking(True)
        response = b""
        while True:
            buf = bytearray(min(size-len(response), chunkby))
            try:
                recvd = self.sock.recv_into(buf, min(size-len(response), chunkby))
            except OSError as e:
                if e.errno == EAGAIN:
                    recvd = -1
                else:
                    raise
            response += buf
            del buf
            logging.debug(f"Received {recvd} bytes")
            if recvd == 0:
                del recvd
                break
        logging.debug(f"Received stuff:\n{response}")
        return response
