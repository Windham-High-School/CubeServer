"""Data Structures for Beacon-Server Communications"""

from enum import Enum, unique

from cubeserver_common.models.beaconmessage import BeaconMessage, OutputDestination

BEACONCOM_VERSION = b'\x01'

@unique
class BeaconStatus(Enum):
    ACK = b'\x06'
    NAK = b'\x15'
    NUL = b'\x00'

@unique
class BeaconDestination(Enum):
    RED = b'\x01'
    IR  = b'\x02'

    @classmethod
    def from_OutputDestination(cls, database_doc: OutputDestination):
        return {
            OutputDestination.IR: BeaconDestination.IR,
            OutputDestination.RED: BeaconDestination.RED
        }[database_doc.destination]

class BeaconCommand:
    """Describes a command sent to the beacon-
    <Version Byte> <Destination Byte> <Intensity Byte> <Message Length MSB> <Message Length LSB> <8 Reserved Bytes> <Message Bytes> <NULL>
    """
    def __init__(
        self,
        dest: BeaconDestination,
        intensity: int,
        message: bytes
    ):
        self.dest = dest
        self.intensity = intensity.to_bytes(1, 'big')

        self.message = message

    @classmethod
    def from_BeaconMessage(cls, database_doc: BeaconMessage):
        """Creates a BeaconCommand instance from a BeaconMessage database document"""
        instance = cls(
            BeaconDestination.from_OutputDestination(database_doc.destination),
            database_doc.intensity,
            database_doc.full_message_bytes
        )
        instance.db_doc = database_doc
        return instance

    def serialize(self) -> bytes:
        """Serializes the command/message to bytes
        that can be sent as a packet to the beacon
        """
        if self.db_doc:  # Mark this as having been processed...
            self.db_doc.past = True
            self.db_doc.save()
        length = len(self.message).to_bytes(2, 'big')
        return b''.join(
            [
                BEACONCOM_VERSION,
                self.dest.value,
                self.intensity,
                length,
                bytes(8),
                self.message,
                BeaconStatus.NUL.value
            ]
        )
