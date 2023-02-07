"""
"""

from .beaconserver import SSLSocketServer
from . import scheduler
from sys import argv

print("Creating Beacon Server")
server = SSLSocketServer(
    host=argv[1],
    port=int(argv[2])
)

print("Running Beacon Server")
server.run_server()
