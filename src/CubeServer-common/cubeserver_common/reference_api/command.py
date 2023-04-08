"""Describes a command to be sent to a reference station

The communication scheme will occur as follows:
"""

import dataclasses
import enum
import struct


class ReferenceSignal(enum.Enum):
    NUL  = b'\x00'
    ACK  = b'\x06'
    NAK  = b'\x15'
    EOT  = b'\x04'
    ENQ  = b'\x05'

class ReferenceCommand(enum.Enum):
    NULL = b'\x00'
    MEAS = b'\x01'
    NOOP = b'\x02'
    STAT = b'\x03'

@dataclasses.dataclass
class ReferenceRequest:
    """A command to be sent to a reference station
    """
    id:      bytes            = bytes(1)
    signal:  ReferenceSignal  = ReferenceSignal.NUL
    command: ReferenceCommand = ReferenceCommand.NULL
    param:   bytes            = bytes(1)

    def dump(self) -> bytes:
        """Dumps the request to a byte string"""
        return b''.join([
            self.id,
            self.signal.value,
            self.command.value,
            self.param,
            ReferenceSignal.EOT
        ])

@dataclasses.dataclass
class ReferenceResponse:
    """A response from the reference station
    """
    signal:      ReferenceSignal = ReferenceSignal.NUL
    length:      bytes           = bytes(1)
    struct_type: bytes           = bytes(1)
    response:    bytes           = bytes(0)

    def dump(self) -> bytes:
        """Dumps the response to a byte string"""
        return b''.join([
            self.signal.value,
            self.length,
            self.struct_type,
            self.response,
            ReferenceSignal.EOT
        ])
    
    def get_value(self) -> bytes | int | bool | float:
        """Unpacks the response value and returns it"""
        return struct.unpack(
            self.struct_type,
            self.response
        )

    def set_value(self, format: str | bytes, value: bytes | int | bool | float) -> None:
        """Packs the given value and encodes it into this response object"""
        self.response = struct.pack(
            self.struct_type,
            value
        )
        self.struct_type = format
