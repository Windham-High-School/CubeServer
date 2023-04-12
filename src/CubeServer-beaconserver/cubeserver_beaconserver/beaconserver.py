"""A server for sending stuff to the beacon

The protocol is as follows (B is beacon, S is server):
    B->S    Establish persistent encrypted socket connection
    ...
    S->B    Send command in the form of a byte array
            <Version Byte> <Destination Byte> <Intensity Byte> <Message Length MSB> <Message Length LSB> <8 Reserved Bytes> <Message Bytes> <NULL>
    B->S    Upon receipt of the command, one byte (ACK or NAK)
            At this point, the beacon will transmit the message.
    B->S    Upon completion of the transmission, a byte containing
            the remainder of the length of the message / 255,
            and a NULL byte 
    ...
"""

import logging
from errno import EAGAIN
import time
from ssl import SSLEOFError

from .sslsocketserver import *
from .beaconmessage import BeaconStatus, BeaconDestination, BeaconCommand

class BeaconServer:
    """A server for dealing with the server-beacon communications"""
    def __init__(self, timeout=10, repeat_attempts=10, **kwargs):
        self.socketserver = SSLSocketServer(**kwargs)
        self.repeat_attempts = repeat_attempts
        self.sock = None
        self.timeout = timeout
        self.busy = False

        @self.socketserver.on_connect
        def connect_hook(client_ssl_socket):
            """Runs on connect from beacon"""
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
                    if self.rx_bytes(1) != BeaconStatus.ACK.value:
                        return
                    # Connection is still alive!
                    time.sleep(5)
            except SSLEOFError:
                pass

            # Socket is closed upon this method's return
            return

    def send_cmd(self, message: BeaconCommand) -> bool:
        """Sends a command to the beacon.
        Returns True on success
        """
        logging.debug("\n\n")
        logging.debug(f"send_cmd {message}")
        self.busy = True
        success = False
        for _ in range(self.repeat_attempts):
            logging.debug("\tANOTHER ATTEMPT TO SEND CMD")
            # Send message over:
            self.tx_bytes(message.serialize())
            # Check for ACK:
            response = self.rx_bytes(1)
            if response[0:1] != BeaconStatus.ACK.value:
                logging.debug("No ACK; Resending message")
                continue
            logging.debug("Got beacon ACK")
            # Wait for end of transmission:
            check = self.rx_bytes(2)
            logging.debug("Rx'd okay bytes")
            logging.debug(check[0])
            logging.debug(len(message.message) % 255)
            if check[0] != (len(message.message) % 255):
                continue
            logging.debug("Good length checksum")
            
            success = True
            break
        self.busy = False
        return success

    def run(self):
        """A blocking method that never returns
        Runs the server"""
        self.socketserver.run_server()

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
        """Receives a given number of bytes from the beacon"""
        logging.debug(f"Blocking read for {size} bytes...")
        if self.sock is None:
            return ConnectionError("Connection from the beacon not established")
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