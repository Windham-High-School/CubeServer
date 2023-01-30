"""A simple SSL socket server for the beacon

The beacon will connect to this server (with proper auth)
"""

import socket
import ssl
import hashlib

class SSLSocketServer:
    def __init__(self, host, port, certfile, keyfile, ca_certs, client_cert_reqs):
        self.host = host
        self.port = port
        self.certfile = certfile
        self.keyfile = keyfile
        self.ca_certs = ca_certs
        self.client_cert_reqs = client_cert_reqs
        self.server_socket = None

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print("Listening on {host}:{port}...".format(host=self.host, port=self.port))

        while True:
            client_socket, client_address = self.server_socket.accept()
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

            client_ssl_socket.send(b"Welcome to the SSL-encrypted server!")
            client_ssl_socket.close()
