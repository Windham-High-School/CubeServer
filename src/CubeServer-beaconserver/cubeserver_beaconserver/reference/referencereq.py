"""Data Structures for Reference-Server Communications"""

from enum import Enum, unique
from dataclasses import dataclass

from cubeserver_common.models.datapoint import DataClass, DataPoint

REFERENCECOM_VERSION = b'\x01'

@unique
class ReferenceStatus(Enum):
    ACK = b'\x06'
    NAK = b'\x15'
    NUL = b'\x00'

@unique
class MeasurementType(Enum):
    TEMP = b'\x01'
    PRES = b'\x02'

    _dc_map = {
            DataClass.TEMPERATURE: TEMP,
            DataClass.PRESSURE: PRES
        }

    @classmethod
    def from_DataClass(cls, od: DataClass):
        """Converts from DataClass to MeasurementType"""
        return cls._dc_map[od]
    
    def to_DataClass(self):
        """Returns the equivalent DataClass"""
        return {v: k for k, v in self._dc_map.items()}[self]

class ReferenceCommand:
    """Describes a command sent to the reference station-
    <Version Byte> <Type Byte> <5 Reserved Bytes> <NULL>
    """
    def __init__(
        self,
        type_req: MeasurementType
    ):
        self.type_req = type_req

    def serialize(self) -> bytes:
        """Serializes the command/message to bytes
        that can be sent as a packet to the station
        """
        return b''.join(
            [
                REFERENCECOM_VERSION,
                self.type_req.value,
                bytes(5),
                ReferenceCommand.NUL.value
            ]
        )
