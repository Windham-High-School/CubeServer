"""A simple SSL socket server for the beacon

The beacon will connect to this server (with proper auth)
"""

import socket
import ssl
import hashlib

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

    def run_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print("Listening on {host}:{port}...".format(host=self.host, port=self.port))

        while True:
            print("Listening...")
            client_socket, client_address = self.server_socket.accept()
            print(f"Accepted connection from {client_address}!")
            print("Wrapping...")
            client_ssl_socket = ssl.wrap_socket(client_socket,
                                                server_side=True,
                                                certfile=self.certfile,
                                                keyfile=self.keyfile,
                                                ca_certs=self.ca_certs,
                                                cert_reqs=self.client_cert_reqs)

            client_cert = client_ssl_socket.getpeercert(True)
            client_fingerprint = hashlib.sha256(client_cert).hexdigest()

            # Compare the client's fingerprint to the expected fingerprint
            if False: #client_fingerprint != self.fingerprint:
                print("Rejected connection from {addr} due to invalid fingerprint".format(addr=client_address))
                client_ssl_socket.close()
                continue

            print("Sending message...")
            client_ssl_socket.send(b"Connection Established!")
            print("Closing socket.")
            client_ssl_socket.close()
