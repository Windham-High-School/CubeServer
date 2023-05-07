"""A simple socket server for the beacon

This is heavily based on SSLSocketServer.py, with the SSL stuff stripped out
"""

from errno import EAGAIN
import socket
import logging

class PlainSocketServer:
    def __init__(
        self,
        timeout: int = 10,
        host = "localhost",
        port = 8888
    ):
        """
        Initialize the PlainSocketServer with the specified parameters.

        :param host: The IP address of the server to bind to.
        :type host: str
        :param port: The port number to bind the server to.
        :type port: int
        :param certfile: The path to the certificate file used by the server for SSL.
        :type certfile: str
        :param keyfile: The path to the key file used by the server for SSL.
        :type keyfile: str
        :param ca_certs: The path to a file containing a set of concatenated CA certificates in PEM format.
        :type ca_certs: str
        :param client_cert_reqs: The certificate requirements for client authentication. Can be either ssl.CERT_NONE, ssl.CERT_OPTIONAL or ssl.CERT_REQUIRED.
        :type client_cert_reqs: int (one of ssl.CERT_NONE, ssl.CERT_OPTIONAL, ssl.CERT_REQUIRED)
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.connect_hook = None
        self.timeout = timeout

    def run_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        logging.info("Listening on {host}:{port}...".format(host=self.host, port=self.port))

        self.server_socket.settimeout(self.timeout)

        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                logging.info(f"Accepted connection from {client_address}!")

                try:
                    if self.connect_hook is not None:
                        logging.debug("Executing connect hook...")
                        self.connect_hook(client_socket)
                    else:
                        logging.debug("Sending test message...")
                        client_socket.send(b"Connection Established!")
                except Exception as e:
                    logging.error(f"Error in connect hook: {e}")
                finally:
                    logging.info("Closing socket.")
                    client_socket.close()
            except socket.timeout:
                continue

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
