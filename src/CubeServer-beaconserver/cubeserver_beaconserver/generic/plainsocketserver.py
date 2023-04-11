"""A simple SSL socket server for the beacon

The beacon will connect to this server (with proper auth)
"""

from errno import EAGAIN
import socket
import ssl
import logging

class PlainSocketServer:
    def __init__(
        self,
        host = "localhost",
        port = 8888
    ):
        """
        Initialize the PlainSocketServer with the specified parameters.

        :param host: The IP address of the server to bind to.
        :type host: str
        :param port: The port number to bind the server to.
        :type port: int
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.connect_hook = None

    def run_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        logging.info("Listening on {host}:{port}...".format(host=self.host, port=self.port))

        while True:
            logging.info("Listening...")
            client_socket, client_address = self.server_socket.accept()
            self.sock = client_socket
            logging.info(f"Accepted connection from {client_address}!")

            if self.connect_hook is not None:
                logging.debug("Executing connect hook...")
                self.connect_hook(client_socket)
            else:
                logging.debug("Sending test message...")
                client_socket.send(b"Connection Established!")
            logging.info("Closing socket.")
            client_socket.close()

    def on_connect(self, decorated_method):
        """A decorator for a method of the following declaration:
        connect_hook(client_ssl_socket)
        ...to be run every time a connection is made.
        A new connection cannot be established until this method exits.
        """
        if self.connect_hook is not None:
            raise ValueError("A connect hook has already been registered!")
        self.connect_hook = decorated_method

    def rx_bytes(self, size: int, chunkby: int = 256) -> bytes:
        """Receives a given number of bytes from the station"""
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
            if recvd == 0:
                del recvd
                break
        return response

    def tx_bytes(self, stuff: bytes) -> int:
        """Sends some stuff and returns an int return code"""
        if self.sock is None:
            return ConnectionError("Connection not established")
        #while sent < len(stuff):
        #    sent += self.sock.send(stuff[sent:])
        #    if self.v:
        #        print(f"Sent {sent}/{len(stuff)} bytes")
        # #self.sock.flush()
        self.sock.sendall(stuff)
