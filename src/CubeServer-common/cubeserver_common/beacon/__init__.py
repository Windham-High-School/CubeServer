"""
    A package for interfacing to the IR beacon
"""

from .beaconmessage import BeaconMessage, BeaconMessageEncoding

class Beacon:
    """An abstraction for the beacon electronics
    """

    def __init__(self, ) -> None:
        pass

    def transmit(self, message: bytes):
        """Sends a transmission

        Args:
            message (bytes): the message to transmit
        """

        # TODO: Implement actual transmission!
        print(message.encode('utf-8'))
