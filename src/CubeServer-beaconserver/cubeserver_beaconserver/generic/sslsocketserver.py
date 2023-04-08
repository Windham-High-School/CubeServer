"""A simple SSL socket server for the beacon

The beacon will connect to this server (with proper auth)
"""

from errno import EAGAIN
import socket
import ssl
import logging

class SSLSocketServer:
    def __init__(
        self,
        host = "localhost",
        port = 8888,
        certfile = "/etc/ssl/beacon_cert/server.pem",
        keyfile = "/etc/ssl/beacon_cert/server.key",
        ca_certs = "/etc/ssl/beacon_cert/beacon.pem",
        client_cert_reqs = ssl.CERT_REQUIRED
    ):
        """
        Initialize the SSLSocketServer with the specified parameters.

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
        self.certfile = certfile
        self.keyfile = keyfile
        self.ca_certs = ca_certs
        self.client_cert_reqs = client_cert_reqs
        self.server_socket = None
        self.connect_hook = None

        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.check_hostname = False
        self.context.load_verify_locations(self.ca_certs)
        self.context.verify_mode = self.client_cert_reqs
        self.context.load_cert_chain(self.certfile, self.keyfile)
        self.context.minimum_version = ssl.TLSVersion.TLSv1_2

    def run_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        logging.info("Listening on {host}:{port}...".format(host=self.host, port=self.port))

        while True:
            logging.info("Listening...")
            client_socket, client_address = self.server_socket.accept()
            logging.info(f"Accepted connection from {client_address}!")
            client_ssl_socket = self.context.wrap_socket(client_socket,
#                                                certfile=self.certfile,
#                                                keyfile=self.keyfile,
                                                server_side=True)

            #client_cert = client_ssl_socket.getpeercert(True)

            if self.connect_hook is not None:
                logging.debug("Executing connect hook...")
                self.connect_hook(client_ssl_socket)
            else:
                logging.debug("Sending test message...")
                client_ssl_socket.send(b"Connection Established!")
            logging.info("Closing socket.")
            client_ssl_socket.close()

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