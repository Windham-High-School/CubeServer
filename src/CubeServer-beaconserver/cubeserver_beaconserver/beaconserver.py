"""A server for sending stuff to the beacon

The protocol is as follows (B is beacon, S is server):
    B->S    Establish persistent encrypted socket connection
    ...
    S->B    Send command in the form of a byte array
            <Version Byte> <Destination Byte> <Intensity Byte> <Message Length MSB> <Message Length LSB> <8 Reserved Bytes> <Message Bytes> <NULL>
    B->S    Upon receipt of the command, one byte (ACK or NAK)
            At this point, the beacon will transmit the message.
    B->S    After every packet transmission (a few seconds can cause a timeout)
            the beacon will send a byte (TXG) to indicate that it is still transmitting
    B->S    Upon completion of the transmission, a byte (ACK or NAK)
    B->S    Upon completion of the transmission, a byte containing
            the remainder of the length of the message / 255,
            and an unchecked NULL byte 
    ...
"""

from threading import Lock, Event
import logging
from errno import EAGAIN
import time
from ssl import SSLEOFError
import socket

from .sslsocketserver import *
from .beaconmessage import BeaconStatus, BeaconDestination, BeaconCommand

socket.setdefaulttimeout(10.0)

class BeaconServer:
    """A server for dealing with the server-beacon communications"""
    def __init__(self, timeout=10, repeat_attempts=10, **kwargs):
        self.socketserver = SSLSocketServer(timeout, **kwargs)
        self.repeat_attempts = repeat_attempts
        self.sock = None
        self.timeout = timeout
        self.keepalivetime = time.time() + timeout
        self.lock = Lock()
        self.running = False
        self.connection_present = Event()

        @self.socketserver.on_connect
        def connect_hook(client_ssl_socket):
            """Runs on connect from beacon"""
            self.connection_present.set()

            self.keepalivetime = time.time()

            self.sock = client_ssl_socket
            self.sock.settimeout(self.timeout)

            try:
                while True:
                    if not self.connection_present.is_set():
                        break
                    with self.lock: # Lock to prevent multiple threads from sending at once
                        logging.debug("Sending keepalive...")
                        self.sock.setblocking(True)
                        self.sock.send(b'Keep-Alive\x00\x00\x00')
                        if self.rx_bytes(1) != BeaconStatus.ACK.value:
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

    def send_cmd(self, message: BeaconCommand) -> bool:
        """Sends a command to the beacon.
        Returns True on success
        """
        logging.debug("\n\n")
        logging.info(f"send_cmd {message}")
        self.connection_present.wait()
        with self.lock:  # Lock to prevent multiple threads from sending at once
            success = False
            # Send message over:
            self.tx_bytes(message.serialize())

            # Check for ACK:
            response = self.rx_bytes(1)
            if response[0:1] != BeaconStatus.ACK.value:
                logging.debug("No ACK; aborting")
                return False
            logging.debug("Got beacon ACK")

            # Wait for transmission to finish:
            buf = self.rx_bytes(1)
            while buf == BeaconStatus.TXG.value:
                buf = self.rx_bytes(1)
                logging.debug("Got TXG")
            if buf != BeaconStatus.ACK.value:
                return False
            del buf

            # Wait for end of transmission:
            check = self.rx_bytes(2)
            logging.debug("Rx'd okay bytes")
            logging.debug(check[0])
            logging.debug(len(message.message) % 255)
            if check[0] != (len(message.message) % 255):
                logging.debug("Bad checksum")
                return False
            logging.debug("Good length checksum")
            return True

    def run(self):
        """A blocking method that never returns
        Runs the server"""
        self.running = True
        self.socketserver.run_server()

    def tx_bytes(self, stuff: bytes) -> int:
        """Sends some stuff to the beacon and returns an int return code"""
        if self.sock is None:
            return ConnectionError("Connection from the beacon not established")
        self.keepalivetime = time.time()
        self.sock.sendall(stuff)
        logging.debug(f"Sent stuff: \"{stuff}\"")

    def rx_bytes(self, size: int, chunkby: int = 256) -> bytes:
        """Receives a given number of bytes from the beacon"""
        if self.sock is None:
            return ConnectionError("Connection from the beacon not established")
        self.keepalivetime = time.time()
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
            if recvd == 0:
                del recvd
                break
        logging.debug(f"Received stuff: \"{response}\"")
        return response
